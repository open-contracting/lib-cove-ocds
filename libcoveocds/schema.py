import functools
import json
import logging
import os
import warnings
import zipfile
from collections import defaultdict
from copy import deepcopy
from urllib.parse import urljoin

import requests
from libcove.lib.common import SchemaJsonMixin, get_schema_codelist_paths, load_codelist, load_core_codelists
from ocdsextensionregistry.exceptions import ExtensionCodelistWarning, ExtensionWarning
from ocdsextensionregistry.profile_builder import ProfileBuilder

import libcoveocds.config

logger = logging.getLogger(__name__)


class SchemaOCDS(SchemaJsonMixin):
    def _set_schema_version(self, version):
        schema_version_choice = self.version_choices[version]

        # cove-ocds uses version, e.g. when a user changes the version to validate against.
        self.version = version
        # lib-cove uses schema_host in get_schema_validation_errors(). (This is a URL, not a host.)
        self.schema_host = schema_version_choice[1]
        # Needed by ProfileBuilder.
        self._schema_tag = schema_version_choice[2]

    def __init__(self, select_version=None, package_data=None, lib_cove_ocds_config=None, record_pkg=False):
        """Build the schema object using an specific OCDS schema version

        The version used will be select_version, package_data.get('version') or
        default version, in that order. Invalid version choices in select_version or
        package_data will be skipped and registered as self.invalid_version_argument
        and self.invalid_version_data respectively.
        """
        self.config = lib_cove_ocds_config or libcoveocds.config.LibCoveOCDSConfig()

        # lib-cove uses schema_name in get_schema_validation_errors() if extended is set.
        self.schema_name = "release-schema.json"
        # lib-cove uses version_choices in common_checks_context() via getattr().
        self.version_choices = self.config.config["schema_version_choices"]

        # Report errors in web UI.
        self.missing_package = False
        self.invalid_version_argument = False
        self.invalid_version_data = False

        self._set_schema_version(self.config.config["schema_version"])

        if package_data:
            if "version" not in package_data:
                self._set_schema_version("1.0")
            if "releases" not in package_data and "records" not in package_data:
                self.missing_package = True

        # The selected version overrides the default version and the data version.
        if select_version:
            if select_version in self.version_choices:
                self._set_schema_version(select_version)
            else:
                self.invalid_version_argument = True

                # If invalid, use the "version" field in the data.
                select_version = None

        self.extensions = {}
        if isinstance(package_data, dict):
            if not select_version:
                package_version = package_data.get("version")
                if package_version:
                    if package_version in self.version_choices:
                        self._set_schema_version(package_version)
                    else:
                        self.invalid_version_data = True

            extensions = package_data.get("extensions")
            if isinstance(extensions, list):
                self.extensions = {extension: {} for extension in extensions if isinstance(extension, str)}

        #: The profile builder instance for this package's extensions.
        self.builder = ProfileBuilder(self._schema_tag, list(self.extensions))
        # Initialize extensions once.
        self.builder_extensions = list(self.builder.extensions())

        self.schema_url = urljoin(self.schema_host, "release-schema.json")
        if record_pkg:
            basename = "record-package-schema.json"
        else:
            basename = "release-package-schema.json"
        self.pkg_schema_url = urljoin(self.schema_host, basename)

        self.record_pkg = record_pkg
        if record_pkg:
            self.release_schema = SchemaOCDS(
                select_version=select_version,
                package_data=package_data,
                lib_cove_ocds_config=lib_cove_ocds_config,
                record_pkg=False,
            )

        self.json_deref_error = None
        self.invalid_extension = {}
        self.extended = False
        self.extended_schema_file = None
        self.extended_schema_url = None
        self.codelists = self.config.config["schema_codelists"]["1.1"]

    @functools.lru_cache
    def standard_codelists(self):
        try:
            # OCDS 1.0 uses "code" column.
            # https://github.com/open-contracting/standard/blob/1__0__3/standard/schema/codelists/organizationIdentifierRegistrationAgency_iati.csv  # noqa: 501
            return {
                codelist.name: set(row.get("Code", row.get("code")) for row in codelist.rows)
                for codelist in self.builder.standard_codelists()
            }
        except requests.RequestException as e:
            logger.exception(e)
            return set()

    def process_codelists(self):
        # lib-cove uses these in get_additional_codelist_values().
        # - Used to determine whether a field has a codelist, which codelist and whether it is open.
        self.extended_codelist_schema_paths = get_schema_codelist_paths(self, use_extensions=True)
        # - Used with the `in` operator, to determine whether a codelist is from an extension.
        self.core_codelists = self.standard_codelists()
        # - Used with get(), and the return value is used with `in`, to determine whether a code is included.
        self.extended_codelists = deepcopy(self.core_codelists)
        # - Used to populate "codelist_url" and "codelist_amend_urls".
        self.extended_codelist_urls = defaultdict(list)

        # standard_codelists() returns an empty set on HTTP error. If so, don't cache this empty set, and return.
        if not self.core_codelists:
            self.standard_codelists.cache_clear()
            return

        for extension in self.builder_extensions:
            input_url = extension.input_url
            failed_codelists = self.extensions[input_url]["failed_codelists"]

            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always", category=ExtensionCodelistWarning)

                try:
                    # An unreadable metadata file or a malformed extension URL raises an error.
                    extension_codelists = extension.codelists
                except (requests.RequestException, NotImplementedError):
                    # apply_extensions() will have recorded the metadata file being unreadable.
                    continue

                for warning in w:
                    if issubclass(warning.category, ExtensionWarning):
                        exception = warning.message.exc
                        if isinstance(exception, requests.HTTPError):
                            message = f"{exception.response.status_code}: {exception.response.reason}"
                        elif isinstance(exception, (requests.RequestException, zipfile.BadZipFile)):
                            message = "Couldn't be retrieved"
                        elif isinstance(exception, UnicodeDecodeError):
                            message = "Has non-UTF-8 characters"
                        else:
                            message = f"Unknown Exception, {e}"
                        failed_codelists[warning.message.codelist] = message

            for name, codelist in extension_codelists.items():
                try:
                    codes = set(codelist.codes)
                except KeyError:
                    failed_codelists[name] = 'Has no "Code" column'
                    continue

                if codelist.patch:
                    basename = codelist.basename

                    if basename not in self.core_codelists:
                        failed_codelists[name] = f"References non-existing codelist {basename}"
                        continue

                    patched_codelist = self.extended_codelists[basename]

                    if codelist.addend:
                        patched_codelist |= codes
                    elif codelist.subtrahend:
                        nonexisting_codes = [code for code in codes if code not in patched_codelist]
                        if nonexisting_codes:
                            failed_codelists[name] = f"References non-existing code(s): {', '.join(nonexisting_codes)}"
                        patched_codelist -= codes
                else:
                    self.extended_codelists[name] = codes

                self.extended_codelist_urls[name].append(extension.get_url(f"codelists/{name}"))

    def get_schema_obj(self, deref=False, api=False):
        schema_obj = self._schema_obj
        if self.extended_schema_file:
            with open(self.extended_schema_file) as fp:
                schema_obj = json.load(fp)
        elif self.extensions:
            schema_obj = deepcopy(self._schema_obj)
            self.apply_extensions(schema_obj, api=api)
        if deref:
            if self.extended:
                extended_schema_str = json.dumps(schema_obj)
                schema_obj = self.deref_schema(extended_schema_str)
            else:
                schema_obj = self.deref_schema(self.schema_str)
        return schema_obj

    def get_pkg_schema_obj(self, deref=False, use_extensions=True):
        package_schema_obj = deepcopy(self._pkg_schema_obj)
        if deref:
            if self.extended and use_extensions:

                if self.record_pkg:
                    package_schema_obj = self.deref_schema(self.pkg_schema_str)
                    deref_release_schema_obj = self.release_schema.get_schema_obj(deref=True)
                    package_schema_obj["properties"]["records"]["items"]["properties"][
                        "compiledRelease"
                    ] = deref_release_schema_obj
                    package_schema_obj["properties"]["records"]["items"]["properties"]["releases"]["oneOf"][
                        1
                    ] = deref_release_schema_obj
                else:
                    deref_schema_obj = self.get_schema_obj(deref=True)
                    package_schema_obj["properties"]["releases"]["items"] = {}
                    pkg_schema_str = json.dumps(package_schema_obj)
                    package_schema_obj = self.deref_schema(pkg_schema_str)
                    package_schema_obj["properties"]["releases"]["items"].update(deref_schema_obj)

            else:
                return self.deref_schema(self.pkg_schema_str)
        return package_schema_obj

    def apply_extensions(self, schema_obj, api=False):
        language = self.config.config["current_language"]

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always", category=ExtensionWarning)

            # schema_obj is modified in-place.
            self.builder.patched_release_schema(schema=schema_obj)

            for warning in w:
                if issubclass(warning.category, ExtensionWarning):
                    exception = warning.message.exc
                    if isinstance(exception, requests.HTTPError):
                        message = f"{exception.response.status_code}: {exception.response.reason.lower()}"
                    elif isinstance(exception, (requests.RequestException, zipfile.BadZipFile)):
                        message = "fetching failed"
                    elif isinstance(exception, json.JSONDecodeError):
                        message = "release schema patch is not valid JSON"
                    else:
                        message = str(exception)
                    self.invalid_extension[warning.message.extension.input_url] = message

        for extension in self.builder_extensions:
            input_url = extension.input_url

            # process_codelists() needs this dict.
            details = {"failed_codelists": {}}
            self.extensions[input_url] = details

            # Skip metadata fields in API context.
            if api:
                continue

            details["url"] = input_url
            details["schema_url"] = None

            # ocdsextensionregistry requires the input URL to contain "extension.json" (like the registry). If it
            # doesn't, ocdsextensionregistry can't determine how to retrieve it.
            if not extension.base_url and not extension._url_pattern:
                self.invalid_extension[input_url] = "missing extension.json"
                continue

            try:
                metadata = extension.metadata

                # We *could* check its existence via HTTP, but this is for display only anyway.
                schemas = metadata.get("schemas")
                if isinstance(schemas, list) and "release_schema.json" in schemas:
                    details["schema_url"] = extension.get_url("release-schema.json")

                for field in ("name", "description", "documentationUrl"):
                    language_map = metadata[field]
                    details[field] = language_map.get(language, language_map.get("en", ""))
            except requests.HTTPError as e:
                self.invalid_extension[input_url] = f"{e.response.status_code}: {e.response.reason.lower()}"
            except requests.RequestException:
                self.invalid_extension[input_url] = "fetching failed"
            except json.JSONDecodeError:
                self.invalid_extension[input_url] = "extension metadata is not valid JSON"

        # It's possible for the release schema to be applied, but the metadata file to be unavailable.
        # Nonetheless, for now, preserve prior behavior by reporting as if it were not applied.
        self.extended = len(self.invalid_extension) < len(self.extensions)

    def create_extended_schema_file(self, upload_dir, upload_url, api=False):
        filepath = os.path.join(upload_dir, "extended_schema.json")

        # Always replace any existing extended schema file
        if os.path.exists(filepath):
            os.remove(filepath)
            self.extended_schema_file = None
            self.extended_schema_url = None

        if not self.extensions:
            return

        schema = self.get_schema_obj(api=api)
        if not self.extended:
            return

        with open(filepath, "w") as fp:
            json.dump(schema, fp, ensure_ascii=False, indent=2)
            fp.write("\n")

        self.extended_schema_file = filepath
        self.extended_schema_url = urljoin(upload_url, "extended_schema.json")

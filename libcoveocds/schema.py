import json
import os
import warnings
from copy import deepcopy
from urllib.parse import urljoin

import requests
from libcove.lib.common import SchemaJsonMixin, get_schema_codelist_paths, load_codelist, load_core_codelists
from ocdsextensionregistry.exceptions import ExtensionWarning
from ocdsextensionregistry.profile_builder import ProfileBuilder

import libcoveocds.config


class SchemaOCDS(SchemaJsonMixin):
    def _set_schema_version(self, version):
        schema_version_choice = self.version_choices[version]

        # cove-ocds uses version, e.g. when a user changes the version to validate against.
        self.version = version
        # lib-cove uses schema_host in get_schema_validation_errors(). (This is a URL, not a host.)
        self.schema_host = schema_version_choice[1]
        # Needed by ProfileBuilder.
        self.schema_tag = schema_version_choice[2]

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

    def process_codelists(self):
        core_codelist_schema_paths = get_schema_codelist_paths(self, use_extensions=False)
        self.extended_codelist_schema_paths = get_schema_codelist_paths(self, use_extensions=True)

        core_unique_files = frozenset(value[0] for value in core_codelist_schema_paths.values())
        self.core_codelists = load_core_codelists(self.codelists, core_unique_files, config=self.config)

        self.extended_codelists = deepcopy(self.core_codelists)
        self.extended_codelist_urls = {}

        # load_core_codelists() returns {} on HTTP error. If so, clear the cache.
        if not self.core_codelists:
            load_core_codelists.cache_clear()
            return

        for extension, details in self.extensions.items():
            codelist_list = details.get("codelists")
            if not codelist_list:
                continue

            base_url = "/".join(extension.split("/")[:-1]) + "/codelists/"

            for codelist in codelist_list:
                try:
                    codelist_map = load_codelist(base_url + codelist, config=self.config)
                except UnicodeDecodeError:
                    details["failed_codelists"][codelist] = "Unicode Error, codelists need to be in UTF-8"
                except Exception as e:
                    details["failed_codelists"][codelist] = f"Unknown Exception, {e}"
                    continue

                if not codelist_map:
                    details["failed_codelists"][codelist] = "Codelist Error, Could not find code field in codelist"

                if codelist[0] in ("+", "-"):
                    codelist_extension = codelist[1:]
                    if codelist_extension not in self.extended_codelists:
                        details["failed_codelists"][
                            codelist
                        ] = f"Extension error, Trying to extend non existing codelist {codelist_extension}"
                        continue

                if codelist[0] == "+":
                    self.extended_codelists[codelist_extension].update(codelist_map)
                elif codelist[0] == "-":
                    for code in codelist_map:
                        value = self.extended_codelists[codelist_extension].pop(code, None)
                        if not value:
                            details["failed_codelists"][
                                codelist
                            ] = f"Codelist error, Trying to remove non existing codelist value {code}"
                else:
                    self.extended_codelists[codelist] = codelist_map

                try:
                    self.extended_codelist_urls[codelist].append(base_url + codelist)
                except KeyError:
                    self.extended_codelist_urls[codelist] = [base_url + codelist]

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
        # This indirection is necessary, because ProfileBuilder encapsulates extension handling.
        # This does the reverse of ProfileBuilder.extensions().
        def extension_to_original_url(extension):
            if extension.base_url or extension._url_pattern:
                return extension.get_url("extension.json")
            if extension._file_urls:
                return extension._file_urls["release-schema.json"]
            return extension.download_url

        language = self.config.config["current_language"]

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always", category=ExtensionWarning)

            builder = ProfileBuilder(self.schema_tag, list(self.extensions))
            # schema_obj is modified in-place.
            builder.patched_release_schema(schema=schema_obj)

            for warning in w:
                if issubclass(warning.category, ExtensionWarning):
                    exception = warning.message.exc
                    if isinstance(exception, requests.HTTPError):
                        message = f"{exception.response.status_code}: {exception.response.reason.lower()}"
                    elif isinstance(exception, requests.RequestException):
                        message = "fetching failed"
                    elif isinstance(exception, json.JSONDecodeError):
                        message = "release schema patch is not valid JSON"
                    else:
                        message = str(exception)
                    self.invalid_extension[extension_to_original_url(warning.message.extension)] = message

        self.extended = len(self.invalid_extension) < len(self.extensions)

        for extension in builder.extensions():
            original_url = extension_to_original_url(extension)

            # process_codelists() needs this dict.
            details = {"failed_codelists": {}}
            self.extensions[original_url] = details

            # Skip metadata fields in API context.
            if api:
                continue

            details["url"] = original_url
            details["schema_url"] = None

            # ocdsextensionregistry requires the metadata file to contain extension.json (like the registry). If it
            # doesn't, ocdsextensionregistry can't determine how to retrieve it.
            if not extension.base_url and not extension._url_pattern:
                self.invalid_extension[original_url] = "missing extension.json"
                continue

            try:
                metadata = extension.metadata

                # We *could* check its existence via HTTP, but this is for display only anyway.
                schemas = metadata.get("schemas")
                if isinstance(schemas, list) and "release_schema.json" in schemas:
                    details["schema_url"] = extension.get_url("release-schema.json")

                codelists = metadata.get("codelists")
                if isinstance(codelists, list) and codelists:
                    details["codelists"] = codelists

                for field in ("name", "description", "documentationUrl"):
                    language_map = metadata[field]
                    details[field] = language_map.get(language, language_map.get("en", ""))
            except requests.HTTPError as e:
                self.invalid_extension[original_url] = f"{e.response.status_code}: {e.response.reason.lower()}"
            except requests.RequestException:
                self.invalid_extension[original_url] = "fetching failed"
            except json.JSONDecodeError:
                self.invalid_extension[original_url] = "extension metadata is not valid JSON"

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

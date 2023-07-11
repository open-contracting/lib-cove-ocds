import functools
import json
import logging
import os
import warnings
import zipfile
from collections import defaultdict
from copy import deepcopy
from urllib.parse import urljoin

import jsonref
import requests
from libcove.lib.common import get_schema_codelist_paths, schema_dict_fields_generator
from ocdsextensionregistry.exceptions import DoesNotExist, ExtensionCodelistWarning, ExtensionWarning
from ocdsextensionregistry.profile_builder import ProfileBuilder
from referencing import Registry, Resource

import libcoveocds.config
from libcoveocds.exceptions import OCDSVersionError

logger = logging.getLogger(__name__)


class SchemaOCDS:
    def _set_schema_version(self, version):
        schema_version_choice = self.version_choices[version]

        # lib-cove uses version in common_checks_context() via getattr() to determine whether to set
        # "version_display_choices" and "version_used_display".
        # cove-ocds uses version, e.g. when a user changes the version to validate against.
        self.version = version
        # lib-cove uses schema_host in get_schema_validation_errors() to call CustomRefResolver(). (URL, not host.)
        # The rationale was to allow overriding $ref in schema files. (It would've been easier to edit the schema....)
        # https://github.com/OpenDataServices/cove/commit/ccc46fffe430868a1cb0ddba356c719bb62896b5
        self.schema_host = schema_version_choice[1]
        self._schema_tag = schema_version_choice[2]

    def __init__(self, select_version=None, package_data=None, lib_cove_ocds_config=None, record_pkg=False):
        """Build the schema object using an specific OCDS schema version

        The version used will be select_version, package_data.get('version') or
        default version, in that order. Invalid version choices in select_version or
        package_data will be skipped and registered as self.invalid_version_argument
        and self.invalid_version_data respectively.
        """
        # The main configuration object.
        self.config = lib_cove_ocds_config or libcoveocds.config.LibCoveOCDSConfig()
        # Whether used in an API context.
        self.api = self.config.config["context"] == "api"

        # lib-cove uses schema_name in get_schema_validation_errors() to call CustomRefResolver(), if extended is set.
        # It does this to resolve the release schema $ref to the patched release schema. Although this level of
        # indirection is undesirable, there is no workaround in lib-cove<=0.31.0.
        self.schema_name = "release-schema.json"

        # lib-cove uses codelists in get_additional_codelist_values() for "codelist_url".
        self.codelists = self.config.config["schema_codelists"]["1.1"]
        # lib-cove uses version_choices in common_checks_context() via getattr() for "version_display_choices" and
        # "version_used_display". Re-used in this file for convenience.
        self.version_choices = self.config.config["schema_version_choices"]

        # Report errors in web UI.
        self.missing_package = False
        self.json_deref_error = None  # str
        # Errors are raised instead in API context.
        self.invalid_version_argument = False
        self.invalid_version_data = False

        self._set_schema_version(self.config.config["schema_version"])

        # The selected version overrides the default version and the data version.
        if select_version:
            if select_version in self.version_choices:
                self._set_schema_version(select_version)
            elif self.api:
                raise OCDSVersionError(
                    f"select_version: {select_version} is not one of {', '.join(self.version_choices)}"
                )
            else:
                self.invalid_version_argument = True
                # If invalid, use other strategies.
                select_version = None

        # lib-cove uses extensions in common_checks_context() for "extensions"."extensions".
        # If `self.extensions` is falsy, this logic can be skipped.
        # cove-ocds uses extensions to render extension-related information.
        self.extensions = {}
        if isinstance(package_data, dict):
            if "releases" not in package_data and "records" not in package_data:
                self.missing_package = True
            if not select_version:
                package_version = package_data.get("version")
                if package_version:
                    if package_version in self.version_choices:
                        self._set_schema_version(package_version)
                    elif self.api:
                        raise OCDSVersionError(
                            f"The version in the data is not one of {', '.join(self.version_choices)}"
                        )
                    else:
                        self.invalid_version_data = True

            extensions = package_data.get("extensions")
            if isinstance(extensions, list):
                self.extensions = {extension: {} for extension in extensions if isinstance(extension, str)}

        # (lib-)cove-ocds uses schema_url as a fallback to extended_schema_file, to convert between formats.
        self.schema_url = urljoin(self.schema_host, "release-schema.json")
        # Used in get_pkg_schema_obj() to determine which package to return.
        if record_pkg:
            self._package_schema_name = "record-package-schema.json"
        else:
            self._package_schema_name = "release-package-schema.json"
        # lib-cove uses pkg_schema_url in common_checks_context() for "schema_url".
        self.pkg_schema_url = urljoin(self.schema_host, self._package_schema_name)

        #: The profile builder instance for this package's extensions.
        self.builder = ProfileBuilder(
            self._schema_tag, list(self.extensions), standard_base_url=self.config.config["standard_zip"]
        )
        # Initialize extensions once and preserve locale caches.
        self.builder_extensions = list(self.builder.extensions())

        # lib-cove uses extended in common_checks_context() for "extensions"."is_extended_schema".
        # If `self.extensions` is falsy, this logic can be skipped.
        # cove-ocds uses is_extended_schema to conditionally display content.
        self.extended = False
        # lib-cove uses invalid_extension in common_checks_context() for "extensions"."invalid_extension".
        # If `self.extensions` is falsy, this logic can be skipped.
        # cove-ocds uses invalid_extension to render extension-related errors.
        self.invalid_extension = {}

        # lib-cove uses extended_schema_url in common_checks_context() for "extensions"."extended_schema_url".
        # If `self.extensions` is falsy, this logic can be skipped.
        # cove-ocds uses extended_schema_url to "Get a copy of the schema with extension patches applied".
        self.extended_schema_url = None
        # lib-cove uses extended_schema_file in get_schema_validation_errors() to call CustomRefResolver(), if extended
        # is set. (lib-)cove-ocds uses extended_schema_file to convert between formats, and falls back to schema_url.
        self.extended_schema_file = None

    def _codelist_codes(self, codelist):
        if not codelist.rows:
            return set()
        column = next(column for column in ("Code", "Código", "code") if column in codelist.rows[0])
        return {row[column] for row in codelist.rows}

    def _standard_codelists(self):
        try:
            # OCDS 1.0 uses "code" column. https://github.com/open-contracting/standard/blob/1__0__3/standard/schema/codelists/organizationIdentifierRegistrationAgency_iati.csv  # noqa: 501
            return {codelist.name: self._codelist_codes(codelist) for codelist in self.builder.standard_codelists()}
        except requests.RequestException as e:
            logger.exception(e)
            return {}

    # lib-cove calls this from get_additional_codelist_values().
    @functools.lru_cache
    def process_codelists(self):
        # lib-cove uses these in get_additional_codelist_values().
        # - Used to determine whether a field has a codelist, which codelist and whether it is open.
        self.extended_codelist_schema_paths = get_schema_codelist_paths(self, use_extensions=True)
        # - Used with the `in` operator, to determine whether a codelist is from an extension.
        self.core_codelists = self._standard_codelists()
        # - Used with get(), and the return value is used with `in`, to determine whether a code is included.
        self.extended_codelists = deepcopy(self.core_codelists)
        # - Used to populate "codelist_url" and "codelist_amend_urls".
        self.extended_codelist_urls = defaultdict(list)

        # _standard_codelists() returns an empty dict on HTTP error. If so, don't cache this empty dict, and return.
        if not self.core_codelists:
            self._standard_codelists.cache_clear()
            return

        for extension in self.builder_extensions:
            input_url = extension.input_url

            failed_codelists = self.extensions[input_url].get("failed_codelists")

            # In a web context, skip extensions whose metadata is unavailable.
            if failed_codelists is None:
                continue

            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always", category=ExtensionCodelistWarning)

                try:
                    # An unreadable metadata file or a malformed extension URL raises an error.
                    extension_codelists = extension.codelists
                except (requests.RequestException, NotImplementedError):
                    # patched_release_schema() will have recorded the metadata file being unreadable.
                    continue

                for warning in w:
                    if issubclass(warning.category, ExtensionCodelistWarning):
                        exception = warning.message.exc
                        if isinstance(exception, requests.HTTPError):
                            message = f"{exception.response.status_code}: {exception.response.reason}"
                        elif isinstance(exception, (requests.RequestException, zipfile.BadZipFile)):
                            message = "Couldn't be retrieved"
                        elif isinstance(exception, UnicodeDecodeError):
                            message = "Has non-UTF-8 characters"
                        else:
                            message = f"Unknown error: {exception}"
                        failed_codelists[warning.message.codelist] = message

            for name, codelist in extension_codelists.items():
                try:
                    codes = self._codelist_codes(codelist)
                except StopIteration:
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

    @functools.cached_property
    def registry(self):
        # lib-cove's get_schema_validation_errors() expects a non-dereferenced schema.
        # The cove-ocds test with tenders_releases_1_release_with_extension_broken_json_ref.json fails, otherwise.
        release_schema = Resource.from_contents(self.get_schema_obj())
        versioned_release_schema = Resource.from_contents(
            json.loads(self.builder.get_standard_file_contents("versioned-release-validation-schema.json"))
        )
        return Registry().with_resources(
            [
                (f"{scheme}://standard.open-contracting.org/schema/{self._schema_tag}/{prefix}-schema.json", schema)
                # OCDS 1.0 use the http scheme.
                for scheme in ("http", "https")
                for prefix, schema in (
                    ("release", release_schema),
                    ("versioned-release-validation", versioned_release_schema),
                )
            ]
        )

    def _get_schema(self, name):
        # The ocds_babel.translate.translate() makes these substitutions for published files.
        return json.loads(
            self.builder.get_standard_file_contents(name)
            .replace("{{lang}}", self.config.config["current_language"])
            .replace("{{version}}", self.version)
        )

    # lib-cove calls this from many locations including get_schema_validation_errors().
    # use_extensions is always called as True, so it is ignored.
    #
    # ProfileBuilder.release_package_schema() and record_package_schema() aren't used, because the patched release
    # schema has already been calculated and cached by patched_release_schema().
    #
    # lib-cove resolves the release schema $ref to the patched release schema by overridding jsonschema's resolver. For
    # this to work, lib-cove needs create_extended_schema_file() to have been called before the validator runs, like
    # libcoveocds.api.ocds_json_output() and cove-ocds do.
    #
    # The resolver converts the $ref to its basename, making it impossible to circumvent this logic. It would have been
    # less indirect to set the $ref to the file written by create_extended_schema_file() in this method rather than via
    # the resolver.
    #
    # If using jsonschema>=4.18 and lib-cove#123, self.registry is used to achieve this.
    #
    # For reference, the old code and original commit:
    # https://github.com/open-contracting/lib-cove-ocds/blob/19ed9b3f0e392e9341206c5296d79c4bcc6f1206/libcoveocds/schema.py#L196-L235  # noqa: E501
    # https://github.com/OpenDataServices/cove/commit/1b03d44e3dcfa03313fb6b101075b9732c277ce2
    @functools.lru_cache
    def get_pkg_schema_obj(self, deref=False, use_extensions=True):
        if hasattr(self, "_test_override_package_schema"):
            with open(self._test_override_package_schema) as f:
                if deref:
                    return jsonref.load(f, merge_props=True, proxies=False)
                return json.load(f)
        else:
            schema = self._get_schema(self._package_schema_name)

        if deref:
            patched = self.get_schema_obj(deref=True)
            if self._package_schema_name == "record-package-schema.json":
                schema["definitions"]["record"]["properties"]["compiledRelease"] = patched
                schema["definitions"]["record"]["properties"]["releases"]["oneOf"][1]["items"] = patched
                schema = jsonref.replace_refs(schema, merge_props=True, proxies=False)
            else:
                schema["properties"]["releases"]["items"] = patched

        return schema

    @functools.lru_cache
    def get_schema_obj(self, deref=False):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always", category=ExtensionWarning)

            schema = self.builder.patched_release_schema(schema=self._get_schema("release-schema.json"))
            if deref:
                try:
                    # Preserve "deprecated" as a sibling of "$ref".
                    schema = jsonref.replace_refs(schema, merge_props=True, proxies=False)
                except jsonref.JsonRefError as e:
                    # Callers must check json_deref_error.
                    self.json_deref_error = e.message
                    # This is the prior behavior, however surprising. https://github.com/OpenDataServices/lib-cove/blob/a97f7698d5e5ed519165e930a53fc97cc387362c/libcove/lib/common.py#L393-L405  # noqa: E501
                    schema = {}

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

        language = self.config.config["current_language"]

        for extension in self.builder_extensions:
            input_url = extension.input_url

            # process_codelists() needs this dict.
            details = {"failed_codelists": {}}

            # Skip metadata fields in API context.
            if self.api:
                self.extensions[input_url] = details
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

                # In a web context, set the details only if metadata is available, otherwise cove-ocds' present
                # behavior to create an empty list item for the extension.
                self.extensions[input_url] = details
            except DoesNotExist:
                self.invalid_extension[input_url] = "404: not found"
            except requests.HTTPError as e:
                self.invalid_extension[input_url] = f"{e.response.status_code}: {e.response.reason.lower()}"
            except requests.RequestException:
                self.invalid_extension[input_url] = "fetching failed"
            except json.JSONDecodeError:
                self.invalid_extension[input_url] = "extension metadata is not valid JSON"

        # It's possible for the release schema to be applied, but the metadata file to be unavailable.
        # Nonetheless, for now, preserve prior behavior by reporting as if it were not applied.
        self.extended = len(self.invalid_extension) < len(self.extensions)

        return schema

    # Copied from libcove.lib.common.SchemaJsonMixin.
    @functools.lru_cache
    def get_pkg_schema_fields(self):
        return set(schema_dict_fields_generator(self.get_pkg_schema_obj(deref=True)))

    # This is always called with an `if schema_ocds.extensions` guard.
    def create_extended_schema_file(self, upload_dir, upload_url):
        basename = "extended_schema.json"
        path = os.path.join(upload_dir, basename)

        # Always replace any existing extended schema file
        if os.path.exists(path):
            os.remove(path)
            self.extended_schema_file = None
            self.extended_schema_url = None

        schema = self.get_schema_obj()
        if not self.extended:
            return

        with open(path, "w") as f:
            json.dump(schema, f, ensure_ascii=False, indent=2)
            f.write("\n")
        self.extended_schema_file = path
        self.extended_schema_url = urljoin(upload_url, basename)

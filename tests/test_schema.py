import copy
import json

import pytest
from libcove.lib.common import get_additional_codelist_values

import libcoveocds.config
import libcoveocds.schema
from tests import fixture_path

# Cache for faster tests.
config = libcoveocds.config.LibCoveOCDSConfig()
config.config["cache_all_requests"] = True

DEFAULT_OCDS_VERSION = libcoveocds.config.LIB_COVE_OCDS_CONFIG_DEFAULT["schema_version"]
METRICS_EXT = "https://raw.githubusercontent.com/open-contracting-extensions/ocds_metrics_extension/master/extension.json"  # noqa: E501
API_EXT = "https://chilecompracl.visualstudio.com/a6a3f587-5f23-42f6-9255-ac5852fae1e7/_apis/git/repositories/fb91c43b-011b-434b-901d-9d36ec50c586/items?path=%2Fextension.json&versionDescriptor%5BversionOptions%5D=0&versionDescriptor%5BversionType%5D=0&versionDescriptor%5Bversion%5D=master&resolveLfs=true&%24format=octetStream&api-version=5.0"  # noqa: E501
CODELIST_EXT = "https://raw.githubusercontent.com/INAImexico/ocds_extendedProcurementCategory_extension/0ed54770c85500cf21f46e88fb06a30a5a2132b1/extension.json"  # noqa: E501
UNSUPPORTED_PROTOCOL_EXT = "protocol://example.com/extension.json"
UNRESOLVABLE_HOST_EXT = "http://bad-url-for-extensions.com/extension.json"
NO_EXTENSION_EXT = "https://example.com/not-found"
OTHER_BASENAME_EXT = "https://example.com/not-found/other.json"
NO_FILES_EXT = "https://example.com/not-found/extension.json"
NO_METADATA_EXT = "https://raw.githubusercontent.com/open-contracting/lib-cove-ocds/main/tests/fixtures/extensions/no-metadata/extension.json"  # noqa: E501
INVALID_METADATA_EXT = "https://raw.githubusercontent.com/open-contracting/lib-cove-ocds/main/tests/fixtures/extensions/invalid-metadata/extension.json"  # noqa: E501


@pytest.mark.parametrize("record_pkg", [False, True])
def test_basic_1(record_pkg):
    schema = libcoveocds.schema.SchemaOCDS(record_pkg=record_pkg)

    assert schema.version == "1.1"
    assert schema.schema_url == "https://standard.open-contracting.org/1.1/en/release-schema.json"
    if record_pkg:
        assert schema.pkg_schema_url == "https://standard.open-contracting.org/1.1/en/record-package-schema.json"
    else:
        assert schema.pkg_schema_url == "https://standard.open-contracting.org/1.1/en/release-package-schema.json"
    assert schema.schema_host == "https://standard.open-contracting.org/1.1/en/"
    assert not schema.config.config["cache_all_requests"]


@pytest.mark.parametrize("record_pkg", [False, True])
def test_pass_config_1(record_pkg):

    config = copy.deepcopy(libcoveocds.config.LIB_COVE_OCDS_CONFIG_DEFAULT)
    config["schema_version"] = "1.0"

    lib_cove_ocds_config = libcoveocds.config.LibCoveOCDSConfig(config=config)

    schema = libcoveocds.schema.SchemaOCDS(lib_cove_ocds_config=lib_cove_ocds_config, record_pkg=record_pkg)

    assert schema.version == "1.0"
    assert schema.schema_url == "https://standard.open-contracting.org/1.0/en/release-schema.json"
    if record_pkg:
        assert schema.pkg_schema_url == "https://standard.open-contracting.org/1.0/en/record-package-schema.json"
    else:
        assert schema.pkg_schema_url == "https://standard.open-contracting.org/1.0/en/release-package-schema.json"
    assert schema.schema_host == "https://standard.open-contracting.org/1.0/en/"
    assert not schema.config.config["cache_all_requests"]


@pytest.mark.parametrize(
    ("select_version", "package_data", "version", "invalid_version_argument", "invalid_version_data", "extensions"),
    [
        (None, None, DEFAULT_OCDS_VERSION, False, False, {}),
        ("1.0", None, "1.0", False, False, {}),
        (None, {"version": "1.1"}, "1.1", False, False, {}),
        (None, {"version": "1.1", "extensions": ["c", "d"]}, "1.1", False, False, {"c": {}, "d": {}}),
        ("1.1", {"version": "1.0"}, "1.1", False, False, {}),
        ("1.bad", {"version": "1.1"}, "1.1", True, False, {}),
        ("1.wrong", {"version": "1.bad"}, DEFAULT_OCDS_VERSION, True, True, {}),
        (None, {"version": "1.bad"}, DEFAULT_OCDS_VERSION, False, True, {}),
        (None, {"extensions": ["a", "b"]}, "1.1", False, False, {"a": {}, "b": {}}),
        (None, {"version": "1.1", "extensions": ["a", "b"]}, "1.1", False, False, {"a": {}, "b": {}}),
    ],
)
def test_schema_ocds_constructor(
    select_version, package_data, version, invalid_version_argument, invalid_version_data, extensions
):
    schema = libcoveocds.schema.SchemaOCDS(select_version=select_version, package_data=package_data)
    host = libcoveocds.config.LIB_COVE_OCDS_CONFIG_DEFAULT["schema_version_choices"][version][1]
    url = f"{host}release-package-schema.json"

    assert schema.version == version
    assert schema.schema_host == host
    assert schema.pkg_schema_url == url
    assert schema.invalid_version_argument == invalid_version_argument
    assert schema.invalid_version_data == invalid_version_data
    assert schema.extensions == extensions


@pytest.mark.parametrize(
    ("package_data", "extensions", "invalid_extension", "extended", "extends_schema"),
    [
        (None, {}, {}, False, False),
        ({"version": "1.1", "extensions": [METRICS_EXT]}, {METRICS_EXT: {}}, {}, True, True),
        ({"version": "1.1", "extensions": [API_EXT]}, {API_EXT: {}}, {}, True, True),
        ({"version": "1.1", "extensions": [CODELIST_EXT]}, {CODELIST_EXT: {}}, {}, True, False),
        (
            {"version": "1.1", "extensions": [UNSUPPORTED_PROTOCOL_EXT]},
            {UNSUPPORTED_PROTOCOL_EXT: {}},
            {UNSUPPORTED_PROTOCOL_EXT: "fetching failed"},
            False,
            False,
        ),
        (
            {"version": "1.1", "extensions": [UNRESOLVABLE_HOST_EXT]},
            {UNRESOLVABLE_HOST_EXT: {}},
            {UNRESOLVABLE_HOST_EXT: "fetching failed"},
            False,
            False,
        ),
        (
            {"version": "1.1", "extensions": [NO_EXTENSION_EXT]},
            {NO_EXTENSION_EXT: {}},
            {NO_EXTENSION_EXT: "missing extension.json"},
            False,
            False,
        ),
        (
            {"version": "1.1", "extensions": [OTHER_BASENAME_EXT]},
            {OTHER_BASENAME_EXT: {}},
            {OTHER_BASENAME_EXT: "missing extension.json"},
            False,
            False,
        ),
        (
            {"version": "1.1", "extensions": [NO_FILES_EXT]},
            {NO_FILES_EXT: {}},
            {NO_FILES_EXT: "404: not found"},
            False,
            False,
        ),
        (
            {"version": "1.1", "extensions": [NO_METADATA_EXT]},
            {NO_METADATA_EXT: {}},
            {NO_METADATA_EXT: "404: not found"},
            False,
            False,
        ),
        (
            {"version": "1.1", "extensions": [INVALID_METADATA_EXT]},
            {INVALID_METADATA_EXT: {}},
            {INVALID_METADATA_EXT: "extension metadata is not valid JSON"},
            False,
            False,
        ),
        (
            {"version": "1.1", "extensions": [UNRESOLVABLE_HOST_EXT, METRICS_EXT]},
            {UNRESOLVABLE_HOST_EXT: {}, METRICS_EXT: {}},
            {UNRESOLVABLE_HOST_EXT: "fetching failed"},
            True,
            True,
        ),
    ],
)
def test_schema_ocds_extensions(package_data, extensions, invalid_extension, extended, extends_schema):
    schema = libcoveocds.schema.SchemaOCDS(package_data=package_data, lib_cove_ocds_config=config)
    assert schema.extensions == extensions
    assert not schema.extended

    schema_obj = schema.get_schema_obj()
    assert schema.invalid_extension == invalid_extension
    assert schema.extended is extended

    if extends_schema and METRICS_EXT in extensions:
        assert "Metric" in schema_obj["definitions"]
        assert "agreedMetrics" in schema_obj["definitions"]["Award"]["properties"]
    elif extends_schema and API_EXT in extensions:
        assert "dateCreated" in schema_obj["definitions"]["Contract"]["properties"]
    else:
        assert "Metric" not in schema_obj["definitions"]
        assert not schema_obj["definitions"]["Award"]["properties"].get("agreedMetrics")


# https://github.com/OpenDataServices/cove/issues/1054
@pytest.mark.xfail(reason="lib-cove has a bug")
def test_get_additional_codelist_values_replaced():
    with open(fixture_path("fixtures", "common_checks", "get_additional_codelist_values_replaced.json")) as f:
        package_data = json.load(f)

    # tariffs adds to documentType.csv, then ppp replaces documentType.csv, such that the addition has no consequence.
    # lib-cove's get_additional_codelist_values() determines the correct extension, but the incorrect filename.

    schema_obj = libcoveocds.schema.SchemaOCDS(select_version="1.1", package_data=package_data)
    schema_obj.get_schema_obj()

    additional_codelist_values = get_additional_codelist_values(schema_obj, package_data)

    assert additional_codelist_values["releases/tender/documents/documentType"] == {
        "field": "documentType",
        "codelist": "documentType.csv",
        "path": "releases/tender/documents",
        "codelist_url": "https://raw.githubusercontent.com/open-contracting-extensions/ocds_ppp_extension/master/codelists/documentType.csv",  # noqa
        "extension_codelist": False,
        "isopen": True,
        "codelist_amend_urls": [],
        "values": ["foo"],
    }

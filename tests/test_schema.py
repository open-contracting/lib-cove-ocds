import copy

import pytest

import libcoveocds.config
import libcoveocds.schema

# Cache for faster tests.
config = libcoveocds.config.LibCoveOCDSConfig()
config.config["cache_all_requests"] = True

DEFAULT_OCDS_VERSION = libcoveocds.config.LIB_COVE_OCDS_CONFIG_DEFAULT["schema_version"]
METRICS_EXT = "https://raw.githubusercontent.com/open-contracting-extensions/ocds_metrics_extension/master/extension.json"  # noqa: E501
CODELIST_EXT = "https://raw.githubusercontent.com/INAImexico/ocds_extendedProcurementCategory_extension/0ed54770c85500cf21f46e88fb06a30a5a2132b1/extension.json"  # noqa: E501
UNKNOWN_URL_EXT = "http://bad-url-for-extensions.com/extension.json"
NOT_FOUND_URL_EXT = "https://standard.open-contracting.org/this-file-is-not-found-404.json/en"


@pytest.mark.parametrize("record_pkg", [False, True])
def test_basic_1(record_pkg):
    schema = libcoveocds.schema.SchemaOCDS(record_pkg=record_pkg)

    assert schema.version == "1.1"
    if record_pkg:
        # Ignore schema.schema_name for records, as there's no
        # record-schema.json (this probably causes problems for flatten-tool)
        assert schema.pkg_schema_name == "record-package-schema.json"
    else:
        assert schema.schema_name == "release-schema.json"
        assert schema.pkg_schema_name == "release-package-schema.json"
    assert schema.default_version == "1.1"
    assert schema.default_schema_host == "https://standard.open-contracting.org/1.1/en/"
    assert schema.schema_host == "https://standard.open-contracting.org/1.1/en/"
    assert not schema.config.config["cache_all_requests"]


def test_deprecated_cache_schema_1():
    schema = libcoveocds.schema.SchemaOCDS(cache_schema=True)
    # cache_schema is deprecated but it should still set the new option.
    assert schema.config.config["cache_all_requests"]


@pytest.mark.parametrize("record_pkg", [False, True])
def test_pass_config_1(record_pkg):

    config = copy.deepcopy(libcoveocds.config.LIB_COVE_OCDS_CONFIG_DEFAULT)
    config["schema_version"] = "1.0"

    lib_cove_ocds_config = libcoveocds.config.LibCoveOCDSConfig(config=config)

    schema = libcoveocds.schema.SchemaOCDS(lib_cove_ocds_config=lib_cove_ocds_config, record_pkg=record_pkg)

    assert schema.version == "1.0"
    if record_pkg:
        # Ignore schema.schema_name for records, as there's no
        # record-schema.json (this probably causes problems for flatten-tool)
        assert schema.pkg_schema_name == "record-package-schema.json"
    else:
        assert schema.schema_name == "release-schema.json"
        assert schema.pkg_schema_name == "release-package-schema.json"
    assert schema.default_version == "1.0"
    assert schema.default_schema_host == "https://standard.open-contracting.org/1.0/en/"
    assert schema.schema_host == "https://standard.open-contracting.org/1.0/en/"
    assert not schema.config.config["cache_all_requests"]


@pytest.mark.parametrize(
    ("select_version", "release_data", "version", "invalid_version_argument", "invalid_version_data", "extensions"),
    [
        (None, None, DEFAULT_OCDS_VERSION, False, False, {}),
        ("1.0", None, "1.0", False, False, {}),
        (None, {"version": "1.1"}, "1.1", False, False, {}),
        (None, {"version": "1.1", "extensions": ["c", "d"]}, "1.1", False, False, {"c": (), "d": ()}),
        ("1.1", {"version": "1.0"}, "1.1", False, False, {}),
        ("1.bad", {"version": "1.1"}, "1.1", True, False, {}),
        ("1.wrong", {"version": "1.bad"}, DEFAULT_OCDS_VERSION, True, True, {}),
        (None, {"version": "1.bad"}, DEFAULT_OCDS_VERSION, False, True, {}),
        (None, {"extensions": ["a", "b"]}, "1.0", False, False, {"a": (), "b": ()}),
        (None, {"version": "1.1", "extensions": ["a", "b"]}, "1.1", False, False, {"a": (), "b": ()}),
    ],
)
def test_schema_ocds_constructor(
    select_version, release_data, version, invalid_version_argument, invalid_version_data, extensions
):
    schema = libcoveocds.schema.SchemaOCDS(select_version=select_version, release_data=release_data)
    name = libcoveocds.config.LIB_COVE_OCDS_CONFIG_DEFAULT["schema_name"]["release"]
    host = libcoveocds.config.LIB_COVE_OCDS_CONFIG_DEFAULT["schema_version_choices"][version][1]
    url = host + name

    assert schema.version == version
    assert schema.pkg_schema_name == name
    assert schema.schema_host == host
    assert schema.pkg_schema_url == url
    assert schema.invalid_version_argument == invalid_version_argument
    assert schema.invalid_version_data == invalid_version_data
    assert schema.extensions == extensions


@pytest.mark.parametrize(
    ("release_data", "extensions", "invalid_extension", "extended", "extends_schema"),
    [
        (None, {}, {}, False, False),
        (
            {"version": "1.1", "extensions": [NOT_FOUND_URL_EXT]},
            {NOT_FOUND_URL_EXT: ()},
            {NOT_FOUND_URL_EXT: "404: not found"},
            False,
            False,
        ),
        (
            {"version": "1.1", "extensions": [UNKNOWN_URL_EXT]},
            {UNKNOWN_URL_EXT: ()},
            {UNKNOWN_URL_EXT: "fetching failed"},
            False,
            False,
        ),
        ({"version": "1.1", "extensions": [METRICS_EXT]}, {METRICS_EXT: ()}, {}, True, True),
        ({"version": "1.1", "extensions": [CODELIST_EXT]}, {CODELIST_EXT: ()}, {}, True, False),
        (
            {"version": "1.1", "extensions": [UNKNOWN_URL_EXT, METRICS_EXT]},
            {UNKNOWN_URL_EXT: (), METRICS_EXT: ()},
            {UNKNOWN_URL_EXT: "fetching failed"},
            True,
            True,
        ),
    ],
)
def test_schema_ocds_extensions(release_data, extensions, invalid_extension, extended, extends_schema):
    schema = libcoveocds.schema.SchemaOCDS(release_data=release_data, lib_cove_ocds_config=config)
    assert schema.extensions == extensions
    assert not schema.extended

    schema_obj = schema.get_schema_obj()
    assert schema.invalid_extension == invalid_extension
    assert schema.extended == extended

    if extends_schema:
        assert "Metric" in schema_obj["definitions"].keys()
        assert schema_obj["definitions"]["Award"]["properties"].get("agreedMetrics")
    else:
        assert "Metric" not in schema_obj["definitions"].keys()
        assert not schema_obj["definitions"]["Award"]["properties"].get("agreedMetrics")

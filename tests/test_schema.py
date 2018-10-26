import libcoveocds.schema
import libcoveocds.config
import copy


def test_basic_1():
    schema = libcoveocds.schema.SchemaOCDS()

    assert schema.version == "1.1"
    assert schema.release_schema_name == "release-schema.json"
    assert schema.release_pkg_schema_name == "release-package-schema.json"
    assert schema.record_pkg_schema_name == "record-package-schema.json"
    assert schema.default_version == "1.1"
    assert schema.default_schema_host == "http://standard.open-contracting.org/schema/1__1__3/"
    assert schema.schema_host == "http://standard.open-contracting.org/schema/1__1__3/"
    assert not schema.cache_schema


def test_pass_config_1():

    config = copy.deepcopy(libcoveocds.config.LIB_COVE_OCDS_CONFIG_DEFAULT)
    config['schema_version'] = '1.0'

    lib_cove_ocds_config = libcoveocds.config.LibCoveOCDSConfig(config=config)

    schema = libcoveocds.schema.SchemaOCDS(lib_cove_ocds_config=lib_cove_ocds_config)

    assert schema.version == "1.0"
    assert schema.release_schema_name == "release-schema.json"
    assert schema.release_pkg_schema_name == "release-package-schema.json"
    assert schema.record_pkg_schema_name == "record-package-schema.json"
    assert schema.default_version == "1.0"
    assert schema.default_schema_host == "http://standard.open-contracting.org/schema/1__0__3/"
    assert schema.schema_host == "http://standard.open-contracting.org/schema/1__0__3/"
    assert not schema.cache_schema

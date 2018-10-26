import libcoveocds.schema


def test_basic_1():
    schema = libcoveocds.schema.SchemaOCDS()

    assert schema.version == "1.1"
    assert schema.release_schema_name == "release-schema.json"
    assert schema.release_pkg_schema_name == "release-package-schema.json"
    assert schema.record_pkg_schema_name == "record-package-schema.json"
    assert schema.default_version == "1.1"
    assert schema.default_schema_host == "http://standard.open-contracting.org/schema/1__1__3/"
    assert schema.version == "1.1"
    assert schema.schema_host == "http://standard.open-contracting.org/schema/1__1__3/"
    assert not schema.cache_schema

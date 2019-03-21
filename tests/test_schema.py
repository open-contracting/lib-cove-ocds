import libcoveocds.schema
import libcoveocds.config
import copy
import pytest


DEFAULT_OCDS_VERSION = libcoveocds.config.LIB_COVE_OCDS_CONFIG_DEFAULT['schema_version']
METRICS_EXT = 'https://raw.githubusercontent.com/open-contracting/ocds_metrics_extension/master/extension.json'
CODELIST_EXT = 'https://raw.githubusercontent.com/INAImexico/ocds_extendedProcurementCategory_extension/0ed54770c85500cf21f46e88fb06a30a5a2132b1/extension.json' # noqa
UNKNOWN_URL_EXT = 'http://bad-url-for-extensions.com/extension.json'
NOT_FOUND_URL_EXT = 'http://example.com/extension.json'


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


@pytest.mark.parametrize(('select_version', 'release_data', 'version', 'invalid_version_argument',
                          'invalid_version_data', 'extensions'), [
    (None, None, DEFAULT_OCDS_VERSION, False, False, {}),
    ('1.0', None, '1.0', False, False, {}),
    (None, {'version': '1.1'}, '1.1', False, False, {}),
    (None, {'version': '1.1', 'extensions': ['c', 'd']}, '1.1', False, False, {'c': (), 'd': ()}),
    ('1.1', {'version': '1.0'}, '1.1', False, False, {}),
    ('1.bad', {'version': '1.1'}, '1.1', True, False, {}),
    ('1.wrong', {'version': '1.bad'}, DEFAULT_OCDS_VERSION, True, True, {}),
    (None, {'version': '1.bad'}, DEFAULT_OCDS_VERSION, False, True, {}),
    (None, {'extensions': ['a', 'b']}, '1.0', False, False, {'a': (), 'b': ()}),
    (None, {'version': '1.1', 'extensions': ['a', 'b']}, '1.1', False, False, {'a': (), 'b': ()})
])
def test_schema_ocds_constructor(select_version, release_data, version, invalid_version_argument,
                                 invalid_version_data, extensions):
    schema = libcoveocds.schema.SchemaOCDS(select_version=select_version, release_data=release_data)
    name = libcoveocds.config.LIB_COVE_OCDS_CONFIG_DEFAULT['schema_name']['release']
    host = libcoveocds.config.LIB_COVE_OCDS_CONFIG_DEFAULT['schema_version_choices'][version][1]
    url = host + name

    assert schema.version == version
    assert schema.release_pkg_schema_name == name
    assert schema.schema_host == host
    assert schema.release_pkg_schema_url == url
    assert schema.invalid_version_argument == invalid_version_argument
    assert schema.invalid_version_data == invalid_version_data
    assert schema.extensions == extensions


@pytest.mark.parametrize(('release_data', 'extensions', 'invalid_extension', 'extended', 'extends_schema'), [
    (None, {}, {}, False, False),
    ({'version': '1.1', 'extensions': [NOT_FOUND_URL_EXT]}, {NOT_FOUND_URL_EXT: ()},
     {NOT_FOUND_URL_EXT: '404: not found'}, False, False),
    ({'version': '1.1', 'extensions': [UNKNOWN_URL_EXT]}, {UNKNOWN_URL_EXT: ()},
     {UNKNOWN_URL_EXT: 'fetching failed'}, False, False),
    ({'version': '1.1', 'extensions': [METRICS_EXT]}, {METRICS_EXT: ()}, {}, True, True),
    ({'version': '1.1', 'extensions': [CODELIST_EXT]}, {CODELIST_EXT: ()}, {}, True, False),
    ({'version': '1.1', 'extensions': [UNKNOWN_URL_EXT, METRICS_EXT]}, {UNKNOWN_URL_EXT: (), METRICS_EXT: ()},
     {UNKNOWN_URL_EXT: 'fetching failed'}, True, True),
])
def test_schema_ocds_extensions(release_data, extensions, invalid_extension, extended, extends_schema):
    schema = libcoveocds.schema.SchemaOCDS(release_data=release_data)
    assert schema.extensions == extensions
    assert not schema.extended

    release_schema_obj = schema.get_release_schema_obj()
    assert schema.invalid_extension == invalid_extension
    assert schema.extended == extended

    if extends_schema:
        assert 'Metric' in release_schema_obj['definitions'].keys()
        assert release_schema_obj['definitions']['Award']['properties'].get('agreedMetrics')
    else:
        assert 'Metric' not in release_schema_obj['definitions'].keys()
        assert not release_schema_obj['definitions']['Award']['properties'].get('agreedMetrics')
import json
import os
import pytest
from collections import OrderedDict
from libcoveocds.schema import SchemaOCDS
from libcoveocds.libcore.common import get_additional_codelist_values, get_schema_validation_errors, \
    get_json_data_generic_paths, get_json_data_deprecated_fields, get_json_data_missing_ids, get_fields_present, \
    _get_schema_non_required_ids, _get_schema_deprecated_paths


def test_get_additional_codelist_values():
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fixtures', 'common', 'tenders_releases_2_releases_codelists.json')) as fp: # noqa
        json_data_w_additial_codelists = json.load(fp)

    schema_obj = SchemaOCDS(select_version='1.1')
    additional_codelist_values = get_additional_codelist_values(schema_obj, json_data_w_additial_codelists)

    assert additional_codelist_values == {
        ('releases/tag'): {
            'codelist': 'releaseTag.csv',
            'codelist_url': 'https://raw.githubusercontent.com/open-contracting/standard/1.1/standard/schema/codelists/releaseTag.csv', # noqa
            'codelist_amend_urls': [],
            'field': 'tag',
            'extension_codelist': False,
            'isopen': False,
            'path': 'releases',
            'values': ['oh no']
        },
        ('releases/tender/items/classification/scheme'): {
            'codelist': 'itemClassificationScheme.csv',
            'codelist_url': 'https://raw.githubusercontent.com/open-contracting/standard/1.1/standard/schema/codelists/itemClassificationScheme.csv', # noqa
            'codelist_amend_urls': [],
            'extension_codelist': False,
            'field': 'scheme',
            'isopen': True,
            'path': 'releases/tender/items/classification',
            'values': ['GSINS']}
    }


def test_get_schema_validation_errors():
    schema_obj = SchemaOCDS(select_version='1.0')
    schema_name = schema_obj.release_pkg_schema_name

    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fixtures', 'common', 'tenders_releases_2_releases.json')) as fp: # noqa
        error_list = get_schema_validation_errors(json.load(fp), schema_obj, schema_name, {}, {})
        assert len(error_list) == 0
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fixtures', 'common', 'tenders_releases_2_releases_invalid.json')) as fp: # noqa
        error_list = get_schema_validation_errors(json.load(fp), schema_obj, schema_name, {}, {})
        assert len(error_list) > 0


def test_get_json_data_generic_paths():
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fixtures', 'common', 'tenders_releases_2_releases_with_deprecated_fields.json')) as fp: # noqa
        json_data_w_deprecations = json.load(fp)

    generic_paths = get_json_data_generic_paths(json_data_w_deprecations)
    assert len(generic_paths.keys()) == 36
    assert generic_paths[('releases', 'buyer', 'name')] == {
        ('releases', 1, 'buyer', 'name'): 'Parks Canada',
        ('releases', 0, 'buyer', 'name'): 'Agriculture & Agrifood Canada'
    }


def test_get_json_data_deprecated_fields():
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fixtures', 'common',
                           'tenders_releases_2_releases_with_deprecated_fields.json')) as fp:  # noqa
        json_data_w_deprecations = json.load(fp)

    schema_obj = SchemaOCDS()
    schema_obj.schema_host = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fixtures', 'common/')
    schema_obj.release_pkg_schema_name = 'release_package_schema_ref_release_schema_deprecated_fields.json'
    schema_obj.release_pkg_schema_url = os.path.join(schema_obj.schema_host, schema_obj.release_pkg_schema_name)
    json_data_paths = get_json_data_generic_paths(json_data_w_deprecations)
    deprecated_data_fields = get_json_data_deprecated_fields(json_data_paths, schema_obj)
    expected_result = OrderedDict([
        ('initiationType', {"paths": ('releases/0', 'releases/1'),
                            "explanation": ('1.1', 'Not a useful field as always has to be tender')}),
        ('quantity', {"paths": ('releases/0/tender/items/0',),
                      "explanation": ('1.1', 'Nobody cares about quantities')})
    ])
    for field_name in expected_result.keys():
        assert field_name in deprecated_data_fields
        assert expected_result[field_name]["paths"] == deprecated_data_fields[field_name]["paths"]
        assert expected_result[field_name]["explanation"] == deprecated_data_fields[field_name]["explanation"]


@pytest.mark.parametrize('json_data', [
    '{"version":"1.1", "releases":{"buyer":{"additionalIdentifiers":[]}, "initiationType": "tender"}}',
    # TODO: add more ...
])
def test_corner_cases_for_deprecated_data_fields(json_data):
    data = json.loads(json_data)
    schema = SchemaOCDS(release_data=data)
    json_data_paths = get_json_data_generic_paths(data)
    deprecated_fields = get_json_data_deprecated_fields(json_data_paths, schema)

    assert deprecated_fields['additionalIdentifiers']['explanation'][0] == '1.1'
    assert 'parties section at the top level of a release' in deprecated_fields['additionalIdentifiers']['explanation'][1] # noqa
    assert deprecated_fields['additionalIdentifiers']['paths'] == ('releases/buyer',)
    assert len(deprecated_fields.keys()) == 1
    assert len(deprecated_fields['additionalIdentifiers']['paths']) == 1


def test_get_json_data_missing_ids():
    file_name = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'fixtures', 'common', 'tenders_releases_2_releases_1_1_tenderers_with_missing_ids.json' # noqa
    )
    with open(os.path.join(file_name)) as fp:
        user_data = json.load(fp)

    schema_obj = SchemaOCDS(release_data=user_data)
    results = [
        'releases/0/tender/tenderers/1/id',
        'releases/0/tender/tenderers/2/id',
        'releases/0/tender/tenderers/5/id',
        'releases/1/tender/tenderers/1/id',
        'releases/1/tender/tenderers/2/id',
        'releases/1/tender/tenderers/4/id'
    ]
    user_data_paths = get_json_data_generic_paths(user_data)
    missin_ids_paths = get_json_data_missing_ids(user_data_paths, schema_obj)

    assert missin_ids_paths == results


def test_fields_present_1():
    assert get_fields_present({}) == {}


def test_fields_present_2():
    assert get_fields_present({'a': 1, 'b': 2}) == {"/a": 1, "/b": 1}


def test_fields_present_3():
    assert get_fields_present({'a': {}, 'b': 2}) == {'/a': 1, '/b': 1}


def test_fields_present_4():
    assert get_fields_present({'a': {'c': 1}, 'b': 2}) == {'/a': 1, '/b': 1, '/a/c': 1}


def test_fields_present_5():
    assert get_fields_present({'a': {'c': 1}, 'b': 2}) == {'/a': 1, '/b': 1, '/a/c': 1}


def test_fields_present_6():
    assert get_fields_present({'a': {'c': {'d': 1}}, 'b': 2}) == {'/a': 1, '/b': 1, '/a/c': 1, '/a/c/d': 1}


def test_fields_present_7():
    assert get_fields_present({'a': [{'c': 1}], 'b': 2}) == {'/a': 1, '/b': 1, '/a/c': 1}


def test_fields_present_8():
    assert get_fields_present({'a': {'c': [{'d': 1}]}, 'b': 2}) == {'/a': 1, '/b': 1, '/a/c': 1, '/a/c/d': 1}


def test_fields_present_9():
    assert get_fields_present({'a': {'c_1': [{'d': 1}]}, 'b_1': 2}) == {'/a': 1, '/a/c_1': 1, '/a/c_1/d': 1, '/b_1': 1}


def test_fields_present_10():
    assert get_fields_present({'a': {'c_1': [{'d': 1}, {'d': 1}]}, 'b_1': 2}) == {'/a': 1, '/a/c_1': 1, '/a/c_1/d': 2, '/b_1': 1} # noqa


def test_get_schema_deprecated_paths():
    schema_obj = SchemaOCDS()
    schema_obj.schema_host = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fixtures', 'common/')
    schema_obj.release_pkg_schema_name = 'release_package_schema_ref_release_schema_deprecated_fields.json'
    schema_obj.release_pkg_schema_url = os.path.join(schema_obj.schema_host, schema_obj.release_pkg_schema_name)
    deprecated_paths = _get_schema_deprecated_paths(schema_obj)
    expected_results = [
        (('releases', 'initiationType'), ('1.1', 'Not a useful field as always has to be tender')),
        (('releases', 'planning',), ('1.1', "Testing deprecation for objects with '$ref'")),
        (('releases', 'tender', 'hasEnquiries'), ('1.1', 'Deprecated just for fun')),
        (('releases', 'contracts', 'items', 'quantity'), ('1.1', 'Nobody cares about quantities')),
        (('releases', 'tender', 'items', 'quantity'), ('1.1', 'Nobody cares about quantities')),
        (('releases', 'awards', 'items', 'quantity'), ('1.1', 'Nobody cares about quantities'))
    ]
    assert len(deprecated_paths) == 6
    for path in expected_results:
        assert path in deprecated_paths


def test_get_schema_non_required_ids():
    schema_obj = SchemaOCDS(select_version="1.1")
    non_required_ids = _get_schema_non_required_ids(schema_obj)
    results = [
        ('releases', 'awards', 'amendments', 'id'),
        ('releases', 'awards', 'suppliers', 'id'),
        ('releases', 'contracts', 'amendments', 'id'),
        ('releases', 'contracts', 'relatedProcesses', 'id'),
        ('releases', 'parties', 'id'),
        ('releases', 'relatedProcesses', 'id'),
        ('releases', 'tender', 'amendments', 'id'),
        ('releases', 'tender', 'tenderers', 'id')
    ]

    assert sorted(non_required_ids) == results

import json

from libcoveocds.lib.additional_checks import run_additional_checks, TEST_CLASSES


def test_empty_fields_basic():
    with open('./tests/fixtures/additional_checks/empty_fields.json', encoding='utf-8') as json_file:
        data = json.load(json_file)

    additional_checks = run_additional_checks(data, TEST_CLASSES['additional'])
    result = {
        'empty_field': [
            {'json_location': 'releases/0/parties/0/address'},
            {'json_location': 'releases/0/planning/budget/id'},
            {'json_location': 'releases/0/tender/items/0/additionalClassifications'}
        ]
    }

    assert additional_checks == result


def test_empty_fields_empty_string():
    data = {
        "releases": [
            {
                "ocid": "ocds-213czf-000-00001",
                "date": "",
                "initiationType": "tender",
            }
        ]
    }

    assert run_additional_checks(data, TEST_CLASSES['additional']) == {'empty_field': [{'json_location': 'releases/0/date'}]}


def test_empty_fields_empty_dict():
    data = {"releases": [{"buyer": {}}]}

    assert run_additional_checks(data, TEST_CLASSES['additional']) == {'empty_field': [{'json_location': 'releases/0/buyer'}]}


def test_empty_fields_empty_list():
    data = {"releases": [{"parties": []}]}

    assert run_additional_checks(data, TEST_CLASSES['additional']) == {'empty_field': [{'json_location': 'releases/0/parties'}]}


def test_empty_fields_all_fine():
    with open('./tests/fixtures/additional_checks/basic_1.json', encoding='utf-8') as json_file:
        data = json.load(json_file)

    assert run_additional_checks(data, TEST_CLASSES['additional']) == {}

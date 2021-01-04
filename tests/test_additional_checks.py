import json

from libcoveocds.lib.additional_checks import TEST_CLASSES, run_additional_checks


def test_empty_fields_releases_basic():
    with open("./tests/fixtures/additional_checks/empty_fields_releases.json", encoding="utf-8") as json_file:
        data = json.load(json_file)

    additional_checks = run_additional_checks(data, TEST_CLASSES["additional"])
    result = {
        "empty_field": [
            {"json_location": "releases/0/parties/0/address"},
            {"json_location": "releases/0/planning/budget/id"},
            {"json_location": "releases/0/tender/items/0/additionalClassifications"},
        ]
    }

    assert additional_checks == result


def test_empty_fields_records_basic():
    with open("./tests/fixtures/additional_checks/empty_fields_records.json", encoding="utf-8") as json_file:
        data = json.load(json_file)

    additional_checks = run_additional_checks(data, TEST_CLASSES["additional"])
    result = {
        "empty_field": [
            {"json_location": "records/0/compiledRelease/awards/0/documents/0/id"},
            {"json_location": "records/0/compiledRelease/awards/0/items/0/additionalClassifications"},
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

    assert run_additional_checks(data, TEST_CLASSES["additional"]) == {
        "empty_field": [{"json_location": "releases/0/date"}]
    }


def test_empty_fields_empty_dict():
    data = {"releases": [{"buyer": {}}]}

    assert run_additional_checks(data, TEST_CLASSES["additional"]) == {
        "empty_field": [{"json_location": "releases/0/buyer"}]
    }


def test_empty_fields_empty_list():
    data = {"releases": [{"parties": []}]}

    assert run_additional_checks(data, TEST_CLASSES["additional"]) == {
        "empty_field": [{"json_location": "releases/0/parties"}]
    }


def test_empty_fields_all_fine():
    with open("./tests/fixtures/additional_checks/basic_releases.json", encoding="utf-8") as json_file:
        data = json.load(json_file)

    assert run_additional_checks(data, TEST_CLASSES["additional"]) == {}

    with open("./tests/fixtures/additional_checks/full_record.json", encoding="utf-8") as json_file:
        data = json.load(json_file)

    assert run_additional_checks(data, TEST_CLASSES["additional"]) == {}

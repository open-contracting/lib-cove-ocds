import json

from libcoveocds.lib.additional_checks import run_additional_checks, TEST_CLASSES


def test_empty_fields():
    with open('./tests/fixtures/additional_checks/empty_fields.json', encoding='utf-8') as json_file:
        data = json.load(json_file)

    additional_checks = run_additional_checks(data, TEST_CLASSES['additional'])
    result = [
        {'json_location': 'releases/0/parties/0/address', 'type': 'empty_field'},
        {'json_location': 'releases/0/planning/budget/id', 'type': 'empty_field'},
        {'json_location': 'releases/0/tender/items/0/additionalClassifications', 'type': 'empty_field'}
    ]

    assert additional_checks == result

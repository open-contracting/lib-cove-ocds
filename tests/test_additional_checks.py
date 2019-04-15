import json

from libcoveocds.lib.additional_checks import run_additional_checks, TEST_CLASSES


def test_empty_fields():
    with open('./tests/fixtures/additional_checks/empty_fields.json', encoding='utf-8') as json_file:
        data = json.load(json_file)
    result = {}
    additional_checks = run_additional_checks(data, TEST_CLASSES['additional'])

    assert additional_checks == result

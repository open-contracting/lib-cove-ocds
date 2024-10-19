import json
import os

from libcoveocds.lib.common_checks import get_bad_ocid_prefixes
from tests import fixture_path


def test_release_bad_ocid_prefixes():
    file_name = fixture_path("fixtures", "lib", "tenders_releases_7_releases_check_ocids.json")
    results = [
        ("bad-prefix-000001", "releases/0/ocid"),
        ("bad-prefix-000002", "releases/1/ocid"),
        ("bad-prefix-000002", "releases/2/ocid"),
        ("ocds-bad-000004", "releases/4/ocid"),
        ("ocds-bad-000004", "releases/5/ocid"),
        ("ocds-bad-000004", "releases/6/ocid"),
    ]

    with open(os.path.join(file_name)) as fp:
        user_data = json.load(fp)

    user_data_ocids = [rel["ocid"] for rel in user_data["releases"]]

    assert len(user_data_ocids) == 7  # 1 good, 6 bad ocds prefixes
    assert "ocds-00good-000003" in user_data_ocids  # good ocds prefix
    assert get_bad_ocid_prefixes(user_data) == results


def test_record_bad_ocid_prefixes_with_bad_compiled_release():
    file_name = fixture_path("fixtures", "lib", "record_check_ocids.json")
    results = [
        ("bad-prefix-000001", "records/0/ocid"),
    ]

    with open(os.path.join(file_name)) as fp:
        user_data = json.load(fp)

    assert get_bad_ocid_prefixes(user_data) == results

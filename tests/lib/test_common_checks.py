import json
import os

from libcoveocds.lib.common_checks import get_bad_ocds_prefixes, get_releases_aggregates

EMPTY_RELEASE_AGGREGATE = {
    "award_doc_count": 0,
    "award_doctype": {},
    "award_count": 0,
    "contract_doc_count": 0,
    "contract_doctype": {},
    "contract_count": 0,
    "contracts_without_awards": [],
    "duplicate_release_ids": [],
    "implementation_count": 0,
    "implementation_doc_count": 0,
    "implementation_doctype": {},
    "implementation_milestones_doc_count": 0,
    "implementation_milestones_doctype": {},
    "item_identifier_schemes": [],
    "max_award_date": "",
    "max_contract_date": "",
    "max_release_date": "",
    "max_tender_date": "",
    "min_award_date": "",
    "min_contract_date": "",
    "min_release_date": "",
    "min_tender_date": "",
    "organisations_with_address": 0,
    "organisations_with_contact_point": 0,
    "planning_doc_count": 0,
    "planning_doctype": {},
    "planning_count": 0,
    "award_item_count": 0,
    "contract_item_count": 0,
    "release_count": 0,
    "tender_item_count": 0,
    "tags": {},
    "tender_doc_count": 0,
    "tender_doctype": {},
    "tender_milestones_doc_count": 0,
    "tender_milestones_doctype": {},
    "tender_count": 0,
    "unique_award_id": [],
    "unique_buyers_count": 0,
    "unique_buyers_identifier": {},
    "unique_buyers_name_no_id": [],
    "unique_currency": [],
    "unique_initation_type": [],
    "unique_item_ids_count": 0,
    "unique_lang": [],
    "unique_ocids": [],
    "unique_org_count": 0,
    "unique_org_identifier_count": 0,
    "unique_org_name_count": 0,
    "unique_organisation_schemes": [],
    "unique_procuring_count": 0,
    "unique_procuring_identifier": {},
    "unique_procuring_name_no_id": [],
    "unique_suppliers_count": 0,
    "unique_suppliers_identifier": {},
    "unique_suppliers_name_no_id": [],
    "unique_tenderers_count": 0,
    "unique_tenderers_identifier": {},
    "unique_tenderers_name_no_id": [],
    "processes_implementation_count": 0,
    "processes_award_count": 0,
    "processes_contract_count": 0,
    "total_item_count": 0,
    "unique_buyers": [],
    "unique_procuring": [],
    "unique_suppliers": [],
    "unique_tenderers": [],
}


EXPECTED_RELEASE_AGGREGATE = {
    "award_count": 2,
    "award_doc_count": 3,
    "award_doctype": {"doctype1": 2, "doctype2": 1},
    "award_item_count": 2,
    "contract_count": 2,
    "contract_doc_count": 3,
    "contract_doctype": {"doctype1": 2, "doctype2": 1},
    "contract_item_count": 2,
    "contracts_without_awards": [
        {"awardID": "no", "id": "2", "period": {"startDate": "2015-01-02T00:00Z"}, "value": {"currency": "EUR"}}
    ],
    "duplicate_release_ids": [],
    "implementation_count": 1,
    "implementation_doc_count": 3,
    "implementation_doctype": {"doctype1": 2, "doctype2": 1},
    "implementation_milestones_doc_count": 3,
    "implementation_milestones_doctype": {"doctype1": 2, "doctype2": 1},
    "item_identifier_schemes": ["scheme1", "scheme2"],
    "max_award_date": "2015-01-02T00:00Z",
    "max_contract_date": "2015-01-02T00:00Z",
    "max_release_date": "2015-01-02T00:00Z",
    "max_tender_date": "2015-01-02T00:00Z",
    "min_award_date": "2015-01-01T00:00Z",
    "min_contract_date": "2015-01-01T00:00Z",
    "min_release_date": "2015-01-02T00:00Z",
    "min_tender_date": "2015-01-02T00:00Z",
    "organisations_with_address": 2,
    "organisations_with_contact_point": 2,
    "planning_count": 1,
    "planning_doc_count": 3,
    "planning_doctype": {"doctype1": 2, "doctype2": 1},
    "release_count": 1,
    "tags": {"planning": 1, "tender": 1},
    "tender_count": 1,
    "tender_doc_count": 3,
    "tender_doctype": {"doctype1": 2, "doctype2": 1},
    "tender_item_count": 2,
    "tender_milestones_doc_count": 3,
    "tender_milestones_doctype": {"doctype1": 2, "doctype2": 1},
    "unique_award_id": ["1", "2"],
    "unique_buyers_count": 1,
    "unique_buyers_identifier": {"1": "Gov"},
    "unique_buyers_name_no_id": [],
    "unique_currency": ["EUR", "GBP", "USD", "YEN"],
    "unique_initation_type": ["tender"],
    "unique_item_ids_count": 2,
    "unique_lang": ["English"],
    "unique_ocids": ["1"],
    "unique_org_count": 4,
    "unique_org_identifier_count": 2,
    "unique_org_name_count": 2,
    "unique_organisation_schemes": ["a", "b"],
    "unique_procuring_count": 1,
    "unique_procuring_identifier": {"1": "Gov"},
    "unique_procuring_name_no_id": [],
    "unique_suppliers_count": 3,
    "unique_suppliers_identifier": {"2": "Big corp3"},
    "unique_suppliers_name_no_id": ["Big corp1", "Big corp2"],
    "unique_tenderers_count": 3,
    "unique_tenderers_identifier": {"2": "Big corp3"},
    "unique_tenderers_name_no_id": ["Big corp1", "Big corp2"],
    "processes_implementation_count": 1,
    "processes_award_count": 1,
    "processes_contract_count": 1,
    "total_item_count": 6,
    "unique_buyers": ["Gov (1)"],
    "unique_procuring": ["Gov (1)"],
    "unique_suppliers": ["Big corp1", "Big corp2", "Big corp3 (2)"],
    "unique_tenderers": ["Big corp1", "Big corp2", "Big corp3 (2)"],
}

EXPECTED_RELEASE_AGGREGATE_RANDOM = {
    "award_count": 1477,
    "award_doc_count": 2159,
    "award_item_count": 2245,
    "contract_count": 1479,
    "contract_doc_count": 2186,
    "contract_item_count": 2093,
    "implementation_count": 562,
    "implementation_doc_count": 1140,
    "implementation_milestones_doc_count": 1659,
    "max_award_date": "5137-06-18T19:25:03.403Z",
    "max_contract_date": "5113-08-13T17:04:27.669Z",
    "max_release_date": "5137-06-07T19:44:36.152Z",
    "max_tender_date": "5084-05-16T03:11:56.723Z",
    "min_award_date": "1977-01-18T23:35:50.858Z",
    "min_contract_date": "1970-02-23T13:49:12.592Z",
    "min_release_date": "1970-08-03T00:21:37.491Z",
    "min_tender_date": "1989-03-20T22:29:02.697Z",
    "organisations_with_address": 770,
    "organisations_with_contact_point": 729,
    "planning_count": 339,
    "planning_doc_count": 738,
    "release_count": 1005,
    "tender_count": 467,
    "tender_doc_count": 799,
    "tender_item_count": 770,
    "tender_milestones_doc_count": 1163,
    "unique_buyers_count": 169,
    "unique_item_ids_count": 4698,
    "unique_org_count": 1339,
    "unique_org_identifier_count": 625,
    "unique_org_name_count": 714,
    "unique_procuring_count": 94,
    "unique_suppliers_count": 812,
    "unique_tenderers_count": 286,
    "processes_award_count": 466,
    "processes_contract_count": 467,
    "processes_implementation_count": 327,
    "total_item_count": 5108,
}


def test_get_releases_aggregates():
    assert get_releases_aggregates({}) == EMPTY_RELEASE_AGGREGATE
    assert get_releases_aggregates({"releases": []}) == EMPTY_RELEASE_AGGREGATE
    release_aggregate_3_empty = EMPTY_RELEASE_AGGREGATE.copy()
    release_aggregate_3_empty["release_count"] = 3
    assert get_releases_aggregates({"releases": [{}, {}, {}]}) == release_aggregate_3_empty

    with open(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "fixtures", "common_checks", "release_aggregate.json"
        )
    ) as fp:
        data = json.load(fp)

    assert get_releases_aggregates({"releases": data["releases"]}) == EXPECTED_RELEASE_AGGREGATE

    # test if a release is duplicated
    actual = get_releases_aggregates({"releases": data["releases"] + data["releases"]})
    actual_cleaned = {key: actual[key] for key in actual if "doc" not in key}
    actual_cleaned.pop("contracts_without_awards")

    expected_cleaned = {key: EXPECTED_RELEASE_AGGREGATE[key] for key in EXPECTED_RELEASE_AGGREGATE if "doc" not in key}
    expected_cleaned["tags"] = {"planning": 2, "tender": 2}
    expected_cleaned.pop("contracts_without_awards")
    expected_cleaned["release_count"] = 2
    expected_cleaned["duplicate_release_ids"] = ["1"]

    assert actual_cleaned == expected_cleaned

    with open(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "fixtures", "common_checks", "samplerubbish.json")
    ) as fp:
        data = json.load(fp)

    actual = get_releases_aggregates(data)
    actual_cleaned = {key: actual[key] for key in actual if isinstance(actual[key], (str, int, float))}

    assert actual_cleaned == EXPECTED_RELEASE_AGGREGATE_RANDOM

    with open(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "fixtures", "common_checks", "badfile.json")
    ) as fp:
        data = json.load(fp)

    actual = get_releases_aggregates(data, ignore_errors=True)

    assert actual == {}


def test_release_bad_ocds_prefixes():
    file_name = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "fixtures",
        "common_checks",
        "tenders_releases_7_releases_check_ocids.json",
    )
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

    user_data_ocids = []
    for rel in user_data["releases"]:
        user_data_ocids.append(rel["ocid"])

    assert len(user_data_ocids) == 7  # 1 good, 6 bad ocds prefixes
    assert "ocds-00good-000003" in user_data_ocids  # good ocds prefix
    assert get_bad_ocds_prefixes(user_data) == results


def test_record_bad_ocds_prefixes_with_bad_compiled_release():
    file_name = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "fixtures", "common_checks", "record_check_ocids.json"
    )
    results = [
        ("bad-prefix-000001", "records/0/ocid"),
    ]

    with open(os.path.join(file_name)) as fp:
        user_data = json.load(fp)

    assert get_bad_ocds_prefixes(user_data) == results

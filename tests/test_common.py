import json
import os

from libcoveocds.common_checks import (
    fields_present_generator,
    get_additional_fields_info,
    schema_dict_fields_generator,
)


def test_schema_dict_fields_generator_release_schema_deprecated_fields():
    with open(os.path.join("tests", "fixtures", "release_schema_deprecated_fields.json")) as f:
        package_data = json.load(f)

    data = sorted(set(schema_dict_fields_generator(package_data)))

    assert len(data) == 11

    assert data[0] == "/awards"
    assert data[1] == "/buyer"
    assert data[2] == "/contracts"
    assert data[3] == "/date"
    assert data[4] == "/id"
    assert data[5] == "/initiationType"
    assert data[6] == "/language"
    assert data[7] == "/ocid"
    assert data[8] == "/planning"
    assert data[9] == "/tag"
    assert data[10] == "/tender"


def test_schema_dict_fields_generator_schema_with_list_and_oneof():
    with open(os.path.join("tests", "fixtures", "schema_with_list_and_oneof.json")) as f:
        package_data = json.load(f)

    data = sorted(set(schema_dict_fields_generator(package_data)))

    assert data == [
        "/dissolutionDate",
        "/entityType",
        "/names",
        "/names/familyName",
        "/names/fullName",
        "/names/givenName",
        "/names/patronymicName",
        "/names/type",
        "/source",
        "/source/assertedBy",
        "/source/assertedBy/name",
        "/source/assertedBy/uri",
        "/source/description",
        "/source/retrievedAt",
        "/source/type",
        "/source/url",
    ]


def test_fields_present_generator_tenders_releases_2_releases():
    with open(os.path.join("tests", "fixtures", "tenders_releases_2_releases.json")) as f:
        package_data = json.load(f)

    data = sorted({key for key, _ in fields_present_generator(package_data, [])})

    assert data == [
        "/license",
        "/publishedDate",
        "/publisher",
        "/publisher/name",
        "/publisher/scheme",
        "/publisher/uid",
        "/publisher/uri",
        "/releases",
        "/releases/buyer",
        "/releases/buyer/name",
        "/releases/date",
        "/releases/id",
        "/releases/initiationType",
        "/releases/language",
        "/releases/ocid",
        "/releases/tag",
        "/releases/tender",
        "/releases/tender/awardCriteriaDetails",
        "/releases/tender/documents",
        "/releases/tender/documents/id",
        "/releases/tender/documents/url",
        "/releases/tender/id",
        "/releases/tender/items",
        "/releases/tender/items/classification",
        "/releases/tender/items/classification/description",
        "/releases/tender/items/classification/scheme",
        "/releases/tender/items/description",
        "/releases/tender/items/id",
        "/releases/tender/methodRationale",
        "/releases/tender/procuringEntity",
        "/releases/tender/procuringEntity/name",
        "/releases/tender/procuringEntity/name_fr",
        "/releases/tender/tenderPeriod",
        "/releases/tender/tenderPeriod/endDate",
        "/uri",
        "/version",
    ]


def test_fields_present_generator_data_root_is_list():
    with open(os.path.join("tests", "fixtures", "data_root_is_list.json")) as f:
        bods_data = json.load(f)

    data = sorted({key for key, _ in fields_present_generator(bods_data, [])})

    assert data == [
        "/addresses",
        "/addresses/address",
        "/addresses/country",
        "/addresses/postCode",
        "/addresses/type",
        "/birthDate",
        "/entityType",
        "/foundingDate",
        "/identifiers",
        "/identifiers/id",
        "/identifiers/scheme",
        "/interestedParty",
        "/interestedParty/describedByPersonStatement",
        "/interests",
        "/interests/beneficialOwnershipOrControl",
        "/interests/interestLevel",
        "/interests/share",
        "/interests/share/exact",
        "/interests/startDate",
        "/interests/type",
        "/name",
        "/names",
        "/names/familyName",
        "/names/fullName",
        "/names/givenName",
        "/names/type",
        "/nationalities",
        "/nationalities/code",
        "/personType",
        "/statementDate",
        "/statementID",
        "/statementType",
        "/subject",
        "/subject/describedByEntityStatement",
    ]


def test_get_additional_fields_info():
    simple_data = {
        "non_additional_field": "a",
        "non_additional_list": [1, 2],
        "non_additional_object": {"z": "z"},
        "additional_object": {"a": "a", "b": "b"},
        "additional_list": [
            {"c": "c", "d": "d"},
            {"e": "e", "f": "f"},
            {"e": "e", "f": "f"},
        ],
    }

    schema_fields = {
        "/non_additional_field",
        "/non_additional_list",
        "/non_additional_object",
        "/non_additional_object/z",
    }

    additional_field_info = get_additional_fields_info(json_data=simple_data, schema_fields=schema_fields)
    assert list(additional_field_info) == [
        "/additional_object",
        "/additional_object/a",
        "/additional_object/b",
        "/additional_list",
        "/additional_list/c",
        "/additional_list/d",
        "/additional_list/e",
        "/additional_list/f",
    ]
    assert len(additional_field_info) == 8
    assert sum(info["count"] for info in additional_field_info.values()) == 10
    assert len([info for info in additional_field_info.values() if info["root_additional_field"]]) == 2

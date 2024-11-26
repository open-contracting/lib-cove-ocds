import json
import os

import pytest

from libcoveocds import SchemaOCDS, run_checks
from libcoveocds.common_checks import (
    get_additional_codelist_values,
    get_json_data_deprecated_fields,
    get_json_data_generic_paths,
    get_schema_validation_errors,
)


def test_get_schema_validation_errors():
    with open(os.path.join("tests", "fixtures", "tenders_releases_2_releases.json")) as f:
        package_data = json.load(f)
        schema_obj = SchemaOCDS(package_data, "1.0")
        error_list = get_schema_validation_errors(package_data, schema_obj)

        assert len(error_list) == 0

    with open(os.path.join("tests", "fixtures", "tenders_releases_2_releases_invalid.json")) as f:
        package_data = json.load(f)
        schema_obj = SchemaOCDS(package_data, "1.0")
        error_list = get_schema_validation_errors(package_data, schema_obj)

        assert len(error_list) > 0


def test_get_json_data_generic_paths():
    with open(
        os.path.join(
            "tests",
            "fixtures",
            "tenders_releases_2_releases_with_deprecated_fields.json",
        )
    ) as f:
        json_data_w_deprecations = json.load(f)

    generic_paths = get_json_data_generic_paths(json_data_w_deprecations, json_data_paths={})
    assert len(generic_paths.keys()) == 36
    assert generic_paths[("releases", "buyer", "name")] == {
        ("releases", 1, "buyer", "name"): "Parks Canada",
        ("releases", 0, "buyer", "name"): "Agriculture & Agrifood Canada",
    }


def test_get_json_data_deprecated_fields():
    with open(
        os.path.join(
            "tests",
            "fixtures",
            "tenders_releases_2_releases_with_deprecated_fields.json",
        )
    ) as f:
        json_data_w_deprecations = json.load(f)

    schema_obj = SchemaOCDS(json_data_w_deprecations)
    schema_obj._test_override_package_schema = os.path.join(  # noqa: SLF001
        "tests", "fixtures", "release_package_schema_ref_release_schema_deprecated_fields.json"
    )
    schema_obj.analyze_schema()

    json_data_paths = get_json_data_generic_paths(json_data_w_deprecations, json_data_paths={})
    deprecated_data_fields = get_json_data_deprecated_fields(json_data_paths, schema_obj)
    expected_result = {
        "initiationType": {
            "paths": ("releases/0", "releases/1"),
            "explanation": ("1.1", "Not a useful field as always has to be tender"),
        },
        "quantity": {
            "paths": ("releases/0/tender/items/0",),
            "explanation": ("1.1", "Nobody cares about quantities"),
        },
    }
    for field_name in expected_result:
        assert field_name in deprecated_data_fields
        assert expected_result[field_name]["paths"] == deprecated_data_fields[field_name]["paths"]
        assert expected_result[field_name]["explanation"] == deprecated_data_fields[field_name]["explanation"]


def test_get_schema_deprecated_paths():
    schema_obj = SchemaOCDS({"releases": []})
    schema_obj._test_override_package_schema = os.path.join(  # noqa: SLF001
        "tests", "fixtures", "release_package_schema_ref_release_schema_deprecated_fields.json"
    )
    schema_obj.analyze_schema()

    expected_results = [
        (("releases", "initiationType"), ("1.1", "Not a useful field as always has to be tender")),
        (("releases", "planning"), ("1.1", "Testing deprecation for objects with '$ref'")),
        (("releases", "tender", "hasEnquiries"), ("1.1", "Deprecated just for fun")),
        (("releases", "contracts", "items", "quantity"), ("1.1", "Nobody cares about quantities")),
        (("releases", "tender", "items", "quantity"), ("1.1", "Nobody cares about quantities")),
        (("releases", "awards", "items", "quantity"), ("1.1", "Nobody cares about quantities")),
    ]
    for path in expected_results:
        assert path in schema_obj.deprecated_paths
    assert len(schema_obj.deprecated_paths) == 6


def test_get_additional_codelist_values():
    with open(os.path.join("tests", "fixtures", "tenders_releases_2_releases_codelists.json")) as f:
        json_data_w_additial_codelists = json.load(f)

    schema_obj = SchemaOCDS(json_data_w_additial_codelists, "1.1")
    schema_obj.analyze_schema()

    additional_codelist_values = get_additional_codelist_values(schema_obj, json_data_w_additial_codelists)

    assert additional_codelist_values == {
        ("releases/tag"): {
            "codelist": "releaseTag.csv",
            "codelist_url": "https://raw.githubusercontent.com/open-contracting/standard/1.1/schema/codelists/releaseTag.csv",
            "codelist_amend_urls": [],
            "field": "tag",
            "extension_codelist": False,
            "isopen": False,
            "path": "releases",
            "values": ["oh no"],
        },
        ("releases/tender/items/classification/scheme"): {
            "codelist": "itemClassificationScheme.csv",
            "codelist_url": "https://raw.githubusercontent.com/open-contracting/standard/1.1/schema/codelists/itemClassificationScheme.csv",
            "codelist_amend_urls": [],
            "extension_codelist": False,
            "field": "scheme",
            "isopen": True,
            "path": "releases/tender/items/classification",
            "values": ["GSINS"],
        },
    }


def test_get_additional_codelist_values_one_of():
    json_data = {"data": {"entityType": "additional"}}

    schema_obj = SchemaOCDS(json_data)
    schema_obj._test_override_package_schema = os.path.join(  # noqa: SLF001
        "tests", "fixtures", "schema_with_oneof_codelists.json"
    )
    schema_obj.analyze_schema()

    additional_codelist_values = get_additional_codelist_values(schema_obj, json_data)

    assert additional_codelist_values == {
        "data/entityType": {
            "path": "data",
            "field": "entityType",
            "codelist": "currency.csv",
            "codelist_url": "https://raw.githubusercontent.com/open-contracting/standard/1.1/schema/codelists/currency.csv",
            "codelist_amend_urls": [],
            "isopen": False,
            "values": ["additional"],
            "extension_codelist": False,
        }
    }


@pytest.mark.parametrize(
    "json_data",
    [
        '{"version":"1.1", "releases":{"buyer":{"additionalIdentifiers":[]}, "initiationType": "tender"}}',
        # Add more ...
    ],
)
def test_corner_cases_for_deprecated_data_fields(json_data):
    data = json.loads(json_data)
    schema_obj = SchemaOCDS(data)
    schema_obj.analyze_schema()

    json_data_paths = get_json_data_generic_paths(data, json_data_paths={})
    deprecated_fields = get_json_data_deprecated_fields(json_data_paths, schema_obj)

    assert deprecated_fields["additionalIdentifiers"]["explanation"][0] == "1.1"
    assert (
        "parties section at the top level of a release" in deprecated_fields["additionalIdentifiers"]["explanation"][1]
    )
    assert deprecated_fields["additionalIdentifiers"]["paths"] == ("releases/buyer",)
    assert len(deprecated_fields.keys()) == 1
    assert len(deprecated_fields["additionalIdentifiers"]["paths"]) == 1


def test_get_schema_non_required_ids():
    schema_obj = SchemaOCDS({"releases": []}, "1.1")
    schema_obj.analyze_schema()

    assert sorted(schema_obj.optional_id_paths) == [
        ("releases", "awards", "amendments", "id"),
        ("releases", "awards", "suppliers", "id"),
        ("releases", "contracts", "amendments", "id"),
        ("releases", "contracts", "relatedProcesses", "id"),
        ("releases", "parties", "id"),
        ("releases", "relatedProcesses", "id"),
        ("releases", "tender", "amendments", "id"),
        ("releases", "tender", "tenderers", "id"),
    ]


def test_get_json_data_missing_ids():
    with open(
        os.path.join("tests", "fixtures", "tenders_releases_2_releases_1_1_tenderers_with_missing_ids.json")
    ) as f:
        package_data = json.load(f)

    schema_obj = SchemaOCDS(package_data)

    context = run_checks(package_data, schema_obj)

    assert context["structure_warnings"]["missing_ids"] == [
        "releases/0/tender/tenderers/1/id",
        "releases/0/tender/tenderers/2/id",
        "releases/0/tender/tenderers/5/id",
        "releases/1/tender/tenderers/1/id",
        "releases/1/tender/tenderers/2/id",
        "releases/1/tender/tenderers/4/id",
    ]

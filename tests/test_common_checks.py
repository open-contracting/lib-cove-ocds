import json
import os
import shutil
import tempfile

import pytest

import libcoveocds.common_checks
import libcoveocds.config
import libcoveocds.schema

# Cache for faster tests.
config = libcoveocds.config.LibCoveOCDSConfig()
config.config["cache_all_requests"] = True


def test_basic_1():

    cove_temp_folder = tempfile.mkdtemp(prefix="libcoveocds-tests-", dir=tempfile.gettempdir())
    schema = libcoveocds.schema.SchemaOCDS(lib_cove_ocds_config=config)
    json_filename = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "fixtures", "common_checks", "basic_1.json"
    )
    with open(json_filename) as fp:
        json_data = json.load(fp)

    context = {
        "file_type": "json",
    }

    try:

        results = libcoveocds.common_checks.common_checks_ocds(
            context,
            cove_temp_folder,
            json_data,
            schema,
        )

    finally:
        shutil.rmtree(cove_temp_folder)

    assert results["version_used"] == "1.1"


def test_dupe_ids_1():

    cove_temp_folder = tempfile.mkdtemp(prefix="libcoveocds-tests-", dir=tempfile.gettempdir())
    schema = libcoveocds.schema.SchemaOCDS(lib_cove_ocds_config=config)
    json_filename = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "fixtures", "common_checks", "dupe_ids_1.json"
    )
    with open(json_filename) as fp:
        json_data = json.load(fp)

    context = {
        "file_type": "json",
    }

    try:

        results = libcoveocds.common_checks.common_checks_ocds(
            context,
            cove_temp_folder,
            json_data,
            schema,
        )

    finally:
        shutil.rmtree(cove_temp_folder)

    # https://github.com/OpenDataServices/cove/issues/782 Defines how we want this error shown
    assert len(results["validation_errors"][0][1]) == 2
    # test paths
    assert results["validation_errors"][0][1][0]["path"] == "releases"
    assert results["validation_errors"][0][1][1]["path"] == "releases"
    # test values
    # we don't know what order they will come out in, so fix the order ourselves
    values = [
        results["validation_errors"][0][1][0]["value"],
        results["validation_errors"][0][1][1]["value"],
    ]
    values.sort()
    assert values[0] == "ocds-213czf-000-00001-01-planning"
    assert values[1] == "ocds-213czf-000-00001-02-planning"


@pytest.mark.parametrize(
    "record_pkg,filename,schema_subdir,validation_error_jsons_expected",
    [
        (False, "releases_no_validation_errors.json", "", []),
        (True, "records_no_validation_errors.json", "", []),
        (
            True,
            "records_invalid_releases.json",
            "",
            [
                {
                    "message": "'date' is missing but required within 'releases'",
                    "message_safe": "&#x27;date&#x27; is missing but required within &#x27;releases&#x27;",
                    "validator": "required",
                    "assumption": "embedded_releases",
                    "message_type": "required",
                    "path_no_number": "records/releases",
                    "header": "date",
                    "header_extra": "releases/[number]",
                    "null_clause": "",
                    "error_id": None,
                    "values": [{"path": "records/2/releases/0"}],
                },
                {
                    "message": "'date' is missing but required within 'releases'",
                    "message_safe": "&#x27;date&#x27; is missing but required within &#x27;releases&#x27;",
                    "validator": "required",
                    "assumption": "linked_releases",
                    "message_type": "required",
                    "path_no_number": "records/releases",
                    "header": "date",
                    "header_extra": "releases/[number]",
                    "null_clause": "",
                    "error_id": None,
                    "values": [
                        {"path": "records/1/releases/0"},
                        {"path": "records/3/releases/0"},
                    ],
                },
                {
                    "message": "'initiationType' is missing but required within 'releases'",
                    "message_safe": "&#x27;initiationType&#x27; is missing but required within &#x27;releases&#x27;",
                    "validator": "required",
                    "assumption": "embedded_releases",
                    "message_type": "required",
                    "path_no_number": "records/releases",
                    "header": "initiationType",
                    "header_extra": "releases/[number]",
                    "null_clause": "",
                    "error_id": None,
                    "values": [{"path": "records/2/releases/0"}],
                },
                {
                    "message": "'ocid' is missing but required within 'releases'",
                    "message_safe": "&#x27;ocid&#x27; is missing but required within &#x27;releases&#x27;",
                    "validator": "required",
                    "assumption": "embedded_releases",
                    "message_type": "required",
                    "path_no_number": "records/releases",
                    "header": "ocid",
                    "header_extra": "releases/[number]",
                    "null_clause": "",
                    "error_id": None,
                    "values": [{"path": "records/2/releases/0"}],
                },
                {
                    "message": "'releases' is not a JSON array",
                    "message_safe": "&#x27;releases&#x27; is not a JSON array",
                    "validator": "type",
                    "assumption": "linked_releases",
                    "message_type": "array",
                    "path_no_number": "records/releases",
                    "header": "releases",
                    "header_extra": "releases",
                    "null_clause": "is not null, and",
                    "error_id": None,
                    "values": [
                        {"path": "records/6/releases", "value": "a string"},
                        {"path": "records/7/releases", "value": None},
                        {"path": "records/8/releases"},
                    ],
                },
                {
                    "message": "'tag' is missing but required within 'releases'",
                    "message_safe": "&#x27;tag&#x27; is missing but required within &#x27;releases&#x27;",
                    "validator": "required",
                    "assumption": "embedded_releases",
                    "message_type": "required",
                    "path_no_number": "records/releases",
                    "header": "tag",
                    "header_extra": "releases/[number]",
                    "null_clause": "",
                    "error_id": None,
                    "values": [{"path": "records/2/releases/0"}],
                },
                {
                    "message": "'url' is missing but required within 'releases'",
                    "message_safe": "&#x27;url&#x27; is missing but required within &#x27;releases&#x27;",
                    "validator": "required",
                    "assumption": "linked_releases",
                    "message_type": "required",
                    "path_no_number": "records/releases",
                    "header": "url",
                    "header_extra": "releases/[number]",
                    "null_clause": "",
                    "error_id": None,
                    "values": [{"path": "records/1/releases/0"}],
                },
                {
                    "message": "This array should contain either entirely embedded releases or linked releases. Embedded releases contain an 'id' whereas linked releases do not. Your releases contain a mixture.",  # noqa: E501
                    "message_safe": "This array should contain either entirely embedded releases or linked releases. Embedded releases contain an &#x27;id&#x27; whereas linked releases do not. Your releases contain a mixture.",  # noqa: E501
                    "validator": "oneOf",
                    "assumption": None,
                    "message_type": "oneOf",
                    "path_no_number": "records/releases",
                    "header": "releases",
                    "header_extra": "releases",
                    "null_clause": "",
                    "error_id": "releases_both_embedded_and_linked",
                    "values": [
                        {"path": "records/4/releases"},
                        {"path": "records/5/releases"},
                    ],
                },
                {
                    "message": "[] is too short",
                    "message_safe": "[] is too short",
                    "validator": "minItems",
                    "assumption": "linked_releases",
                    "message_type": "minItems",
                    "path_no_number": "records/releases",
                    "header": "releases",
                    "header_extra": "releases",
                    "null_clause": "",
                    "error_id": None,
                    "values": [{"path": "records/0/releases"}],
                    "instance": [],
                },
            ],
        ),
        (
            True,
            "records_invalid_releases.json",
            "1-0",
            [
                {
                    "message": "'date' is missing but required within 'releases'",
                    "message_safe": "&#x27;date&#x27; is missing but required within &#x27;releases&#x27;",
                    "validator": "required",
                    "assumption": "embedded_releases",
                    "message_type": "required",
                    "path_no_number": "records/releases",
                    "header": "date",
                    "header_extra": "releases/[number]",
                    "null_clause": "",
                    "error_id": None,
                    "values": [{"path": "records/2/releases/0"}],
                },
                {
                    "message": "'date' is missing but required within 'releases'",
                    "message_safe": "&#x27;date&#x27; is missing but required within &#x27;releases&#x27;",
                    "validator": "required",
                    "assumption": "linked_releases",
                    "message_type": "required",
                    "path_no_number": "records/releases",
                    "header": "date",
                    "header_extra": "releases/[number]",
                    "null_clause": "",
                    "error_id": None,
                    "values": [
                        {"path": "records/1/releases/0"},
                        {"path": "records/3/releases/0"},
                    ],
                },
                {
                    "message": "'initiationType' is missing but required within 'releases'",
                    "message_safe": "&#x27;initiationType&#x27; is missing but required within &#x27;releases&#x27;",
                    "validator": "required",
                    "assumption": "embedded_releases",
                    "message_type": "required",
                    "path_no_number": "records/releases",
                    "header": "initiationType",
                    "header_extra": "releases/[number]",
                    "null_clause": "",
                    "error_id": None,
                    "values": [{"path": "records/2/releases/0"}],
                },
                {
                    "message": "'ocid' is missing but required within 'releases'",
                    "message_safe": "&#x27;ocid&#x27; is missing but required within &#x27;releases&#x27;",
                    "validator": "required",
                    "assumption": "embedded_releases",
                    "message_type": "required",
                    "path_no_number": "records/releases",
                    "header": "ocid",
                    "header_extra": "releases/[number]",
                    "null_clause": "",
                    "error_id": None,
                    "values": [{"path": "records/2/releases/0"}],
                },
                {
                    "message": "'releases' is not a JSON array",
                    "message_safe": "&#x27;releases&#x27; is not a JSON array",
                    "validator": "type",
                    "assumption": "linked_releases",
                    "message_type": "array",
                    "path_no_number": "records/releases",
                    "header": "releases",
                    "header_extra": "releases",
                    "null_clause": "is not null, and",
                    "error_id": None,
                    "values": [
                        {"path": "records/6/releases", "value": "a string"},
                        {"path": "records/7/releases", "value": None},
                        {"path": "records/8/releases"},
                    ],
                },
                {
                    "message": "'tag' is missing but required within 'releases'",
                    "message_safe": "&#x27;tag&#x27; is missing but required within &#x27;releases&#x27;",
                    "validator": "required",
                    "assumption": "embedded_releases",
                    "message_type": "required",
                    "path_no_number": "records/releases",
                    "header": "tag",
                    "header_extra": "releases/[number]",
                    "null_clause": "",
                    "error_id": None,
                    "values": [{"path": "records/2/releases/0"}],
                },
                {
                    "message": "'url' is missing but required within 'releases'",
                    "message_safe": "&#x27;url&#x27; is missing but required within &#x27;releases&#x27;",
                    "validator": "required",
                    "assumption": "linked_releases",
                    "message_type": "required",
                    "path_no_number": "records/releases",
                    "header": "url",
                    "header_extra": "releases/[number]",
                    "null_clause": "",
                    "error_id": None,
                    "values": [{"path": "records/1/releases/0"}],
                },
                {
                    "message": "This array should contain either entirely embedded releases or linked releases. Embedded releases contain an 'id' whereas linked releases do not. Your releases contain a mixture.",  # noqa: E501
                    "message_safe": "This array should contain either entirely embedded releases or linked releases. Embedded releases contain an &#x27;id&#x27; whereas linked releases do not. Your releases contain a mixture.",  # noqa: E501
                    "validator": "oneOf",
                    "assumption": None,
                    "message_type": "oneOf",
                    "path_no_number": "records/releases",
                    "header": "releases",
                    "header_extra": "releases",
                    "null_clause": "",
                    "error_id": "releases_both_embedded_and_linked",
                    "values": [
                        {"path": "records/4/releases"},
                        {"path": "records/5/releases"},
                    ],
                },
                {
                    "message": "[] is too short",
                    "message_safe": "[] is too short",
                    "validator": "minItems",
                    "assumption": "linked_releases",
                    "message_type": "minItems",
                    "path_no_number": "records/releases",
                    "header": "releases",
                    "header_extra": "releases",
                    "null_clause": "",
                    "error_id": None,
                    "values": [{"path": "records/0/releases"}],
                    "instance": [],
                },
            ],
        ),
        (
            False,
            "releases_non_unique.json",
            "",
            [
                {
                    "message": "Non-unique id values",
                    "message_safe": "Non-unique id values",
                    "validator": "uniqueItems",
                    "assumption": None,
                    "message_type": "uniqueItems",
                    "path_no_number": "releases",
                    "header": "releases",
                    "header_extra": "releases",
                    "null_clause": "",
                    "error_id": "uniqueItems_with_id",
                    "values": [
                        {"path": "releases", "value": "EXAMPLE-1-1"},
                        {"path": "releases", "value": "EXAMPLE-1-2"},
                    ],
                }
            ],
        ),
        (
            True,
            "records_non_unique.json",
            "",
            [
                {
                    "message": "Non-unique ocid values",
                    "message_safe": "Non-unique ocid values",
                    "validator": "uniqueItems",
                    "assumption": None,
                    "message_type": "uniqueItems",
                    "path_no_number": "records",
                    "header": "records",
                    "header_extra": "records",
                    "null_clause": "",
                    "error_id": "uniqueItems_with_ocid",
                    "values": [
                        {"path": "records", "value": "EXAMPLE-1"},
                        {"path": "records", "value": "EXAMPLE-2"},
                    ],
                }
            ],
        ),
        (
            False,
            "releases_non_unique_no_id.json",
            "",
            [
                {
                    "message": "'id' is missing but required",
                    "message_safe": "&#x27;id&#x27; is missing but required",
                    "validator": "required",
                    "assumption": None,
                    "message_type": "required",
                    "path_no_number": "releases",
                    "header": "id",
                    "header_extra": "releases/[number]",
                    "null_clause": "",
                    "error_id": None,
                    "values": [{"path": "releases/0"}, {"path": "releases/1"}],
                },
                {
                    "message": "Array has non-unique elements",
                    "message_safe": "Array has non-unique elements",
                    "validator": "uniqueItems",
                    "assumption": None,
                    "message_type": "uniqueItems",
                    "path_no_number": "releases",
                    "header": "releases",
                    "header_extra": "releases",
                    "null_clause": "",
                    "error_id": "uniqueItems_no_ids",
                    "values": [{"path": "releases"}],
                },
            ],
        ),
        (
            True,
            "records_non_unique_no_ocid.json",
            "",
            [
                {
                    "message": "'ocid' is missing but required",
                    "message_safe": "&#x27;ocid&#x27; is missing but required",
                    "validator": "required",
                    "assumption": None,
                    "message_type": "required",
                    "path_no_number": "records",
                    "header": "ocid",
                    "header_extra": "records/[number]",
                    "null_clause": "",
                    "error_id": None,
                    "values": [{"path": "records/0"}, {"path": "records/1"}],
                },
                {
                    "message": "Array has non-unique elements",
                    "message_safe": "Array has non-unique elements",
                    "validator": "uniqueItems",
                    "assumption": None,
                    "message_type": "uniqueItems",
                    "path_no_number": "records",
                    "header": "records",
                    "header_extra": "records",
                    "null_clause": "",
                    "error_id": "uniqueItems_no_ids",
                    "values": [{"path": "records"}],
                },
            ],
        ),
        # Check that we handle unique arrays correctly also
        # (e.g. that we don't incorrectly claim they are not unique)
        (
            False,
            "releases_unique.json",
            "",
            [
                {
                    "message": "'id' is missing but required",
                    "message_safe": "&#x27;id&#x27; is missing but required",
                    "validator": "required",
                    "assumption": None,
                    "message_type": "required",
                    "path_no_number": "releases",
                    "header": "id",
                    "header_extra": "releases/[number]",
                    "null_clause": "",
                    "error_id": None,
                    "values": [{"path": "releases/0"}, {"path": "releases/1"}],
                }
            ],
        ),
        (
            True,
            "records_unique.json",
            "",
            [
                {
                    "message": "'ocid' is missing but required",
                    "message_safe": "&#x27;ocid&#x27; is missing but required",
                    "validator": "required",
                    "assumption": None,
                    "message_type": "required",
                    "path_no_number": "records",
                    "header": "ocid",
                    "header_extra": "records/[number]",
                    "null_clause": "",
                    "error_id": None,
                    "values": [{"path": "records/0"}, {"path": "records/1"}],
                }
            ],
        ),
    ],
)
def test_validation_release_or_record_package(record_pkg, filename, validation_error_jsons_expected, schema_subdir):
    schema_host = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "fixtures",
        "common_checks",
        schema_subdir,
        "",
    )
    with open(os.path.join(schema_host, filename)) as fp:
        json_data = json.load(fp)

    cove_temp_folder = tempfile.mkdtemp(prefix="libcoveocds-tests-", dir=tempfile.gettempdir())
    schema = libcoveocds.schema.SchemaOCDS(lib_cove_ocds_config=config, record_pkg=record_pkg)
    context = {
        "file_type": "json",
    }

    results = libcoveocds.common_checks.common_checks_ocds(
        context,
        cove_temp_folder,
        json_data,
        schema,
    )

    validation_errors = results["validation_errors"]

    validation_error_jsons = []
    for validation_error_json, values in validation_errors:
        validation_error_json = json.loads(validation_error_json)
        validation_error_json["values"] = values
        # Remove this as it can be a rather large schema object
        del validation_error_json["validator_value"]
        # TODO: these are removed as they were't present in the lib-cove JSON
        # We should maybe add them to the validation error fixtures now
        if "docs_ref" in validation_error_json:
            del validation_error_json["docs_ref"]
        if "schema_description_safe" in validation_error_json:
            del validation_error_json["schema_description_safe"]
        if "schema_title" in validation_error_json:
            del validation_error_json["schema_title"]
        validation_error_jsons.append(validation_error_json)

    def strip_nones(list_of_dicts):
        out = []
        for a_dict in list_of_dicts:
            out.append({key: value for key, value in a_dict.items() if value is not None})
        return out

    assert strip_nones(validation_error_jsons) == strip_nones(validation_error_jsons_expected)

import json
import os
import shutil
import tempfile

import pytest

import libcoveocds.config
from libcoveocds.api import ocds_json_output
from libcoveocds.exceptions import OCDSVersionError
from tests import fixture_path

# Cache for faster tests.
config = libcoveocds.config.LibCoveOCDSConfig()
config.config["cache_all_requests"] = True


def test_basic_1():

    cove_temp_folder = tempfile.mkdtemp(prefix="lib-cove-ocds-tests-", dir=tempfile.gettempdir())
    json_filename = fixture_path("fixtures", "api", "basic_1.json")

    results = ocds_json_output(
        cove_temp_folder, json_filename, schema_version="", convert=False, lib_cove_ocds_config=config
    )

    assert results["version_used"] == "1.1"
    assert results["validation_errors"] == []


def test_basic_record_package():

    cove_temp_folder = tempfile.mkdtemp(prefix="lib-cove-ocds-tests-", dir=tempfile.gettempdir())
    json_filename = fixture_path("fixtures", "api", "basic_record_package.json")

    results = ocds_json_output(
        cove_temp_folder, json_filename, schema_version="", convert=False, lib_cove_ocds_config=config, record_pkg=True
    )

    assert results["version_used"] == "1.1"
    assert results["validation_errors"] == []


@pytest.mark.parametrize(
    "json_data,exception,expected",
    [
        (
            "{[,]}",
            json.JSONDecodeError,
            (
                "unexpected character: line 1 column 2 (char 1)",
                "Expecting property name enclosed in double quotes: line 1 column 2 (char 1)",
            ),
        ),
        (
            '{"version": "1.bad"}',
            OCDSVersionError,
            ("The version in the data is not one of 1.0, 1.1",),
        ),
    ],
)
def test_ocds_json_output_bad_data(json_data, exception, expected):
    cove_temp_folder = tempfile.mkdtemp(prefix="lib-cove-ocds-tests-", dir=tempfile.gettempdir())

    file_path = os.path.join(cove_temp_folder, "bad_data.json")
    with open(file_path, "w") as fp:
        fp.write(json_data)
    try:
        with pytest.raises(exception) as excinfo:
            ocds_json_output(cove_temp_folder, file_path, schema_version="", convert=False)

        assert str(excinfo.value) in expected
    finally:
        shutil.rmtree(cove_temp_folder)

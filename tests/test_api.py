import os
import shutil
import tempfile

import pytest

import libcoveocds.config
from libcoveocds.api import APIException, ocds_json_output
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
    "json_data,expected",
    [
        ("{[,]}", "The file looks like invalid json"),
        (
            '{"version": "1.bad"}',
            "\x1b[1;31mThe schema version in your data is not valid. Accepted values: ['1.0', '1.1']\x1b[1;m",
        ),
    ],
)
def test_ocds_json_output_bad_data(json_data, expected):
    cove_temp_folder = tempfile.mkdtemp(prefix="lib-cove-ocds-tests-", dir=tempfile.gettempdir())

    file_path = os.path.join(cove_temp_folder, "bad_data.json")
    with open(file_path, "w") as fp:
        fp.write(json_data)
    try:
        with pytest.raises(APIException) as excinfo:
            ocds_json_output(cove_temp_folder, file_path, schema_version="", convert=False)

        assert str(excinfo.value) == expected
    finally:
        shutil.rmtree(cove_temp_folder)

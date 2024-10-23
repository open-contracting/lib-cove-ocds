import json
import os
import shutil
import tempfile

import pytest
from click.testing import CliRunner

from libcoveocds.__main__ import main
from libcoveocds.exceptions import OCDSVersionError


@pytest.mark.parametrize(
    ("data", "exception", "expected"),
    [
        (
            "{[,]}",
            json.JSONDecodeError,
            (
                "unexpected character: line 1 column 2 (char 1)",
                "Expecting property name enclosed in double quotes: line 1 column 2 (char 1)",  # orjson
                "Key name must be string at char: line 1 column 2 (char 1)",  # pypy
            ),
        ),
        (
            '{"version": "1.bad"}',
            OCDSVersionError,
            ("The version in the data is not one of 1.0, 1.1",),
        ),
    ],
)
def test_failure(data, exception, expected, tmpdir):
    path = os.path.join(tmpdir, "bad_data.json")
    with open(path, "w") as f:
        f.write(data)

    runner = CliRunner()
    result = runner.invoke(main, [path])

    assert result.exit_code == 1
    assert result.output == ""
    assert result.exc_info[0] is exception
    assert str(result.exc_info[1]) in expected


@pytest.mark.parametrize(
    "path",
    [
        os.path.join("tests", "fixtures", "common_checks", "basic_1.json"),
        os.path.join("tests", "fixtures", "api", "basic_1.json"),
        os.path.join("tests", "fixtures", "api", "basic_record_package.json"),
    ],
)
def test_success(path):
    runner = CliRunner()
    result = runner.invoke(main, [path])
    data = json.loads(result.output)

    assert result.exit_code == 0
    assert data["validation_errors"] == []


def test_old_schema():
    runner = CliRunner()
    result = runner.invoke(main, ["-s", "1.0", os.path.join("tests", "fixtures", "common_checks", "basic_1.json")])

    assert result.exit_code == 0


def test_set_output_dir():
    output_dir = tempfile.mkdtemp(
        prefix="lib-cove-ocds-tests-",
        dir=tempfile.gettempdir(),
    )
    runner = CliRunner()
    result = runner.invoke(
        main, ["-o", output_dir, os.path.join("tests", "fixtures", "common_checks", "basic_1.json")]
    )

    # This will fail because tempfile.mkdtemp already will make the directory, and so it already exists
    assert result.exit_code == 1
    assert result.output.startswith("Directory ")
    assert result.output.endswith("already exists\n")

    shutil.rmtree(output_dir)


def test_set_output_dir_and_delete():
    output_dir = tempfile.mkdtemp(
        prefix="lib-cove-ocds-tests-",
        dir=tempfile.gettempdir(),
    )
    runner = CliRunner()
    result = runner.invoke(
        main, ["-d", "-o", output_dir, os.path.join("tests", "fixtures", "common_checks", "basic_1.json")]
    )
    # Should have results file and original file and nothing else
    expected_files = ["basic_1.json", "results.json"]

    assert result.exit_code == 0

    assert sorted(os.listdir(output_dir)) == sorted(expected_files)

    shutil.rmtree(output_dir)


def test_set_output_dir_and_delete_and_exclude():
    output_dir = tempfile.mkdtemp(
        prefix="lib-cove-ocds-tests-",
        dir=tempfile.gettempdir(),
    )
    runner = CliRunner()
    result = runner.invoke(
        main, ["-d", "-e", "-o", output_dir, os.path.join("tests", "fixtures", "common_checks", "basic_1.json")]
    )
    # Should have results file only
    expected_files = ["results.json"]

    assert result.exit_code == 0

    assert sorted(os.listdir(output_dir)) == sorted(expected_files)

    shutil.rmtree(output_dir)

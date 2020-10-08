import json
import os
import shutil
import tempfile

from click.testing import CliRunner

from libcoveocds.cli.__main__ import process


def test_basic():
    runner = CliRunner()
    result = runner.invoke(process, os.path.join("tests", "fixtures", "common_checks", "basic_1.json"))
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "1.1" == data.get("version_used")


def test_old_schema():
    runner = CliRunner()
    result = runner.invoke(process, "-s 1.0 " + os.path.join("tests", "fixtures", "common_checks", "basic_1.json"))
    print(result.output)
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "1.0" == data.get("version_used")


def test_set_output_dir():
    output_dir = tempfile.mkdtemp(
        prefix="lib-cove-ocds-tests-",
        dir=tempfile.gettempdir(),
    )
    runner = CliRunner()
    result = runner.invoke(
        process, " -o " + output_dir + " " + os.path.join("tests", "fixtures", "common_checks", "basic_1.json")
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
        process, " -d -o " + output_dir + " " + os.path.join("tests", "fixtures", "common_checks", "basic_1.json")
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "1.1" == data.get("version_used")
    # Should have results file and original file and nothing else
    expected_files = ["basic_1.json", "results.json"]
    assert sorted(os.listdir(output_dir)) == sorted(expected_files)
    shutil.rmtree(output_dir)


def test_set_output_dir_and_delete_and_exclude():
    output_dir = tempfile.mkdtemp(
        prefix="lib-cove-ocds-tests-",
        dir=tempfile.gettempdir(),
    )
    runner = CliRunner()
    result = runner.invoke(
        process, " -d -e -o " + output_dir + " " + os.path.join("tests", "fixtures", "common_checks", "basic_1.json")
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "1.1" == data.get("version_used")
    # Should have results file only
    expected_files = ["results.json"]
    assert sorted(os.listdir(output_dir)) == sorted(expected_files)
    shutil.rmtree(output_dir)


def test_set_output_dir_and_convert():
    output_dir = tempfile.mkdtemp(
        prefix="lib-cove-ocds-tests-",
        dir=tempfile.gettempdir(),
    )
    runner = CliRunner()
    result = runner.invoke(
        process, " -c -d -o " + output_dir + " " + os.path.join("tests", "fixtures", "common_checks", "basic_1.json")
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "1.1" == data.get("version_used")
    # Should have results file and original file and the converted files
    expected_files = ["basic_1.json", "flattened", "flattened.ods", "flattened.xlsx", "results.json"]
    assert sorted(os.listdir(output_dir)) == sorted(expected_files)
    # Flattened should be a directory of csv's.
    # We aren't going to check names fully
    # That would leave this test brittle if flatten-tools naming scheme changed,
    # so we will just check extension
    for filename in os.listdir(os.path.join(output_dir, "flattened")):
        assert filename.endswith(".csv")
    shutil.rmtree(output_dir)

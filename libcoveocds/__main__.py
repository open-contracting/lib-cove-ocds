import json
import os
import shutil
import sys
import tempfile

import click

import libcoveocds.api
from libcoveocds.config import LibCoveOCDSConfig
from libcoveocds.lib.additional_checks import CHECKS


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


@click.command()
@click.argument("filename")
@click.option("-c", "--convert", is_flag=True, help="Convert data from nested (json) to flat format (spreadsheet)")
@click.option(
    "-o", "--output-dir", default=None, help="Directory where the output is created, defaults to the name of the file"
)
@click.option(
    "-s",
    "--schema-version",
    type=click.Choice(LibCoveOCDSConfig().config["schema_version_choices"]),
    help="Version of the schema to validate the data, eg '1.0'",
)
@click.option("-d", "--delete", is_flag=True, help="Delete existing directory if it exits")
@click.option("-e", "--exclude-file", is_flag=True, help="Do not include the file in the output directory")
@click.option(
    "--additional-checks", default="all", type=click.Choice(CHECKS), help="The set of additional checks to perform"
)
@click.option("--skip-aggregates", is_flag=True, help="Skip releases_aggregates and records_aggregates")
@click.option(
    "--standard-zip",
    type=click.Path(exists=True, dir_okay=False),
    help="Path to a ZIP file containing the standard repository",
)
def main(
    filename,
    output_dir,
    convert,
    schema_version,
    delete,
    exclude_file,
    additional_checks,
    skip_aggregates,
    standard_zip,
):
    if standard_zip:
        standard_zip = f"file://{standard_zip}"

    config = LibCoveOCDSConfig()
    config.config["standard_zip"] = standard_zip
    config.config["cache_all_requests"] = True
    config.config["additional_checks"] = additional_checks
    config.config["skip_aggregates"] = skip_aggregates
    config.config["context"] = "api"

    # Do we have output on disk? We only do in certain modes
    has_disk_output = output_dir or convert or delete or exclude_file
    if has_disk_output:
        if not output_dir:
            output_dir = filename.split("/")[-1].split(".")[0]

        if os.path.exists(output_dir):
            if delete:
                shutil.rmtree(output_dir)
            else:
                print(f"Directory {output_dir} already exists")
                sys.exit(1)
        os.makedirs(output_dir)

        if not exclude_file:
            shutil.copy2(filename, output_dir)
    else:
        # If not, just put in /tmp and delete after
        output_dir = tempfile.mkdtemp(
            prefix="lib-cove-ocds-cli-",
            dir=tempfile.gettempdir(),
        )

    try:
        result = libcoveocds.api.ocds_json_output(
            output_dir, filename, schema_version, convert=convert, file_type="json", lib_cove_ocds_config=config
        )
    finally:
        if not has_disk_output:
            shutil.rmtree(output_dir)

    output = json.dumps(result, indent=2, cls=SetEncoder)
    if has_disk_output:
        with open(os.path.join(output_dir, "results.json"), "w") as fp:
            fp.write(output)

    print(output)


if __name__ == "__main__":
    main()

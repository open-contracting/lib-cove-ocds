import json
import os
import shutil
import sys
import tempfile

import click

import libcoveocds.api
from libcoveocds.config import LibCoveOCDSConfig


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
@click.option("-s", "--schema-version", default=None, help="Version of the schema to validate the data, eg '1.0'")
@click.option("-d", "--delete", is_flag=True, help="Delete existing directory if it exits")
@click.option("-e", "--exclude-file", is_flag=True, help="Do not include the file in the output directory")
def process(filename, output_dir, convert, schema_version, delete, exclude_file):

    if schema_version:
        lib_cove_ocds_config = LibCoveOCDSConfig()
        version_choices = lib_cove_ocds_config.config.get("schema_version_choices")
        if schema_version not in version_choices:
            print(
                "Value for schema version option is not valid. Accepted values: {}".format(", ".join(version_choices))
            )
            sys.exit(1)

    # Do we have output on disk? We only do in certain modes
    has_disk_output = output_dir or convert or delete or exclude_file
    if has_disk_output:
        if not output_dir:
            output_dir = filename.split("/")[-1].split(".")[0]

        if os.path.exists(output_dir):
            if delete:
                shutil.rmtree(output_dir)
            else:
                print("Directory {} already exists".format(output_dir))
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
            output_dir, filename, schema_version, convert=convert, cache_schema=True, file_type="json"
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
    process()

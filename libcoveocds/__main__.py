import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

import click

from libcoveocds.common_checks import common_checks_ocds
from libcoveocds.lib.additional_checks import CHECKS
from libcoveocds.lib.api import context_api_transform
from libcoveocds.schema import SchemaOCDS


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


@click.command()
@click.argument("filename")
@click.option(
    "-s",
    "--schema-version",
    help="OCDS version againsts which to validate, like '1.0' (defaults to version declared in data)",
)
@click.option(
    "-o",
    "--output-dir",
    type=click.Path(path_type=Path),
    help="Output directory (defaults to basename of FILENAME)",
)
@click.option("-d", "--delete", is_flag=True, help="Delete output directory if it exists")
@click.option("-e", "--exclude-file", is_flag=True, help="Exclude FILENAME from the output directory")
@click.option(
    "--additional-checks", default="all", type=click.Choice(CHECKS), help="The set of additional checks to perform"
)
@click.option("--skip-aggregates", is_flag=True, help="Skip count and unique_ocids_count")
@click.option(
    "--standard-zip",
    type=click.Path(exists=True, dir_okay=False),
    help="Path to a ZIP file containing the standard repository",
)
def main(
    filename,
    output_dir,
    schema_version,
    delete,
    exclude_file,
    additional_checks,
    skip_aggregates,
    standard_zip,
):
    if standard_zip:
        standard_zip = f"file://{standard_zip}"

    if output_dir:
        if output_dir.exists():
            if delete:
                shutil.rmtree(output_dir)
            else:
                sys.exit(f"Directory {output_dir} already exists")
        output_dir.mkdir(parents=True)

        # Including the file helps when batch processing.
        if not exclude_file:
            shutil.copy2(filename, output_dir)
    else:
        output_dir = tempfile.mkdtemp(prefix="lib-cove-ocds-cli-", dir=tempfile.gettempdir())

    try:
        with open(filename, "rb") as f:
            json_data = json.loads(f.read())

        schema_obj = SchemaOCDS(
            schema_version, json_data, record_pkg="records" in json_data, api=True, standard_base_url=standard_zip
        )

        context = {"file_type": "json"}

        # context is edited in-place.
        context_api_transform(
            common_checks_ocds(
                context,
                output_dir,
                json_data,
                schema_obj,
                # common_checks_context(cache=True) caches the results to a file, which is not needed in API context.
                cache=False,
                api=True,
                additional_checks=additional_checks,
                skip_aggregates=skip_aggregates,
            )
        )

        if schema_obj.json_deref_error:
            context["json_deref_error"] = schema_obj.json_deref_error
    finally:
        if not output_dir:
            shutil.rmtree(output_dir)

    output = json.dumps(context, indent=2, cls=SetEncoder)
    if output_dir:
        with open(os.path.join(output_dir, "results.json"), "w") as f:
            f.write(output)
    click.echo(output)


if __name__ == "__main__":
    main()

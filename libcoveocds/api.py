import os
import warnings

from libcove.lib.tools import get_file_type

from libcoveocds.common_checks import common_checks_ocds
from libcoveocds.config import LibCoveOCDSConfig
from libcoveocds.lib.api import context_api_transform
from libcoveocds.schema import SchemaOCDS
from libcoveocds.util import json

try:
    from libcove.lib.common import get_spreadsheet_meta_data
    from libcove.lib.converters import convert_json, convert_spreadsheet
except ImportError:
    pass


class APIException(Exception):
    pass


def ocds_json_output(
    output_dir,
    file,
    schema_version,
    convert,
    file_type=None,
    json_data=None,
    lib_cove_ocds_config=None,
    record_pkg=None,
):
    """
    If flattentool is not installed, ``file_type`` must be ``"json"`` and ``convert`` must be falsy.
    """

    if not lib_cove_ocds_config:
        lib_cove_ocds_config = LibCoveOCDSConfig()
    if not file_type:
        file_type = get_file_type(file)
    if not json_data and file_type == "json":
        with open(file, "rb") as f:
            try:
                json_data = json.loads(f.read())
            except ValueError:
                raise APIException("The file looks like invalid json")

    if record_pkg is None:
        record_pkg = "records" in json_data

    if file_type == "json":
        schema_obj = SchemaOCDS(
            schema_version, json_data, lib_cove_ocds_config=lib_cove_ocds_config, record_pkg=record_pkg
        )
    else:
        metatab_schema_url = SchemaOCDS(select_version="1.1", lib_cove_ocds_config=lib_cove_ocds_config).pkg_schema_url
        metatab_data = get_spreadsheet_meta_data(output_dir, file, metatab_schema_url, file_type=file_type)
        schema_obj = SchemaOCDS(schema_version, lib_cove_ocds_config=lib_cove_ocds_config, package_data=metatab_data)

    if schema_obj.invalid_version_data:
        msg = "\033[1;31mThe schema version in your data is not valid. Accepted values: {}\033[1;m"
        raise APIException(msg.format(str(list(lib_cove_ocds_config.config["schema_version_choices"]))))

    if schema_obj.extensions:
        schema_obj.create_extended_schema_file(output_dir, "")

    # Used in conversions.
    schema_url = schema_obj.extended_schema_file or schema_obj.schema_url

    context = {"file_type": file_type}
    if file_type == "json":
        if convert:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore")  # flattentool uses UserWarning, so we can't set a specific category

                context.update(
                    convert_json(
                        output_dir,
                        "",
                        file,
                        lib_cove_ocds_config,
                        schema_url=schema_url,
                        cache=False,
                        flatten=True,
                    )
                )
    else:
        context.update(
            convert_spreadsheet(
                output_dir,
                "",
                file,
                file_type,
                lib_cove_ocds_config,
                schema_url=schema_url,
                cache=False,
                pkg_schema_url=schema_obj.pkg_schema_url,
            )
        )

        with open(context["converted_path"], encoding="utf-8") as fp:
            json_data = json.load(fp)

    # context is edited in-place.
    context_api_transform(
        common_checks_ocds(
            context,
            output_dir,
            json_data,
            schema_obj,
            # `cache` writes the results to a file, which is only relevant in the context of repetitive web requests.
            cache=False,
        )
    )

    context["json_deref_error"] = schema_obj.json_deref_error
    context["invalid_version_data"] = schema_obj.invalid_version_data

    if file_type == "xlsx":
        # Remove unwanted files in the output
        # TODO: can we do this by no writing the files in the first place?
        os.remove(os.path.join(output_dir, "heading_source_map.json"))
        os.remove(os.path.join(output_dir, "cell_source_map.json"))

    return context

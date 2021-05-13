import json
import os
from collections import OrderedDict

from libcove.lib.common import get_spreadsheet_meta_data
from libcove.lib.converters import convert_json, convert_spreadsheet
from libcove.lib.tools import get_file_type

from libcoveocds.common_checks import common_checks_ocds
from libcoveocds.config import LibCoveOCDSConfig
from libcoveocds.lib.api import context_api_transform
from libcoveocds.schema import SchemaOCDS


class APIException(Exception):
    pass


def ocds_json_output(
    output_dir,
    file,
    schema_version,
    convert,
    cache_schema=False,
    file_type=None,
    json_data=None,
    lib_cove_ocds_config=None,
    record_pkg=False,
):

    if not lib_cove_ocds_config:
        lib_cove_ocds_config = LibCoveOCDSConfig()

    # cache_schema is a deprecated option - now set cache_all_requests in the config instead.
    if cache_schema:
        lib_cove_ocds_config.config["cache_all_requests"] = True

    context = {}
    if not file_type:
        file_type = get_file_type(file)
    context = {"file_type": file_type}

    if file_type == "json":
        if not json_data:
            with open(file, encoding="utf-8") as fp:
                try:
                    json_data = json.load(fp, object_pairs_hook=OrderedDict)
                except ValueError:
                    raise APIException("The file looks like invalid json")

        schema_ocds = SchemaOCDS(schema_version, json_data, lib_cove_ocds_config=lib_cove_ocds_config,
                                 record_pkg=record_pkg)

        if schema_ocds.invalid_version_data:
            msg = "\033[1;31mThe schema version in your data is not valid. Accepted values: {}\033[1;m"
            raise APIException(msg.format(str(list(schema_ocds.version_choices.keys()))))
        if schema_ocds.extensions:
            schema_ocds.create_extended_schema_file(output_dir, "")

        url = schema_ocds.extended_schema_file or schema_ocds.schema_url

        if convert:
            context.update(
                convert_json(output_dir, "", file, lib_cove_ocds_config, schema_url=url, flatten=True, cache=False)
            )

    else:
        metatab_schema_url = SchemaOCDS(select_version="1.1", lib_cove_ocds_config=lib_cove_ocds_config).pkg_schema_url
        metatab_data = get_spreadsheet_meta_data(output_dir, file, metatab_schema_url, file_type=file_type)
        schema_ocds = SchemaOCDS(schema_version, release_data=metatab_data, lib_cove_ocds_config=lib_cove_ocds_config)

        if schema_ocds.invalid_version_data:
            msg = "\033[1;31mThe schema version in your data is not valid. Accepted values: {}\033[1;m"
            raise APIException(msg.format(str(list(schema_ocds.version_choices.keys()))))
        if schema_ocds.extensions:
            schema_ocds.create_extended_schema_file(output_dir, "")

        url = schema_ocds.extended_schema_file or schema_ocds.schema_url
        pkg_url = schema_ocds.pkg_schema_url

        context.update(
            convert_spreadsheet(
                output_dir,
                "",
                file,
                file_type,
                lib_cove_ocds_config,
                schema_url=url,
                pkg_schema_url=pkg_url,
                cache=False,
            )
        )

        with open(context["converted_path"], encoding="utf-8") as fp:
            json_data = json.load(fp, object_pairs_hook=OrderedDict)

    context = context_api_transform(
        common_checks_ocds(context, output_dir, json_data, schema_ocds, api=True, cache=False)
    )

    if file_type == "xlsx":
        # Remove unwanted files in the output
        # TODO: can we do this by no writing the files in the first place?
        os.remove(os.path.join(output_dir, "heading_source_map.json"))
        os.remove(os.path.join(output_dir, "cell_source_map.json"))

    return context

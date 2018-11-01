import os
import json
from libcoveocds.libcore.tools import get_file_type
from libcoveocds.lib.api import APIException
from libcoveocds.schema import SchemaOCDS
from libcoveocds.libcore.converters import convert_json, convert_spreadsheet
from libcoveocds.libcore.common import get_spreadsheet_meta_data
from libcoveocds.common_checks import common_checks_ocds
from libcoveocds.lib.api import context_api_transform
from libcoveocds.config import LibCoveOCDSConfig


def ocds_json_output(output_dir, file, schema_version, convert, cache_schema=False, file_type=None, json_data=None,
                     lib_cove_ocds_config=None):

    if not lib_cove_ocds_config:
        lib_cove_ocds_config = LibCoveOCDSConfig()

    context = {}
    if not file_type:
        file_type = get_file_type(file)
    context = {"file_type": file_type}

    if file_type == 'json':
        if not json_data:
            with open(file, encoding='utf-8') as fp:
                try:
                    json_data = json.load(fp)
                except ValueError:
                    raise APIException('The file looks like invalid json')

        schema_ocds = SchemaOCDS(schema_version, json_data, cache_schema=cache_schema)

        if schema_ocds.invalid_version_data:
            msg = '\033[1;31mThe schema version in your data is not valid. Accepted values: {}\033[1;m'
            raise APIException(msg.format(str(list(schema_ocds.version_choices.keys()))))
        if schema_ocds.extensions:
            schema_ocds.create_extended_release_schema_file(output_dir, "")

        url = schema_ocds.extended_schema_file or schema_ocds.release_schema_url

        if convert:
            context.update(convert_json(
                output_dir, '', file, lib_cove_ocds_config, schema_url=url, flatten=True, cache=False)
            )

    else:
        metatab_schema_url = SchemaOCDS(select_version='1.1').release_pkg_schema_url
        metatab_data = get_spreadsheet_meta_data(output_dir, file, metatab_schema_url, file_type=file_type)
        schema_ocds = SchemaOCDS(schema_version, release_data=metatab_data, cache_schema=cache_schema)

        if schema_ocds.invalid_version_data:
            msg = '\033[1;31mThe schema version in your data is not valid. Accepted values: {}\033[1;m'
            raise APIException(msg.format(str(list(schema_ocds.version_choices.keys()))))
        if schema_ocds.extensions:
            schema_ocds.create_extended_release_schema_file(output_dir, '')

        url = schema_ocds.extended_schema_file or schema_ocds.release_schema_url
        pkg_url = schema_ocds.release_pkg_schema_url

        context.update(convert_spreadsheet(
            output_dir, '', file, file_type, lib_cove_ocds_config, schema_url=url, pkg_schema_url=pkg_url, cache=False)
        )

        with open(context['converted_path'], encoding='utf-8') as fp:
            json_data = json.load(fp)

    context = context_api_transform(
        common_checks_ocds(context, output_dir, json_data, schema_ocds, api=True, cache=False)
    )

    if file_type == 'xlsx':
        # Remove unwanted files in the output
        # TODO: can we do this by no writing the files in the first place?
        os.remove(os.path.join(output_dir, 'heading_source_map.json'))
        os.remove(os.path.join(output_dir, 'cell_source_map.json'))

    return context

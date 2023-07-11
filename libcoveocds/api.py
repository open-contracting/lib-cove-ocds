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


def ocds_json_output(
    output_dir: str = "",
    file=None,  # : str | None
    schema_version=None,  # : str | None
    convert: bool = False,
    file_type=None,  # : str | None
    json_data=None,  # : dict | None
    lib_cove_ocds_config=None,  # : LibCoveOCDSConfig | None
    record_pkg=None,  # : bool | None
):
    """
    If flattentool is not installed, ``file_type`` must be ``"json"`` and ``convert`` must be falsy.

    ``file`` is required if:

    - ``file_type`` is empty
    - ``file_type`` is "json" and ``json_data`` is empty
    - ``file_type`` is "json" and ``convert`` is truthy
    - ``file_type` is not "json"

    In other words, ``file`` is optional if ``file_type`` is "json", ``json_data`` is present and ``convert`` is falsy.

    ``output_dir`` is required if:

    - ``file_type`` is "json" and ``convert`` is truthy
    - ``file_type` is not "json"
    - lib-cove hasn't merged #123

    In other words, ``output_dir`` is optional if ``file_type`` is "json" and ``convert`` is falsy.

    :param output_dir: The output directory
    :param file: The input data as a file
    :param schema_version: The major.minor version, e.g. "1.1". If not provided, it is determined by the ``version``
                           field in JSON data or the ``version`` cell in a metadata tab.
    :param convert: Whether to convert from JSON to XLSX
    :param file_type: The file format: "csv", "json" or "xlsx". If not provided, it is determined by the ``file``
                      extension or its first byte (i.e. ``{`` or ``[`` for JSON).
    :param json_data: The input data. If not provided, and if ``file_type`` is "json", it is read from the ``file``.
    :param lib_cove_ocds_config: A custom configuration of lib-cove-ocds
    :param record_pkg: Whether the input data is a record package. If not provided, it is determined by the presence of
                       the ``records`` field.
    """

    if not lib_cove_ocds_config:
        lib_cove_ocds_config = LibCoveOCDSConfig()
        lib_cove_ocds_config.config["context"] = "api"

    if not file_type:
        file_type = get_file_type(file)

    if not json_data and file_type == "json":
        with open(file, "rb") as f:
            json_data = json.loads(f.read())

    if record_pkg is None:
        record_pkg = "records" in json_data

    if file_type == "json":
        schema_obj = SchemaOCDS(schema_version, json_data, lib_cove_ocds_config, record_pkg=record_pkg)
    else:
        metatab_schema_url = SchemaOCDS("1.1", lib_cove_ocds_config=lib_cove_ocds_config).pkg_schema_url
        metatab_data = get_spreadsheet_meta_data(output_dir, file, metatab_schema_url, file_type=file_type)
        schema_obj = SchemaOCDS(schema_version, metatab_data, lib_cove_ocds_config)

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
            # common_checks_context(cache=True) caches the results to a file, which is not needed in API context.
            cache=False,
        )
    )

    if schema_obj.json_deref_error:
        context["json_deref_error"] = schema_obj.json_deref_error

    if file_type == "xlsx":
        # Remove unwanted files in the output
        # TODO: can we do this by no writing the files in the first place?
        os.remove(os.path.join(output_dir, "heading_source_map.json"))
        os.remove(os.path.join(output_dir, "cell_source_map.json"))

    return context

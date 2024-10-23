from libcoveocds.common_checks import common_checks_ocds
from libcoveocds.config import LibCoveOCDSConfig
from libcoveocds.lib.api import context_api_transform
from libcoveocds.schema import SchemaOCDS
from libcoveocds.util import json


def ocds_json_output(
    output_dir: str = "",
    file=None,  # : str | None
    schema_version=None,  # : str | None
    *,
    json_data=None,  # : dict | None
    lib_cove_ocds_config=None,  # : LibCoveOCDSConfig | None
    record_pkg=None,  # : bool | None
):
    """
    ``file`` is required if ``json_data`` is empty.

    :param output_dir: The output directory
    :param file: The input data as a file
    :param schema_version: The major.minor version, e.g. "1.1". If not provided, it is determined by the ``version``
                           field in JSON data or the ``version`` cell in a metadata tab.
    :param json_data: The input data. If not provided, it is read from the ``file``.
    :param lib_cove_ocds_config: A custom configuration of lib-cove-ocds
    :param record_pkg: Whether the input data is a record package. If not provided, it is determined by the presence of
                       the ``records`` field.
    """
    if not lib_cove_ocds_config:
        lib_cove_ocds_config = LibCoveOCDSConfig()
        lib_cove_ocds_config.config["context"] = "api"

    if not json_data:
        with open(file, "rb") as f:
            json_data = json.loads(f.read())

    if record_pkg is None:
        record_pkg = "records" in json_data

    schema_obj = SchemaOCDS(schema_version, json_data, lib_cove_ocds_config, record_pkg=record_pkg)

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
        )
    )

    if schema_obj.json_deref_error:
        context["json_deref_error"] = schema_obj.json_deref_error

    return context

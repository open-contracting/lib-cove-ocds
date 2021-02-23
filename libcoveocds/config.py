from collections import OrderedDict

LIB_COVE_OCDS_CONFIG_DEFAULT = {
    "app_name": "cove_ocds",
    "app_base_template": "cove_ocds/base.html",
    "app_verbose_name": "Open Contracting Data Standard Validator",
    "app_strapline": "Validate and Explore your data.",
    "schema_name": {"release": "release-package-schema.json", "record": "record-package-schema.json"},
    "schema_item_name": "release-schema.json",
    "schema_host": None,
    "schema_version_choices": OrderedDict(
        (  # {version: (display, url)}
            ("1.0", ("1.0", "https://standard.open-contracting.org/1.0/en/")),
            ("1.1", ("1.1", "https://standard.open-contracting.org/1.1/en/")),
        )
    ),
    "schema_codelists": OrderedDict(
        (  # {version: codelist_dir}
            ("1.1", "https://raw.githubusercontent.com/open-contracting/standard/1.1/schema/codelists/"),
        )
    ),
    "root_list_path": "releases",
    "root_id": "ocid",
    "convert_titles": False,
    "input_methods": ["upload", "url", "text"],
    "support_email": "data@open-contracting.org",
    "current_language": "en",
    "flatten_tool": {
        "disable_local_refs": True,
        "remove_empty_schema_columns": True,
    },
    "cache_all_requests": False,
}

# Set default schema version to the latest version
LIB_COVE_OCDS_CONFIG_DEFAULT["schema_version"] = list(LIB_COVE_OCDS_CONFIG_DEFAULT["schema_version_choices"].keys())[
    -1
]


class LibCoveOCDSConfig:
    def __init__(self, config=None):
        # We need to make sure we take a copy,
        #   so that changes to one config object don't end up effecting other config objects.
        if config:
            self.config = config.copy()
        else:
            self.config = LIB_COVE_OCDS_CONFIG_DEFAULT.copy()

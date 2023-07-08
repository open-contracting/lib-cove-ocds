LIB_COVE_OCDS_CONFIG_DEFAULT = {
    "app_name": "cove_ocds",
    "app_base_template": "cove_ocds/base.html",
    "app_verbose_name": "Open Contracting Data Review Tool",
    "app_strapline": "Review your OCDS data.",
    "schema_host": None,
    "schema_version_choices": {
        # version: (display, url, tag),
        "1.0": ("1.0", "https://standard.open-contracting.org/1.0/en/", "1__0__3"),
        "1.1": ("1.1", "https://standard.open-contracting.org/1.1/en/", "1__1__5"),
    },
    "schema_codelists": {
        # version: codelist_dir,
        "1.1": "https://raw.githubusercontent.com/open-contracting/standard/1.1/schema/codelists/",
    },
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
    "skip_aggregates": False,
    "standard_zip": None,
}

# Set default schema version to the latest version
LIB_COVE_OCDS_CONFIG_DEFAULT["schema_version"] = list(LIB_COVE_OCDS_CONFIG_DEFAULT["schema_version_choices"])[-1]


class LibCoveOCDSConfig:
    def __init__(self, config=None):
        # We need to make sure we take a copy,
        #   so that changes to one config object don't end up effecting other config objects.
        if config:
            self.config = config.copy()
        else:
            self.config = LIB_COVE_OCDS_CONFIG_DEFAULT.copy()

LIB_COVE_OCDS_CONFIG_DEFAULT = {
    # SchemaOCDS options
    # Note: "schema_version" is set after this dict.
    #
    # Used indirectly by lib-cove for "version_display_choices" and "version_used_display".
    "schema_version_choices": {
        # version: (display, url, tag),
        "1.0": ("1.0", "https://standard.open-contracting.org/1.0/en/", "1__0__3"),
        "1.1": ("1.1", "https://standard.open-contracting.org/1.1/en/", "1__1__5"),
    },
    # Used indirectly by lib-cove to construct "codelist_url".
    "schema_codelists": {
        # version: codelist_dir,
        "1.1": "https://raw.githubusercontent.com/open-contracting/standard/1.1/schema/codelists/",
    },
    # The language key to use to read extension metadata.
    "current_language": "en",
    # Path to ZIP file of standard repository.
    "standard_zip": None,
    #
    # lib-cove-web options
    #
    "app_name": "cove_ocds",
    "app_base_template": "cove_ocds/base.html",
    "app_verbose_name": "Open Contracting Data Review Tool",
    "app_strapline": "Review your OCDS data.",
    "input_methods": ["upload", "url", "text"],
    "support_email": "data@open-contracting.org",
    #
    # Flatten Tool options
    #
    "root_list_path": "releases",
    "root_id": "ocid",
    "convert_titles": False,
    "flatten_tool": {
        "disable_local_refs": True,
        "remove_empty_schema_columns": True,
    },
    #
    # lib-cove-ocds options
    #
    # Whether to cache requests that pass through to lib-cove.
    "cache_all_requests": False,
    # Which additional checks to perform ("all" or "none", per libcoveocds.lib.additional_checks.CHECKS).
    "additional_checks": "all",
    # Whether to add "releases_aggregates" and "records_aggregates" to the context.
    "skip_aggregates": False,
    # The context in which lib-cove-ocds is used ("web" or "api").
    "context": "web",
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

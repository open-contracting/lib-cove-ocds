import copy

LIB_COVE_OCDS_CONFIG_DEFAULT = {
    # SchemaOCDS options
    # Note: "schema_version" is set after this dict.
    #
    # Used by lib-cove in common_checks_context() via SchemaOCDS for "version_display_choices", "version_used_display".
    "schema_version_choices": {
        # version: (display, url, tag),
        "1.0": ("1.0", "https://standard.open-contracting.org/1.0/en/", "1__0__3"),
        "1.1": ("1.1", "https://standard.open-contracting.org/1.1/en/", "1__1__5"),
    },
    # Used by lib-cove in get_additional_codelist_values() via SchemaOCDS for "codelist_url".
    "schema_codelists": {
        # version: codelist_dir,
        "1.1": "https://raw.githubusercontent.com/open-contracting/standard/1.1/schema/codelists/",
    },
    # Path to ZIP file of standard repository.
    "standard_zip": None,
}

# Set default schema version to the latest version
LIB_COVE_OCDS_CONFIG_DEFAULT["schema_version"] = list(LIB_COVE_OCDS_CONFIG_DEFAULT["schema_version_choices"])[-1]


class LibCoveOCDSConfig:
    def __init__(self, config=None):
        self.config = copy.deepcopy(LIB_COVE_OCDS_CONFIG_DEFAULT)
        if config:
            self.config.update(config)

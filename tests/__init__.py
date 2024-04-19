import os.path

import libcoveocds.common_checks
import libcoveocds.config

if libcoveocds.common_checks.WEB_EXTRA_INSTALLED:
    CONFIG = None
else:
    CONFIG = libcoveocds.config.LibCoveOCDSConfig()
    CONFIG.config["context"] = "api"


def fixture_path(*paths):
    return os.path.join("tests", *paths)

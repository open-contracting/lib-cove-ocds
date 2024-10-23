import os.path

import libcoveocds.common_checks
import libcoveocds.config

CONFIG = None if libcoveocds.common_checks.WEB_EXTRA_INSTALLED else libcoveocds.config.LibCoveOCDSConfig()


def fixture_path(*paths):
    return os.path.join("tests", *paths)

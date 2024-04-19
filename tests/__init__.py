import os.path

import libcoveocds.config

try:
    import django  # noqa: F401

    CONFIG = None
except ImportError:
    CONFIG = libcoveocds.config.LibCoveOCDSConfig()
    CONFIG.config["context"] = "api"


def fixture_path(*paths):
    return os.path.join("tests", *paths)

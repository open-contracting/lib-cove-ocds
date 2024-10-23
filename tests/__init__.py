import os.path


def fixture_path(*paths):
    return os.path.join("tests", *paths)

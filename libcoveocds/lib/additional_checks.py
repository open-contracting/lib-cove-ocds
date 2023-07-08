from collections import defaultdict

import libcove.lib.tools as tools


def flatten_dict(data, path=""):
    for key, value in data.items():
        if not value:
            yield (f"{path}/{key}", value)
        elif isinstance(value, dict):
            yield from flatten_dict(value, f"{path}/{key}")
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    yield from flatten_dict(item, f"{path}/{key}/{i}")
                else:
                    yield (f"{path}/{key}/{i}", item)
        else:
            yield (f"{path}/{key}", value)


def empty_field(data, path_prefix):
    """Identifying when fields, objects and arrays exist but are empty or contain only whitespace"""

    for key, value in flatten_dict(data):
        if isinstance(value, str) and not value.strip() or isinstance(value, (dict, list)) and not value:
            yield {"json_location": f"{path_prefix}{key}"}


CHECKS = {"all": [empty_field], "none": []}


@tools.ignore_errors
def run_additional_checks(data, functions):
    if "records" in data:
        key = "records"
    elif "releases" in data:
        key = "releases"
    else:
        return []

    results = defaultdict(list)

    for i, data in enumerate(data[key]):
        for function in functions:
            for output in function(data, f"{key}/{i}"):
                results[function.__name__].append(output)

    # https://stackoverflow.com/a/12842716/244258
    results.default_factory = None
    return results

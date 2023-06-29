import libcove.lib.tools as tools


def flatten_dict(data, path=""):
    for key, value in sorted(data.items()):
        if isinstance(value, list):
            if len(value) == 0:
                yield (f"{path}/{key}", value)
            for num, item in enumerate(value):
                if isinstance(item, dict):
                    yield from flatten_dict(item, f"{path}/{key}/{num}")
                else:
                    yield (f"{path}/{key}/{num}", item)
        elif isinstance(value, dict):
            if len(value) == 0:
                yield (f"{path}/{key}", value)
            yield from flatten_dict(value, f"{path}/{key}")
        else:
            yield (f"{path}/{key}", value)


class AdditionalCheck:
    def __init__(self, **kw):
        self.failed = False
        self.output = []

    def process(self, data, path_prefix):
        pass


class EmptyFieldCheck(AdditionalCheck):
    """Identifying when fields, objects and arrays exist but are empty or contain only whitespace"""

    def update_object(self, path_prefix, key):
        self.failed = True
        self.output.append({"type": "empty_field", "json_location": path_prefix + key})

    def process(self, data, path_prefix):
        flattened_data = dict(flatten_dict(data))

        for key, value in flattened_data.items():
            if isinstance(value, str) and len(value.strip()) == 0:
                self.update_object(path_prefix, key)
            elif isinstance(value, dict) and len(value) == 0:
                self.update_object(path_prefix, key)
            elif isinstance(value, list) and len(value) == 0:
                self.update_object(path_prefix, key)


TEST_CLASSES = {"additional": [EmptyFieldCheck]}


def get_additional_checks_results(test_instances):
    results = {}

    for test_instance in test_instances:
        if not test_instance.failed:
            continue

        for output in test_instance.output:
            type = output["type"]
            results.setdefault(type, [])
            output.pop("type", None)
            results[type].append(output)

    return results


def get_file_type_records_or_releases(json_data):
    if json_data.get("releases"):
        return "releases"
    return "records"


@tools.ignore_errors
def run_additional_checks(json_data, test_classes):
    if json_data.get("releases") is None and json_data.get("records") is None:
        return []

    file_type = get_file_type_records_or_releases(json_data)

    test_instances = [test_cls(data=json_data[file_type]) for test_cls in test_classes]

    for num, data in enumerate(json_data[file_type]):
        for test_instance in test_instances:
            test_instance.process(data, f"{file_type}/{num}")

    return get_additional_checks_results(test_instances)

from collections import OrderedDict

import libcove.lib.tools as tools


def flatten_dict(release, path=""):
    for key, value in sorted(release.items()):
        if isinstance(value, list):
            if len(value) == 0:
                yield ("{}/{}".format(path, key), value)
            for num, item in enumerate(value):
                if isinstance(item, dict):
                    yield from flatten_dict(item, "{}/{}/{}".format(path, key, num))
                else:
                    yield ("{}/{}/{}".format(path, key, num), item)
        elif isinstance(value, dict):
            if len(value) == 0:
                yield ("{}/{}".format(path, key), value)
            yield from flatten_dict(value, "{}/{}".format(path, key))
        else:
            yield ("{}/{}".format(path, key), value)


class AdditionalCheck():
    def __init__(self, **kw):
        self.releases = kw.get('releases')
        self.failed = False
        self.output = []

    def process(self, release, path_prefix):
        pass


class EmptyFieldCheck(AdditionalCheck):
    """Identifying when fields, objects and arrays exist but are empty or contain only whitespace"""

    def update_object(self, path_prefix, key):
        self.failed = True
        self.output.append({
            'type': 'empty_field',
            'json_location': path_prefix + key
        })

    def process(self, release, path_prefix):
        flattened_release = OrderedDict(flatten_dict(release))

        for key, value in flattened_release.items():
            if isinstance(value, str) and len(value.strip()) == 0:
                self.update_object(path_prefix, key)
            elif isinstance(value, dict) and len(value) == 0:
                self.update_object(path_prefix, key)
            elif isinstance(value, list) and len(value) == 0:
                self.update_object(path_prefix, key)


TEST_CLASSES = {
    'additional': [
        EmptyFieldCheck
    ]
}


def get_additional_checks_results(test_instances):
    results = {}

    for test_instance in test_instances:
        if not test_instance.failed:
            continue

        for output in test_instance.output:
            type = output['type']
            if type not in results:
                results[type] = []
            output.pop('type', None)
            results[type].append(output)

    return results


@tools.ignore_errors
def run_additional_checks(json_data, test_classes):
    if 'releases' not in json_data:
        return []
    test_instances = [test_cls(releases=json_data['releases']) for test_cls in test_classes]

    for num, release in enumerate(json_data['releases']):
        for test_instance in test_instances:
            test_instance.process(release, 'releases/{}'.format(num))

    return get_additional_checks_results(test_instances)

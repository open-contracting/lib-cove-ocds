import tempfile
import shutil
import libcoveocds.common_checks
import libcoveocds.schema
import os
import json


def test_basic_1():

    cove_temp_folder = tempfile.mkdtemp(prefix='libcoveocds-tests-', dir=tempfile.gettempdir())
    schema = libcoveocds.schema.SchemaOCDS()
    json_filename = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), 'fixtures', 'common_checks', 'basic_1.json'
    )
    with open(json_filename) as fp:
        json_data = json.load(fp)

    context = {
        'file_type': 'json',
    }

    try:

        results = libcoveocds.common_checks.common_checks_ocds(
            context,
            cove_temp_folder,
            json_data,
            schema,
        )

    finally:
        shutil.rmtree(cove_temp_folder)

    assert results['version_used'] == '1.1'


def test_dupe_ids_1():

    cove_temp_folder = tempfile.mkdtemp(prefix='libcoveocds-tests-', dir=tempfile.gettempdir())
    schema = libcoveocds.schema.SchemaOCDS()
    json_filename = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), 'fixtures', 'common_checks', 'dupe_ids_1.json'
    )
    with open(json_filename) as fp:
        json_data = json.load(fp)

    context = {
        'file_type': 'json',
    }

    try:

        results = libcoveocds.common_checks.common_checks_ocds(
            context,
            cove_temp_folder,
            json_data,
            schema,
        )

    finally:
        shutil.rmtree(cove_temp_folder)

    # https://github.com/OpenDataServices/cove/issues/782 Defines how we want this error shown
    assert len(results['validation_errors'][0][1]) == 2
    # test paths
    assert results['validation_errors'][0][1][0]['path'] == 'releases'
    assert results['validation_errors'][0][1][1]['path'] == 'releases'
    # test values
    # we don't know what order they will come out in, so fix the order ourselves
    values = [
        results['validation_errors'][0][1][0]['value'],
        results['validation_errors'][0][1][1]['value'],
    ]
    values.sort()
    assert values[0] == 'ocds-213czf-000-00001-01-planning'
    assert values[1] == 'ocds-213czf-000-00001-02-planning'

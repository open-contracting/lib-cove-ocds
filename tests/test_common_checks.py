import tempfile
import shutil
import libcoveocds.common_checks
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

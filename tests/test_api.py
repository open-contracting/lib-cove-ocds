import os
import shutil
import tempfile

import pytest

from libcoveocds.api import APIException, ocds_json_output


def test_basic_1():

    cove_temp_folder = tempfile.mkdtemp(prefix='lib-cove-ocds-tests-', dir=tempfile.gettempdir())
    json_filename = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), 'fixtures', 'api', 'basic_1.json'
    )

    results = ocds_json_output(cove_temp_folder, json_filename, schema_version='', convert=False)

    assert results['version_used'] == '1.1'


@pytest.mark.parametrize('json_data', ['{[,]}', '{"version": "1.bad"}'])
def test_ocds_json_output_bad_data(json_data):

    cove_temp_folder = tempfile.mkdtemp(prefix='lib-cove-ocds-tests-', dir=tempfile.gettempdir())

    file_path = os.path.join(cove_temp_folder, 'bad_data.json')
    with open(file_path, 'w') as fp:
        fp.write(json_data)
    try:
        with pytest.raises(APIException):
            ocds_json_output(cove_temp_folder, file_path, schema_version='', convert=False)
    finally:
        shutil.rmtree(cove_temp_folder)

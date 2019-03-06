import pytest
import tempfile
import shutil
import datetime
import os
from libcoveocds.api import ocds_json_output, APIException


def test_once():

    cove_temp_folder = tempfile.mkdtemp(prefix='lib-cove-ocds-tests-', dir=tempfile.gettempdir())
    json_filename = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), 'tests', 'fixtures', 'speed_test.json'
    )

    results = ocds_json_output(cove_temp_folder, json_filename, schema_version='', convert=False)

    print('.', end ="")

if __name__ == '__main__':

    start = datetime.datetime.utcnow()

    for i in range(1, 100):
        test_once()

    end = datetime.datetime.utcnow()

    print('')
    print((end - start).total_seconds())

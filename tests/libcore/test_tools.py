import pytest
import os
from libcoveocds.libcore.tools import get_file_type
from libcoveocds.libcore.exceptions import UnrecognisedFileType


@pytest.mark.parametrize('file_name', ['basic.xlsx', 'basic.XLSX'])
def test_get_file_type_xlsx_string(file_name):
    assert get_file_type(file_name) == 'xlsx'


@pytest.mark.parametrize('file_name', ['test.csv', 'test.CSV'])
def test_get_file_type_csv_string(file_name):
    assert get_file_type(file_name) == 'csv'


def test_get_file_type_json_string():
    assert get_file_type('test.json') == 'json'


def test_get_file_type_json_noextension_string():
    file_name = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'fixtures', 'tools', 'test'
    )
    assert get_file_type(file_name) == 'json'


def test_get_file_unrecognised_file_type_string():
    with pytest.raises(UnrecognisedFileType):
        get_file_type('test')

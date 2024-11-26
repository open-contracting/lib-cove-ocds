import jsonschema
import pytest
from referencing.exceptions import Unresolvable

from libcoveocds import SchemaOCDS, run_checks
from libcoveocds.exceptions import ValidatorError
from libcoveocds.validator import get_schema_validation_errors

UNRESOLVABLE = {
    "extensions": [
        "https://raw.githubusercontent.com/open-contracting/cove-ocds/main/tests/fixtures/referror_extension/extension.json"
    ],
    "releases": [{"broken": 1}],
}


def test_unresolvable():
    validator = SchemaOCDS(UNRESOLVABLE).validator(jsonschema.validators.Draft4Validator, jsonschema.FormatChecker())

    with pytest.raises(Unresolvable) as excinfo:
        list(validator.iter_errors(UNRESOLVABLE))

    assert str(excinfo.value).startswith("PointerToNowhere: '/definitions/Broken' does not exist within")


def test_validator_error():
    schema_obj = SchemaOCDS(UNRESOLVABLE)

    with pytest.raises(ValidatorError) as excinfo:
        get_schema_validation_errors(UNRESOLVABLE, schema_obj, {}, {})

    assert str(excinfo.value).startswith("PointerToNowhere: '/definitions/Broken' does not exist within")


def test_run_checks_error():
    schema_obj = SchemaOCDS(UNRESOLVABLE)

    context = run_checks(UNRESOLVABLE, schema_obj)

    assert context == {
        "json_deref_error": (
            "Error while resolving `#/definitions/Broken`: Unresolvable JSON pointer: '/definitions/Broken'"
        ),
    }

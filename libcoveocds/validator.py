import collections
import numbers
import re

import jsonschema
from jsonschema._utils import uniq
from jsonschema.exceptions import UndefinedTypeCheck, ValidationError, _RefResolutionError
from referencing.exceptions import Unresolvable

from libcoveocds.exceptions import ValidatorError

try:
    import orjson as json
except ImportError:
    import json

REQUIRED_RE = re.compile(r"^'([^']+)'")

VALIDATION_ERROR_TEMPLATE_LOOKUP = {
    "date-time": "Date is not in the correct format",
    "uri": "Invalid 'uri' found",
    "string": "{}'{}' is not a string. Check that the value {} has quotes at the start and end. "
    "Escape any quotes in the value with '\\'",
    "integer": "{}'{}' is not a integer. Check that the value {} doesn't contain decimal points "
    "or any characters other than 0-9. Integer values should not be in quotes. ",
    "number": "{}'{}' is not a number. Check that the value {} doesn't contain any characters "
    "other than 0-9 and dot ('.'). Number values should not be in quotes. ",
    "object": "{}'{}' is not a JSON object",
    "array": "{}'{}' is not a JSON array",
}


def get_schema_validation_errors(
    json_data,
    schema_obj,
    cell_source_map=None,
    heading_source_map=None,
):
    if cell_source_map is None:
        cell_source_map = {}
    if heading_source_map is None:
        heading_source_map = {}

    validation_errors = collections.defaultdict(list)

    # Force jsonschema to use our validator.
    # https://github.com/python-jsonschema/jsonschema/issues/994
    jsonschema.validators.validates("http://json-schema.org/draft-04/schema#")(VALIDATOR)

    our_validator = schema_obj.validator(VALIDATOR, jsonschema.FormatChecker())

    try:
        for e in our_validator.iter_errors(json_data):
            message = e.message
            path = "/".join(str(item) for item in e.path)
            path_no_number = "/".join(str(item) for item in e.path if not isinstance(item, int))

            value = {"path": path}
            cell_reference = cell_source_map.get(path)

            if cell_reference:
                first_reference = cell_reference[0]
                len_first_reference = len(first_reference)
                if len_first_reference == 4:  # noqa: PLR2004
                    (value["sheet"], value["col_alpha"], value["row_number"], value["header"]) = first_reference
                elif len_first_reference == 2:  # noqa: PLR2004
                    value["sheet"], value["row_number"] = first_reference

            header = value.get("header")

            header_extra = None
            pre_header = ""
            # Mostly we don't want this, but in a couple of specific cases we'll
            # set it
            instance = None

            if not header and len(e.path):
                header = e.path[-1]
                # Ignore the "releases" or "records" array.
                if isinstance(e.path[-1], int) and len(e.path) > 1:
                    # We're dealing with elements in an array of items at this point
                    pre_header = "Array element "
                    header_extra = f"{e.path[-2]}/[number]"

            null_clause = ""
            validator_type = e.validator
            if e.validator in {"format", "type"}:
                validator_type = e.validator_value
                if isinstance(e.validator_value, list):
                    validator_type = e.validator_value[0]
                    if "null" not in e.validator_value:
                        null_clause = "is not null, and"
                else:
                    null_clause = "is not null, and"

                message_template = VALIDATION_ERROR_TEMPLATE_LOOKUP.get(validator_type, message)

                if message_template:
                    message = message_template.format(pre_header, header, null_clause)

            if e.validator == "oneOf" and e.validator_value[0] == {"format": "date-time"}:
                # Give a nice date related error message for 360Giving date `oneOf`s.
                message = VALIDATION_ERROR_TEMPLATE_LOOKUP["date-time"]
                validator_type = "date-time"

            if not isinstance(e.instance, (dict, list)):
                value["value"] = e.instance

            if e.validator == "required":
                match = REQUIRED_RE.search(e.message)  # match "'id' is a required property"
                field_name = match.group(1) if match else e.message
                parent_name = None
                if len(e.path) > 2:  # noqa: PLR2004
                    parent_name = e.path[-2] if isinstance(e.path[-1], int) else e.path[-1]

                if heading := heading_source_map.get(f"{path_no_number}/{e.message}"):
                    field_name = heading[0][1]
                    value["header"] = heading[0][1]
                header = field_name
                if parent_name:
                    message = f"'{field_name}' is missing but required within '{parent_name}'"
                else:
                    message = f"'{field_name}' is missing but required"

            if e.validator == "enum":
                if "codelist" in e.schema and e.schema.get("openCodelist", False) is False:
                    continue
                message = f"Invalid code found in '{header}'"

            if e.validator in {
                "minItems",
                "minLength",
                "maxItems",
                "maxLength",
                "minProperties",
                "maxProperties",
                "minimum",
                "maximum",
                "anyOf",
                "multipleOf",
                "not",
            }:
                instance = e.instance

            if e.validator == "format" and validator_type not in {"date-time", "uri"}:
                instance = e.instance

            if getattr(e, "error_id", None) in {"oneOf_any", "oneOf_each"}:  # one_of_draft4
                instance = e.instance

            if header_extra is None:
                header_extra = header

            unique_validator_key = {
                "message": message,
                "validator": e.validator,
                "assumption": e.assumption if hasattr(e, "assumption") else None,
                # Don't pass this value for 'enum' and 'required' validators,
                # because it is not needed, and it will mean less grouping, which
                # we don't want.
                "validator_value": e.validator_value if e.validator not in {"enum", "required"} else None,
                "message_type": validator_type,
                "path_no_number": path_no_number,
                "header": header,
                "header_extra": header_extra,
                "null_clause": null_clause,
                "error_id": e.error_id if hasattr(e, "error_id") else None,
                "exclusiveMinimum": e.schema.get("exclusiveMinimum"),
                "exclusiveMaximum": e.schema.get("exclusiveMaximum"),
                "extras": getattr(e, "extras", None),
                "each": getattr(e, "each", None),
                "property": getattr(e, "property", None),
                "reprs": getattr(e, "reprs", None),  # one_of_draft4
            }
            if instance is not None:
                unique_validator_key["instance"] = instance
            validation_errors[json.dumps(unique_validator_key)].append(value)
    # iter_errors() can raise a subclass of Unresolvable if, for example, a $ref is broken, or _RefResolutionError.
    # For example: "PointerToNowhere: '/definitions/Unresolvable' does not exist within {big JSON blob}"
    except (Unresolvable, _RefResolutionError) as e:
        raise ValidatorError(e) from e
    finally:
        # Restore jsonschema's default validator, to not interfere with other software.
        # https://github.com/python-jsonschema/jsonschema/issues/994
        jsonschema.validators.validates("http://json-schema.org/draft-04/schema#")(
            jsonschema.validators.Draft4Validator
        )

    return dict(validation_errors)


def unique_ids_or_ocids(validator, ui, instance, schema):
    # `records` key from the JSON schema doesn't get passed through to here, so we look out for this $ref.
    # This may change if the way the schema files are structured changes.
    if schema.get("items") == {"$ref": "#/definitions/record"}:
        return unique_ids(validator, ui, instance, ["ocid"])

    if "$ref" in schema.get("items", {}) and schema["items"]["$ref"].endswith("release-schema.json"):
        return unique_ids(validator, ui, instance, ["ocid", "id"])

    return unique_ids(validator, ui, instance, ["id"])


# https://github.com/python-jsonschema/jsonschema/blob/ff9c75bcb596c17082c5b565c929e44741e1c010/jsonschema/_keywords.py#L206
def unique_ids(validator, ui, instance, id_names):
    if ui and validator.is_type(instance, "array"):
        seen = set()
        dupe = set()
        # Ensure `uniq(instance)` runs at most once when iterating over `instance`.
        uniq_has_run = False

        for item in instance:
            item_ids = tuple(item.get(id_name) for id_name in id_names) if isinstance(item, dict) else None
            if item_ids and all(item_id is not None and not isinstance(item_id, (dict, list)) for item_id in item_ids):
                if item_ids in seen:
                    dupe.add(item_ids)
                else:
                    seen.add(item_ids)
            elif not uniq_has_run:
                if not uniq(instance):
                    err = ValidationError("Array has non-unique elements", instance=instance)
                    err.error_id = "uniqueItems_no_ids"
                    yield err
                    return
                uniq_has_run = True

        for item_id in sorted(dupe):
            if len(id_names) == 1:
                msg = f"Non-unique {id_names[0]} values"
            else:
                msg = "Non-unique combination of {} values".format(", ".join(id_names))
            err = ValidationError(msg, instance=", ".join(map(str, item_id)))
            err.error_id = "uniqueItems_with_{}".format("__".join(id_names))
            yield err


# https://github.com/python-jsonschema/jsonschema/blob/ff9c75bcb596c17082c5b565c929e44741e1c010/jsonschema/_keywords.py#L351
def one_of_draft4(validator, one_of, instance, schema):
    """
    Yield individual errors for linked or embedded releases within a record.

    Return more information on the ValidationError, to allow us to use a translated message in cove-ocds.
    """
    subschemas = enumerate(one_of)
    all_errors = []
    for index, subschema in subschemas:
        errs = list(validator.descend(instance, subschema, schema_path=index))
        if not errs:
            first_valid = subschema
            break

        # STARTCHANGE
        # We check the title, because we don't have access to the field name, as it lives in the parent.
        # It will not match the releases array in a release package, because there is no oneOf.
        if (
            schema.get("title") == "Releases"
            or schema.get("description") == "An array of linking identifiers or releases"
        ):
            # If instance is not a list, or is empty, then validating against either subschema will work.
            # Assume instance is an array of Linked releases, if there are no "id"s in any of the releases.
            if not isinstance(instance, list) or all("id" not in release for release in instance):
                if "properties" in subschema.get("items", {}) and "id" not in subschema["items"]["properties"]:
                    for err in errs:
                        err.assumption = "linked_releases"
                        yield err
                    return
            # Assume instance is an array of Embedded releases, if there is an "id" in each of the releases.
            elif all("id" in release for release in instance):
                if "id" in subschema.get("items", {}).get("properties", {}) or subschema.get("items", {}).get(
                    "$ref", ""
                ).endswith("release-schema.json"):
                    for err in errs:
                        err.assumption = "embedded_releases"
                        yield err
                    return
            else:
                err = ValidationError(
                    "This array should contain either entirely embedded releases or linked releases. Embedded "
                    "releases contain an 'id' whereas linked releases do not. Your releases contain a mixture."
                )
                err.error_id = "releases_both_embedded_and_linked"
                yield err
                return
        # ENDCHANGE

        all_errors.extend(errs)
    else:
        err = ValidationError(f"{instance!r} is not valid under any of the given schemas", context=all_errors)
        # CHANGE
        err.error_id = "oneOf_any"
        yield err

    if more_valid := [each for _, each in subschemas if validator.evolve(schema=each).is_valid(instance)]:
        more_valid.append(first_valid)
        reprs = ", ".join(repr(schema) for schema in more_valid)
        err = ValidationError(f"{instance!r} is valid under each of {reprs}")
        # CHANGE
        err.error_id = "oneOf_each"
        # CHANGE
        err.reprs = reprs
        yield err


class TypeChecker:
    def is_type(self, instance, type_):
        # In simple order of number of occurrences in dereferenced-release-schema.json.
        match type_:
            case "null":
                return instance is None
            case "string":
                return isinstance(instance, str)
            case "object":
                return isinstance(instance, dict)
            case "array":
                return isinstance(instance, list)
            case "number":
                if isinstance(instance, bool):
                    return False
                return isinstance(instance, numbers.Number)
            case "integer":
                if isinstance(instance, bool):
                    return False
                return isinstance(instance, int)
            case "boolean":
                return isinstance(instance, bool)
            case _:
                raise UndefinedTypeCheck(type_)


VALIDATOR = jsonschema.validators.extend(jsonschema.validators.Draft4Validator, type_checker=TypeChecker())
# Removed for performance in https://github.com/OpenDataServices/cove/pull/156
VALIDATOR.VALIDATORS.pop("patternProperties")
VALIDATOR.VALIDATORS["uniqueItems"] = unique_ids_or_ocids
VALIDATOR.VALIDATORS["oneOf"] = one_of_draft4

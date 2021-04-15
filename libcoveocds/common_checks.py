import json

import bleach
from django.utils.html import conditional_escape, escape, format_html, mark_safe
from jsonschema.exceptions import ValidationError
from libcove.lib.common import common_checks_context, get_additional_codelist_values, unique_ids, validator
from libcove.lib.tools import decimal_default
from markdown_it import MarkdownIt

from libcoveocds.lib.additional_checks import TEST_CLASSES, run_additional_checks
from libcoveocds.lib.common_checks import (
    add_conformance_rule_errors,
    get_records_aggregates,
    get_releases_aggregates,
    lookup_schema,
)

md = MarkdownIt()

validation_error_lookup = {
    "date-time": mark_safe(
        'Incorrect date format. Dates should use the form YYYY-MM-DDT00:00:00Z. Learn more about <a href="https://standard.open-contracting.org/latest/en/schema/reference/#date">dates in OCDS</a>.'  # noqa: E501
    ),
}


def unique_ids_or_ocids(validator, ui, instance, schema):
    # `records` key from the JSON schema doesn't get passed through to here, so
    # we look out for this $ref — this may change if the way the schema files
    # are structured changes.
    if schema.get("items") == {"$ref": "#/definitions/record"}:
        return unique_ids(validator, ui, instance, schema, id_name="ocid")
    else:
        return unique_ids(validator, ui, instance, schema, id_name="id")


def oneOf_draft4(validator, oneOf, instance, schema):
    """
    oneOf_draft4 validator from
    https://github.com/Julian/jsonschema/blob/d16713a4296663f3d62c50b9f9a2893cb380b7af/jsonschema/_validators.py#L337

    Modified to:
    - sort the instance JSON, so we get a reproducible output that we
      can can test more easily
    - Yield all the individual errors for linked or embedded releases within a
      record.
    - Return more information on the ValidationError object, to allow us to
      replace the translation with a message in cove-ocds
    """
    subschemas = enumerate(oneOf)
    all_errors = []
    for index, subschema in subschemas:
        errs = list(validator.descend(instance, subschema, schema_path=index))
        if not errs:
            first_valid = subschema
            break
        # We check the title, because we don't have access to the field name,
        # as it lives in the parent.
        # It will not match the releases array in a release package, because
        # there is no oneOf.
        if (
            schema.get("title") == "Releases"
            or schema.get("description") == "An array of linking identifiers or releases"
        ):
            # If instance is not a list, or is a list of zero length, then
            # validating against either subschema will work.
            # Assume instance is an array of Linked releases, if there are no
            # "id"s in any of the releases.
            if type(instance) is not list or all("id" not in release for release in instance):
                if "properties" in subschema.get("items", {}) and "id" not in subschema["items"]["properties"]:
                    for err in errs:
                        err.assumption = "linked_releases"
                        yield err
                    return
            # Assume instance is an array of Embedded releases, if there is an
            # "id" in each of the releases
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
                    "This array should contain either entirely embedded releases or "
                    "linked releases. Embedded releases contain an 'id' whereas linked "
                    "releases do not. Your releases contain a mixture."
                )
                err.error_id = "releases_both_embedded_and_linked"
                yield err
                break

        all_errors.extend(errs)
    else:
        err = ValidationError(
            "%s is not valid under any of the given schemas"
            % (json.dumps(instance, sort_keys=True, default=decimal_default),),
            context=all_errors,
        )
        err.error_id = "oneOf_any"
        yield err

    more_valid = [s for i, s in subschemas if validator.is_valid(instance, s)]
    if more_valid:
        more_valid.append(first_valid)
        reprs = ", ".join(repr(schema) for schema in more_valid)
        err = ValidationError("%r is valid under each of %s" % (instance, reprs))
        err.error_id = "oneOf_each"
        err.reprs = reprs
        yield err


validator.VALIDATORS["uniqueItems"] = unique_ids_or_ocids
validator.VALIDATORS["oneOf"] = oneOf_draft4


def common_checks_ocds(context, upload_dir, json_data, schema_obj, api=False, cache=True):
    schema_name = schema_obj.pkg_schema_name
    common_checks = common_checks_context(
        upload_dir, json_data, schema_obj, schema_name, context, fields_regex=True, api=api, cache=cache
    )
    validation_errors = common_checks["context"]["validation_errors"]

    new_validation_errors = []
    for (json_key, values) in validation_errors:
        error = json.loads(json_key)
        new_message = validation_error_lookup.get(error["message_type"])
        if new_message:
            error["message_safe"] = conditional_escape(new_message)
        else:
            if "message_safe" in error:
                error["message_safe"] = mark_safe(error["message_safe"])
            else:
                error["message_safe"] = conditional_escape(error["message"])

        schema_block, ref_info = lookup_schema(schema_obj.get_pkg_schema_obj(deref=True), error["path_no_number"])
        if schema_block and error["message_type"] != "required":
            if "description" in schema_block:
                error["schema_title"] = escape(schema_block.get("title", ""))
                error["schema_description_safe"] = mark_safe(
                    bleach.clean(md.render(schema_block["description"]), tags=bleach.sanitizer.ALLOWED_TAGS + ["p"])
                )
            if ref_info:
                ref = ref_info["reference"]["$ref"]
                if ref.endswith("release-schema.json"):
                    ref = ""
                else:
                    ref = ref.strip("#")
                ref_path = "/".join(ref_info["path"])
                schema = "release-schema.json"
            else:
                ref = ""
                ref_path = error["path_no_number"]
                schema = "release-package-schema.json"
            error["docs_ref"] = format_html("{},{},{}", schema, ref, ref_path)

        new_validation_errors.append([json.dumps(error, sort_keys=True), values])
    common_checks["context"]["validation_errors"] = new_validation_errors

    context.update(common_checks["context"])

    if schema_name == "record-package-schema.json":
        context["records_aggregates"] = get_records_aggregates(json_data, ignore_errors=bool(validation_errors))
        # Do this for records, as there's no record-schema.json (this probably
        # causes problems for flatten-tool)
        context["schema_url"] = schema_obj.pkg_schema_url
    else:
        additional_codelist_values = get_additional_codelist_values(schema_obj, json_data)
        closed_codelist_values = {
            key: value for key, value in additional_codelist_values.items() if not value["isopen"]
        }
        open_codelist_values = {key: value for key, value in additional_codelist_values.items() if value["isopen"]}

        context.update(
            {
                "releases_aggregates": get_releases_aggregates(json_data, ignore_errors=bool(validation_errors)),
                "additional_closed_codelist_values": closed_codelist_values,
                "additional_open_codelist_values": open_codelist_values,
            }
        )

    additional_checks = run_additional_checks(
        json_data, TEST_CLASSES["additional"], ignore_errors=True, return_on_error=None
    )

    context.update({"additional_checks": additional_checks})

    context = add_conformance_rule_errors(context, json_data, schema_obj)
    return context

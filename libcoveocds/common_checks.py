import json
import re

from jsonschema.exceptions import ValidationError, _RefResolutionError
from libcove.lib.common import common_checks_context, get_additional_codelist_values, unique_ids, validator
from libcove.lib.tools import decimal_default
from referencing.exceptions import Unresolvable

from libcoveocds.lib.additional_checks import CHECKS, run_additional_checks
from libcoveocds.lib.common_checks import get_bad_ocid_prefixes, get_records_aggregates, get_releases_aggregates

try:
    import bleach
    from django.utils.html import conditional_escape, escape, format_html, mark_safe
    from markdown_it import MarkdownIt

    md = MarkdownIt()

    validation_error_lookup = {
        "date-time": mark_safe(
            "Incorrect date format. Dates should use the form YYYY-MM-DDT00:00:00Z. Learn more about "
            '<a href="https://standard.open-contracting.org/latest/en/schema/reference/#date">dates in OCDS</a>.'
        ),
    }
except ImportError:
    pass


def unique_ids_or_ocids(validator, ui, instance, schema):
    # `records` key from the JSON schema doesn't get passed through to here, so
    # we look out for this $ref — this may change if the way the schema files
    # are structured changes.
    if schema.get("items") == {"$ref": "#/definitions/record"}:
        return unique_ids(validator, ui, instance, schema, id_names=["ocid"])
    elif "$ref" in schema.get("items", {}) and schema["items"]["$ref"].endswith("release-schema.json"):
        return unique_ids(validator, ui, instance, schema, id_names=["ocid", "id"])
    else:
        return unique_ids(validator, ui, instance, schema, id_names=["id"])


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
                return

        all_errors.extend(errs)
    else:
        err = ValidationError(
            f"{json.dumps(instance, sort_keys=True, default=decimal_default)} "
            "is not valid under any of the given schemas",
            context=all_errors,
        )
        err.error_id = "oneOf_any"
        yield err

    more_valid = [s for i, s in subschemas if validator.evolve(schema=s).is_valid(instance)]
    if more_valid:
        more_valid.append(first_valid)
        reprs = ", ".join(repr(schema) for schema in more_valid)
        err = ValidationError(f"{instance!r} is valid under each of {reprs}")
        err.error_id = "oneOf_each"
        err.reprs = reprs
        yield err


validator.VALIDATORS["uniqueItems"] = unique_ids_or_ocids
validator.VALIDATORS["oneOf"] = oneOf_draft4


# ref_into is used calculate the HTML anchor for the field in the OCDS documentation.
def _lookup_schema(schema, path, ref_info=None):
    if not path:
        return schema, ref_info

    if hasattr(schema, "__reference__"):
        ref_info = {"path": path, "reference": schema.__reference__}

    if "items" in schema:
        return _lookup_schema(schema["items"], path, ref_info)
    if "properties" in schema:
        head, *tail = path
        if head in schema["properties"]:
            return _lookup_schema(schema["properties"][head], tail, ref_info)
    return None, None


def common_checks_ocds(
    context,
    upload_dir,
    json_data,
    schema_obj,
    cache=True,
):
    """
    param skip_aggregates: whether to skip "releases_aggregates" and "records_aggregates"
    """
    skip_aggregates = schema_obj.config.config["skip_aggregates"]
    additional_checks = CHECKS[schema_obj.config.config["additional_checks"]]

    # Pass "-" as the schema name. The associated logic is not required by lib-cove-ocds.
    try:
        common_checks = common_checks_context(
            upload_dir, json_data, schema_obj, "-", context, fields_regex=True, api=schema_obj.api, cache=cache
        )
    except (Unresolvable, _RefResolutionError) as e:
        # "PointerToNowhere: '/definitions/Unresolvable' does not exist within {big JSON blob}"
        schema_obj.json_deref_error = re.sub(r" within .+", "", str(e))
        return context

    ignore_errors = bool(common_checks["context"]["validation_errors"])

    # Note: Pelican checks whether the OCID prefix is registered.
    ocds_prefixes_bad_format = get_bad_ocid_prefixes(json_data)
    if ocds_prefixes_bad_format:
        context["conformance_errors"] = {"ocds_prefixes_bad_format": ocds_prefixes_bad_format}

    # If called in an API context:
    # - Skip the schema description and reference URL for OCID prefix conformance errors.
    # - Skip the formatted message, schema title, schema description and reference URL for validation errors.
    if not schema_obj.api:
        if "conformance_errors" in context:
            ocid_description = schema_obj.get_schema_obj()["properties"]["ocid"]["description"]
            # XXX: The last sentence is assumed to be a link to guidance in all versions of OCDS.
            index = ocid_description.rindex(". ") + 1
            context["conformance_errors"]["ocid_description"] = ocid_description[:index]
            context["conformance_errors"]["ocid_info_url"] = re.search(r"\((\S+)\)", ocid_description[index:]).group(1)

        new_validation_errors = []
        for (json_key, values) in common_checks["context"]["validation_errors"]:
            error = json.loads(json_key)

            new_message = validation_error_lookup.get(error["message_type"])
            if new_message:
                error["message_safe"] = conditional_escape(new_message)
            else:
                if "message_safe" in error:
                    error["message_safe"] = mark_safe(error["message_safe"])
                else:
                    error["message_safe"] = conditional_escape(error["message"])

            schema_block, ref_info = _lookup_schema(
                schema_obj.get_pkg_schema_obj(deref=True), error["path_no_number"].split("/")
            )
            if schema_block and error["message_type"] != "required":
                if "description" in schema_block:
                    error["schema_title"] = escape(schema_block.get("title", ""))
                    error["schema_description_safe"] = mark_safe(
                        bleach.clean(
                            md.render(schema_block["description"]), tags=bleach.sanitizer.ALLOWED_TAGS | {"p"}
                        )
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

    if not skip_aggregates:
        if "records" in json_data:
            context["records_aggregates"] = get_records_aggregates(json_data, ignore_errors=ignore_errors)
        else:
            context["releases_aggregates"] = get_releases_aggregates(json_data, ignore_errors=ignore_errors)

    additional_codelist_values = get_additional_codelist_values(schema_obj, json_data)
    context["additional_closed_codelist_values"] = {
        key: value for key, value in additional_codelist_values.items() if not value["isopen"]
    }
    context["additional_open_codelist_values"] = {
        key: value for key, value in additional_codelist_values.items() if value["isopen"]
    }

    if additional_checks:
        context["additional_checks"] = run_additional_checks(
            json_data, additional_checks, ignore_errors=True, return_on_error=[]
        )

    return context

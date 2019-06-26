import json

from libcove.lib.common import common_checks_context, get_additional_codelist_values

from libcoveocds.lib.additional_checks import run_additional_checks, TEST_CLASSES
from libcoveocds.lib.common_checks import lookup_schema, get_releases_aggregates, \
    get_records_aggregates, add_conformance_rule_errors

# This is so it can work with commonmark v0.8.1 and up (commonmark only!) and 0.7.5 and down (CommonMark only!)
try:
    import commonmark
except ImportError:
    import CommonMark as commonmark

import bleach

from django.utils.html import mark_safe, escape, conditional_escape, format_html


validation_error_lookup = {
    'date-time': mark_safe('Incorrect date format. Dates should use the form YYYY-MM-DDT00:00:00Z. Learn more about <a href="https://standard.open-contracting.org/latest/en/schema/reference/#date">dates in OCDS</a>.'), # noqa
}


def common_checks_ocds(context, upload_dir, json_data, schema_obj, api=False, cache=True):
    schema_name = schema_obj.release_pkg_schema_name
    if 'records' in json_data:
        schema_name = schema_obj.record_pkg_schema_name
    common_checks = common_checks_context(upload_dir, json_data, schema_obj, schema_name, context,
                                          fields_regex=True, api=api, cache=cache)
    validation_errors = common_checks['context']['validation_errors']

    new_validation_errors = []
    for (json_key, values) in validation_errors:
        error = json.loads(json_key)
        new_message = validation_error_lookup.get(error['message_type'])
        if new_message:
            error['message_safe'] = conditional_escape(new_message)
        else:
            if 'message_safe' in error:
                error['message_safe'] = mark_safe(error['message_safe'])
            else:
                error['message_safe'] = conditional_escape(error['message'])

        schema_block, ref_info = lookup_schema(schema_obj.get_release_pkg_schema_obj(deref=True), error['path_no_number']) # noqa
        if schema_block and error['message_type'] != 'required':
            if 'description' in schema_block:
                error['schema_title'] = escape(schema_block.get('title', ''))
                error['schema_description_safe'] = mark_safe(bleach.clean(
                    commonmark.commonmark(schema_block['description']),
                    tags=bleach.sanitizer.ALLOWED_TAGS + ['p']
                ))
            if ref_info:
                ref = ref_info['reference']['$ref']
                if ref.endswith('release-schema.json'):
                    ref = ''
                else:
                    ref = ref.strip('#')
                ref_path = '/'.join(ref_info['path'])
                schema = 'release-schema.json'
            else:
                ref = ''
                ref_path = error['path_no_number']
                schema = 'release-package-schema.json'
            error['docs_ref'] = format_html('{},{},{}', schema, ref, ref_path)

        new_validation_errors.append([json.dumps(error, sort_keys=True), values])
    common_checks['context']['validation_errors'] = new_validation_errors

    context.update(common_checks['context'])

    if schema_name == 'record-package-schema.json':
        context['records_aggregates'] = get_records_aggregates(json_data, ignore_errors=bool(validation_errors))
        context['schema_url'] = schema_obj.record_pkg_schema_url
    else:
        additional_codelist_values = get_additional_codelist_values(schema_obj, json_data)
        closed_codelist_values = {key: value for key, value in additional_codelist_values.items() if not value['isopen']} # noqa
        open_codelist_values = {key: value for key, value in additional_codelist_values.items() if value['isopen']}

        context.update({
            'releases_aggregates': get_releases_aggregates(json_data, ignore_errors=bool(validation_errors)),
            'additional_closed_codelist_values': closed_codelist_values,
            'additional_open_codelist_values': open_codelist_values
        })

    additional_checks = run_additional_checks(
        json_data, TEST_CLASSES['additional'], ignore_errors=True, return_on_error=None)

    context.update({
        'additional_checks': additional_checks
    })

    context = add_conformance_rule_errors(context, json_data, schema_obj)
    return context

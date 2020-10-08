from libcoveocds.lib.api import context_api_transform


def test_context_api_transform_validation_additional_fields():
    context = {
        "validation_errors": [
            [
                '{"message_type":"type_a", "message":"description_a", "path_no_number":"field_a"}',
                [{"path": "path_to_a", "value": "a_value"}],
            ],
            [
                '{"message_type":"type_b", "message":"description_b", "path_no_number":"field_b"}',
                [{"path": "path_to_b", "value": ""}],
            ],
            [
                '{"message_type":"type_c", "message":"description_c", "path_no_number":"field_c"}',
                [{"path": "path_to_c"}],
            ],
        ],
        "data_only": [["path_to_d", "field_d", 1], ["path_to_e", "field_e", 2], ["path_to_f", "field_f", 3]],
        "additional_fields": {"path_to_d": {"some_info": "some_value"}},
        "additional_fields_count": 6,
        "validation_errors_count": 3,
    }
    expected_context = {
        "additional_fields": [
            {"field": "field_d", "path": "path_to_d", "usage_count": 1},
            {"field": "field_e", "path": "path_to_e", "usage_count": 2},
            {"field": "field_f", "path": "path_to_f", "usage_count": 3},
        ],
        "all_additional_fields": [{"some_info": "some_value"}],
        "deprecated_fields": [],
        "extensions": {},
        "validation_errors": [
            {
                "description": "description_a",
                "field": "field_a",
                "path": "path_to_a",
                "type": "type_a",
                "value": "a_value",
            },
            {
                "description": "description_b",
                "field": "field_b",
                "path": "path_to_b",
                "type": "type_b",
                "value": "",
            },
            {"description": "description_c", "field": "field_c", "path": "path_to_c", "type": "type_c", "value": ""},
        ],
    }
    transform_context = context_api_transform(context)

    validation_errors = zip(transform_context["validation_errors"], expected_context["validation_errors"])
    for result in validation_errors:
        assert len(result[0]) == len(result[1])
        for k, v in result[0].items():
            assert result[1][k] == v
    assert len(transform_context["validation_errors"]) == len(expected_context["validation_errors"])

    additional_fields = zip(transform_context["additional_fields"], expected_context["additional_fields"])
    for result in additional_fields:
        assert len(result[0]) == len(result[1])
        for k, v in result[0].items():
            assert result[1][k] == v
    assert len(transform_context["additional_fields"]) == len(expected_context["additional_fields"])

    assert transform_context["extensions"] == expected_context["extensions"]
    assert transform_context["deprecated_fields"] == expected_context["deprecated_fields"]
    assert "validation_errors_count" not in transform_context.keys()
    assert "additional_fields_count" not in transform_context.keys()
    assert "data_only" not in transform_context.keys()


def test_context_api_transform_extensions():
    """Expected result for extensions after trasform:

    'extensions': {
        'extended_schema_url': 'extended_release_schema.json',
        'extensions': [
            {'description': 'description_a', 'documentationUrl': 'documentation_a', 'name': 'a', 'url': 'url_a'},
            {'description': 'description_b', 'documentationUrl': 'documentation_b', 'name': 'b', 'url': 'url_b'},
            {'description': 'description_c', 'documentationUrl': 'documentation_c', 'name': 'c', 'url': 'url_c'},
            {'description': 'description_d', 'documentationUrl': 'documentation_d', 'name': 'd', 'url': 'url_d'},
        ],
        'invalid_extensions': [['bad_url_x', 'x_error_msg'],
                               ['bad_url_z', 'z_error_msg'],
                               ['bad_url_y', 'y_error_msg']],
        'is_extended_schema': True
    }
    """
    context = {
        "extensions": {
            "is_extended_schema": True,
            "invalid_extension": {"bad_url_x": "x_error_msg", "bad_url_y": "y_error_msg", "bad_url_z": "z_error_msg"},
            "extensions": {
                "url_a": {
                    "description": "description_a",
                    "url": "url_a",
                    "documentationUrl": "documentation_a",
                    "name": "a",
                },
                "url_b": {
                    "description": "description_b",
                    "url": "url_b",
                    "documentationUrl": "documentation_b",
                    "name": "b",
                },
                "url_c": {
                    "description": "description_c",
                    "url": "url_c",
                    "documentationUrl": "documentation_c",
                    "name": "c",
                },
                "url_d": {
                    "description": "description_d",
                    "url": "url_d",
                    "documentationUrl": "documentation_d",
                    "name": "d",
                },
                "bad_url_x": [],
                "bad_url_y": [],
                "bad_url_z": [],
            },
            "extended_schema_url": "extended_release_schema.json",
        },
        "validation_errors_count": 0,
        "additional_fields_count": 0,
        "data_only": [],
        "additional_fields": [],
        "deprecated_fields": [],
    }

    transformed_ext_context = context_api_transform(context)["extensions"]

    assert isinstance(transformed_ext_context["extensions"], list)
    assert len(transformed_ext_context["extensions"]) == 4
    for extension in transformed_ext_context["extensions"]:
        assert len(extension) == 4

    assert len(transformed_ext_context["invalid_extensions"]) == 3
    for inv_extension in transformed_ext_context["invalid_extensions"]:
        assert len(inv_extension) == 2
        for extension in transformed_ext_context["extensions"]:
            assert extension["url"] != inv_extension[0]

    assert transformed_ext_context["is_extended_schema"] == context["extensions"]["is_extended_schema"]
    assert transformed_ext_context["extended_schema_url"] == context["extensions"]["extended_schema_url"]


def test_context_api_transform_deprecations():
    """Expected result for deprecated field after trasform:

    'deprecated_fields': [
        {"field": "a", "paths": ["path_to_a/0/a", "path_to_a/1/a"], "explanation": ["1.1", "description_a"]},
        {"field": "b", "paths": ["path_to_b/0/b", "path_to_b/1/b"], "explanation": ["1.1", "description_b"]}
    ]
    """
    context = {
        "deprecated_fields": {
            "a": {"paths": ["path_to_a/0/a", "path_to_a/1/a"], "explanation": ["1.1", "description_a"]},
            "b": {"paths": ["path_to_b/0/b", "path_to_b/1/b"], "explanation": ["1.1", "description_b"]},
        },
        "validation_errors": [],
        "validation_errors_count": 0,
        "data_only": [],
        "additional_fields": [],
        "additional_fields_count": 0,
        "extensions": {},
    }

    transformed_depr_context = context_api_transform(context)["deprecated_fields"]

    assert isinstance(transformed_depr_context, list)
    assert len(transformed_depr_context) == 2

    for deprecated_field in transformed_depr_context:
        assert isinstance(deprecated_field, dict)
        assert len(deprecated_field) == 3
        assert len(deprecated_field["paths"]) == 2
        assert len(deprecated_field["explanation"]) == 2
        assert deprecated_field.get("field")

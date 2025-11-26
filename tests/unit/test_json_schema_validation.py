import json
import pytest
from src.oal_agent.security.validation import Validator, JsonSchemaError


@pytest.fixture
def setup_schemas(tmp_path):
    valid_schema_path = tmp_path / "valid_schema.json"
    invalid_json_path = tmp_path / "invalid.json"
    non_existent_path = tmp_path / "non_existent.json"

    valid_schema_content = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer", "minimum": 0}
        },
        "required": ["name", "age"]
    }
    with open(valid_schema_path, "w") as f:
        json.dump(valid_schema_content, f)

    with open(invalid_json_path, "w") as f:
        f.write("{invalid json}")

    return {
        "valid_schema_path": valid_schema_path,
        "invalid_json_path": invalid_json_path,
        "non_existent_path": non_existent_path,
    }


class TestJsonSchemaValidation:
    def test_load_json_schema_success(self, setup_schemas):
        schema = Validator.load_json_schema(setup_schemas["valid_schema_path"])
        assert isinstance(schema, dict)
        assert "name" in schema["properties"]

    def test_load_json_schema_file_not_found(self, setup_schemas):
        with pytest.raises(FileNotFoundError):
            Validator.load_json_schema(setup_schemas["non_existent_path"])

    def test_load_json_schema_invalid_json(self, setup_schemas):
        with pytest.raises(json.JSONDecodeError):
            Validator.load_json_schema(setup_schemas["invalid_json_path"])

    def test_validate_json_with_schema_success(self, setup_schemas):
        schema = Validator.load_json_schema(setup_schemas["valid_schema_path"])
        valid_data = {"name": "Alice", "age": 30}
        Validator.validate_json_with_schema(valid_data, schema)

    def test_validate_json_with_schema_failure_required(self, setup_schemas):
        schema = Validator.load_json_schema(setup_schemas["valid_schema_path"])
        invalid_data_missing_field = {"name": "Bob"}
        with pytest.raises(JsonSchemaError, match=r"JSON schema validation failed: 'age' is a required property"):
            Validator.validate_json_with_schema(invalid_data_missing_field, schema)

    def test_validate_json_with_schema_failure_type(self, setup_schemas):
        schema = Validator.load_json_schema(setup_schemas["valid_schema_path"])
        invalid_data_wrong_type = {"name": "Charlie", "age": "twenty"}
        with pytest.raises(JsonSchemaError, match=r"JSON schema validation failed: 'twenty' is not of type 'integer'"):
            Validator.validate_json_with_schema(invalid_data_wrong_type, schema)

    def test_validate_json_with_schema_failure_min_value(self, setup_schemas):
        schema = Validator.load_json_schema(setup_schemas["valid_schema_path"])
        invalid_data_min_value = {"name": "David", "age": -5}
        with pytest.raises(JsonSchemaError, match=r"JSON schema validation failed: -5 is less than the minimum of 0"):
            Validator.validate_json_with_schema(invalid_data_min_value, schema)

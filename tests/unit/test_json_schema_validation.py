import json
import os
import pytest
from src.oal_agent.security.validation import Validator, JsonSchemaError


class TestJsonSchemaValidation:
    def setup_method(self):
        # Create a temporary directory for schema files
        self.temp_dir = "temp_schemas"
        os.makedirs(self.temp_dir, exist_ok=True)
        self.valid_schema_path = os.path.join(self.temp_dir, "valid_schema.json")
        self.invalid_json_path = os.path.join(self.temp_dir, "invalid.json")
        self.non_existent_path = os.path.join(self.temp_dir, "non_existent.json")

        # Create a valid schema file
        valid_schema_content = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer", "minimum": 0}
            },
            "required": ["name", "age"]
        }
        with open(self.valid_schema_path, "w") as f:
            json.dump(valid_schema_content, f)

        # Create an invalid JSON file (not a schema, just for testing error handling)
        with open(self.invalid_json_path, "w") as f:
            f.write("{invalid json}")

    def teardown_method(self):
        # Clean up the temporary directory and files
        if os.path.exists(self.temp_dir):
            for f_name in os.listdir(self.temp_dir):
                os.remove(os.path.join(self.temp_dir, f_name))
            os.rmdir(self.temp_dir)

    def test_load_json_schema_success(self):
        schema = Validator.load_json_schema(self.valid_schema_path)
        assert isinstance(schema, dict)
        assert "name" in schema["properties"]

    def test_load_json_schema_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            Validator.load_json_schema(self.non_existent_path)

    def test_load_json_schema_invalid_json(self):
        with pytest.raises(json.JSONDecodeError):
            Validator.load_json_schema(self.invalid_json_path)

    def test_validate_json_with_schema_success(self):
        schema = Validator.load_json_schema(self.valid_schema_path)
        valid_data = {"name": "Alice", "age": 30}
        try:
            Validator.validate_json_with_schema(valid_data, schema)
        except JsonSchemaError:
            pytest.fail("Validation unexpectedly failed for valid data.")

    def test_validate_json_with_schema_failure(self):
        schema = Validator.load_json_schema(self.valid_schema_path)
        invalid_data_missing_field = {"name": "Bob"}
        with pytest.raises(JsonSchemaError, match="JSON schema validation failed: 'age' is a required property"):
            Validator.validate_json_with_schema(invalid_data_missing_field, schema)

        invalid_data_wrong_type = {"name": "Charlie", "age": "twenty"}
        with pytest.raises(JsonSchemaError, match="JSON schema validation failed: 'twenty' is not of type 'integer'"):
            Validator.validate_json_with_schema(invalid_data_wrong_type, schema)

        invalid_data_min_value = {"name": "David", "age": -5}
        with pytest.raises(JsonSchemaError, match="JSON schema validation failed: -5 is less than the minimum of 0"):
            Validator.validate_json_with_schema(invalid_data_min_value, schema)

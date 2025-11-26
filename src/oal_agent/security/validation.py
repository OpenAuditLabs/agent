"""Input validation."""

import json
from typing import Any, Dict, Optional

from jsonschema import validate
from jsonschema.exceptions import ValidationError


class JsonSchemaError(ValueError):
    """Custom exception for JSON schema validation errors."""
    pass


class Validator:
    """Validates inputs for security."""

    @staticmethod
    def _trim_whitespace(input_string: Optional[str]) -> str:
        """Trim leading/trailing whitespace from input.

        Args:
            input_string: The string to trim

        Returns:
            Trimmed string, or empty string if input is None
        """
        if input_string is None:
            return ""
        if not isinstance(input_string, str):
            raise TypeError(f"Expected str, got {type(input_string).__name__}")
        return input_string.strip()

    @staticmethod
    def validate_contract_code(code: str) -> bool:
        """Validate contract code."""
        sanitized_code = Validator._trim_whitespace(code)
        # TODO: Implement more comprehensive validation for contract code
        return bool(sanitized_code)  # Basic check: not empty after sanitization

    @staticmethod
    def validate_address(address: str) -> bool:
        """Validate contract address."""
        sanitized_address = Validator._trim_whitespace(address)
        # Basic checks: non-empty, exact length, starts with '0x'
        if not sanitized_address or len(sanitized_address) != 42:
            return False
        if not sanitized_address.startswith("0x"):
            return False
        # Verify all characters after '0x' are valid hex digits
        try:
            int(sanitized_address[2:], 16)
            return True
        except ValueError:
            return False

    @staticmethod
    def load_json_schema(schema_path: str) -> Dict[str, Any]:
        """Loads a JSON schema from a file.

        Args:
            schema_path: The absolute path to the JSON schema file.

        Returns:
            The loaded JSON schema as a dictionary.

        Raises:
            FileNotFoundError: If the schema file does not exist.
            json.JSONDecodeError: If the schema file is not valid JSON.
        """
        with open(schema_path, "r") as f:
            return json.load(f)

    @staticmethod
    def validate_json_with_schema(
        json_data: Dict[str, Any], schema: Dict[str, Any]
    ) -> None:
        """Validates a JSON object against a given JSON schema.

        Args:
            json_data: The JSON object to validate.
            schema: The JSON schema to validate against.

        Raises:
            JsonSchemaError: If the JSON data does not conform to the schema.
        """
        try:
            validate(instance=json_data, schema=schema)
        except ValidationError as e:
            raise JsonSchemaError(f"JSON schema validation failed: {e.message}") from e

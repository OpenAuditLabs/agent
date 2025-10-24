import pytest
from src.oal_agent.security.validation import Validator

class TestValidator:
    def test_sanitize_string_input(self):
        assert Validator._trim_whitespace("  hello world  ") == "hello world"
        assert Validator._trim_whitespace("hello\nworld") == "hello\nworld"
        assert Validator._trim_whitespace("  ") == ""
        assert Validator._trim_whitespace("") == ""

    def test_validate_contract_code(self):
        assert Validator.validate_contract_code("  some_code  ") is True
        assert Validator.validate_contract_code("  ") is False
        assert Validator.validate_contract_code("") is False
        assert Validator.validate_contract_code("valid_code") is True

    def test_validate_address(self):
        # Valid Ethereum address format
        assert Validator.validate_address("  0x1234567890123456789012345678901234567890  ") is True
        assert Validator.validate_address("0x1234567890123456789012345678901234567890") is True
        # Invalid addresses
        assert Validator.validate_address("  ") is False
        assert Validator.validate_address("") is False
        assert Validator.validate_address("0x123") is False  # Too short
        assert Validator.validate_address("abcdef1234567890abcdef1234567890abcdef") is False  # Missing 0x
        assert Validator.validate_address("0xabcdef1234567890abcdef1234567890abcde") is False # Too short

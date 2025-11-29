import os

import pytest

from src.oal_agent.utils.env import (
    get_env, require_env, validate_env_variables, get_env_int, get_env_bool, get_env_list
)


class TestEnvUtils:
    def setup_method(self):
        # Clear environment variables before each test to ensure isolation
        self._original_environ = os.environ.copy()
        os.environ.clear()

    def teardown_method(self):
        # Restore original environment variables after each test
        os.environ.clear()
        os.environ.update(self._original_environ)

    def test_get_env_str_success(self):
        os.environ["TEST_VAR"] = "hello"
        assert get_env("TEST_VAR") == "hello"

    def test_get_env_str_with_default(self):
        assert get_env("NON_EXISTENT_VAR", default="default_value") == "default_value"

    def test_get_env_str_missing_no_default(self):
        assert get_env("NON_EXISTENT_VAR") is None

    def test_get_env_int_success(self):
        os.environ["TEST_INT"] = "123"
        assert get_env("TEST_INT", cast_to=int) == 123

    def test_get_env_int_with_default(self):
        assert get_env("NON_EXISTENT_INT", default=456, cast_to=int) == 456

    def test_get_env_int_invalid_value(self):
        os.environ["TEST_INT_INVALID"] = "abc"
        with pytest.raises(ValueError, match="expected to be an integer"):
            get_env("TEST_INT_INVALID", cast_to=int)

    def test_get_env_bool_true(self):
        os.environ["TEST_BOOL_TRUE1"] = "true"
        os.environ["TEST_BOOL_TRUE2"] = "1"
        os.environ["TEST_BOOL_TRUE3"] = "yes"
        assert get_env("TEST_BOOL_TRUE1", cast_to=bool) is True
        assert get_env("TEST_BOOL_TRUE2", cast_to=bool) is True
        assert get_env("TEST_BOOL_TRUE3", cast_to=bool) is True

    def test_get_env_bool_false(self):
        os.environ["TEST_BOOL_FALSE1"] = "false"
        os.environ["TEST_BOOL_FALSE2"] = "0"
        os.environ["TEST_BOOL_FALSE3"] = "no"
        os.environ["TEST_BOOL_FALSE4"] = "anything_else"
        assert get_env("TEST_BOOL_FALSE1", cast_to=bool) is False
        assert get_env("TEST_BOOL_FALSE2", cast_to=bool) is False
        assert get_env("TEST_BOOL_FALSE3", cast_to=bool) is False
        assert get_env("TEST_BOOL_FALSE4", cast_to=bool) is False

    def test_require_env_str_success(self):
        os.environ["REQUIRED_STR"] = "some_value"
        assert require_env("REQUIRED_STR") == "some_value"

    def test_require_env_str_missing(self):
        with pytest.raises(
            ValueError, match="Required environment variable REQUIRED_STR is not set"
        ):
            require_env("REQUIRED_STR")

    def test_require_env_int_success(self):
        os.environ["REQUIRED_INT"] = "100"
        assert require_env("REQUIRED_INT", cast_to=int) == 100

    def test_require_env_int_invalid(self):
        os.environ["REQUIRED_INT_INVALID"] = "not_an_int"
        with pytest.raises(ValueError, match="expected to be an integer"):
            require_env("REQUIRED_INT_INVALID", cast_to=int)

    def test_validate_env_variables_success(self):
        os.environ["VAR1"] = "value1"
        os.environ["VAR2"] = "123"
        os.environ["VAR3"] = "true"
        required_vars = {
            "VAR1": str,
            "VAR2": int,
            "VAR3": bool,
        }
        validate_env_variables(required_vars)  # Should not raise an error

    def test_validate_env_variables_missing_str(self):
        os.environ["VAR2"] = "123"
        required_vars = {
            "VAR1": str,
            "VAR2": int,
        }
        with pytest.raises(
            ValueError, match="Required environment variable VAR1 is not set"
        ):
            validate_env_variables(required_vars)

    def test_validate_env_variables_missing_int(self):
        os.environ["VAR1"] = "value1"
        required_vars = {
            "VAR1": str,
            "VAR2": int,
        }
        with pytest.raises(
            ValueError, match="Required environment variable VAR2 is not set"
        ):
            validate_env_variables(required_vars)

    def test_validate_env_variables_invalid_int(self):
        os.environ["VAR1"] = "value1"
        os.environ["VAR2"] = "not_an_int"
        required_vars = {
            "VAR1": str,
            "VAR2": int,
        }
        with pytest.raises(
            ValueError, match="Environment variable VAR2 expected to be an integer"
        ):
            validate_env_variables(required_vars)

    def test_get_env_int_success_with_min_max(self):
        os.environ["TEST_INT_RANGE"] = "50"
        assert get_env_int("TEST_INT_RANGE", default=0, min_value=10, max_value=100) == 50

    def test_get_env_int_below_min(self):
        os.environ["TEST_INT_BELOW_MIN"] = "5"
        with pytest.raises(
            ValueError, match="value 5 is less than the minimum allowed value 10"
        ):
            get_env_int("TEST_INT_BELOW_MIN", default=0, min_value=10)

    def test_get_env_int_above_max(self):
        os.environ["TEST_INT_ABOVE_MAX"] = "150"
        with pytest.raises(
            ValueError, match="value 150 is greater than the maximum allowed value 100"
        ):
            get_env_int("TEST_INT_ABOVE_MAX", default=0, max_value=100)

    def test_get_env_int_default_with_min_max(self):
        assert get_env_int("NON_EXISTENT_INT_RANGE", default=50, min_value=10, max_value=100) == 50

    def test_get_env_int_default_below_min(self):
        with pytest.raises(
            ValueError, match="default value 5 is less than the minimum allowed value 10"
        ):
            get_env_int("NON_EXISTENT_DEFAULT_BELOW_MIN", default=5, min_value=10)

    def test_get_env_int_default_above_max(self):
        with pytest.raises(
            ValueError, match="default value 150 is greater than the maximum allowed value 100"
        ):
            get_env_int("NON_EXISTENT_DEFAULT_ABOVE_MAX", default=150, max_value=100)


    def test_get_env_bool_success(self):
        os.environ["TEST_BOOL"] = "True"
        assert get_env_bool("TEST_BOOL", default=False) is True
        os.environ["TEST_BOOL"] = "false"
        assert get_env_bool("TEST_BOOL", default=True) is False

    def test_get_env_bool_default(self):
        assert get_env_bool("NON_EXISTENT_BOOL", default=True) is True
        assert get_env_bool("NON_EXISTENT_BOOL_FALSE", default=False) is False

    def test_get_env_list_success(self):
        os.environ["TEST_LIST"] = "item1,item2, item3"
        assert get_env_list("TEST_LIST", default=[]) == ["item1", "item2", "item3"]

    def test_get_env_list_with_custom_separator(self):
        os.environ["TEST_LIST_SEP"] = "val1;val2; val3"
        assert get_env_list("TEST_LIST_SEP", default=[], separator=";") == ["val1", "val2", "val3"]

    def test_get_env_list_default(self):
        assert get_env_list("NON_EXISTENT_LIST", default=["default1", "default2"]) == ["default1", "default2"]

    def test_get_env_list_empty_string(self):
        os.environ["EMPTY_LIST"] = ""
        assert get_env_list("EMPTY_LIST", default=["a"]) == ["a"]

    def test_get_env_list_empty_items(self):
        os.environ["EMPTY_ITEMS_LIST"] = " , item1, , item2 , "
        assert get_env_list("EMPTY_ITEMS_LIST", default=[]) == ["item1", "item2"]



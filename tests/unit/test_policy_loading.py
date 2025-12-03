import logging
import sys

import pytest

from oal_agent.core.config import reset_settings, settings
from oal_agent.security.policies import load_additional_policies


@pytest.fixture(autouse=True)
def run_around_tests():
    # Reset settings before each test to ensure a clean state
    reset_settings()
    yield
    # Clean up sys.modules after each test to prevent side effects
    keys_to_remove = [k for k in sys.modules if k.startswith("test_policy_")]
    for key in keys_to_remove:
        del sys.modules[key]
    reset_settings()


def test_load_additional_policies_from_valid_directory(tmp_path, caplog):
    """Tests that additional policy modules are loaded from a valid directory."""
    caplog.set_level(logging.INFO)

    # Create a dummy policy file
    policy_content = """
import logging
def register_policies(policy_instance):
    logging.info("Dummy policy registered!")
    policy_instance.ALLOWED_ACTIONS.append("dummy_action")
"""
    policy_file = tmp_path / "test_policy_dummy.py"
    policy_file.write_text(policy_content)

    # Configure settings to point to the temporary directory
    settings.additional_policies_path = str(tmp_path)

    # Call the function to load additional policies
    load_additional_policies()

    # Assert that the module was loaded and its registration function was called (via log)
    assert (
        "Successfully loaded policy module: oal_agent.security.dynamic_policies.test_policy_dummy"
        in caplog.text
    )
    # Verify that the dummy_action was added to the ALLOWED_ACTIONS
    # This requires a way to access the SecurityPolicy instance, which is not directly exposed by load_additional_policies
    # For now, we'll rely on the log message to confirm loading.
    # A more robust test would involve passing a mock SecurityPolicy instance to register_policies
    # and asserting changes on it.


def test_load_additional_policies_no_path_configured(caplog):
    """Tests that no policies are loaded if no additional_policies_path is configured."""
    caplog.set_level(logging.INFO)
    settings.additional_policies_path = None
    load_additional_policies()
    assert "Loading additional policies from" not in caplog.text


def test_load_additional_policies_invalid_directory(caplog):
    """Tests that a warning is logged if the configured directory does not exist."""
    caplog.set_level(logging.WARNING)
    settings.additional_policies_path = "/non/existent/path/for/policies"
    load_additional_policies()
    assert "Additional policies directory not found" in caplog.text


def test_load_additional_policies_with_error_in_module(tmp_path, caplog):
    """Tests that errors during module loading are caught and logged."""
    caplog.set_level(logging.ERROR)

    # Create a policy file with an error
    error_policy_content = """
raise ImportError("Simulated import error")
"""
    error_policy_file = tmp_path / "test_policy_error.py"
    error_policy_file.write_text(error_policy_content)

    settings.additional_policies_path = str(tmp_path)
    load_additional_policies()

    assert (
        "Failed to load policy module oal_agent.security.dynamic_policies.test_policy_error"
        in caplog.text
    )
    assert "Simulated import error" in caplog.text

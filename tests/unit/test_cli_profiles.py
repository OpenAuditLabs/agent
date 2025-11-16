# Copyright (C) 2025 OpenAuditLabs
# SPDX-License-Identifier: AGPL-3.0-or-later

import os
from click.testing import CliRunner
from src.oal_agent.cli import cli
from src.oal_agent.core.config import reset_settings

def test_cli_profile_option_loads_settings(tmp_path):
    """Test that the --profile option correctly loads profile-specific settings."""
    reset_settings()
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path) as fs_root:
        # Create a dummy .env.test_profile file directly in the isolated filesystem root
        profile_env_content = "API_PORT=8081\nLLM_PROVIDER=test_llm"
        profile_env_path = os.path.join(fs_root, ".env.test_profile")
        with open(profile_env_path, "w") as f:
            f.write(profile_env_content)

        result = runner.invoke(cli, ["--profile", "test_profile", "serve", "--help"])

        assert result.exit_code == 0
        assert "Using profile-specific configuration from '.env.test_profile'" in result.output
        # Cannot assert on global settings directly as click.CliRunner isolates the environment

def test_cli_profile_option_non_existent_file(tmp_path):
    """Test that a warning is issued if the profile file does not exist."""
    reset_settings()
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["--profile", "non_existent", "serve", "--help"])

        assert result.exit_code == 0
        assert "Warning: Profile configuration file '.env.non_existent' not found." in result.output
        assert "Using profile-specific configuration from '.env.non_existent'" not in result.output # Ensure it's not loaded

def test_cli_profile_and_config_options_precedence(tmp_path):
    """Test that --profile settings take precedence over --config settings."""
    reset_settings()
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path) as fs_root:
        # Create a dummy .env.config file
        config_env_content = "API_PORT=8082\nLLM_PROVIDER=config_llm"
        config_env_path = os.path.join(fs_root, ".env.config")
        with open(config_env_path, "w") as f:
            f.write(config_env_content)

        # Create a dummy .env.profile file
        profile_env_content = "API_PORT=8083\nLLM_PROVIDER=profile_llm"
        profile_env_path = os.path.join(fs_root, ".env.profile")
        with open(profile_env_path, "w") as f:
            f.write(profile_env_content)

        result = runner.invoke(cli, ["--config", config_env_path, "--profile", "profile", "serve", "--help"])

        assert result.exit_code == 0
        assert f"Using configuration from '{config_env_path}'" in result.output
        assert "Using profile-specific configuration from '.env.profile'" in result.output
        # Cannot assert on global settings directly as click.CliRunner isolates the environment

def test_cli_config_and_profile_options_precedence_reversed(tmp_path):
    """Test that --config settings are applied if --profile does not override them."""
    reset_settings()
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path) as fs_root:
        # Create a dummy .env.config file
        config_env_content = "API_PORT=8082\nLLM_PROVIDER=config_llm"
        config_env_path = os.path.join(fs_root, ".env.config")
        with open(config_env_path, "w") as f:
            f.write(config_env_content)

        # Create a dummy .env.profile file with only one setting
        profile_env_content = "API_HOST=1.2.3.4"
        profile_env_path = os.path.join(fs_root, ".env.profile")
        with open(profile_env_path, "w") as f:
            f.write(profile_env_content)

        result = runner.invoke(cli, ["--config", config_env_path, "--profile", "profile", "serve", "--help"])

        assert result.exit_code == 0
        assert f"Using configuration from '{config_env_path}'" in result.output
        assert "Using profile-specific configuration from '.env.profile'" in result.output
        # Cannot assert on global settings directly as click.CliRunner isolates the environment

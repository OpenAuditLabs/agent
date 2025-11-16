# Copyright (C) 2025 OpenAuditLabs
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Command-line interface for the OpenAuditLabs Agent.

This CLI provides tools to interact with the OAL Agent, including starting the API server
and analyzing smart contract files.

Usage Example:
    oal-agent --config ~/.oal_agent.env serve --port 8001
    oal-agent analyze my_contract.sol
"""


import os
from typing import Optional

import click
import requests
from dotenv import dotenv_values

from .app.schemas.jobs import JobResponse
from .core.config import Settings, settings


@click.group(
    help="""OAL Agent CLI.

    Use this command-line interface to interact with the OpenAuditLabs Agent.
    """
)
@click.option(
    "--config",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    help="Path to configuration file (e.g., ~/.oal_agent.env or config.env)",
)
@click.option(
    "--profile",
    type=str,
    help="Load profile-specific settings from .env.<profile_name> (e.g., 'dev' loads .env.dev)",
)
@click.pass_context
def cli(ctx: click.Context, config: Optional[str], profile: Optional[str]):
    """OAL Agent CLI."""
    all_env_vars = {}

    if config:
        config_env_vars = dotenv_values(config)
        # Convert keys to lowercase for pydantic_settings
        all_env_vars.update(
            {k.lower(): v for k, v in config_env_vars.items() if v is not None}
        )
        click.echo(f"Using configuration from '{config}'")

    if profile:
        profile_config_path = f".env.{profile}"
        if not os.path.exists(profile_config_path):
            click.echo(
                f"Warning: Profile configuration file '{profile_config_path}' not found."
            )
        else:
            profile_env_vars = dotenv_values(profile_config_path)
            # Convert keys to lowercase for pydantic_settings
            # Profile settings take precedence over config settings
            all_env_vars.update(
                {k.lower(): v for k, v in profile_env_vars.items() if v is not None}
            )
            click.echo(
                f"Using profile-specific configuration from '{profile_config_path}'"
            )

    if all_env_vars:
        ctx.obj = Settings.from_dict(all_env_vars)
    else:
        ctx.obj = settings


@cli.command(help="Start the OAL Agent API server.")
@click.option("--host", default=None, help="API host")
@click.option("--port", default=None, help="API port")
@click.pass_context
def serve(ctx: click.Context, host: Optional[str], port: Optional[int]):
    """Start the API server.

    This command launches the FastAPI application that powers the OAL Agent.
    """
    import uvicorn

    from .app.main import app

    current_settings = ctx.obj
    uvicorn.run(
        app,
        host=host or current_settings.api_host,
        port=port or current_settings.api_port,
    )


@cli.command(help="Analyze a smart contract file.")
@click.argument(
    "contract_file", type=click.Path(exists=True, dir_okay=False, resolve_path=True)
)
@click.pass_context
def analyze(ctx: click.Context, contract_file: str):
    """Analyze a smart contract file.

    This command takes a smart contract file as input and initiates an analysis process.
    """
    click.echo(f"Analyzing {contract_file}...")
    # TODO: Implement analysis logic


@cli.command(help="Get the status of an analysis job.")
@click.argument("job_id", type=str)
@click.pass_context
def status(ctx: click.Context, job_id: str):
    """Get the status of an analysis job.

    This command queries the API for the status of a specific job ID.

    """
    current_settings = ctx.obj
    api_url = f"http://{current_settings.api_host}:{current_settings.api_port}/analysis/{job_id}"
    click.echo(f"Fetching status for job ID: {job_id} from {api_url}...")
    try:
        # Use a timeout to avoid the CLI hanging indefinitely. Adjust default as needed or make configurable.
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        job_response = JobResponse.model_validate(response.json())
        click.echo(f"Job ID: {job_response.job_id}")
        click.echo(f"Status: {job_response.status}")
        if job_response.message:
            click.echo(f"Message: {job_response.message}")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            click.echo(f"Error: Job with ID '{job_id}' not found.")
        else:
            click.echo(f"HTTP error occurred: {e}")
    except requests.exceptions.ConnectionError as e:
        click.echo(f"Error: Could not connect to the API server. Is it running? ({e})")
    except requests.exceptions.Timeout as e:
        click.echo(f"Error: The request timed out: {e}")
    except requests.exceptions.RequestException as e:
        click.echo(f"An unexpected error occurred: {e}")


@cli.command(
    name="_debug_settings", hidden=True, help="Debug command to print current settings."
)
@click.pass_context
def _debug_settings(ctx: click.Context):
    """Debug command to print current settings for testing purposes."""
    current_settings = ctx.obj
    click.echo(f"API_PORT={current_settings.api_port}")
    click.echo(f"LLM_PROVIDER={current_settings.llm_provider}")
    click.echo(f"API_HOST={current_settings.api_host}")


if __name__ == "__main__":
    cli()

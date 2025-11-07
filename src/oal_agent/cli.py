# Copyright (C) 2025 OpenAuditLabs
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Command-line interface for the OpenAuditLabs Agent.

This CLI provides tools to interact with the OAL Agent, including starting the API server
and analyzing smart contract files.

Usage Example:
    oal-agent --config ~/.oal_agent.env serve --port 8001
    oal-agent analyze my_contract.sol
"""

from pathlib import Path
from typing import Optional

import click
import requests

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
def cli(config: Optional[str]):
    """OAL Agent CLI."""
    if config:
        global settings
        settings = Settings(_env_file=Path(config))
        click.echo(f"Using configuration from '{config}'")
    pass


@cli.command(help="Start the OAL Agent API server.")
@click.option("--host", default=settings.api_host, help="API host")
@click.option("--port", default=settings.api_port, help="API port")
def serve(host: str, port: int):
    """Start the API server.

    This command launches the FastAPI application that powers the OAL Agent.
    """
    import uvicorn

    from .app.main import app

    uvicorn.run(app, host=host, port=port)


@cli.command(help="Analyze a smart contract file.")
@click.argument(
    "contract_file", type=click.Path(exists=True, dir_okay=False, resolve_path=True)
)
def analyze(contract_file: str):
    """Analyze a smart contract file.

    This command takes a smart contract file as input and initiates an analysis process.
    """
    click.echo(f"Analyzing {contract_file}...")
    # TODO: Implement analysis logic


@cli.command(help="Get the status of an analysis job.")
@click.argument("job_id", type=str)
def status(job_id: str):
    """Get the status of an analysis job.

    This command queries the API for the status of a specific job ID.

    """
    api_url = f"http://{settings.api_host}:{settings.api_port}/analysis/{job_id}"
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


if __name__ == "__main__":
    cli()

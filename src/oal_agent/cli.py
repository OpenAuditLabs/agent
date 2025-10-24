# Copyright (C) 2025 OpenAuditLabs
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Command-line interface for the OpenAuditLabs Agent.

This CLI provides tools to interact with the OAL Agent, including starting the API server
and analyzing smart contract files.

Usage Example:
    oal-agent --config ~/.oal_agent.env serve --port 8001
    oal-agent analyze my_contract.sol
"""

import click

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
def cli(config: str | None):
    """OAL Agent CLI."""
    if config:
        # Re-initialize settings with the custom config file
        global settings
        settings = Settings(_env_file=config)
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
@click.argument("contract_file", type=click.Path(exists=True, dir_okay=False, resolve_path=True))
def analyze(contract_file: str):
    """Analyze a smart contract file.

    This command takes a smart contract file as input and initiates an analysis process.
    """
    click.echo(f"Analyzing {contract_file}...")
    # TODO: Implement analysis logic


if __name__ == "__main__":
    cli()

# Copyright (C) 2025 OpenAuditLabs
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Command-line interface."""

import click

from .core.config import Settings, settings


@click.group()
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


@cli.command()
@click.option("--host", default=settings.api_host, help="API host")
@click.option("--port", default=settings.api_port, help="API port")
def serve(host: str, port: int):
    """Start the API server."""
    import uvicorn

    from .app.main import app

    uvicorn.run(app, host=host, port=port)


@cli.command()
@click.argument("contract_file")
def analyze(contract_file: str):
    """Analyze a smart contract file."""
    click.echo(f"Analyzing {contract_file}...")
    # TODO: Implement analysis logic


if __name__ == "__main__":
    cli()

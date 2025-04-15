"""CLI команды для finsight_worker."""

import typer

from cli.finsight_worker.commands import fetch, worker

cli = typer.Typer(no_args_is_help=True)

cli.add_typer(worker.cli, name='worker')
cli.add_typer(fetch.cli, name='fetch')

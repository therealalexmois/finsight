"""Основная CLI-группа для finsight-api."""

import click

from finsight_api.cli import server, version


@click.group(help='Команды для управления finsight-api.')
def cli() -> None:
    """Корневая CLI-группа finsight-api с подкомандами server и version."""


cli.add_command(server.server)
cli.add_command(version.version)

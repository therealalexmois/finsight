"""Основная CLI-группа для finsight-api."""

import click

from cli.finsight_api import server, version


@click.group(help='Команды для управления finsight-api.')
def cli() -> None:
    """Корневая CLI-группа."""


cli.add_command(server.server)
cli.add_command(version.version)

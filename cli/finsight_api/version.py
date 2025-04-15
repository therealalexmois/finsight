"""Команда CLI для отображения версии проекта."""

import click

from src.finsight_api.infrastructure.utils.pyproject import extract_project_field, find_pyproject_path


@click.command(help='Показывает текущую версию finsight-api из pyproject.toml.')
def version() -> None:
    """Печатает версию проекта."""
    pyproject_path = find_pyproject_path()
    version = extract_project_field('version', pyproject_path)
    click.echo(f'finsight-api version: {version}')

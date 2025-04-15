"""CLI-команды для управления HTTP-сервером."""

import click

from src.finsight_api.main import start_app


@click.group(help='Команды управления сервером.')
def server() -> None:
    """Группа команд для сервера."""


@server.command(help='Запускает HTTP-сервер finsight-api.')
@click.option('--host', help='Хост для сервера.')
@click.option('--port', type=int, help='Порт для сервера.')
@click.option('--reload', is_flag=True, help='Перезапуск при изменениях кода (только для разработки).')
def start(host: str | None, port: int | None, reload: bool) -> None:
    """Запускает сервер, используя встроенную функцию `start_app()` с CLI аргументами."""
    start_app(host=host, port=port, reload=reload)

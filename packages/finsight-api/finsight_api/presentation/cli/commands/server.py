"""CLI-команды для управления HTTP-сервером."""

import click

from finsight_api.main import start_app


@click.group(help='Команды управления сервером.')
def server() -> None:
    """Группа команд для сервера."""


@server.command(help='Запускает HTTP-сервер finsight-api.')
@click.option('--host', help='Хост для сервера.')
@click.option('--port', type=int, help='Порт для сервера.')
@click.option('--reload', is_flag=True, help='Перезапуск при изменениях кода (только для разработки).')
def start(host: str | None, port: int | None, reload: bool) -> None:
    """Запускает HTTP-сервер finsight-api через `start_app()`.

    Args:
        host: Хост для сервера; None — значение по умолчанию из настроек.
        port: Порт для сервера; None — значение по умолчанию из настроек.
        reload: Включает перезапуск при изменениях кода (режим разработки).
    """
    start_app(host=host, port=port, reload=reload)

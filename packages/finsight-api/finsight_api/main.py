"""Точка входа в приложение: сборка через AppFactory и запуск uvicorn."""

import os
import pathlib

import uvicorn

from finsight_api.infrastructure.container import app_container
from finsight_api.presentation.webserver.app_factory import AppFactory


def start_app(
    host: str | None = None,
    port: int | None = None,
    reload: bool | None = None,
) -> None:
    """Собирает приложение через AppFactory и запускает его в uvicorn.

    Значения host, port и reload, если переданы, переопределяют настройки из конфигурации.

    Args:
        host: Хост приложения. Если None — берётся из настроек.
        port: Порт приложения. Если None — берётся из настроек.
        reload: Режим авто-перезагрузки. Если None — берётся из настроек.
    """
    settings = app_container.settings()
    logger = app_container.logger()

    # Переопределение значений из CLI
    if host:
        settings.app.host = host
    if port:
        settings.app.port = port
    if reload is not None:
        settings.app.reload = reload

    current_dir = str(pathlib.Path.cwd())

    logger.info('Will watch for changes in these directories', extra={'directories': [current_dir]})
    logger.info(f'Uvicorn running on http://{settings.app.host}:{settings.app.port} (Press CTRL+C to quit)')
    logger.info('Started reloader process', extra={'pid': os.getpid(), 'reloader': 'StatReload'})

    app = AppFactory(settings).create_app()

    uvicorn.run(
        app,
        host=settings.app.host,
        port=settings.app.port,
        # TODO: Вынести в конфиг
        access_log=False,
        log_config=None,
        log_level=settings.logging.log_level.value,
    )


if __name__ == '__main__':
    start_app()

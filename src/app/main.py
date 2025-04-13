"""Точка входа в приложение. Настраивает и запускает сервер."""

import os
import pathlib

import uvicorn

from src.app.infrastructure.adapters.logger.logging import configure_logging
from src.app.infrastructure.config import Settings
from src.app.infrastructure.container import AppContainer
from src.app.presentation.webserver.app_factory import AppFactory


def start_app() -> None:
    """Запускает приложение с помощью uvicorn."""
    settings = Settings()

    AppContainer.config.from_pydantic(settings)

    app_container = AppContainer()
    app_container.wire(modules=[__name__])

    configure_logging(
        app_name=settings.app.name,
        app_version=settings.app.version,
        env=settings.app.env,
        instance=settings.app.host,
        log_level=settings.logging.log_level,
    )

    logger = app_container.logger()

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

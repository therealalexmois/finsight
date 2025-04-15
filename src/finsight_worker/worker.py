"""Создание и конфигурация приложения."""

from typing import TYPE_CHECKING

from celery import Celery

from src.finsight_worker.infrastructure.adapters.logger.logging import configure_logging

if TYPE_CHECKING:
    from src.finsight_worker.infrastructure.config import Settings


def create_celery_app(settings: 'Settings') -> 'Celery':
    """Создает и настраивает экземпляр Celery."""
    configure_logging(
        app_name=settings.worker.name,
        app_version=settings.worker.version,
        env=settings.worker.env,
        instance=settings.worker.host,
        log_level=settings.logging.log_level,
    )

    app = Celery(
        main=settings.worker.name,
        broker=settings.redis.broker_url,
        backend=settings.redis.result_backend,
    )

    app.conf.update(
        task_track_started=True,
        task_serializer='json',
        result_serializer='json',
        accept_content=['json'],
        timezone='UTC',
        enable_utc=True,
    )

    return app

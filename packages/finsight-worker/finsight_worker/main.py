"""Точка входа для приложения finsight_worker.

Загружает зависимости, настраивает Celery и импортирует задачи.
"""

from finsight_worker.infrastructure.config import Settings
from finsight_worker.infrastructure.container import WorkerContainer
from finsight_worker.infrastructure.tasks import download_historical_data
from finsight_worker.worker import create_celery_app

settings = Settings()
container = WorkerContainer()
container.config.from_pydantic(settings)

celery_app = create_celery_app(settings)

download_historical_data.register_tasks(celery_app)

__all__ = ['celery_app']

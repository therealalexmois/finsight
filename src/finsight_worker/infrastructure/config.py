"""Конфигурация и настройки сервиса finsight-worker."""

import os
from pathlib import Path  # noqa: TC003
from socket import gethostname
from typing import Final  # noqa: TC003

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.finsight_worker.domain.constants import AppEnv, LogLevel
from src.finsight_worker.infrastructure.utils.pyproject import extract_project_field, find_pyproject_path

DEFAULT_WORKER_ENV: Final[str] = 'local'
DEFAULT_APP_VERSION: Final[str] = '0.0.0'
DEFAULT_WORKER_NAME: Final[str] = 'finsight_worker'
DEFAULT_LOG_LEVEL: Final[LogLevel] = LogLevel.INFO
DEFAULT_REDIS_HOST: Final[str] = 'localhost'
DEFAULT_REDIS_PORT: Final[int] = 6379
DEFAULT_REDIS_DB: Final[int] = 0
DEFAULT_REDIS_URL: Final[str] = f'redis://{DEFAULT_REDIS_HOST}:{DEFAULT_REDIS_PORT}/{DEFAULT_REDIS_DB}'
DEFAULT_CELERY_BACKEND: Final[str] = DEFAULT_REDIS_URL

PYPROJECT_PATH: Final[Path] = find_pyproject_path()

_ENV_PREFIX = 'FINSIGHT_WORKER_'
_ENV_FILE = '.env.local' if os.environ.get(f'{_ENV_PREFIX}ENV', DEFAULT_WORKER_ENV) == DEFAULT_WORKER_ENV else None

_ENV_SETTINGS: Final[SettingsConfigDict] = SettingsConfigDict(
    env_prefix=_ENV_PREFIX,
    env_file=_ENV_FILE,
    env_ignore_empty=True,
    extra='ignore',
)


class WorkerSettings(BaseSettings):
    """Настройки Celery-воркера."""

    name: str = Field(
        default_factory=lambda: extract_project_field('name', PYPROJECT_PATH) or DEFAULT_WORKER_NAME,
        description='Имя воркера из pyproject.toml',
    )
    env: AppEnv = Field(
        default=AppEnv.LOCAL,
        description='Окружение воркера: local, dev, production',
    )
    host: str = Field(
        default_factory=gethostname,
        description='Имя хоста или IP, где запущен воркер',
    )
    version: str = Field(
        default_factory=lambda: extract_project_field('version', PYPROJECT_PATH) or DEFAULT_APP_VERSION,
        description='Версия приложения, полученная из pyproject.toml.',
    )

    model_config = SettingsConfigDict(**_ENV_SETTINGS)


class LoggingSettings(BaseSettings):
    """Настройки логирования."""

    log_level: LogLevel = Field(
        default=DEFAULT_LOG_LEVEL,
        description='Уровень логирования воркера',
    )

    model_config = SettingsConfigDict(**_ENV_SETTINGS)


class RedisSettings(BaseSettings):
    """Настройки Redis брокера и backend."""

    host: str = Field(default=DEFAULT_REDIS_HOST, description='Хост Redis.')
    port: int = Field(default=DEFAULT_REDIS_PORT, description='Порт Redis.')
    db: int = Field(default=DEFAULT_REDIS_DB, description='Номер базы данных Redis.')

    @property
    def broker_url(self) -> str:
        """Формирует URL подключения к Redis как брокеру задач Celery.

        Returns:
            Строка подключения к Redis.
        """
        return f'redis://{self.host}:{self.port}/{self.db}'

    @property
    def result_backend(self) -> str:
        """Формирует URL backend-хранилища для результатов задач Celery.

        Возвращает тот же URL, что и broker_url.

        Returns:
            Строка подключения к Redis.
        """
        return self.broker_url

    model_config = SettingsConfigDict(**_ENV_SETTINGS)


class Settings(BaseSettings):
    """Основная точка входа для всех настроек воркера."""

    worker: WorkerSettings = Field(default_factory=WorkerSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)

    model_config = SettingsConfigDict(**_ENV_SETTINGS)

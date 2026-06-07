"""Конфигурация приложения, основанная на переменных окружения.

Загружает настройки из .env.local в режиме 'local'. В других окружениях .env не используется.
"""

import os
from pathlib import Path  # noqa: TC003
from typing import Final  # noqa: TC003

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from finsight_api.domain.constants import AppEnv, LogLevel
from finsight_api.infrastructure.utils.pyproject import extract_project_field, find_pyproject_path

DEFAULT_APP_ENV: Final[str] = 'local'
DEFAULT_APP_HOST: Final[str] = '127.0.0.1'
DEFAULT_APP_PORT: Final[int] = 8000
DEFAULT_APP_VERSION: Final[str] = '0.0.0'
DEFAULT_APP_LOG_LEVEL: Final[LogLevel] = LogLevel.INFO
DEFAULT_APP_ENV_FILE: Final[str] = '.env.local'
DEFAULT_APP_NAME: Final[str] = 'finsight'
DEFAULT_APP_DESCRIPTION: Final[str] = (
    'FastAPI-based REST API for integrating with Tinkoff Invest and predicting short-term stock movements.'
)
DEFAULT_APP_RELOAD: Final[bool] = False
DEFAULT_APP_DEBUG: Final[bool] = False

PYPROJECT_PATH: Final[Path] = find_pyproject_path()

_BASE_ENV_PREFIX: Final[str] = 'APP_'
_ENV_NESTED_DELIMITER: Final[str] = '__'

# Для nested-конфига env окружение хранится в APP_APP__ENV.
_ENV_FILE = DEFAULT_APP_ENV_FILE if os.environ.get('APP_APP__ENV', DEFAULT_APP_ENV) == DEFAULT_APP_ENV else None

_ENV_SETTINGS = SettingsConfigDict(
    env_prefix=_BASE_ENV_PREFIX,
    env_file=_ENV_FILE,
    env_file_encoding='utf-8',
    env_ignore_empty=True,
    extra='ignore',
    env_nested_delimiter=_ENV_NESTED_DELIMITER,
)


class AppSettings(BaseModel):
    """Настройки приложения.

    Вложенная секция настроек с env-префиксом APP_APP__ (например APP_APP__ENV).
    Поля name, description и version по умолчанию читаются из секции [project]
    файла pyproject.toml.

    Attributes:
        name: Название приложения.
        description: Описание приложения.
        host: Адрес запуска приложения.
        port: Порт запуска приложения (1025–65535).
        env: Окружение выполнения (local, dev, production).
        version: Версия приложения.
        reload: Режим авто-перезагрузки.
        debug: Режим отладки FastAPI.
    """

    name: str = Field(
        default_factory=lambda: extract_project_field('name', PYPROJECT_PATH) or DEFAULT_APP_NAME,
        description='Название приложения, полученное из pyproject.toml.',
    )
    description: str = Field(
        default_factory=lambda: extract_project_field('description', PYPROJECT_PATH) or DEFAULT_APP_DESCRIPTION,
        description='Описание приложения, полученное из pyproject.toml.',
    )
    host: str = Field(
        default=DEFAULT_APP_HOST,
        description='Адрес, на котором запускается приложение (например, 127.0.0.1 или 0.0.0.0).',
    )
    port: int = Field(
        default=DEFAULT_APP_PORT,
        gt=1024,
        le=65535,
        description='Порт запуска приложения (допустимы значения от 1025 до 65535).',
    )
    env: AppEnv = Field(
        default=AppEnv.LOCAL,
        description='Окружение, в котором работает приложение: local, dev или production.',
    )
    version: str = Field(
        default_factory=lambda: extract_project_field('version', PYPROJECT_PATH) or DEFAULT_APP_VERSION,
        description='Версия приложения, полученная из pyproject.toml.',
    )
    reload: bool = Field(default=DEFAULT_APP_RELOAD, description='Включать режим авто-перезагрузки.')
    debug: bool = Field(default=DEFAULT_APP_DEBUG, description='Включает режим отладки FastAPI.')


class LoggingSettings(BaseModel):
    """Настройки логирования.

    Вложенная секция с env-префиксом APP_LOGGING__ (например APP_LOGGING__LOG_LEVEL).

    Attributes:
        log_level: Уровень логирования приложения.
    """

    log_level: LogLevel = Field(
        default=DEFAULT_APP_LOG_LEVEL,
        description='Уровень логирования приложения: debug, info, warning или error (в зависимости от enum).',
    )


class TinkoffInvestApiSettings(BaseModel):
    """Настройки интеграции с Tinkoff Invest API.

    Вложенная секция с env-префиксом APP_TINKOFF_INVEST_API__ (например
    APP_TINKOFF_INVEST_API__TOKEN). Используется токен с правами только на чтение:
    он должен быть активным и действующим, истекает через 3 месяца с момента
    последнего использования и может быть отозван вручную в личном кабинете.

    Attributes:
        token: Read-only токен Tinkoff Invest API. Торговые поручения недоступны.
        sandbox_token: Публичный sandbox токен (опционально).
    """

    token: str = Field(
        description=('Read-only токен Tinkoff Invest API. С этим токеном нельзя выставлять торговые поручения.')
    )
    sandbox_token: str | None = Field(
        default=None,
        description='Публичный sandbox токен для Tinkoff Invest API (опционально).',
    )


class Settings(BaseSettings):
    """Корневые настройки приложения, собираемые из окружения.

    Источники значений: переменные окружения с префиксом APP_ и (только в окружении
    local) файл .env.local. Вложенность секций задаётся разделителем '__'.

    Attributes:
        app: Настройки приложения.
        logging: Настройки логирования.
        tinkoff_invest_api: Настройки интеграции с Tinkoff Invest API.
    """

    app: AppSettings = Field(default_factory=AppSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    tinkoff_invest_api: TinkoffInvestApiSettings

    model_config = _ENV_SETTINGS

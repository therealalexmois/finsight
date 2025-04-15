"""Конфигурация приложения, основанная на переменных окружения.

Загружает настройки из .env.local в режиме 'local'. В других окружениях .env не используется.
"""

import logging
import os
from pathlib import Path  # noqa: TC003
from socket import gethostname
from typing import Final  # noqa: TC003

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.finsight_api.domain.constants import AppEnv, LogLevel
from src.finsight_api.infrastructure.utils.pyproject import extract_project_field, find_pyproject_path

logger = logging.getLogger(__name__)

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

_BASE_ENV_PREFIX = 'APP_'
_ENV_FILE = (
    DEFAULT_APP_ENV_FILE if os.environ.get(f'{_BASE_ENV_PREFIX}ENV', DEFAULT_APP_ENV) == DEFAULT_APP_ENV else None
)

_ENV_SETTINGS: Final[SettingsConfigDict] = SettingsConfigDict(
    env_prefix=_BASE_ENV_PREFIX,
    env_file=_ENV_FILE,
    env_ignore_empty=True,
    extra='ignore',
)


class AppSettings(BaseSettings):
    """Настройки приложения."""

    name: str = Field(
        default_factory=lambda: extract_project_field('name', PYPROJECT_PATH) or DEFAULT_APP_NAME,
        description='Название приложения, полученное из pyproject.toml.',
    )
    description: str = Field(
        default_factory=lambda: extract_project_field('description', PYPROJECT_PATH) or DEFAULT_APP_DESCRIPTION,
        description='Название приложения, полученное из pyproject.toml.',
    )
    host: str = Field(
        default_factory=gethostname, description='Имя хоста или IP-адрес, на котором запускается приложение.'
    )
    port: int = Field(
        default=DEFAULT_APP_PORT,
        gt=1024,
        le=65536,
        description='Порт, на котором запускается приложение (допустимы значения от 1025 до 65536).',
    )
    env: AppEnv = Field(
        default=AppEnv.LOCAL, description='Окружение, в котором работает приложение: local, dev или production.'
    )
    version: str = Field(
        default_factory=lambda: extract_project_field('version', PYPROJECT_PATH) or DEFAULT_APP_VERSION,
        description='Версия приложения, полученная из pyproject.toml.',
    )
    reload: bool = Field(default=DEFAULT_APP_RELOAD, description='Включать режим авто-перезагрузки.')
    debug: bool = Field(default=DEFAULT_APP_DEBUG, description='Включает режим отладки FastAPI.')

    model_config = SettingsConfigDict(**_ENV_SETTINGS)


class LoggingSettings(BaseSettings):
    """Настройки логирования."""

    log_level: LogLevel = Field(
        default=DEFAULT_APP_LOG_LEVEL, description='Уровень логирования приложения: info, warning или error.'
    )

    model_config = SettingsConfigDict(**_ENV_SETTINGS)


class TinkoffInvestApiSettings(BaseSettings):
    """Настройки интеграции с Tinkoff Invest API.

    Используется sandbox токен с правами только на чтение. Токен должен быть активным и действующим.
    Истекает через 3 месяца с момента последнего использования. Может быть отозван вручную в личном кабинете.

    Подробнее: https://tinkoff.github.io/investAPI/token/
    """

    token: str = Field(
        alias='APP_TINKOFF_INVEST_API_READONLY_TOKEN',
        description=(
            'Токен для получения информации: например, состояние портфеля, '
            'расписание торгов различных торговых площадок, текущие котировки, '
            'исторические данные. С этим типом токена нельзя выставлять торговые поручения.'
        ),
        frozen=True,
    )

    sandbox_token: str | None = Field(
        default=None,
        alias='APP_TINKOFF_INVEST_API_SANDBOX_TOKEN',
        description=(
            'Публичный sandbox токен для Tinkoff Invest API, используется для чтения истории и портфеля. '
            'Не является обязательным.'
        ),
    )

    model_config = SettingsConfigDict(**_ENV_SETTINGS)


class Settings(BaseSettings):
    """Основная точка доступа к настройкам всего приложения."""

    app: AppSettings = Field(default_factory=AppSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    tinkoff_invest_api: TinkoffInvestApiSettings = Field(
        default_factory=lambda: TinkoffInvestApiSettings()  # type: ignore[arg-type, call-arg]
    )

    model_config = SettingsConfigDict(**_ENV_SETTINGS)

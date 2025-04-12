"""Конфигурация приложения, основанная на переменных окружения.

Загружает настройки из .env.local в режиме 'local'. В других окружениях .env не используется.
"""

import logging
import os
import tomllib
from pathlib import Path
from socket import gethostname
from typing import cast, Final  # noqa: TC003

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.app.domain.constants import AppEnv, LogLevel

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

_APP_PACKAGE_CONFIG_PATH: Final[Path] = Path().absolute() / 'pyproject.toml'

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
        default_factory=lambda: _extract_project_field('name', _APP_PACKAGE_CONFIG_PATH) or DEFAULT_APP_NAME,
        description='Название приложения, полученное из pyproject.toml.',
    )
    description: str = Field(
        default_factory=lambda: _extract_project_field('description', _APP_PACKAGE_CONFIG_PATH)
        or DEFAULT_APP_DESCRIPTION,
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
        default_factory=lambda: _extract_project_field('version', _APP_PACKAGE_CONFIG_PATH) or DEFAULT_APP_VERSION,
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


class Settings(BaseSettings):
    """Основная точка доступа к настройкам всего приложения."""

    app: AppSettings = Field(default_factory=AppSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)

    model_config = SettingsConfigDict(**_ENV_SETTINGS)


def _extract_project_field(field_name: str, app_config_path: Path) -> str | None:
    """Извлекает поле из секции [project] файла pyproject.toml.

    Args:
        field_name: Название поля (например, 'name', 'version').
        app_config_path: Путь к pyproject.toml.

    Returns:
        Значение поля в виде строки.

    Raises:
        OSError: Ошибка при открытии файла.
        tomllib.TOMLDecodeError: Ошибка при разборе TOML.
        KeyError: Указанное поле не найдено.
    """
    try:
        with open(app_config_path, 'rb') as file:
            data = tomllib.load(file)
            return cast('str', data['project'][field_name])
    except OSError as error:
        logger.error(f'Ошибка при открытии {app_config_path}: {error}')
        raise
    except tomllib.TOMLDecodeError as error:
        logger.error(f'Ошибка при разборе TOML файла {app_config_path}: {error}')
        raise
    except KeyError as error:
        logger.error(f'Поле {field_name!r} не найдено в секции [project] файла {app_config_path}: {error}')
        raise

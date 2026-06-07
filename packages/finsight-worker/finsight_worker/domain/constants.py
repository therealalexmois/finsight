"""Константы и перечисления, используемые в приложении."""

from enum import StrEnum, unique
from typing import Final  # noqa: TC003

LOGGER_NAME: Final[str] = 'finsight-worker'


@unique
class AppEnv(StrEnum):
    """Перечисление окружений приложения."""

    LOCAL = 'local'
    DEV = 'dev'
    PROD = 'production'


@unique
class LogLevel(StrEnum):
    """Уровни журналирования в приложении."""

    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'


@unique
class LogAttrName(StrEnum):
    """Название технических атрибутов записи в лог."""

    ENV = 'env'
    ERROR = 'error'
    INSTANCE = 'instance'
    LEVEL = 'level'
    MESSAGE = 'message'
    REQUEST_ID = 'request_id'
    SYSTEM = 'system'
    TIMESTAMP = 'timestamp'
    USERNAME = 'username'
    VERSION = 'version'

"""Константы и перечисления, используемые в приложении."""

from enum import Enum, unique
from typing import Final  # noqa: TC003

LOGGER_NAME: Final[str] = 'app'

DEFAULT_DISABLED_LOGGER_NAMES: frozenset[str] = frozenset(['uvicorn.access'])


class AppEnv(str, Enum):
    """Перечисление окружений приложения."""

    LOCAL = 'local'
    DEV = 'dev'
    PROD = 'production'


class LogLevel(str, Enum):
    """Уровни журналирования в приложении."""

    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'


@unique
class LogAttrName(str, Enum):
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

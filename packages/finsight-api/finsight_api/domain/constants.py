# TODO: Убрать из домена
"""Константы и перечисления, используемые в приложении."""

from enum import Enum, unique
from typing import Final  # noqa: TC003

LOGGER_NAME: Final[str] = 'finsight-api'


@unique
class AppEnv(str, Enum):
    """Перечисление окружений приложения."""

    LOCAL = 'local'
    DEV = 'dev'
    PROD = 'production'


@unique
class LogLevel(str, Enum):
    """Уровни журналирования в приложении."""

    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'


@unique
class LogAttrName(str, Enum):
    """Имена технических атрибутов записи лога."""

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

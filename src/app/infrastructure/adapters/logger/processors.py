"""Кастомные обработчики structlog для дополнения логов техническими атрибутами."""

from datetime import datetime, UTC
from typing import TYPE_CHECKING

from structlog.processors import ExceptionRenderer

from src.app.domain.constants import LogAttrName
from src.app.infrastructure.adapters.logger.context import get_request_id

if TYPE_CHECKING:
    from structlog.typing import EventDict, WrappedLogger

    from src.app.domain.constants import AppEnv


class UvicornColorMessageDropper:
    """Удаляет цветовое сообщение Uvicorn из event_dict."""

    def __call__(self, _: 'WrappedLogger', __: str, event_dict: 'EventDict') -> 'EventDict':
        """Вызов обработчика."""
        event_dict.pop('color_message', None)
        return event_dict


class ExceptionInfoAttrRenamer(ExceptionRenderer):
    """Добавление информации об исключении в запись лога."""

    def __call__(self, logger: 'WrappedLogger', name: str, event_dict: 'EventDict') -> 'EventDict':
        """Вызов обработчика."""
        event_dict = super().__call__(logger, name, event_dict)

        if exc_info := event_dict.pop('exception', None):
            event_dict[LogAttrName.ERROR.value] = exc_info
        return event_dict


class LogLevelNormalizer:
    """Нормальизация значения уровня логирования в запись лога."""

    def __call__(self, _: 'WrappedLogger', name: str, event_dict: 'EventDict') -> 'EventDict':
        """Вызов обработчика."""
        event_dict[LogAttrName.LEVEL.value] = name.upper()
        return event_dict


class MessageAttrRenamer:
    """Переименование атрибута event в логe."""

    def __call__(self, _: 'WrappedLogger', __: str, event_dict: 'EventDict') -> 'EventDict':
        """Вызов обработчика."""
        message = event_dict.pop('event', None)
        event_dict[LogAttrName.MESSAGE.value] = message or ''
        return event_dict


class RequestIdAdder:
    """Добавляет идентификатор запроса в запись лога."""

    def __call__(self, _: 'WrappedLogger', __: str, event_dict: 'EventDict') -> 'EventDict':
        """Вызов обработчика."""
        request_id = get_request_id()

        if request_id:
            event_dict[LogAttrName.REQUEST_ID.value] = request_id

        return event_dict


class CommonAttrsAdder:
    """Добавляет общие параметры запроса в запись лога."""

    def __init__(self, app_name: str, app_version: str, env: 'AppEnv', instance: str) -> None:
        """Инициализирует обработчик общих параметров для логов.

        Args:
            app_name: Название приложения.
            app_version: Версия приложения.
            env: Текущая среда выполнения.
            instance: Идентификатор инстанса приложения.
        """
        self.app_name: str = app_name
        self.env: AppEnv = env
        self.instance: str = instance
        self.app_version: str = app_version

    def __call__(self, _: 'WrappedLogger', __: str, event_dict: 'EventDict') -> 'EventDict':
        """Вызов обработчика."""
        event_dict[LogAttrName.ENV.value] = self.env.value
        event_dict[LogAttrName.INSTANCE.value] = self.instance
        event_dict[LogAttrName.SYSTEM.value] = self.app_name
        event_dict[LogAttrName.TIMESTAMP.value] = self._get_datetime_as_string()
        event_dict[LogAttrName.VERSION.value] = self.app_version

        return event_dict

    def _get_datetime_as_string(self, now: datetime | None = None) -> str:
        return (now or datetime.now(UTC)).isoformat(timespec='milliseconds').removesuffix('Z')

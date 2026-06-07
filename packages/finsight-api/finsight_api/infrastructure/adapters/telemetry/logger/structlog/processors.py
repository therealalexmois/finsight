"""Кастомные обработчики structlog для дополнения логов техническими атрибутами."""

from datetime import datetime, UTC
from typing import TYPE_CHECKING

from structlog.processors import ExceptionRenderer

from finsight_api.domain.constants import LogAttrName

# from finsight_api.infrastructure.adapters.logger.context import get_request_id

if TYPE_CHECKING:
    from structlog.typing import EventDict, WrappedLogger

    from finsight_api.domain.constants import AppEnv


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
    """Записывает уровень логирования в event_dict в верхнем регистре."""

    def __call__(self, _: 'WrappedLogger', name: str, event_dict: 'EventDict') -> 'EventDict':
        """Вызов обработчика."""
        event_dict[LogAttrName.LEVEL.value] = name.upper()
        return event_dict


class MessageAttrRenamer:
    """Переименовывает атрибут event записи лога в LogAttrName.MESSAGE."""

    def __call__(self, _: 'WrappedLogger', __: str, event_dict: 'EventDict') -> 'EventDict':
        """Вызов обработчика."""
        message = event_dict.pop('event', None)
        event_dict[LogAttrName.MESSAGE.value] = message or ''
        return event_dict


# class RequestIdAdder:
#     """Добавляет идентификатор запроса в запись лога."""
#
#     def __call__(self, _: 'WrappedLogger', __: str, event_dict: 'EventDict') -> 'EventDict':
#         """Вызов обработчика."""
#         request_id = get_request_id()
#
#         if request_id:
#             event_dict[LogAttrName.REQUEST_ID.value] = request_id
#
#         return event_dict


class CommonAttrsAdder:
    """Добавляет общие параметры запроса в запись лога."""

    def __init__(
        self,
        app_name: str,
        app_version: str,
        app_env: 'AppEnv',
        instance: str,
    ) -> None:
        """Инициализирует обработчик общих параметров для логов.

        Args:
            app_name: Название приложения.
            app_version: Версия приложения.
            app_env: Текущая среда выполнения.
            instance: Идентификатор инстанса приложения.
        """
        self._app_name: str = app_name
        self._app_env: AppEnv = app_env
        self._instance: str = instance
        self._app_version: str = app_version

    def __call__(self, _: 'WrappedLogger', __: str, event_dict: 'EventDict') -> 'EventDict':
        """Вызов обработчика."""
        event_dict[LogAttrName.ENV.value] = self._app_env.value
        event_dict[LogAttrName.INSTANCE.value] = self._instance
        event_dict[LogAttrName.SYSTEM.value] = self._app_name
        event_dict[LogAttrName.TIMESTAMP.value] = self._get_datetime_as_string()
        event_dict[LogAttrName.VERSION.value] = self._app_version

        return event_dict

    def _get_datetime_as_string(self, now: datetime | None = None) -> str:
        """Возвращает метку времени в ISO 8601 с точностью до миллисекунд.

        Args:
            now: Момент времени для форматирования. Если None — берётся текущее время в UTC.

        Returns:
            Строка ISO 8601 без суффикса 'Z'.
        """
        return (now or datetime.now(UTC)).isoformat(timespec='milliseconds').removesuffix('Z')

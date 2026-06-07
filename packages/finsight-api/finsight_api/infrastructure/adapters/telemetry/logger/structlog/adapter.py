"""Реализация интерфейса логгера с использованием библиотеки structlog."""

import logging
import sys
from contextvars import ContextVar
from typing import cast, TYPE_CHECKING

import orjson
import structlog
from structlog import configure
from structlog.contextvars import merge_contextvars
from structlog.processors import JSONRenderer
from structlog.stdlib import (
    BoundLogger,
    ExtraAdder,
    LoggerFactory,
    PositionalArgumentsFormatter,
    ProcessorFormatter,
)

from finsight_api.application.ports.logger import LoggerPort
from finsight_api.presentation.webserver.constants import DEFAULT_DISABLED_LOGGER_NAMES

from .processors import (
    CommonAttrsAdder,
    ExceptionInfoAttrRenamer,
    LogLevelNormalizer,
    MessageAttrRenamer,
    # RequestIdAdder,
    UvicornColorMessageDropper,
)

if TYPE_CHECKING:
    from collections.abc import Iterable
    from types import TracebackType
    from typing import Any

    from structlog.typing import Processor

    from finsight_api.domain.constants import AppEnv, LogLevel


_logger_ctx: ContextVar[LoggerPort | None] = ContextVar('_logger', default=None)


class StructlogLogger(LoggerPort):
    """Реализация порта LoggerPort поверх structlog.

    При инициализации настраивает structlog и стандартный logging: JSON-вывод через
    orjson, проброс контекстных переменных, добавление общих атрибутов (env, instance,
    система, версия). Перехватывает необработанные исключения через sys.excepthook
    и переключает сторонние логгеры (включая uvicorn) на общий обработчик.
    """

    def __init__(
        self,
        *,
        app_name: str,
        app_version: str,
        app_env: 'AppEnv',
        app_instance: str,
        log_level: 'LogLevel',
    ) -> None:
        """Инициализирует экземпляр structlog логгера.

        Args:
            app_name: Название приложения.
            app_version: Версия приложения.
            app_env: Текущая среда выполнения.
            app_instance: Идентификатор инстанса приложения.
            log_level: Уровень журналирования приложения.
        """
        self._logger = structlog.get_logger(app_name)
        self._app_name = app_name
        self._app_version = app_version
        self._app_env = app_env
        self._app_instance = app_instance
        self._log_level = log_level

        self._configure(
            app_name=self._app_name,
            app_version=self._app_version,
            app_env=self._app_env,
            app_instance=self._app_instance,
            log_level=self._log_level,
        )

    def info(self, event: str, **kwargs: 'Any') -> None:
        """Логгирует информационное сообщение.

        Args:
            event: Название события.
            **kwargs: Дополнительные параметры события.
        """
        self._logger.info(event, **kwargs)

    def warning(self, event: str, **kwargs: 'Any') -> None:
        """Логгирует предупреждающее сообщение.

        Args:
            event: Название события.
            **kwargs: Дополнительные параметры события.
        """
        self._logger.warning(event, **kwargs)

    def error(self, event: str, **kwargs: 'Any') -> None:
        """Логгирует сообщение об ошибке.

        Args:
            event: Название события.
            **kwargs: Дополнительные параметры события.
        """
        self._logger.error(event, **kwargs)

    def clear_context_vars(self) -> None:
        """Очищает все привязанные контекстные переменные."""
        structlog.contextvars.clear_contextvars()

    def bind_context_vars(self, **kwargs: 'Any') -> None:
        """Добавляет переменные в контекст логгера."""
        structlog.contextvars.bind_contextvars(**kwargs)

    def unbind_context_vars(self, *keys: str) -> None:
        """Удаляет переменные из контекста логгера по ключам."""
        structlog.contextvars.unbind_contextvars(*keys)

    def _configure(  # noqa: PLR0913
        self,
        *,
        app_name: str,
        app_version: str,
        app_env: 'AppEnv',
        app_instance: str,
        log_level: 'LogLevel',
        disabled_logger_names: 'Iterable[str] | None' = None,
    ) -> None:
        """Настраивает structlog и стандартный logging для всего процесса.

        Args:
            app_name: Название приложения.
            app_version: Версия приложения.
            app_env: Текущая среда выполнения.
            app_instance: Идентификатор инстанса приложения.
            log_level: Уровень журналирования приложения.
            disabled_logger_names: Имена логгеров, которые нужно отключить. Если None —
                используется DEFAULT_DISABLED_LOGGER_NAMES.
        """
        root_logger = logging.getLogger()

        def handle_exception(
            exc_type: type[BaseException], exc_value: BaseException, exc_traceback: 'TracebackType | None'
        ) -> None:
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return

            root_logger.exception('Unknown error', exc_info=(exc_type, exc_value, exc_traceback))

        def serializer(*args: 'Any', **kwargs: 'Any') -> str:
            """Сериализует словарь события в строку JSON."""
            return orjson.dumps(*args, **kwargs).decode('utf-8')

        sys.excepthook = handle_exception

        shared_processors: list[Processor] = [
            merge_contextvars,
            UvicornColorMessageDropper(),
            ExceptionInfoAttrRenamer(),
            ExtraAdder(),
            PositionalArgumentsFormatter(),
            LogLevelNormalizer(),
            MessageAttrRenamer(),
            # RequestIdAdder(),
            CommonAttrsAdder(app_name=app_name, app_version=app_version, app_env=app_env, instance=app_instance),
        ]

        configure(
            processors=shared_processors + [ProcessorFormatter.wrap_for_formatter],
            context_class=dict,
            logger_factory=LoggerFactory(),
            wrapper_class=BoundLogger,
            cache_logger_on_first_use=True,
        )

        formatter = ProcessorFormatter(
            foreign_pre_chain=shared_processors,
            processors=[
                ProcessorFormatter.remove_processors_meta,
                JSONRenderer(serializer=serializer),
            ],
        )

        handler: logging.Handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        root_logger.addHandler(handler)
        root_logger.setLevel(log_level.value.upper())

        disabled = disabled_logger_names or DEFAULT_DISABLED_LOGGER_NAMES

        for logger_name in logging.root.manager.loggerDict:
            logger = logging.getLogger(logger_name)

            logger.setLevel(root_logger.level)

            logger.disabled, logger.handlers = False, cast('list[logging.Handler]', [handler])

            if logger_name in disabled:
                logger.disabled, logger.handlers = True, []

        uvicorn_logger_names: Iterable[str] = ['uvicorn', 'uvicorn.error', 'uvicorn.access']

        for name in uvicorn_logger_names:
            logger = logging.getLogger(name)
            logger.handlers = [handler]
            logger.setLevel(root_logger.level)
            logger.propagate = False

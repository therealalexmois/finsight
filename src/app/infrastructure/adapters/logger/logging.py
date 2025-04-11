"""Настройка логирования через structlog."""

import logging
import sys
from contextvars import ContextVar
from typing import cast, TYPE_CHECKING

import orjson
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

from src.app.domain.constants import DEFAULT_DISABLED_LOGGER_NAMES

if TYPE_CHECKING:
    from collections.abc import Iterable
    from types import TracebackType
    from typing import Any

    from structlog.typing import Processor

    from src.app.application.ports.logger import Logger
    from src.app.domain.constants import AppEnv, LogLevel


from src.app.infrastructure.adapters.logger.processors import (
    CommonAttrsAdder,
    ExceptionInfoAttrRenamer,
    LogLevelNormalizer,
    MessageAttrRenamer,
    RequestIdAdder,
    UvicornColorMessageDropper,
)

_logger_ctx: ContextVar['Logger | None'] = ContextVar('_logger', default=None)


def configure_logging(  # noqa: PLR0913
    app_name: str,
    app_version: str,
    env: 'AppEnv',
    instance: str,
    log_level: 'LogLevel',
    disabled_logger_names: 'Iterable[str] | None' = None,
    propagate_log_message: bool = False,
) -> None:
    """Настраивает структуру логирования с использованием structlog."""
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
        RequestIdAdder(),
        CommonAttrsAdder(app_name=app_name, app_version=app_version, env=env, instance=instance),
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

        logger.propagate = propagate_log_message
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

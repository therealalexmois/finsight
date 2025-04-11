"""Утилиты уровня представления, связанные с авторизацией и HTTP-исключениями."""

from http import HTTPStatus
from typing import TYPE_CHECKING

from fastapi import HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.app.domain.exceptions import BaseAppError
from src.app.infrastructure.container import AppContainer

if TYPE_CHECKING:
    from collections.abc import Sequence

    from fastapi import Request


logger = AppContainer.logger()


async def base_app_error_handler(_: 'Request', exc: Exception) -> JSONResponse:
    """Обработчик ошибок приложения.

    Args:
        _: Объект запроса (не используется).
        exc: Исключение, которое должно быть экземпляром BaseAppError.

    Returns:
        JSON-ответ с сообщением об ошибке и HTTP-статусом.
    """
    if isinstance(exc, BaseAppError):
        logger.warning('application_error', message=exc.message, status_code=exc.status_code)
        return _internal_error_response(status_code=exc.status_code, content=exc.message)

    logger.error('unexpected_exception', exc_info=exc)
    return _internal_error_response(
        status_code=int(HTTPStatus.INTERNAL_SERVER_ERROR),
        content=HTTPStatus.INTERNAL_SERVER_ERROR.phrase,
    )


async def validation_error_handler(_: 'Request', exc: 'Exception') -> JSONResponse:
    """Обработчик ошибок FastAPI-валидации.

    Args:
        _: Объект запроса.
        exc: Исключение RequestValidationError.

    Returns:
        JSON-ответ с деталями ошибки.
    """
    if isinstance(exc, RequestValidationError):
        logger.warning('validation_error', errors=exc.errors())
        return _internal_error_response(status_code=int(HTTPStatus.BAD_REQUEST), content=exc.errors())

    logger.error('unexpected_validation_handler_path', exc_info=exc)
    return _internal_error_response(
        status_code=int(HTTPStatus.INTERNAL_SERVER_ERROR),
        content=HTTPStatus.INTERNAL_SERVER_ERROR.phrase,
    )


def build_unauthorized_exception(detail: str | None = HTTPStatus.UNAUTHORIZED.phrase) -> HTTPException:
    """Создает исключение HTTP 401 с заголовком WWW-Authenticate.

    Args:
        detail: Сообщение об ошибке.

    Returns:
        Исключение HTTPException с кодом 401.
    """
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={'WWW-Authenticate': 'Bearer'},
    )


def _internal_error_response(status_code: int, content: 'str | Sequence[dict[str, object]]') -> JSONResponse:
    """Формирует JSON-ответ с заданным HTTP-статусом и телом ошибки.

    Args:
        status_code: HTTP-статус ответа.
        content: Содержимое поля `detail` в теле ответа.

    Returns:
        Объект JSONResponse.
    """
    return JSONResponse(
        status_code=status_code,
        content={'detail': content},
    )

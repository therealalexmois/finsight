"""Инициализация системных маршрутов.

Модуль содержит маршруты для проверки работоспособности приложения:
- startup: проверка запуска приложения;
- readiness: проверка готовности приложения обрабатывать запросы;
- liveness: проверка активности приложения.
"""

from http import HTTPStatus

from fastapi import APIRouter
from fastapi.responses import JSONResponse

system_router: APIRouter = APIRouter(prefix='/system', tags=['system'])


@system_router.get('/startup', status_code=HTTPStatus.OK, summary='Проверка запуска приложения')
async def startup() -> JSONResponse:
    """Возвращает статус запуска приложения.

    Returns:
        JSONResponse: JSON-ответ с признаком доступности.
    """
    return JSONResponse(content={'status': 'ok'})


@system_router.get('/readiness', status_code=HTTPStatus.OK, summary='Проверка готовности')
async def readiness() -> JSONResponse:
    """Проверяет, готово ли приложение обрабатывать запросы.

    Returns:
        JSONResponse: JSON-ответ с признаком доступности.
    """
    return JSONResponse(content={'status': 'ok'})


@system_router.get('/liveness', status_code=HTTPStatus.OK, summary='Проверка активности')
async def liveness() -> JSONResponse:
    """Проверяет, активно ли приложение.

    Returns:
        JSONResponse: JSON-ответ с признаком доступности.
    """
    return JSONResponse(content={'status': 'ok'})

"""Инициализация системных маршрутов.

Модуль содержит маршруты для проверки работоспособности приложения:
- startup: проверка запуска приложения;
- readiness: проверка готовности приложения обрабатывать запросы;
- liveness: проверка активности приложения.
"""

from http import HTTPStatus

from fastapi import APIRouter

from src.finsight_api.presentation.schemas.system import SystemStatusResponse

system_router: APIRouter = APIRouter(prefix='/system', tags=['System'])


@system_router.get('/startup', status_code=HTTPStatus.OK, summary='Проверка запуска приложения')
async def startup() -> SystemStatusResponse:
    """Возвращает статус запуска приложения."""
    return SystemStatusResponse(status='ok')


@system_router.get('/readiness', status_code=HTTPStatus.OK, summary='Проверка готовности')
async def readiness() -> SystemStatusResponse:
    """Проверяет, готово ли приложение обрабатывать запросы."""
    return SystemStatusResponse(status='ok')


@system_router.get('/liveness', status_code=HTTPStatus.OK, summary='Проверка активности')
async def liveness() -> SystemStatusResponse:
    """Проверяет, активно ли приложение."""
    return SystemStatusResponse(status='ok')

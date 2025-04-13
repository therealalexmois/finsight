"""Инициализация маршрутов версии API v1."""

from fastapi import APIRouter

from src.app.presentation.api.constants import API_V1_PREFIX
from src.app.presentation.api.rest.v1.routes.account import router as account_router
from src.app.presentation.api.rest.v1.routes.portfolio import router as portfolio_router

api_v1_router = APIRouter(prefix=API_V1_PREFIX)

api_v1_router.include_router(account_router)
api_v1_router.include_router(portfolio_router)

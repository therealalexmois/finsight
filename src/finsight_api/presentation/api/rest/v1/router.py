"""Инициализация маршрутов версии API v1."""

from fastapi import APIRouter

from src.finsight_api.presentation.api.constants import API_V1_PREFIX
from src.finsight_api.presentation.api.rest.v1.routes.account import router as account_router
from src.finsight_api.presentation.api.rest.v1.routes.portfolio import router as portfolio_router

api_v1_router = APIRouter(prefix=API_V1_PREFIX)

api_v1_router.include_router(account_router)
api_v1_router.include_router(portfolio_router)

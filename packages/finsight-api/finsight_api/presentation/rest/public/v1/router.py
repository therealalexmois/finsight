"""Инициализация маршрутов версии API v1."""

from fastapi import APIRouter

from finsight_api.presentation.rest.constants import API_V1_PREFIX
from finsight_api.presentation.rest.public.v1.account.router import router as account_router
from finsight_api.presentation.rest.public.v1.portfolio.router import router as portfolio_router

api_v1_router = APIRouter(prefix=API_V1_PREFIX)

api_v1_router.include_router(account_router)
api_v1_router.include_router(portfolio_router)

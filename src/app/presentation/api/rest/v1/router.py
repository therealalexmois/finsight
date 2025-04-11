"""Инициализация маршрутов версии API v1."""

from fastapi import APIRouter

from src.app.presentation.api.constants import API_V1_PREFIX

api_v1_router = APIRouter(prefix=API_V1_PREFIX)

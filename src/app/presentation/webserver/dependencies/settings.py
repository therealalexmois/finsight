"""Зависимости FastAPI для повторного использования логики."""

from typing import Annotated

from fastapi import Depends

from src.app.infrastructure.config import get_settings, Settings


def get_app_settings() -> 'Settings':
    """Возвращает экземпляр настроек приложения."""
    return get_settings()


AppSettingsDep = Annotated[Settings, Depends(get_app_settings)]

"""Зависимости FastAPI для повторного использования логики."""

from typing import Annotated

from fastapi import Depends

from finsight_api.infrastructure.config import Settings
from finsight_api.infrastructure.container import AppContainer


def get_app_settings() -> 'Settings':
    """Возвращает экземпляр настроек приложения."""
    return AppContainer.config()


AppSettingsDep = Annotated[Settings, Depends(get_app_settings)]

"""Модели ответов системных маршрутов."""

from pydantic import BaseModel


class SystemStatusResponse(BaseModel):
    """Ответ, возвращаемый системными проверками состояния приложения."""

    status: str

"""Модели ответов системных маршрутов."""

from pydantic import BaseModel


class SystemStatusResponse(BaseModel):
    """Ответ, возвращаемый системными проверками состояния приложения.

    Attributes:
        status: Текстовый статус проверки.
    """

    status: str

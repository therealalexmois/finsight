"""Модель доменного уровня для пользователя."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime
    from uuid import UUID


@dataclass(frozen=True)
class User:
    """Модель пользователя в доменном слое."""

    id: 'UUID'
    login: str
    created_at: 'datetime'

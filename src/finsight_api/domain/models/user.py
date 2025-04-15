"""Модель доменного уровня для пользователя."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime
    from uuid import UUID


@dataclass(frozen=True)
class User:
    """Модель пользователя, представляющая базовую информацию о клиенте системы.

    Используется для идентификации владельца транзакций, прогнозов и других сущностей.

    Attributes:
        id: Уникальный идентификатор пользователя.
        login: Уникальный логин или имя пользователя.
        created_at: Дата и время создания пользователя в системе.
    """

    id: 'UUID'
    login: str
    created_at: 'datetime'

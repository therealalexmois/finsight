"""Модуль модели портфеля пользователя.

Содержит dataclass `PortfolioModel`, который агрегирует все позиции пользователя
по конкретному счёту. Используется для отображения полной информации о портфеле,
включая его стоимость, валюту и список активов.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    from src.finsight_api.domain.value_objects.portfolio_position import PortfolioPosition


@dataclass(frozen=True)
class PortfolioModel:
    """Сводная модель портфеля по конкретному счёту.

    Attributes:
        account_id: Идентификатор счёта.
        total_value: Общая стоимость портфеля.
        currency: Валюта портфеля.
        positions: Список позиций в портфеле.
    """

    account_id: str
    total_value: float
    currency: str
    positions: 'Sequence[PortfolioPosition]'

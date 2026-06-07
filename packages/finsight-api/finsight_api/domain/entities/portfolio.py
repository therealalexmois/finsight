"""Модуль модели портфеля пользователя.

Содержит dataclass `PortfolioModel`, который агрегирует все позиции пользователя
по конкретному счёту. Используется для отображения полной информации о портфеле,
включая его стоимость, валюту и список активов.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence
    from decimal import Decimal

    from finsight_api.domain.value_objects.portfolio_position import PortfolioPosition


@dataclass(frozen=True, slots=True, kw_only=True)
class PortfolioEntity:
    """Сводная модель портфеля по конкретному счёту.

    Attributes:
        account_id: Идентификатор счёта.
        total_amount_shares: Общая стоимость акций в портфеле.
        total_amount_bonds: Общая стоимость облигаций в портфеле.
        total_amount_etf: Общая стоимость фондов в портфеле.
        total_amount_futures: Общая стоимость фьючерсов в портфеле.
        total_value: Общая стоимость портфеля.
        cash_balance: Остаток денежных средств (денежная часть портфеля).
        currency: Валюта портфеля.
        positions: Список позиций в портфеле.
    """

    account_id: str
    total_amount_shares: 'Decimal'
    total_amount_bonds: 'Decimal'
    total_amount_etf: 'Decimal'
    total_amount_futures: 'Decimal'
    total_value: 'Decimal'
    cash_balance: 'Decimal'
    currency: str
    positions: 'Sequence[PortfolioPosition]'

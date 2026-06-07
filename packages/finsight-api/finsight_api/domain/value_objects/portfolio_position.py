"""Модуль модели позиции в портфеле.

Представляет позицию пользователя в инвестиционном портфеле.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from decimal import Decimal

    from finsight_api.domain.value_objects.instrument_type import InstrumentType


@dataclass(frozen=True, slots=True, kw_only=True)
class PortfolioPosition:
    """Позиции в портфеле пользователя.

    Attributes:
        figi: FIGI инструмента.
        instrument_type: Тип финансового инструмента (акция, облигация и т.д.).
        quantity: Количество лотов в позиции.
        expected_yield: Ожидаемая доходность позиции.
        average_position_price: Средняя цена позиции.
        current_price: Текущая рыночная цена инструмента.
        current_nkd: НКД (накопленный купонный доход) для облигаций на текущую дату.
        value: Рыночная стоимость позиции.
        instrument_uid: Уникальный идентификатор инструмента.
    """

    figi: str
    instrument_type: 'InstrumentType'
    quantity: 'Decimal'
    expected_yield: 'Decimal'
    average_position_price: 'Decimal'
    current_price: 'Decimal'
    current_nkd: 'Decimal | None'
    value: 'Decimal'
    instrument_uid: str

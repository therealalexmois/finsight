"""Value Object купона облигации."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from finsight_api.domain.value_objects.money import Money


@dataclass(frozen=True, slots=True, kw_only=True)
class BondCoupon:
    """Купон облигации (immutable событие/значение).

    Attributes:
        figi: FIGI облигации.
        coupon_date: Дата выплаты купона.
        coupon_number: Номер купона.
        fix_date: Дата фиксации (для флоатеров).
        pay_one_bond: Выплата на 1 облигацию.
        coupon_type: Тип купона (как строка; доменная нормализация может быть добавлена позже).
        coupon_start_date: Начало купонного периода.
        coupon_end_date: Конец купонного периода.
        coupon_period: Длительность периода (в днях/как в API).
    """

    figi: str
    coupon_date: 'datetime'
    coupon_number: int
    fix_date: 'datetime'
    pay_one_bond: 'Money'
    coupon_type: str
    coupon_start_date: 'datetime'
    coupon_end_date: 'datetime'
    coupon_period: int

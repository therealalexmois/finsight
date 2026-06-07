"""Value Object для денежных значений.

Используется для хранения денежных сумм с валютой без потери точности.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from decimal import Decimal


@dataclass(frozen=True, slots=True, kw_only=True)
class Money:
    """Денежная сумма.

    Attributes:
        currency: Код валюты (например, 'rub').
        amount: Сумма в валюте (Decimal для точности).
    """

    currency: str
    amount: 'Decimal'

"""Тип-значение типа инструмента.

Используется для нормализации строковых значений типа инструмента, приходящих
из внешних источников (например, SDK брокера), и для исключения "магических строк"
в домене и инфраструктурных мапперах.
"""

from enum import auto, StrEnum, unique


@unique
class InstrumentType(StrEnum):
    """Тип инструмента в портфеле.

    Attributes:
        BOND: Облигация.
        SHARE: Акция.
        ETF: Биржевой фонд.
        CURRENCY: Валюта.
        FUTURES: Фьючерс.
        OPTION: Опцион.
        SP: Структурная нота.
        UNSPECIFIED: Тип не определён или не распознан.
    """

    BOND = auto()
    SHARE = auto()
    ETF = auto()
    CURRENCY = auto()
    FUTURES = auto()
    OPTION = auto()
    SP = auto()
    UNSPECIFIED = auto()

    @classmethod
    def from_sdk(cls, value: str) -> 'InstrumentType':
        """Нормализует строковый тип инструмента из внешнего источника.

        Args:
            value: Строковое значение типа инструмента.

        Returns:
            InstrumentType: нормализованный тип инструмента.
        """
        normalized = (value or '').strip().lower()
        return cls(normalized) if normalized in cls._value2member_map_ else cls.UNSPECIFIED

"""Модуль содержит тип-значение ISIN с валидацией.

ISIN — международный идентификационный код ценной бумаги (12 символов, буквенно-цифровой).
"""

from dataclasses import dataclass

_ISIN_LENGTH = 12  # Длина ISIN-кода согласно стандарту ISO 6166


@dataclass(frozen=True)
class ISIN:
    """Тип-значение для ISIN с встроенной валидацией.

    ISIN (International Securities Identification Number) используется для уникальной идентификации ценных бумаг.

    Attributes:
        value: Строка длиной 12 символов, содержащая буквенно-цифровой код.
    """

    value: str

    def __post_init__(self) -> None:
        """Выполняет валидацию ISIN при создании объекта.

        Raises:
            ValueError: Если ISIN некорректного формата.
        """
        if len(self.value) != _ISIN_LENGTH or not self.value.isalnum():
            raise ValueError('Некорректный формат ISIN: должен содержать 12 буквенно-цифровых символов')

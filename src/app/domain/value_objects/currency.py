"""Модуль содержит тип-значение валюты.

Валюта представляет собой трёхбуквенный код в формате ISO 4217 (например, USD, EUR, RUB).
"""

from dataclasses import dataclass

_CURRENCY_CODE_LENGTH = 3  # Длина кода валюты по ISO 4217


@dataclass(frozen=True)
class Currency:
    """Тип-значение для валюты с валидацией по ISO 4217.

    Используется для указания валюты в финансовых операциях.

    Attributes:
        code: Код валюты в формате ISO 4217 (3 латинские буквы).
    """

    code: str

    def __post_init__(self) -> None:
        """Выполняет валидацию валютного кода.

        Raises:
            ValueError: Если код валюты не соответствует ISO 4217.
        """
        if len(self.code) != _CURRENCY_CODE_LENGTH or not self.code.isalpha():
            raise ValueError(f'Некорректный код валюты: должен содержать {_CURRENCY_CODE_LENGTH} буквы')

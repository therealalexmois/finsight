"""Модуль содержит тип-значение денежной суммы (Amount).

Amount представляет собой положительное число с фиксированной точностью.
"""

from dataclasses import dataclass

_MIN_AMOUNT = 0.0  # Минимально допустимая сумма (исключительно)


@dataclass(frozen=True)
class Amount:
    """Тип-значение для представления денежных сумм."""

    value: float

    def __post_init__(self) -> None:
        """Проверяет, что сумма положительна.

        Raises:
            ValueError: Если сумма отрицательная или ноль.
        """
        if self.value <= _MIN_AMOUNT:
            raise ValueError('Сумма должна быть положительным числом')

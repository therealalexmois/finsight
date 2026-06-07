"""Модуль содержит тип-значение PredictionDirection.

Показывает направление движения цены: рост, падение или нейтрально.
"""

from enum import auto, StrEnum, unique


@unique
class PredictionDirection(StrEnum):
    """Перечисление направлений движения цены актива."""

    UP = auto()
    DOWN = auto()
    NEUTRAL = auto()

    def is_growth(self) -> bool:
        """Проверяет, является ли направление прогнозом роста."""
        return self is PredictionDirection.UP

    def is_decline(self) -> bool:
        """Проверяет, является ли направление прогнозом падения."""
        return self is PredictionDirection.DOWN

    def is_neutral(self) -> bool:
        """Проверяет, является ли направление прогнозом нейтральным."""
        return self is PredictionDirection.NEUTRAL

"""Тесты для value object PredictionDirection."""

import pytest

from src.app.domain.value_objects.prediction_direction import PredictionDirection


@pytest.mark.unit
class TestPredictionDirection:
    """Тесты для перечисления PredictionDirection."""

    def test_is_growth__returns_true_for_up(self) -> None:
        """Должен возвращать True для роста."""
        assert PredictionDirection.UP.is_growth() is True

    def test_is_decline__returns_true_for_down(self) -> None:
        """Должен возвращать True для падения."""
        assert PredictionDirection.DOWN.is_decline() is True

    def test_is_neutral__returns_true_for_neutral(self) -> None:
        """Должен возвращать True для нейтрального направления."""
        assert PredictionDirection.NEUTRAL.is_neutral() is True

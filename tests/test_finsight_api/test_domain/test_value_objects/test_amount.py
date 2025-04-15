"""Тесты для value object Amount."""

import pytest

from src.finsight_api.domain.value_objects.amount import Amount


@pytest.mark.unit
class TestAmount:
    """Тесты для проверки корректности суммы."""

    @staticmethod
    def test_amount__valid_positive() -> None:
        """Должен успешно создавать положительное значение."""
        test_value = 99.99
        amt = Amount(test_value)
        assert amt.value == test_value

    @staticmethod
    @pytest.mark.parametrize('val', [0, -1, -123.45])
    def test_amount__non_positive_raises_value_error(val: float) -> None:
        """Должен выбрасывать ValueError для нуля и отрицательных значений."""
        with pytest.raises(ValueError, match='Сумма должна быть положительным числом'):
            Amount(val)

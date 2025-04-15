"""Тесты для value object TransactionType."""

import pytest

from src.finsight_api.domain.value_objects.transaction_type import TransactionType


@pytest.mark.unit
class TestTransactionType:
    """Тесты для перечисления TransactionType."""

    @staticmethod
    def test_enum__values() -> None:
        """Должен содержать значения BUY и SELL."""
        assert TransactionType.BUY.value == 'buy'
        assert TransactionType.SELL.value == 'sell'

"""Тесты для value object Currency."""

import pytest

from finsight_api.domain.value_objects.currency import Currency


@pytest.mark.unit
class TestCurrency:
    """Тесты для проверки корректности и валидации валюты."""

    def test_currency__valid_code(self) -> None:
        """Должен успешно создавать объект с корректным кодом валюты."""
        cur = Currency('usd')
        assert cur.code == 'USD'

    @pytest.mark.parametrize('code', ['', 'EU', 'USDE', '12$', 'RU1'])
    def test_currency__invalid_code_raises_value_error(self, code: str) -> None:
        """Должен выбрасывать ValueError при некорректном коде валюты."""
        with pytest.raises(ValueError, match='Некорректный код валюты'):
            Currency(code)

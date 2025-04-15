"""Тесты для value object ISIN."""

import pytest

from src.finsight_api.domain.value_objects.isin import ISIN


@pytest.mark.unit
class TestISIN:
    """Тесты для проверки корректности и валидации ISIN."""

    @staticmethod
    def test_isin__valid_code() -> None:
        """Должен успешно создавать корректный ISIN."""
        isin = ISIN('RU000A0JX0J2')
        assert isin.value == 'RU000A0JX0J2'

    @staticmethod
    @pytest.mark.parametrize('code', ['', '123', 'RU@000JX0J2', 'RU000A0JX0J23'])
    def test_isin__invalid_code_raises_value_error(code: str) -> None:
        """Должен выбрасывать ValueError при некорректном формате ISIN."""
        with pytest.raises(ValueError, match='Некорректный формат ISIN'):
            ISIN(code)

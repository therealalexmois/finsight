"""Юнит-тесты для DTO свечей Tinkoff Invest API."""

from datetime import datetime, UTC

import pytest
from tinkoff.invest import HistoricCandle, Quotation

from src.app.infrastructure.dto.tinkoff.candle_dto import CandleDTO


@pytest.mark.unit
class TestCandleDTO:
    @staticmethod
    @pytest.mark.parametrize(
        'units_open, nano_open, units_close, nano_close, units_high, nano_high, units_low, nano_low, volume',
        [
            (100, 123_000_000, 105, 456_000_000, 110, 789_000_000, 95, 987_000_000, 1000),
            (10, 0, 15, 0, 20, 0, 5, 0, 500),
            (0, 999_999_999, 0, 111_111_111, 0, 222_222_222, 0, 333_333_333, 0),
        ],
    )
    def test_from_sdk__should_convert_sdk_candle_to_dto(  # noqa: PLR0913
        units_open: int,
        nano_open: int,
        units_close: int,
        nano_close: int,
        units_high: int,
        nano_high: int,
        units_low: int,
        nano_low: int,
        volume: int,
    ) -> None:
        """Должен корректно преобразовывать свечу Tinkoff SDK в DTO."""
        candle = HistoricCandle(
            time=datetime(2024, 4, 1, tzinfo=UTC),
            volume=volume,
            is_complete=True,
            open=Quotation(units=units_open, nano=nano_open),
            close=Quotation(units=units_close, nano=nano_close),
            high=Quotation(units=units_high, nano=nano_high),
            low=Quotation(units=units_low, nano=nano_low),
        )

        dto = CandleDTO.from_sdk(candle)

        assert dto.time == candle.time
        assert dto.volume == volume
        assert dto.open == units_open + nano_open / 1e9
        assert dto.close == units_close + nano_close / 1e9
        assert dto.high == units_high + nano_high / 1e9
        assert dto.low == units_low + nano_low / 1e9

    @staticmethod
    def test_to_model__should_convert_dto_to_domain_model() -> None:
        """Должен корректно преобразовывать DTO в доменную модель."""
        dto = CandleDTO(
            time=datetime(2024, 4, 1, tzinfo=UTC),
            open=100.123,
            close=105.456,
            high=110.789,
            low=95.987,
            volume=1000,
        )

        model = dto.to_model()

        assert model.time == dto.time
        assert model.open == dto.open
        assert model.close == dto.close
        assert model.high == dto.high
        assert model.low == dto.low
        assert model.volume == dto.volume

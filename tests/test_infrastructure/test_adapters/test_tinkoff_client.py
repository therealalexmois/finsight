"""Интеграционные тесты клиента Tinkoff Invest API."""

from datetime import date, timedelta
from typing import TYPE_CHECKING

import pytest

from src.app.domain.models.account_summary import AccountSummaryModel
from src.app.domain.models.candle import CandleModel

if TYPE_CHECKING:
    from src.app.application.ports.gateways.tinkoff_gateway import TinkoffInvestGateway


@pytest.mark.integration
class TestTinkoffInvestApiClient:
    @staticmethod
    @pytest.mark.asyncio
    async def test_get_account_summary__ok(tinkoff_gateway: 'TinkoffInvestGateway') -> None:
        """Должен возвращать сводную информацию о счёте в виде доменной модели AccountSummaryModel."""
        summary = await tinkoff_gateway.get_account_summary()

        assert isinstance(summary, AccountSummaryModel)
        assert isinstance(summary.accounts_count, int)
        assert all(isinstance(aid, str) for aid in summary.account_ids)

    @staticmethod
    @pytest.mark.asyncio
    async def test_get_candles_by_isin__ok(tinkoff_gateway: 'TinkoffInvestGateway') -> None:
        """Должен возвращать список свечей CandleModel по заданному ISIN за последние 7 дней."""
        isin = 'RU000A0JX0J2'
        today = date.today()
        week_ago = today - timedelta(days=7)

        candles = await tinkoff_gateway.get_candles_by_isin(isin, week_ago, today)

        assert isinstance(candles, list)
        assert all(isinstance(c, CandleModel) for c in candles)

    @staticmethod
    @pytest.mark.asyncio
    async def test_verify_token__should_return_true_if_token_is_valid(tinkoff_gateway: 'TinkoffInvestGateway') -> None:
        """Должен возвращать True, если токен Tinkoff Invest API валиден."""
        result = await tinkoff_gateway.verify_token(debug=True)

        assert result is True

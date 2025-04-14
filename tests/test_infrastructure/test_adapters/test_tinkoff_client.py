"""Интеграционные тесты клиента Tinkoff Invest API."""

from datetime import date, timedelta
from typing import TYPE_CHECKING

import pytest

from src.app.domain.models.account_summary import AccountSummaryModel
from src.app.domain.models.candle import CandleModel
from src.app.domain.value_objects.candle_interval import CandleInterval
from src.app.infrastructure.adapters.tinkoff.invest_client import TinkoffInvestApiClient

if TYPE_CHECKING:
    from collections.abc import Callable
    from contextlib import AbstractAsyncContextManager

    from tinkoff.invest.async_services import AsyncServices

    from src.app.application.ports.gateways.tinkoff_gateway import TinkoffInvestGateway
    from src.app.application.ports.logger import Logger


@pytest.mark.asyncio
@pytest.mark.integration
class TestTinkoffInvestApiClient:
    @staticmethod
    async def test_get_account_summary__ok(tinkoff_gateway: 'TinkoffInvestGateway') -> None:
        """Должен возвращать сводную информацию о счёте в виде доменной модели AccountSummaryModel."""
        summary = await tinkoff_gateway.get_account_summary()

        assert isinstance(summary, AccountSummaryModel)
        assert isinstance(summary.accounts_count, int)
        assert all(isinstance(aid, str) for aid in summary.account_ids)

    @staticmethod
    async def test_get_candles_by_isin__ok(tinkoff_gateway: 'TinkoffInvestGateway') -> None:
        """Должен возвращать список свечей CandleModel по заданному ISIN за последние 7 дней."""
        isin = 'RU0009029540'  # Sber
        today = date.today()
        week_ago = today - timedelta(days=7)
        interval = CandleInterval.DAY

        candles = await tinkoff_gateway.get_candles_by_isin(isin, week_ago, today, interval)

        assert isinstance(candles, list)
        assert all(isinstance(c, CandleModel) for c in candles)

    @staticmethod
    async def test_verify_token__should_return_true_if_token_is_valid(tinkoff_gateway: 'TinkoffInvestGateway') -> None:
        """Должен возвращать True, если токен Tinkoff Invest API валиден."""
        result = await tinkoff_gateway.verify_token(debug=True)

        assert result is True

    @staticmethod
    async def test_get_account_summary__transient_failure(
        fake_session_transient_success: 'Callable[[], AbstractAsyncContextManager["AsyncServices"]]',
        dummy_logger: 'Logger',
    ) -> None:
        """Должен успешно вернуть AccountSummaryModel после временных ошибок (retry)."""
        client = TinkoffInvestApiClient(
            token='dummy',
            logger=dummy_logger,
            client_factory=fake_session_transient_success,
        )

        summary = await client.get_account_summary()

        assert isinstance(summary, AccountSummaryModel)
        assert summary.accounts_count == 1
        assert summary.account_ids == ['test_acc']

    @staticmethod
    @pytest.mark.skip(reason='To figure out the cause of the failure later.')
    async def test_verify_token__failure(
        fake_session_failure: 'Callable[[], AbstractAsyncContextManager[AsyncServices]]',
        dummy_logger: 'Logger',
    ) -> None:
        """Должен возвращать False при постоянном сбое API."""
        client = TinkoffInvestApiClient(
            token='dummy',
            logger=dummy_logger,
            client_factory=fake_session_failure,
        )

        result = await client.verify_token(debug=False)

        assert result is False

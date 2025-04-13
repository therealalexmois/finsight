"""Адаптер клиента Tinkoff Invest API с использованием официального SDK."""

from collections.abc import Callable
from datetime import date, datetime
from typing import TYPE_CHECKING

from tinkoff.invest import (
    CandleInterval,
    GetAccountsResponse,
    GetUserTariffResponse,
    RequestError,
)

from src.app.application.ports.gateways.tinkoff_gateway import TinkoffInvestGateway
from src.app.domain.models.portfolio import PortfolioModel
from src.app.infrastructure.adapters.tinkoff.factories import async_client_factory
from src.app.infrastructure.dto.tinkoff.account_summary_dto import AccountSummaryDTO
from src.app.infrastructure.dto.tinkoff.candle_dto import CandleDTO
from src.app.infrastructure.dto.tinkoff.portfolio_dto import PortfolioPositionDTO
from src.app.infrastructure.utils.retry import retry_on_exception

if TYPE_CHECKING:
    from collections.abc import Sequence
    from contextlib import AbstractAsyncContextManager

    from tinkoff.invest.async_services import AsyncServices

    from src.app.application.ports.logger import Logger
    from src.app.domain.models.account_summary import AccountSummaryModel
    from src.app.domain.models.candle import CandleModel


AsyncClientFactory = Callable[[], 'AbstractAsyncContextManager[AsyncServices]']


class TinkoffInvestApiClient(TinkoffInvestGateway):
    """Реализация клиента Tinkoff Invest API."""

    def __init__(
        self,
        token: str,
        logger: 'Logger',
        client_factory: 'AsyncClientFactory | None' = None,
    ) -> None:
        """Инициализирует клиента с заданным токеном.

        Args:
            token: Токен авторизации в Tinkoff Invest API.
            logger: Логгер приложения.
            client_factory: Фабрика для создания клиента. Если не задана, используется стандартный AsyncClient.
        """
        self._token = token
        self._logger = logger
        self._client_factory = client_factory or (lambda: async_client_factory(self._token))

    @retry_on_exception(exceptions=(RequestError,))
    async def get_account_summary(self) -> 'AccountSummaryModel':  # type: ignore[override]
        """Возвращает краткую информацию о счетах пользователя.

        Returns:
            Доменная модель со сводной информацией о счетах.
        """
        async with self._client_factory() as client:
            accounts = await client.users.get_accounts()
            return AccountSummaryDTO.from_sdk(accounts.accounts).to_model()

    @retry_on_exception(exceptions=(RequestError,))
    async def get_candles_by_isin(self, isin: str, from_date: date, to_date: date) -> 'Sequence[CandleModel]':  # type: ignore[override]
        """Возвращает исторические котировки по ISIN.

        Args:
            isin: ISIN-идентификатор ценной бумаги.
            from_date: Начальная дата периода.
            to_date: Конечная дата периода.

        Returns:
            Список словарей с информацией о свечах.
        """
        async with self._client_factory() as client:
            figi = await self._resolve_figi(client, isin)
            response = await client.market_data.get_candles(
                figi=figi,
                from_=datetime.combine(from_date, datetime.min.time()),
                to=datetime.combine(to_date, datetime.min.time()),
                interval=CandleInterval.CANDLE_INTERVAL_DAY,
            )
            return [CandleDTO.from_sdk(candle).to_model() for candle in response.candles]

    async def _resolve_figi(self, client: 'AsyncServices', isin: str) -> str:
        """Получает FIGI по ISIN.

        Args:
            client: Клиент Tinkoff Invest API.
            isin: ISIN-идентификатор.

        Returns:
            FIGI-идентификатор.
        """
        instrument = await client.instruments.find_instrument(query=isin)
        return instrument.instruments[0].figi

    @retry_on_exception(exceptions=(RequestError,))
    async def get_portfolio(self, account_id: str) -> 'PortfolioModel':  # type: ignore[override]
        """Получает текущий портфель по идентификатору счёта.

        Args:
            account_id: Идентификатор счёта.

        Returns:
            Модель PortfolioModel с информацией о бумагах, позициях и их стоимости.
        """
        async with self._client_factory() as client:
            response = await client.operations.get_portfolio(account_id=account_id)

            positions = [PortfolioPositionDTO.from_sdk(p).to_model() for p in response.positions]
            total_value = float(sum(p.value for p in positions))

            return PortfolioModel(
                account_id=account_id,
                total_value=total_value,
                currency='—',
                positions=positions,
            )

    async def verify_token(self, debug: bool = False) -> bool:
        """Проверяет валидность токена Tinkoff API.

        Выполняет запрос получения счетов. При включенном debug выводит
        дополнительную отладочную информацию: лимиты, тарифы, user info.

        Args:
            debug: Флаг включения отладочного режима.

        Returns:
            True — токен действителен, False — нет.
        """
        try:
            async with self._client_factory() as client:
                accounts = await client.users.get_accounts()
                if debug:
                    await self._log_debug_info(client, accounts)
            return True
        except Exception as ex:
            self._logger.warning(f'Ошибка при проверке токена: {ex!r}')
            return False

    async def _log_debug_info(self, client: 'AsyncServices', accounts: GetAccountsResponse) -> None:
        """Выводит расширенную отладочную информацию о текущем токене.

        Включает информацию о счетах, тарифных лимитах и данных пользователя.
        Используется в debug-режиме для диагностики состояния API-доступа.

        Args:
            client: Асинхронный клиент Tinkoff Invest API.
            accounts: Ответ от метода get_accounts, содержащий список счетов.
        """
        self._logger.info('Начало отладочной информации токена')

        try:
            self._logger.info('Счета клиента:')
            for account in accounts.accounts:
                self._logger.info(f'• {account}')

            tariff: GetUserTariffResponse = await client.users.get_user_tariff()

            self._logger.info('Тарифные лимиты (unary):')
            for unary_limit in tariff.unary_limits:
                self._logger.info(f'- {unary_limit.limit_per_minute}/мин: {", ".join(unary_limit.methods)}')

            self._logger.info('Лимиты потоков (stream):')
            for stream_limit in tariff.stream_limits:
                self._logger.info(f'- {stream_limit.limit} соединений: {", ".join(stream_limit.streams)}')

            user_info = await client.users.get_info()
            self._logger.info(f'Информация о пользователе: {user_info}')
        except Exception as ex:
            self._logger.warning(f'Ошибка при выводе отладочной информации: {ex!r}')
        self._logger.info('Отладочная проверка завершена успешно')

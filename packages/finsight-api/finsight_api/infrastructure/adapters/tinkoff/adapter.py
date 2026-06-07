"""Адаптер клиента Tinkoff Invest API с использованием официального SDK."""

from collections.abc import Callable, Collection
from datetime import date, datetime
from typing import TYPE_CHECKING

from t_tech.invest import (
    AioRequestError,
    BondsResponse,
    GetAccountsResponse,
    GetUserTariffResponse,
    InstrumentIdType,
)

from finsight_api.application.ports.tinkoff import TinkoffInvestPort
from finsight_api.infrastructure.adapters.tinkoff.mappers import map_candle_interval_to_sdk

from .mappers import (
    map_accounts_from_sdk,
    map_bond_from_sdk,
    map_brand_from_sdk,
    map_candle_from_sdk,
    map_coupon_from_sdk,
    map_order_book_from_sdk,
    map_portfolio_from_sdk,
)

if TYPE_CHECKING:
    from collections.abc import Sequence
    from contextlib import AbstractAsyncContextManager

    from t_tech.invest.async_services import AsyncServices

    from finsight_api.application.ports.logger import LoggerPort
    from finsight_api.domain.entities.account import AccountEntity
    from finsight_api.domain.entities.bond import BondEntity
    from finsight_api.domain.entities.brand import BrandEntity
    from finsight_api.domain.entities.candle import CandleEntity
    from finsight_api.domain.entities.portfolio import PortfolioEntity
    from finsight_api.domain.value_objects.bond_coupon import BondCoupon
    from finsight_api.domain.value_objects.candle_interval import CandleInterval
    from finsight_api.domain.value_objects.isin import ISIN
    from finsight_api.domain.value_objects.order_book import OrderBook


AsyncClientFactory = Callable[[], 'AbstractAsyncContextManager[AsyncServices]']


class TinkoffInvestAdapter(TinkoffInvestPort):
    """Реализация порта TinkoffInvestPort поверх официального async SDK Tinkoff Invest.

    На каждый вызов открывает сессию клиента через client_factory и маппит ответы SDK
    в доменные сущности и value objects. Токен используется в режиме read-only:
    торговые поручения недоступны.
    """

    def __init__(
        self,
        token: str,
        client_factory: 'AsyncClientFactory',
        logger: 'LoggerPort',
    ) -> None:
        """Инициализирует адаптер с заданным токеном.

        Args:
            token: Токен авторизации в Tinkoff Invest API.
            client_factory: Фабрика для создания асинхронного клиента SDK.
            logger: Логгер приложения.
        """
        self._token = token
        self._client_factory = client_factory
        self._logger = logger

    async def get_accounts(self) -> Collection['AccountEntity']:
        """Возвращает список счетов пользователя.

        Returns:
            Доменные сущности счетов.
        """
        async with self._client_factory() as client:
            accounts = await client.users.get_accounts()
            return map_accounts_from_sdk(accounts.accounts)

    async def get_candles_by_isin(
        self,
        isin: str,
        from_date: date,
        to_date: date,
        interval: 'CandleInterval',
    ) -> 'Sequence[CandleEntity]':
        """Возвращает историю котировок по ISIN за указанный период и интервал.

        Args:
            isin: ISIN-идентификатор ценной бумаги.
            from_date: Начальная дата периода.
            to_date: Конечная дата периода.
            interval: Интервал свечей.

        Returns:
            Sequence[CandleModel]: список доменных свечей.
        """
        async with self._client_factory() as client:
            figi = await self._get_figi_by_isin(client, isin)
            sdk_interval = map_candle_interval_to_sdk(interval)

            response = await client.market_data.get_candles(
                figi=figi,
                from_=datetime.combine(from_date, datetime.min.time()),
                to=datetime.combine(to_date, datetime.min.time()),
                interval=sdk_interval,
            )

            return [map_candle_from_sdk(c, figi=figi, interval=interval) for c in response.candles]

    async def _get_figi_by_isin(
        self,
        client: 'AsyncServices',
        isin: str,
    ) -> str:
        """Получает FIGI по ISIN.

        Args:
            client: Асинхронный клиент Tinkoff Invest API.
            isin: ISIN-идентификатор.

        Returns:
            str: FIGI-идентификатор.

        Raises:
            ValueError: Если инструмент по ISIN не найден.
        """
        instrument = await client.instruments.find_instrument(query=isin)

        if not instrument.instruments:
            raise ValueError(f'Инструмент не найден по ISIN: {isin}')

        return instrument.instruments[0].figi

    async def get_portfolio(self, account_id: str) -> 'PortfolioEntity':
        """Получает текущий портфель по идентификатору счёта.

        Args:
            account_id: Идентификатор счёта.

        Returns:
            PortfolioModel: доменная модель портфеля.
        """
        async with self._client_factory() as client:
            response = await client.operations.get_portfolio(account_id=account_id)
            return map_portfolio_from_sdk(response, account_id=account_id)

    async def get_bond_by_figi(self, figi: str) -> 'BondEntity':
        """Возвращает метаданные облигации по FIGI.

        Args:
            figi: FIGI-идентификатор облигации.

        Returns:
            Bond: доменная сущность облигации.
        """
        async with self._client_factory() as client:
            response = await client.instruments.bond_by(
                id=figi,
                id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI,
            )
            return map_bond_from_sdk(response.instrument)

    async def get_bond_by_isin(self, isin: 'ISIN') -> 'BondEntity | None':
        """Возвращает метаданные облигации по ISIN.

        Args:
            isin: ISIN облигации.

        Returns:
            Найденная облигация или None, если SDK вернул ошибку AioRequestError
            (причина пишется в лог).
        """
        async with self._client_factory() as client:
            try:
                response = await client.instruments.bond_by(
                    id=isin.value,
                    id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_TICKER,
                    class_code='TQCB',
                )
                # response = await client.instruments.find_instrument(
                #     query=isin.value,
                #     instrument_kind=InstrumentType.INSTRUMENT_TYPE_BOND,
                # )
                return response
                # return map_bond_from_sdk(response.instrument)
            except AioRequestError as exc:
                metadata = exc.metadata

                self._logger.error(
                    f'Failed to resolve bond by ISIN directly: {exc!r}',
                    isin=isin.value,
                    message=getattr(metadata, 'message', None),
                    tracking_id=getattr(metadata, 'tracking_id', None),
                    ratelimit_limit=getattr(metadata, 'ratelimit_limit', None),
                    ratelimit_remaining=getattr(metadata, 'ratelimit_remaining', None),
                    ratelimit_reset=getattr(metadata, 'ratelimit_reset', None),
                )
                return None

    async def get_bonds(self) -> BondsResponse:
        """Запрашивает список облигаций через instruments.bonds()."""
        async with self._client_factory() as client:
            response = await client.instruments.bonds()
            return len(response)

    async def get_bond_coupons(
        self,
        *,
        figi: str,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list['BondCoupon']:
        """Возвращает список купонов по облигации.

        Args:
            figi: FIGI облигации.
            from_date: Начало диапазона (включительно). Если None — без нижней границы.
            to_date: Конец диапазона (включительно). Если None — без верхней границы.

        Returns:
            list[BondCoupon]: список купонов (VO).
        """
        async with self._client_factory() as client:
            from_dt = datetime.combine(from_date, datetime.min.time()) if from_date else None
            to_dt = datetime.combine(to_date, datetime.min.time()) if to_date else None

            response = await client.instruments.get_bond_coupons(
                figi=figi,
                from_=from_dt,
                to=to_dt,
            )

            return [map_coupon_from_sdk(c) for c in response.events]

    async def get_order_book(self, *, figi: str, depth: int = 1) -> 'OrderBook':
        """Возвращает стакан по инструменту (snapshot).

        Args:
            figi: FIGI инструмента.
            depth: Глубина стакана.

        Returns:
            OrderBook: доменный снимок стакана (VO).
        """
        async with self._client_factory() as client:
            response = await client.market_data.get_order_book(figi=figi, depth=depth)
            return map_order_book_from_sdk(response)

    async def get_brands(self) -> list['BrandEntity']:
        """Возвращает список брендов.

        Returns:
            list[Brand]: доменные сущности Brand.
        """
        async with self._client_factory() as client:
            response = await client.instruments.get_brands()
            return [map_brand_from_sdk(b) for b in response.brands]

    async def _verify_token(self, debug: bool = False) -> bool:
        """Проверяет валидность токена Tinkoff API.

        Args:
            debug: Флаг включения отладочного режима.

        Returns:
            bool: True — токен действителен, False — нет.
        """
        try:
            async with self._client_factory() as client:
                accounts = await client.users.get_accounts()
                if debug:
                    await self._log_debug_info(client, accounts)
            return True
        except Exception as exec:
            self._logger.warning(f'Ошибка при проверке токена: {exec!r}')
            return False

    async def _log_debug_info(self, client: 'AsyncServices', accounts: GetAccountsResponse) -> None:
        """Выводит расширенную отладочную информацию о текущем токене.

        Args:
            client: Асинхронный клиент Tinkoff Invest API.
            accounts: Ответ get_accounts со списком счетов.
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

"""Мапперы и утилиты преобразования SDK-объектов Tinkoff Invest в доменные сущности.

Модуль содержит функции конвертации числовых типов SDK (units/nano, MoneyValue,
Quotation) в Decimal и доменные value objects, а также мапперы SDK-сущностей
(Tinkoff Invest) в доменные модели FinSight.
"""

from collections.abc import Collection
from decimal import Decimal
from typing import TYPE_CHECKING

from t_tech.invest import CandleInterval as SDKCandleInterval

from finsight_api.domain.entities.account import AccountEntity
from finsight_api.domain.entities.bond import BondEntity
from finsight_api.domain.entities.brand import BrandEntity
from finsight_api.domain.entities.candle import CandleEntity
from finsight_api.domain.entities.portfolio import PortfolioEntity
from finsight_api.domain.value_objects.account_status import AccountStatus
from finsight_api.domain.value_objects.account_type import AccountType
from finsight_api.domain.value_objects.bond_coupon import BondCoupon
from finsight_api.domain.value_objects.candle_interval import CandleInterval
from finsight_api.domain.value_objects.instrument_type import InstrumentType
from finsight_api.domain.value_objects.money import Money
from finsight_api.domain.value_objects.order_book import OrderBook, OrderBookLevel
from finsight_api.domain.value_objects.portfolio_position import PortfolioPosition
from finsight_api.domain.value_objects.risk_level import RiskLevel

if TYPE_CHECKING:
    from t_tech.invest import Account as SdkAccount
    from t_tech.invest import Bond as SdkBond
    from t_tech.invest import Brand as SdkBrand
    from t_tech.invest import Coupon as SdkCoupon
    from t_tech.invest import GetOrderBookResponse, MoneyValue, Quotation
    from t_tech.invest import HistoricCandle as SdkHistoricCandle
    from t_tech.invest import PortfolioPosition as SdkPortfolioPosition
    from t_tech.invest import PortfolioResponse as SdkPortfolioResponse


_NANO_FACTOR = Decimal('1_000_000_000')


def _decimal_from_units_nano(units: int, nano: int) -> Decimal:
    """Конвертирует пару (units, nano) в Decimal без потери точности.

    Args:
        units: Целая часть значения.
        nano: Дробная часть в миллиардных долях (10^-9).

    Returns:
        Decimal-представление значения units + nano / 1e9.
    """
    return Decimal(units) + (Decimal(nano) / _NANO_FACTOR)


def _money_value_to_decimal(value: 'MoneyValue') -> Decimal:
    """Преобразует SDK MoneyValue в Decimal.

    Args:
        value: Объект MoneyValue из Tinkoff Invest SDK.

    Returns:
        Денежное значение в виде Decimal.
    """
    return _decimal_from_units_nano(int(value.units), int(value.nano))


def _quotation_to_decimal(value: 'Quotation') -> Decimal:
    """Преобразует SDK Quotation в Decimal.

    Args:
        value: Объект Quotation из Tinkoff Invest SDK.

    Returns:
        Числовое значение котировки в виде Decimal.
    """
    return _decimal_from_units_nano(int(value.units), int(value.nano))


def _money_from_sdk(value: 'MoneyValue') -> Money:
    """Конвертирует SDK MoneyValue в доменный value object Money.

    Args:
        value: Объект MoneyValue из Tinkoff Invest SDK.

    Returns:
        Доменный объект Money с валютой и числовым значением.
    """
    return Money(currency=value.currency, amount=_money_value_to_decimal(value))


def map_accounts_from_sdk(accounts: 'Collection[SdkAccount]') -> Collection[AccountEntity]:
    """Преобразует список SDK Account в доменные сущности AccountEntity.

    Args:
        accounts: Счета из Tinkoff Invest SDK.

    Returns:
        Уникальные доменные сущности счетов.
    """
    return tuple(
        AccountEntity(
            id=a.id,
            type=AccountType(int(a.type)),
            name=a.name,
            status=AccountStatus(int(a.status)),
        )
        for a in accounts
    )


def map_candle_from_sdk(
    candle: 'SdkHistoricCandle',
    *,
    figi: str,
    interval: CandleInterval,
) -> CandleEntity:
    """Преобразует SDK HistoricCandle в доменную сущность CandleEntity.

    Args:
        candle: Свеча из Tinkoff Invest SDK.
        figi: FIGI инструмента.
        interval: Доменный интервал свечи.

    Returns:
        Доменная сущность CandleEntity.
    """
    return CandleEntity(
        time=candle.time,
        open=float(candle.open.units) + candle.open.nano / 1e9,
        close=float(candle.close.units) + candle.close.nano / 1e9,
        high=float(candle.high.units) + candle.high.nano / 1e9,
        low=float(candle.low.units) + candle.low.nano / 1e9,
        volume=candle.volume,
        figi=figi,
        interval=interval,
    )


def map_portfolio_position_from_sdk(position: 'SdkPortfolioPosition') -> PortfolioPosition:
    """Преобразует SDK PortfolioPosition в доменный VO PortfolioPosition.

    Args:
        position: Позиция портфеля из Tinkoff Invest SDK.

    Returns:
        Доменный VO PortfolioPosition.
    """
    quantity = _quotation_to_decimal(position.quantity)
    current_price = _money_value_to_decimal(position.current_price)
    current_nkd = _money_value_to_decimal(position.current_nkd)

    instrument_type = InstrumentType.from_sdk(position.instrument_type)

    normalized_current_nkd = None
    if instrument_type == InstrumentType.BOND or current_nkd != Decimal(0):
        normalized_current_nkd = current_nkd

    return PortfolioPosition(
        figi=position.figi,
        instrument_type=instrument_type,
        quantity=quantity,
        expected_yield=_quotation_to_decimal(position.expected_yield),
        average_position_price=_money_value_to_decimal(position.average_position_price),
        current_price=current_price,
        current_nkd=normalized_current_nkd,
        value=current_price * quantity,
        instrument_uid=position.instrument_uid,
    )


def map_bond_from_sdk(bond: 'SdkBond') -> BondEntity:
    """Преобразует SDK Bond в доменную сущность Bond.

    Args:
        bond: Объект Bond из Tinkoff Invest SDK.

    Returns:
        Доменная сущность BondEntity.
    """
    aci = _money_from_sdk(bond.aci_value) if getattr(bond, 'aci_value', None) else None

    return BondEntity(
        figi=bond.figi,
        uid=bond.uid,
        isin=bond.isin,
        name=bond.name,
        currency=bond.currency,
        sector=bond.sector,
        risk_level=RiskLevel(bond.risk_level),
        coupon_quantity_per_year=bond.coupon_quantity_per_year,
        maturity_date=bond.maturity_date,
        nominal=_money_from_sdk(bond.nominal),
        aci_value=aci,
        class_code=bond.class_code,
        issue_size=int(bond.issue_size),
        issue_size_plan=int(bond.issue_size_plan),
        floating_coupon_flag=bond.floating_coupon_flag,
        amortization_flag=bond.amortization_flag,
        liquidity_flag=bond.liquidity_flag,
    )


def map_coupon_from_sdk(coupon: 'SdkCoupon') -> BondCoupon:
    """Преобразует SDK Coupon в доменный value object BondCoupon.

    Args:
        coupon: Объект Coupon из Tinkoff Invest SDK.

    Returns:
        Доменный объект BondCoupon.
    """
    return BondCoupon(
        figi=coupon.figi,
        coupon_date=coupon.coupon_date,
        coupon_number=int(coupon.coupon_number),
        fix_date=coupon.fix_date,
        pay_one_bond=_money_from_sdk(coupon.pay_one_bond),
        coupon_type=str(coupon.coupon_type),
        coupon_start_date=coupon.coupon_start_date,
        coupon_end_date=coupon.coupon_end_date,
        coupon_period=int(coupon.coupon_period),
    )


def map_order_book_from_sdk(response: 'GetOrderBookResponse') -> OrderBook:
    """Преобразует SDK GetOrderBookResponse в доменный value object OrderBook.

    Args:
        response: Ответ GetOrderBookResponse из Tinkoff Invest SDK.

    Returns:
        Доменный объект OrderBook с уровнями bid/ask и ценами.
    """
    bids = [
        OrderBookLevel(
            price=Money(currency='rub', amount=_quotation_to_decimal(o.price)),
            quantity=int(o.quantity),
        )
        for o in response.bids
    ]
    asks = [
        OrderBookLevel(
            price=Money(currency='rub', amount=_quotation_to_decimal(o.price)),
            quantity=int(o.quantity),
        )
        for o in response.asks
    ]

    last_price = (
        Money(currency='rub', amount=_quotation_to_decimal(response.last_price)) if response.last_price else None
    )
    close_price = (
        Money(currency='rub', amount=_quotation_to_decimal(response.close_price)) if response.close_price else None
    )

    return OrderBook(
        figi=response.figi,
        depth=int(response.depth),
        bids=bids,
        asks=asks,
        last_price=last_price,
        close_price=close_price,
        timestamp=response.orderbook_ts if getattr(response, 'orderbook_ts', None) else None,
    )


def map_brand_from_sdk(brand: 'SdkBrand') -> BrandEntity:
    """Преобразует SDK Brand в доменную сущность Brand.

    Args:
        brand: Объект Brand из Tinkoff Invest SDK.

    Returns:
        Доменная сущность BrandEntity.
    """
    return BrandEntity(
        uid=brand.uid,
        name=brand.name,
        description=brand.description,
        info=brand.info,
        company=brand.company,
        sector=brand.sector,
        country_of_risk=brand.country_of_risk,
        country_of_risk_name=brand.country_of_risk_name,
    )


def map_candle_interval_to_sdk(interval: CandleInterval) -> SDKCandleInterval:
    """Преобразует доменный интервал в соответствующий интервал SDK.

    Args:
        interval: Интервал из бизнес-домена.

    Returns:
        Интервал SDK Tinkoff.
    """
    return {
        CandleInterval.MIN_1: SDKCandleInterval.CANDLE_INTERVAL_1_MIN,
        CandleInterval.MIN_2: SDKCandleInterval.CANDLE_INTERVAL_2_MIN,
        CandleInterval.MIN_3: SDKCandleInterval.CANDLE_INTERVAL_3_MIN,
        CandleInterval.MIN_5: SDKCandleInterval.CANDLE_INTERVAL_5_MIN,
        CandleInterval.MIN_10: SDKCandleInterval.CANDLE_INTERVAL_10_MIN,
        CandleInterval.MIN_15: SDKCandleInterval.CANDLE_INTERVAL_15_MIN,
        CandleInterval.MIN_30: SDKCandleInterval.CANDLE_INTERVAL_30_MIN,
        CandleInterval.HOUR: SDKCandleInterval.CANDLE_INTERVAL_HOUR,
        CandleInterval.HOUR_2: SDKCandleInterval.CANDLE_INTERVAL_2_HOUR,
        CandleInterval.HOUR_4: SDKCandleInterval.CANDLE_INTERVAL_4_HOUR,
        CandleInterval.DAY: SDKCandleInterval.CANDLE_INTERVAL_DAY,
        CandleInterval.WEEK: SDKCandleInterval.CANDLE_INTERVAL_WEEK,
        CandleInterval.MONTH: SDKCandleInterval.CANDLE_INTERVAL_MONTH,
    }[interval]


def map_portfolio_from_sdk(response: 'SdkPortfolioResponse', *, account_id: str) -> 'PortfolioEntity':
    """Преобразует ответ SDK get_portfolio в доменную сущность PortfolioEntity.

    Args:
        response: Ответ Tinkoff Invest SDK от operations.get_portfolio.
        account_id: Идентификатор счета, для которого запрошен портфель.

    Returns:
        PortfolioEntity: доменная сущность портфеля.
    """
    positions = [map_portfolio_position_from_sdk(p) for p in response.positions]

    total_amount_shares = _money_value_to_decimal(response.total_amount_shares)
    total_amount_bonds = _money_value_to_decimal(response.total_amount_bonds)
    total_amount_etf = _money_value_to_decimal(response.total_amount_etf)
    total_amount_futures = _money_value_to_decimal(response.total_amount_futures)
    total_value = _money_value_to_decimal(response.total_amount_portfolio)
    cash_balance = _money_value_to_decimal(response.total_amount_currencies)
    currency = response.total_amount_portfolio.currency

    return PortfolioEntity(
        account_id=account_id,
        total_amount_shares=total_amount_shares,
        total_amount_bonds=total_amount_bonds,
        total_amount_etf=total_amount_etf,
        total_amount_futures=total_amount_futures,
        total_value=total_value,
        cash_balance=cash_balance,
        currency=currency,
        positions=positions,
    )

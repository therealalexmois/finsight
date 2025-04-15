"""Маппер интервалов свечей между доменной моделью и SDK Tinkoff."""

from tinkoff.invest import CandleInterval as SDKCandleInterval

from src.finsight_api.domain.value_objects.candle_interval import CandleInterval


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

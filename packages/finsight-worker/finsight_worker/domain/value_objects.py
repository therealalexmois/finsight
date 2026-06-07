"""Перечисление возможных интервалов свечей."""

from enum import StrEnum


class CandleInterval(StrEnum):
    """Интервал свечей для исторических данных.

    Используется при запросах к Tinkoff Invest API.
    """

    MIN_1 = '1min'
    MIN_2 = '2min'
    MIN_3 = '3min'
    MIN_5 = '5min'
    MIN_10 = '10min'
    MIN_15 = '15min'
    MIN_30 = '30min'
    HOUR = 'hour'
    HOUR_2 = '2hour'
    HOUR_4 = '4hour'
    DAY = 'day'
    WEEK = 'week'
    MONTH = 'month'

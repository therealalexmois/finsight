"""DTO и маппер для преобразования свечей из Tinkoff SDK в доменные модели."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.app.domain.models.candle import CandleModel

if TYPE_CHECKING:
    from datetime import datetime

    from tinkoff.invest import HistoricCandle

    from src.app.domain.value_objects.candle_interval import CandleInterval


@dataclass(frozen=True)
class CandleDTO:
    """DTO для представления свечи из Tinkoff SDK.

    Используется для преобразования внешней модели `HistoricCandle`
    во внутреннюю доменную модель `CandleModel`.

    Attributes:
        time: Временная метка свечи.
        open: Цена открытия.
        close: Цена закрытия.
        high: Максимальная цена за период.
        low: Минимальная цена за период.
        volume: Объём торгов.
        figi: Идентификатор инструмента.
        interval: Интервал свечи (например, '1min', 'day').
    """

    time: 'datetime'
    open: float
    close: float
    high: float
    low: float
    volume: int
    figi: str
    interval: 'CandleInterval'

    @classmethod
    def from_sdk(cls, candle: 'HistoricCandle', figi: str, interval: 'CandleInterval') -> 'CandleDTO':
        """Создаёт DTO из модели свечи SDK.

        Преобразует объект `HistoricCandle` из Tinkoff SDK в внутреннюю DTO-модель,
        включая идентификатор инструмента и интервал свечи.

        Args:
            candle: Объект свечи `HistoricCandle` из Tinkoff SDK.
            figi: FIGI идентификатор инструмента, для которого получена свеча.
            interval: Интервал свечи, соответствующий `CandleInterval`.

        Returns:
            Экземпляр `CandleDTO`, содержащий преобразованные данные.
        """
        return cls(
            time=candle.time,
            open=float(candle.open.units) + candle.open.nano / 1e9,
            close=float(candle.close.units) + candle.close.nano / 1e9,
            high=float(candle.high.units) + candle.high.nano / 1e9,
            low=float(candle.low.units) + candle.low.nano / 1e9,
            volume=candle.volume,
            figi=figi,
            interval=interval,
        )

    def to_model(self) -> 'CandleModel':
        """Преобразует DTO в доменную модель.

        Returns:
            Объект `CandleModel` для использования в бизнес-логике.
        """
        return CandleModel(
            time=self.time,
            open=self.open,
            close=self.close,
            high=self.high,
            low=self.low,
            volume=self.volume,
            figi=self.figi,
            interval=self.interval,
        )

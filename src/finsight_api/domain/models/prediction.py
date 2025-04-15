"""Модель прогноза движения цены акции."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date
    from uuid import UUID

    from src.finsight_api.domain.value_objects.isin import ISIN
    from src.finsight_api.domain.value_objects.prediction_direction import PredictionDirection


@dataclass(frozen=True)
class Prediction:
    """Модель прогноза движения цены по ценной бумаге.

    Содержит информацию о направлении предсказания, его вероятности,
    дате, к которой оно относится, и идентификаторе прогноза.

    Attributes:
        id: Уникальный идентификатор прогноза.
        isin: ISIN-идентификатор ценной бумаги.
        date: Дата, на которую делается прогноз.
        direction: Прогнозируемое направление движения (вверх, вниз, без изменений).
        confidence: Уверенность модели в прогнозе (от 0 до 1).
    """

    id: 'UUID'
    isin: 'ISIN'
    date: 'date'
    direction: 'PredictionDirection'
    confidence: float

"""Entity бренда инструмента (справочник)."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class BrandEntity:
    """Бренд.

    Attributes:
        uid: Уникальный идентификатор бренда.
        name: Имя бренда.
        description: Описание.
        info: Доп. информация (как приходит из API).
        company: Компания.
        sector: Сектор.
        country_of_risk: Код страны риска.
        country_of_risk_name: Название страны риска.
    """

    uid: str
    name: str
    description: str
    info: str
    company: str
    sector: str
    country_of_risk: str
    country_of_risk_name: str

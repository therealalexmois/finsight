"""Entity облигации (метаданные инструмента)."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from finsight_api.domain.value_objects.money import Money
    from finsight_api.domain.value_objects.risk_level import RiskLevel


@dataclass(frozen=True, slots=True, kw_only=True)
class BondEntity:
    """Метаданные облигации.

    Это Entity: идентичность определяется `figi` (и/или `uid`).

    Attributes:
        figi: FIGI облигации.
        uid: UID облигации.
        isin: ISIN (может быть пустым).
        name: Наименование облигации.
        currency: Валюта номинала/расчётов из метаданных инструмента.
        sector: Сектор (Tinkoff taxonomy, строка).
        risk_level: Оценка риска со стороны Тинькофф.
        coupon_quantity_per_year: Количество выплат купона в год.
        maturity_date: Дата погашения (UTC).
        nominal: Номинал облигации.
        aci_value: НКД (ACI) на дату из метаданных инструмента (если задано).
        class_code: Код класса/торговой площадки.
        issue_size: Объём выпуска (фактический).
        issue_size_plan: Плановый объём выпуска.
        floating_coupon_flag: Признак плавающего купона.
        amortization_flag: Признак амортизации долга.
        # TODO: Убрать упоминание Тинькофф
        liquidity_flag: Признак ликвидности (по оценке Тинькофф).
        for_iis_flag: Признак доступности для ИИС.
        for_qual_investor_flag: Флаг отображающий доступность торговли инструментом только для квалифицированных инвесторов.
    """

    # issuer: str
    figi: str
    uid: str
    isin: str
    name: str
    currency: str
    sector: str
    risk_level: 'RiskLevel'
    coupon_quantity_per_year: int
    maturity_date: 'datetime'
    nominal: 'Money'
    aci_value: 'Money | None'
    class_code: str
    issue_size: int
    issue_size_plan: int
    # TODO: Переименовать флаги на другой булевый признак
    floating_coupon_flag: bool
    amortization_flag: bool
    liquidity_flag: bool
    for_iis_flag: bool
    for_qual_investor_flag: bool


# - issuer: "<string|UNKNOWN>"
#   sector: "<banks|oil_gas|developers|leasing|it|other|UNKNOWN>"
#   isin: "<string|UNKNOWN>"
#   qty: <int|UNKNOWN>
#   nominal_rub: 1000
#   price: <number|UNKNOWN>
#   price_unit: "pct_of_nominal"   # or "rub"
#   nkd_rub: <number|UNKNOWN>
#   ytm_pct: <number|UNKNOWN>
#   duration: <number|UNKNOWN>
#
#   coupon_type: "<fixed|floating|UNKNOWN>"
#
#   floating_coupon:
#     index: "<key_rate|ruonia|UNKNOWN>"
#     spread_pct: <number|UNKNOWN>   # спред в процентных пунктах, если указан
#
#   credit_ratings:
#     acra: "<string|UNKNOWN>"        # только АКРА (например: "AA-(RU)")
#     expert: "<string|UNKNOWN>"      # только Эксперт РА (например: "ruAA-")
#

# Test Plan — finsight

**Дата:** 2026-06-07  
**Пакеты:** `finsight-api`, `finsight-worker`  
**Тест-раннер:** pytest · `asyncio_mode = auto` · маркеры: `unit`, `integration`, `api`, `slow`, `critical`

---

## 1. Текущее состояние

### Покрыто

| Слой | Модуль | Маркер |
|------|--------|--------|
| `domain/value_objects` | `ISIN` — валидация формата | `unit` |
| `domain/value_objects` | `Amount` — граничные значения | `unit` |
| `domain/value_objects` | `Currency` — формат ISO 4217 | `unit` |
| `domain/value_objects` | `PredictionDirection` — методы `is_*` | `unit` |
| `domain/value_objects` | `TransactionType` (перечисление) | `unit` |
| `infrastructure/utils` | `pyproject.py` — чтение версии | `unit` |
| `infrastructure/utils` | `retry.py` — повторы и backoff | `unit` |
| `infrastructure` | `config.py` — загрузка `Settings` | `unit` |

### Не покрыто

| Слой | Модуль | Приоритет |
|------|--------|-----------|
| `domain/value_objects` | `Money`, `BondCoupon`, `OrderBook`, `OrderBookLevel` | P1 |
| `domain/value_objects` | `AccountStatus`, `AccountType`, `RiskLevel`, `InstrumentType`, `CandleInterval`, `CreditRatings`, `CreditRatingAgency` | P2 |
| `application/use_cases` | `GetPortfolioUseCase` | P1 |
| `application/use_cases` | `GetBondByIsinUseCase` | P1 |
| `application/use_cases` | `GetBondsByIsinUseCase` | P1 |
| `application/use_cases` | `BuildPortfolioSnapshotUseCase` | P1 |
| `application/use_cases` | `GetAccountsUseCase` | P2 |
| `application/use_cases` | `DownloadHistoricalCandlesUseCase` | P2 |
| `infrastructure/adapters/tinkoff` | `mappers.py` — конвертации units/nano | P1 |
| `infrastructure/adapters/dohod` | `adapter.py` | P3 |
| `presentation/rest` | system health-check роуты | P2 |
| `presentation/rest` | account и portfolio роуты | P2 |
| `presentation/rest` | `portfolio/mappers.py`, `portfolio/schemas.py` | P2 |
| `finsight-worker` | `DownloadHistoricalDataUseCase` | P2 |
| `finsight-worker` | `infrastructure/tasks/download_historical_data` | P3 |

---

## 2. Структура тестов

```
packages/finsight-api/tests/
├── conftest.py                        # фикстуры: settings, fastapi_app, api_client, tinkoff_gateway
├── test_domain/
│   └── test_value_objects/
│       ├── test_amount.py             # ✅ существует
│       ├── test_currency.py           # ✅ существует
│       ├── test_isin.py               # ✅ существует
│       ├── test_prediction_direction.py  # ✅ существует
│       ├── test_transaction_type.py   # ✅ существует
│       └── test_money.py              # ❌ написать
├── test_application/
│   └── test_use_cases/
│       ├── test_get_portfolio.py      # ❌ написать
│       ├── test_get_bond_by_isin.py   # ❌ написать
│       ├── test_get_bonds_by_isin.py  # ❌ написать
│       └── test_build_portfolio_snapshot.py  # ❌ написать
├── test_infrastructure/
│   ├── test_adapters/
│   │   └── test_tinkoff_mappers.py   # ❌ написать
│   ├── test_dto/                      # ❌ пусто, написать
│   └── conftest.py                    # существует
└── test_presentation/
    ├── test_system_routes.py          # ❌ написать
    └── test_portfolio_routes.py       # ❌ написать

packages/finsight-worker/tests/
└── test_application/
    └── test_download_historical_data.py  # ❌ написать
```

---

## 3. Детальные сценарии по приоритетам

### P1 — Высокий приоритет

#### 3.1 `domain/value_objects/money.py` — `Money`

`Money` — frozen dataclass без встроенной валидации; тесты фиксируют контракт.

| Тест | Ожидание |
|------|----------|
| `test_money__stores_currency_and_amount` | `currency`, `amount` хранятся без изменений |
| `test_money__immutable` | попытка `money.amount = ...` бросает `FrozenInstanceError` |
| `test_money__two_equal_instances_are_equal` | `Money(currency='RUB', amount=Decimal('10')) == Money(...)` |

#### 3.2 `application/use_cases/get_portfolio.py` — `GetPortfolioUseCase`

UseCase пересчитывает `total_value` как сумму `position.value` из позиций.

| Тест | Ожидание |
|------|----------|
| `test_execute__calculates_total_value_from_positions` | `total_value = sum(p.value for p in positions)` |
| `test_execute__passes_account_id_to_gateway` | шлюз получает тот же `account_id` |
| `test_execute__returns_entity_with_portfolio_fields` | `account_id`, `currency` совпадают |
| `test_execute__empty_positions_gives_zero_total` | `positions=[]` → `total_value = 0` |

Тест-двойник: `AsyncMock` для `TinkoffInvestPort.get_portfolio`.

#### 3.3 `application/use_cases/get_bond_by_isin.py` — `GetBondByIsinUseCase`

UseCase перехватывает исключения и возвращает их в поле `error`, не проброшенными.

| Тест | Ожидание |
|------|----------|
| `test_execute__success__returns_bond_and_no_error` | `output.bond` заполнен, `output.error is None` |
| `test_execute__gateway_raises__returns_no_bond_and_error_message` | `output.bond is None`, `output.error` содержит текст |
| `test_execute__gateway_raises__logs_error` | логгер вызван с уровнем `error` |
| `test_execute__preserves_isin_in_output` | `output.isin == data.isin` для обеих веток |

#### 3.4 `application/use_cases/get_bonds_by_isin.py` — `GetBondsByIsinUseCase`

UseCase обрабатывает частичные ошибки и параллельность.

| Тест | Ожидание |
|------|----------|
| `test_execute__all_success__returns_all_bonds_and_no_errors` | `failed_count == 0`, `len(bonds) == N` |
| `test_execute__one_fails__rest_succeed` | один ISIN → `errors`, остальные → `bonds` |
| `test_execute__all_fail__returns_empty_bonds_and_all_errors` | `bonds == ()`, `failed_count == N` |
| `test_execute__failed_isin_logged` | логгер вызван для каждой ошибки |
| `test_execute__zero_concurrency_raises_value_error` | `ValueError` при `concurrency=0` |
| `test_execute__negative_concurrency_raises_value_error` | `ValueError` при `concurrency=-1` |
| `test_execute__empty_isins_returns_empty_output` | `bonds == ()`, `errors == ()`, `failed_count == 0` |

#### 3.5 `application/use_cases/build_portfolio_snapshot.py` — `BuildPortfolioSnapshotUseCase`

Сложная оркестрация: обогащение bond-позиций по трём шагам (bond_by_figi, coupons, order_book), изоляция ошибок.

| Тест | Ожидание |
|------|----------|
| `test_execute__non_bond_positions_not_enriched` | не-bond позиции → `enrichment is None`, без ошибок |
| `test_execute__bond_position_enriched_with_bond_coupons_order_book` | все три поля `BondEnrichment` заполнены |
| `test_execute__bond_by_figi_fails__enrichment_bond_is_none` | `enrichment.bond is None`, ошибка в `enrichment_errors` со `step='bond_by_figi'` |
| `test_execute__coupons_fail__enrichment_coupons_empty` | `enrichment.coupons == ()`, ошибка со `step='coupons'` |
| `test_execute__order_book_fails__enrichment_order_book_is_none` | `enrichment.order_book is None`, ошибка со `step='order_book'` |
| `test_execute__one_step_fails__other_steps_still_called` | остальные шаги вызваны (не прерываются) |
| `test_execute__enrichment_failed_count_matches_errors` | `enrichment_failed_count == len(enrichment_errors)` |
| `test_execute__credit_ratings_always_none` | `enrichment.credit_ratings is None` (контракт до реализации) |
| `test_execute__output_contains_created_at_in_utc` | `output.created_at.tzinfo` — UTC |

#### 3.6 `infrastructure/adapters/tinkoff/mappers.py`

Функции конвертации units/nano — источник ошибок при работе с Decimal.

| Тест | Ожидание |
|------|----------|
| `test_decimal_from_units_nano__positive_values` | `(1, 500_000_000)` → `Decimal('1.5')` |
| `test_decimal_from_units_nano__zero_nano` | `(100, 0)` → `Decimal('100')` |
| `test_decimal_from_units_nano__negative_units` | `(-1, 0)` → `Decimal('-1')` |
| `test_decimal_from_units_nano__max_nano` | `(0, 999_999_999)` → `Decimal('0.999999999')` |
| `test_map_portfolio_position__maps_all_fields` | проверка figi, quantity, value, expected_yield |
| `test_map_accounts_from_sdk__returns_all_entities` | количество и поля AccountEntity |

---

### P2 — Средний приоритет

#### 3.7 `presentation/rest/system` — health-check роуты

Маркер: `@pytest.mark.api`.  
Фикстура: `api_client` из `conftest.py` (ASGI в памяти, без реального Tinkoff).

| Тест | HTTP-метод | Путь | Ожидаемый статус |
|------|-----------|------|-----------------|
| `test_startup__returns_200_and_ok_status` | GET | `/system/startup` | 200, `{"status":"ok"}` |
| `test_readiness__returns_200_and_ok_status` | GET | `/system/readiness` | 200, `{"status":"ok"}` |
| `test_liveness__returns_200_and_ok_status` | GET | `/system/liveness` | 200, `{"status":"ok"}` |

#### 3.8 `presentation/rest/public/v1/portfolio` — portfolio роут

| Тест | Ожидание |
|------|----------|
| `test_get_portfolio__valid_account_id__returns_200` | мок use case → 200, корректная схема ответа |
| `test_get_portfolio__use_case_raises__returns_error_response` | `BaseAppError` → соответствующий HTTP-статус |

#### 3.9 `finsight-worker / DownloadHistoricalDataUseCase`

| Тест | Ожидание |
|------|----------|
| `test_execute__calls_gateway_with_figi_and_interval` | шлюз получает правильные аргументы |
| `test_execute__gateway_raises__propagates_error` | исключение пробрасывается (воркер логирует на уровне задачи) |

#### 3.10 Оставшиеся value objects (перечисления)

`AccountStatus`, `AccountType`, `RiskLevel`, `InstrumentType`, `CandleInterval` — StrEnum/IntEnum.  
Для каждого: тест полноты членов и, если есть методы, — поведения методов.

---

### P3 — Низкий приоритет

| Область | Что тестировать |
|---------|----------------|
| `infrastructure/adapters/dohod` | мок HTTP-ответа → `CreditRatingsPort` контракт |
| `infrastructure/adapters/tinkoff/adapter.py` | мок SDK-клиента → преобразование SDK → domain entity (для каждого метода порта) |
| `finsight-worker/tasks` | запуск Celery-задачи, retry при ошибке шлюза |
| Интеграционные (Tinkoff API, маркер `api_integration`) | только в CI с реальным sandbox-токеном |

---

## 4. Организация выполнения

### Порядок реализации

```
1. P1-unit: money, use_cases (get_portfolio, get_bond_by_isin, get_bonds_by_isin, build_portfolio_snapshot)
2. P1-unit: tinkoff mappers (units/nano)
3. P2-api:  system routes (api_client, мок use cases)
4. P2-api:  portfolio route
5. P2-unit: finsight-worker DownloadHistoricalDataUseCase
6. P2-unit: перечисления (AccountStatus, RiskLevel и др.)
7. P3: dohod adapter, tinkoff adapter, worker tasks
```

### Принципы

- Тест-двойники: только `AsyncMock` / `Mock` для внешних портов; реальные доменные объекты для данных.
- Фикстуры inline до тех пор, пока объект не нужен в трёх и более тестах.
- Маркер `unit` — для изолированных тестов без IO.
- Маркер `api` — для тестов через `api_client` (ASGI in-memory, без реального Tinkoff).
- Маркер `integration` — зарезервирован для тестов с реальной БД/брокером.
- `api_integration` — тесты с реальным Tinkoff sandbox; запускаются только в CI вручную.
- `asyncio_mode = auto` в `pytest.ini` — `async def` тесты не требуют декоратора.
- Docstring каждого теста: условие → действие → ожидаемый результат.

### Целевое покрытие

| Пакет | Текущее | После P1 | После P2 |
|-------|---------|----------|----------|
| `finsight-api` | ~20% | ~55% | ~75% |
| `finsight-worker` | ~0% | ~0% | ~45% |

---

## 5. Открытые вопросы

1. **`GetPortfolioUseCase.execute`** конвертирует `position.value` через `float(sum(...))` — возможна потеря точности Decimal. Нужно ли исправить в коде до написания тестов или зафиксировать текущее поведение как контракт?
2. **`BuildPortfolioSnapshotUseCase`** использует `datetime.now(tz=UTC)` напрямую — тест на `created_at` потребует мока `datetime.now`. Нужно договориться о точке инъекции (параметр / `clock`-порт).
3. **`test_presentation`** — portfolio роут зависит от DI-контейнера. Нужно ли переопределять зависимость через `app.dependency_overrides` или создавать отдельный test container?

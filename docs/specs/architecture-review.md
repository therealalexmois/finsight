# Architecture Review — FinSight (deepening)

**Дата:** 2026-06-07
**Область:** `packages/finsight-api`, `packages/finsight-worker`, `packages/finsight-core`
**Ревьюер:** Claude Code (improve-codebase-architecture skill)

> **Статус:** snapshot-ревью. Зафиксированные пункты — точки улучшения архитектуры (*deepening*), не текущий контракт. Реализованные исправления отражаются в коде и не удаляются из этого документа.

## Цель и словарь

Поиск *deepening*-возможностей: где *module* мелкий (*shallow* — *interface* почти так же сложен, как *implementation*), где *seam* протекает, где SDK просачивается сквозь контракт. Цель — *locality* (изменения и баги концентрируются в одном месте) и тестируемость через один *interface*.

Термины: **module** — что-либо с *interface* и *implementation*; **interface** — всё, что должен знать вызывающий; **seam** — место, где живёт *interface* и где поведение можно подменить; **adapter** — конкретная реализация в *seam*; **deep/shallow** — много/мало поведения за *interface*; **leverage** — выигрыш вызывающего; **locality** — выигрыш поддерживающего.

**Заметка по факту дерева.** `CLAUDE.md` описывает Poetry / `src/`; репозиторий уже на uv workspace со структурой `packages/*`. Обзор сделан по фактическому коду. Попутно найдены **два runtime-разрыва** — они и есть симптомы мелких *seam* (кандидаты 1 и 2).

---

## Сводка кандидатов

| # | Кандидат | Сила | Категория | Runtime-риск |
|---|---|---|---|---|
| 1 | Свернуть проводку use case в контейнер | **Strong** | in-process · DI | Да — `Singleton` в обход |
| 2 | Поднять Tinkoff market-data в `finsight_core` | **Strong** | ports & adapters | Да — worker не запускается |
| 3 | Сузить порт Tinkoff и закрыть утечку SDK | Worth exploring | ports & adapters | Частично — SDK-типы в use case |
| 4 | Один внутренний seam для сессии SDK | Speculative | internal seam | Нет |

---

## 1. Свернуть проводку use case в контейнер — `Strong`

**Файлы:**
`presentation/webserver/dependencies/get_portfolio_use_case.py`,
`presentation/webserver/dependencies/get_account_summary_use_case.py`,
`infrastructure/container.py`,
`presentation/webserver/error_handler.py`.

**Проблема.** Проводка размазана по N модулям `dependencies/`, каждый дублирует сборку use case и поднимает *свой* `AppContainer()`:

```python
# get_portfolio_use_case.py
def get_portfolio_use_case() -> GetPortfolioUseCase:
    container = AppContainer()                       # новый контейнер на запрос
    return GetPortfolioUseCase(gateway=container.tinkoff_invest())
```

`tinkoff_invest` объявлен как `providers.Singleton`, но синглтон не разделяется: новый `AppContainer()` на каждый запрос → новый `TinkoffInvestAdapter` (и потенциально новая сессия SDK) на каждый запрос. Синглтон `app_container` существует, но web-путь его не использует — только `main.py` (startup) и CLI. То есть web и CLI пересекают **разные** *seam* сборки одних и тех же зависимостей. В `get_portfolio_use_case.py` уже стоит `# TODO: Вынести tinkoff_invest_gateway через DI`. Дополнительно `error_handler.py` дёргает `AppContainer.logger()` на уровне импорта (module-level side effect).

**Deletion-тест.** Удаляем модули проводки — сложность не исчезает, а концентрируется в контейнере (провайдеры use case + wiring). Значит это *shallow* pass-through, который вдобавок вносит баг.

**Решение.** Объявить use cases провайдерами в `AppContainer`; роутеры получают их через wiring `dependency-injector` (`@inject` + `Provide[...]`) от единого `app_container`. Модули-обёртки `dependencies/*_use_case.py` и ручной `AppContainer()` удаляются. `error_handler` получает logger не на импорте.

**Выигрыш:**
- locality: сборка зависимостей в одном месте;
- чинит баг: один *adapter* на приложение вместо нового на запрос;
- удаляются N *shallow*-модулей проводки;
- web и CLI пересекают один *seam*;
- *interface* добавления use case: +1 провайдер;
- тесты подменяют adapter через `container.override()`.

---

## 2. Поднять Tinkoff market-data в общий deep-модуль — `Strong`

**Файлы:**
`worker/application/ports/gateway.py`,
`worker/infrastructure/tasks/download_historical_data.py`,
`worker/infrastructure/container.py`,
`worker/application/use_cases/download_historical_data.py`,
`api/infrastructure/adapters/tinkoff/{adapter,mappers}.py`,
`packages/finsight-core/`.

**Проблема.** Концепт «исторические свечи» раздвоен:
- В `finsight_api` есть рабочая `TinkoffInvestAdapter.get_candles_by_isin(...)` + мапперы свечей + `CandleInterval`.
- В `finsight_worker` объявлен порт `MarketDataGateway.download_candles(request) -> Sequence[object]` с **нулём adapters** (в `infrastructure/adapters/` только `logger`). Это *hypothetical seam* без реализации.
- Провайдера `market_data_gateway()` в `WorkerContainer` **нет** (там только `config` и `logger`), а задача его вызывает:

```python
# worker/infrastructure/tasks/download_historical_data.py
use_case = DownloadHistoricalDataUseCase(
    market_data_gateway=container.market_data_gateway(),   # провайдера не существует
    logger=container.logger(),
)
```

При этом задача зовёт `use_case.execute(isin=..., from_date=..., ...)` kwargs-ами, а сигнатура — `execute(self, dto: DownloadHistoricalDataInputDto)`. Контракт задачи и use case разошёлся. `finsight_core` создан ровно для общего кода, но содержит только telemetry.

**Решение.** Вынести market-data в `finsight_core` как один *deep module*: `MarketDataPort` + `TinkoffMarketDataAdapter` + мапперы свечей (`CandleEntity`, `CandleInterval`). Оба сервиса зависят от него; `Sequence[object]` заменяется типизированным `Sequence[CandleEntity]`. Добавить провайдер в `WorkerContainer`, согласовать вызов задачи с DTO-сигнатурой use case.

**Выигрыш:**
- locality: свечи в одном *module*;
- worker начинает работать (есть *adapter* и провайдер);
- leverage: один *interface*, два сервиса-потребителя (два adapter оправдывают *seam*);
- `Sequence[object]` → типизированные `CandleEntity`;
- мапперы свечей тестируются один раз;
- `finsight_core` наполняется по назначению.

---

## 3. Сузить порт Tinkoff и закрыть утечку SDK — `Worth exploring`

**Файлы:**
`application/ports/tinkoff/{base,operations,instruments,market_data}.py`,
`application/use_cases/*.py`,
`infrastructure/adapters/tinkoff/adapter.py`.

**Проблема.** Под-порты по подсервисам (`operations` / `instruments` / `market_data`) уже определены — это хорошее разбиение. Но `base.py` собирает их в композит `TinkoffInvestPort`, и use cases типизируются композитом, хотя нужен срез: `GetPortfolioUseCase` нужен только `get_portfolio`, `GetAccountsUseCase` — только `get_accounts`. *Interface*, который учит вызывающий, шире необходимого.

Хуже — *seam* местами не держит, SDK-типы просачиваются сквозь контракт, обещающий domain-сущности:

```python
# adapter.py — get_bond_by_isin
response = await client.instruments.bond_by(...)
return response                       # сырой SDK-объект; map_bond_from_sdk закомментирован

# adapter.py — get_bonds, тип возврата BondsResponse
response = await client.instruments.bonds()
return len(response)                  # возвращает int
```

**Решение.** Типизировать use cases узким под-портом (`GetPortfolioUseCase → TinkoffOperationsPort` и т.п.) — под-порты уже есть. Привести adapter к контракту: везде возвращать domain-сущности через мапперы. Композит `TinkoffInvestPort` оставить для DI и CLI, где удобна единая точка.

**Выигрыш:**
- *seam* держит: SDK не покидает adapter;
- leverage: use case учит только нужный срез контракта;
- объём mock в тесте = под-порт, не 9 методов;
- композит остаётся для DI и CLI.

---

## 4. Один внутренний seam для сессии SDK внутри adapter — `Speculative`

**Файлы:**
`infrastructure/adapters/tinkoff/adapter.py`,
`infrastructure/adapters/tinkoff/factory.py`,
`infrastructure/utils/retry.py`.

**Проблема.** Управление сессией SDK дублировано: `async with self._client_factory() as client` повторяется в 9 методах adapter. Политику ретраев/обработки ошибок негде закрепить — она расползётся по всем методам.

**Решение.** Внутренний helper (`_with_client` / короткоживущий клиент за приватным *interface*); методы зовут его и занимаются только маппингом. Это **внутренний** *seam* (приватный для *implementation*), не меняющий внешний *interface* порта.

**Выигрыш:**
- locality: lifecycle сессии в одном месте;
- политика ошибок/ретраев — одна точка;
- методы adapter короче и про суть (маппинг).

---

## Приоритетный план

1. **Кандидат 1 — DI-свёртка.** *Seam*, который пересекает каждый запрос. Минимальный blast radius, чинит реальный баг (`Singleton` в обход), задаёт паттерн сборки для последующих пунктов.
2. **Кандидат 2 — market-data в `finsight_core`.** Самый крупный провал *locality*: worker сейчас не запускается. Лучше делать после п.1, опираясь на установленный паттерн DI.
3. **Кандидат 3 — узкие под-порты + закрытие утечки SDK.** Снимает SDK-течь сквозь *seam*; под-порты уже готовы.
4. **Кандидат 4 — внутренний seam сессии.** Косметика *locality*; делать при следующем заходе в adapter.

> Полная визуальная версия (Mermaid + before/after диаграммы) сгенерирована отдельно как HTML-отчёт во временной директории; этот документ — actionable-срез для работы.

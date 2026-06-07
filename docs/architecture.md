# Архитектура FinSight

Документ описывает фактическую структуру репозитория после миграции на uv workspace: слои clean architecture, поток запроса, DI, интеграцию с T-Bank Invest API, логирование и точки входа. Высокоуровневый замысел системы — в [RFC: Проектирование системы](rfc/system_design.md).

## Обзор

FinSight — REST API (FastAPI) для интеграции с Tinkoff Invest API и предсказания краткосрочного движения акций. Репозиторий содержит два независимых сервиса с общим стилем clean architecture и общий пакет утилит:

- `finsight_api` — HTTP-сервис (портфель, счёт, облигации, инференс).
- `finsight_worker` — Celery-воркер для фоновых задач (загрузка исторических свечей).
- `finsight_core` — общий код, переиспользуемый сервисами.

Python 3.13, uv workspace, Ruff, Mypy strict.

## Структура workspace

Репозиторий — это **uv workspace**. Корневой `pyproject.toml` объявляет workspace и его members:

```toml
[tool.uv.workspace]
members = ["packages/*"]

[tool.uv.sources]
finsight-core = { workspace = true }
finsight-api = { workspace = true }
finsight-worker = { workspace = true }
```

Корневой пакет `finsight` (`tool.uv.package = false`) агрегирует зависимости `finsight-api` и `finsight-worker`. Каждый member живёт в `packages/`, имеет **flat layout** (без вложенного `src/`), собственный `pyproject.toml` и собственные `cli/` и `tests/`. Сборка каждого пакета — через `hatchling`.

```
packages/
  finsight-core/
    finsight_core/
      telemetry/context.py     # request-id ContextVar и helpers
      py.typed
    pyproject.toml
  finsight-api/
    finsight_api/
      domain/
      application/
      infrastructure/
      presentation/
      cli/
      main.py
    tests/
    pyproject.toml
  finsight-worker/
    finsight_worker/
      domain/
      application/
      infrastructure/
      cli/
      main.py
      worker.py
    tests/
    pyproject.toml
```

### Пакет `finsight-core`

Общий пакет (экспортируется как `finsight_core`). Оба сервиса зависят от него через `tool.uv.sources` (`workspace = true`). Сейчас содержит только модуль телеметрии:

- `finsight_core/telemetry/context.py` — хранение и доступ к `X-Request-ID` через `ContextVar`:
  - константа `DEFAULT_REQUEST_ID_HEADER = 'X-Request-ID'`;
  - `extract_request_id(request)` — извлекает заголовок из входящего запроса;
  - `set_request_id(value=None, request_id_generator=None)` — устанавливает значение в контекст (генерирует UUID4, если значение не передано);
  - `get_request_id()` — возвращает текущее значение или `None`.

## Слои (clean architecture)

Оба сервиса следуют слоям clean architecture. Зависимости направлены **внутрь, к `domain`**: внешний слой знает о внутреннем, не наоборот.

```
presentation/   ──▶ application/ ──▶ domain/
       │                  │
       └──────────────────┴──▶ infrastructure/ (реализует ports, собирается в DI)
```

### domain/

Ядро без внешних зависимостей.

- `entities/` — доменные модели: `account`, `bond`, `brand`, `candle`, `portfolio`, `prediction`, `stock_history`, `transaction`, `user`.
- `value_objects/` — неизменяемые типы-значения: `amount`, `money`, `currency`, `isin`, `account_status`, `account_type`, `bond_coupon`, `candle_interval`, `credit_rating_agency`, `credit_ratings`, `instrument_type`, `order_book`, `portfolio_position`, `prediction_direction`, `risk_level`, `transaction_type`.
- `repositories/` — интерфейсы репозиториев (`candle_repository`).
- `constants`, `exceptions` — доменные ошибки наследуют `BaseAppError`.

### application/

- `use_cases/` — оркестрация бизнес-сценариев: `build_portfolio_snapshot`, `download_historical_candles`, `get_account_summary`, `get_bond_by_isin`, `get_bonds_by_isin`, `get_portfolio`.
- `ports/` — протоколы для адаптеров. Use case зависит от порта, не от конкретной реализации:
  - `ports/logger.py` — `LoggerPort`;
  - `ports/credit_ratings.py` — порт рейтингов;
  - `ports/tinkoff/{base,instruments,operations,market_data}.py` — Tinkoff-порт, разбитый по доменам API; агрегирующий `TinkoffInvestPort` в `ports/tinkoff/__init__.py`.

### infrastructure/

Реализации портов и техническая обвязка.

- `adapters/tinkoff/` — `adapter.py` (`TinkoffInvestAdapter`, реализует `TinkoffInvestPort`), `factory.py` (async-клиент по токену), `mappers.py` (SDK DTO → domain).
- `adapters/dohod/` — адаптер кредитных рейтингов.
- `adapters/telemetry/logger/structlog/` — структурированный логгер (`StructlogLogger`).
- `config.py` — настройки (`pydantic-settings`).
- `container.py` — DI-контейнер (`AppContainer`, синглтон `app_container`).
- `utils/` — инфраструктурные утилиты.

### presentation/

- `webserver/` — `app_factory.py` (сборка `FastAPI`), `middlewares/` (`request_id`, `request_logging`), `error_handler.py` (`base_app_error_handler`, `validation_error_handler`), `dependencies/` (FastAPI-зависимости достают use case из контейнера).
- `rest/` — роутеры, схемы и мапперы, сгруппированные по версии и домену: `rest/public/v1/{account,portfolio}/` (агрегирующий `router.py` → `api_v1_router`) и `rest/system/` (`router.py` → `system_router`).
- `cli/` — CLI-команды презентационного слоя.

## Поток запроса

Жизненный цикл HTTP-запроса на примере получения портфеля:

```
GET /account/{account_id}/portfolio
  → RequestIDMiddleware → RequestLoggingMiddleware
  → router (presentation/rest/public/v1/portfolio/router.py)
  → PortfolioUseCaseDep — зависимость достаёт use case из app_container
  → GetPortfolioUseCase.execute(account_id)        (application/use_cases)
  → TinkoffInvestPort.get_portfolio(...)           (порт)
  → TinkoffInvestAdapter + mappers                 (SDK DTO → PortfolioEntity)
  → map_portfolio_to_response → PortfolioResponse  (presentation-схема)
```

1. Входящий HTTP-запрос.
2. `RequestIDMiddleware` — извлекает `X-Request-ID` (`extract_request_id`), кладёт в контекст (`set_request_id`) и добавляет заголовок в ответ.
3. `RequestLoggingMiddleware` — структурированное логирование запроса; пути `/health` и `/metrics` исключены.
4. FastAPI-роутер из `presentation/rest`.
5. FastAPI-зависимость из `presentation/webserver/dependencies` достаёт use case из контейнера (`AppContainer`).
6. Use case из `application/use_cases`.
7. Use case вызывает порт (`TinkoffInvestPort`).
8. Адаптер из `infrastructure/adapters/tinkoff` реализует порт и обращается к T-Bank Invest API.
9. Результат маппится в доменную модель, затем в схему ответа и возвращается клиенту.

Middlewares регистрируются в `AppFactory.create_app()` в порядке `RequestLoggingMiddleware`, затем `RequestIDMiddleware`; Starlette применяет их в обратном порядке, поэтому `RequestIDMiddleware` отрабатывает первым. Там же подключаются роутеры (`system_router`, `api_v1_router`) и обработчики ошибок: доменные ошибки (`BaseAppError`) перехватываются `base_app_error_handler`, прочие — `validation_error_handler`.

## Dependency injection

DI реализован через `dependency-injector`.

### finsight_api — AppContainer

`finsight_api/infrastructure/container.py`. Синглтон-инстанс — `app_container`. Провайдеры:

- `settings` — `Singleton(Settings)`.
- `logger` — `Factory(StructlogLogger, ...)` с параметрами из `settings` (`app.name`, `app.version`, `app.env`, `app.host`, `logging.log_level`).
- `tinkoff_client_factory` — `Factory` фабрики async-клиента по токену.
- `tinkoff_invest` — `Singleton(TinkoffInvestAdapter, ...)` с токеном, логгером и фабрикой клиента; реализует `TinkoffInvestPort`.

FastAPI-зависимости в `presentation/webserver/dependencies/` собирают use cases, доставая адаптеры из контейнера. Например, `get_portfolio_use_case()` создаёт `GetPortfolioUseCase(gateway=container.tinkoff_invest())`.

### finsight_worker — WorkerContainer

`finsight_worker/infrastructure/container.py`. Провайдеры:

- `config` — `providers.Configuration()`, заполняется из `Settings` через `config.from_pydantic(settings)` в `finsight_worker/main.py`.
- `logger` — `Factory(StructlogLogger, name=LOGGER_NAME)`.

## Интеграция с Tinkoff / T-Bank Invest API

Важно: исходный PyPI-пакет `tinkoff-investments` помещён в **карантин** на PyPI и больше не устанавливается. Проект использует официальный SDK T-Bank — `t-tech-investments==1.49.0` — из приватного индекса.

Конфигурация индекса в корневом `pyproject.toml`:

```toml
[tool.uv.sources]
t-tech-investments = { index = "tbank" }

[[tool.uv.index]]
name = "tbank"
url = "https://opensource.tbank.ru/api/v4/projects/238/packages/pypi/simple/"
explicit = true
```

Из-за смены SDK изменилось пространство имён импорта: с `tinkoff.invest` на **`t_tech.invest`** (например `from t_tech.invest import AsyncClient`, `from t_tech.invest.async_services import AsyncServices`).

Адаптер живёт в `finsight_api/infrastructure/adapters/tinkoff/`:

- `adapter.py` — `TinkoffInvestAdapter`, реализует `TinkoffInvestPort`.
- `factory.py` — `async_client_factory(token)`: async context manager поверх `AsyncClient`.
- `mappers.py` — преобразование SDK DTO в доменные модели (счета, облигации, купоны, портфель, свечи, стакан).

Порты разделены по доменам Tinkoff API, что позволяет use case зависеть только от нужного среза контракта. Токен read-only — торговые поручения недоступны.

## Логирование

`structlog` со сквозной трассировкой по request-id. Контекст request-id общий между сервисами — `finsight_core.telemetry.context` (`ContextVar`, заголовок `X-Request-ID`).

- `finsight_api`: адаптер логгера `StructlogLogger` в `infrastructure/adapters/telemetry/logger/structlog/`. Идентификатор запроса проставляется `RequestIDMiddleware` и доступен во всех логах запроса; пути `/health` и `/metrics` исключены из логирования.
- `finsight_worker`: собственный адаптер логгера в `infrastructure/adapters/logger/` (`structlog_logger.py`, `logging.py`, `processors.py`), имя логгера — `LOGGER_NAME`.

## Точки входа

Скрипты объявлены в `[project.scripts]` соответствующих пакетов:

- `finsight-api = "finsight_api.cli.main:cli"` (click).
- `finsight-worker = "finsight_worker.cli.main:cli"` (typer).

Запуск:

```bash
uv run finsight-api server start            # HTTP-сервер
uv run finsight-api server start --reload   # с авто-перезагрузкой
uv run finsight-worker worker start         # Celery-воркер
```

Те же команды доступны через Makefile: `make finsight-api-start`, `make finsight-api-dev`, `make finsight-worker-start`.

### HTTP-сервис

`finsight_api/cli/main.py` (`cli`) → команда `server start` (`cli/server.py`) → `finsight_api/main.py:start_app` → `AppFactory(settings).create_app()` → `uvicorn.run(...)`. CLI-группа также включает команду `version`. CLI-слой тонкий; логика запуска — в `main.py`.

### Воркер

`finsight_worker/cli/main.py` (`cli`, typer) подключает sub-приложения `worker` и `fetch`. Команда `worker start` (`cli/commands/worker.py`) запускает Celery через `subprocess`:

```
celery -A finsight_worker.main worker --loglevel=info
```

`finsight_worker/main.py` создаёт `Settings`, заполняет `WorkerContainer` (`config.from_pydantic`), создаёт `celery_app` (`create_celery_app(settings)` в `worker.py`) и регистрирует задачи (`download_historical_data.register_tasks(celery_app)` из `infrastructure/tasks/`).

## Конфигурация

`pydantic-settings`. Префикс env — `APP_`, вложенность через `__` (например `APP_APP__ENV`, `APP_TINKOFF_INVEST_API__TOKEN`). Настройки `finsight_api` — `infrastructure/config.py` (`Settings`, `env_file`, кодировка UTF-8). Локальная настройка: `cp .env.local.sample .env.local`.

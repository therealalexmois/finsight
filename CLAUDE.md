# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

FinSight — REST API (FastAPI) для интеграции с Tinkoff Invest API и предсказания краткосрочного движения акций. Репозиторий содержит два независимых сервиса с общим стилем clean architecture:

- `finsight_api` — синхронный/async HTTP-сервис (портфель, счёт, облигации, инференс).
- `finsight_worker` — Celery-воркер для фоновых задач (загрузка исторических данных).

Python 3.13, Poetry (`package-mode = false`), Ruff, Mypy strict.

## Commands

Все команды идут через `make` (обёртки над `poetry run`).

```bash
make install          # poetry install
make install-dev      # + dev-зависимости
make install-test     # + test-зависимости

make lint             # ruff check .
make lint-fix         # ruff check . --fix
make lint-format      # ruff format .
make type-check       # mypy по src/ cli/ tests/ (--no-incremental)
make ci-checks        # lint + type-check
make pre-commit       # pre-commit на всех файлах

make test                  # pytest (cov включён через pytest.ini)
make test-with-coverage    # pytest + term-missing

# Запуск сервиса finsight-api (через CLI):
make finsight-api-start    # python -m cli.finsight_api server start
make finsight-api-dev      # ... server start --reload
make finsight-worker-start # python -m cli.finsight_worker worker start
```

### Запуск одного теста

`make test` пробрасывает `ARGS`:

```bash
make test ARGS="tests/test_finsight_api/test_domain/test_value_objects/test_isin.py"
make test ARGS="-k test_isin and valid"
make test ARGS="-m unit"      # по маркеру
```

Маркеры (`pytest.ini`): `unit`, `integration`, `api`, `slow`, `critical`. `asyncio_mode = auto` — async-тесты не требуют декоратора. `pythonpath = src`.

## Entry points

- HTTP-сервис: CLI `cli/finsight_api` (click) → `src/finsight_api/main.py:start_app` → `AppFactory.create_app()` → uvicorn.
- Воркер: CLI `cli/finsight_worker` (typer) → `src/finsight_worker/main.py` создаёт `celery_app` и регистрирует задачи.
- `cli/` — тонкий слой команд; вся логика запуска в `src/`.

## Architecture

> Детальное описание слоёв, потока запроса, DI и состояния рефакторинга — в [docs/architecture.md](docs/architecture.md).

Оба сервиса следуют слоям clean architecture (зависимости направлены внутрь, к domain):

- `domain/` — `entities/`, `value_objects/`, `repositories/` (интерфейсы), `constants`, `exceptions`. Без внешних зависимостей. Доменные ошибки наследуют `BaseAppError`.
- `application/` — `use_cases/` (оркестрация) и `ports/` (протоколы для адаптеров: `tinkoff/`, `logger`, `credit_ratings`). Use case зависит от port, не от конкретного адаптера.
- `infrastructure/` — реализации портов в `adapters/` (`tinkoff/`, `dohod/`, `telemetry/logger/structlog/`), `config.py` (Pydantic Settings), `container.py` (DI).
- `presentation/` — `webserver/` (FastAPI: `app_factory`, middlewares, error handlers, dependencies), `rest/` (роутеры, схемы, мапперы по версиям/доменам), `cli/`.

### Dependency injection

`dependency-injector`. Контейнеры — `src/finsight_api/infrastructure/container.py` (`AppContainer`, singleton-инстанс `app_container`) и `src/finsight_worker/infrastructure/container.py`. Провайдеры собирают `settings`, `logger`, адаптеры Tinkoff. FastAPI-зависимости в `presentation/webserver/dependencies/` достают use cases из контейнера.

### Tinkoff integration

Порты разбиты по доменам Tinkoff API: `application/ports/tinkoff/{base,instruments,operations,market_data}.py`. Адаптер `infrastructure/adapters/tinkoff/adapter.py` + `factory.py` (async-клиент по токену) + `mappers.py` (Tinkoff DTO → domain). Токен read-only — торговые поручения недоступны.

### Configuration

`pydantic-settings`. Префикс env — `APP_`, вложенность через `__` (например `APP_APP__ENV`, `APP_TINKOFF_INVEST_API__TOKEN`). `.env.local` подхватывается только в окружении `local`. Часть полей (`name`, `version`, `description`) читается из `pyproject.toml`. Локальная настройка: `cp .env.local.sample .env.local`.

### Logging

`structlog` с request-id трассировкой. Адаптер логгера в `infrastructure/adapters/telemetry/logger/structlog/`. Middlewares `RequestIDMiddleware` и `RequestLoggingMiddleware` (пути `/health`, `/metrics` исключены из логов).

## Conventions

- Mypy `strict = True` (`disallow_untyped_defs`, `disallow_any_generics`, `warn_unreachable` и т.д.). Все публичные функции типизированы.
- Ruff: `line-length = 120`, `target-version = py313`, docstring-конвенция Google, одинарные кавычки.
- Docstrings — на русском, заголовки секций (`Args`, `Returns`, `Raises`) — на английском.
- Тяжёлые импорты только для типов — под `if TYPE_CHECKING:`.

## Notes

- Репозиторий в процессе рефакторинга структуры (см. `git status` — переименования domain/models → domain/entities, перенос presentation-роутеров). Часть импортов может временно не совпадать с текущим деревом файлов — сверяйся с фактическим расположением перед правками.
- Файлы в корне (`a.py`, `b.py`, `test.py`, `*.json`) — экспериментальные скрипты/выгрузки, вне основного пакета.

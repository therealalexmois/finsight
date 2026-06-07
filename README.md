# FinSight

REST API на базе FastAPI для интеграции с T-Bank Invest API и получения финансовых данных по портфелю и счёту. Фоновая загрузка исторических свечей реализована через Celery-воркер.

---

## Возможности

- Получение списка инвестиционных счётов через T-Bank Invest API.
- Получение портфеля по идентификатору счёта.
- Фоновая загрузка исторических свечей (Celery + Redis).
- Структурированное логирование с трассировкой запросов (structlog, request-id).
- Конфигурация через переменные окружения (pydantic-settings).
- Строгая типизация (Mypy strict), линтинг (Ruff), тесты (pytest).

---

## Структура

Репозиторий организован как uv workspace:

```
packages/
  finsight-api/     # HTTP-сервис (FastAPI)
  finsight-worker/  # Celery-воркер
  finsight-core/    # Общий код (телеметрия, request-id)
```

---

## Быстрый старт

### 1. Клонировать репозиторий

```bash
git clone https://github.com/therealalexmois/finsight
cd finsight
```

### 2. Установить зависимости

```bash
make install
```

Команда выполняет `uv sync` для всех пакетов workspace, включая группы `dev`, `lint`, `test`.

### 3. Настроить окружение

```bash
cp .env.local.sample .env.local
```

Откройте `.env.local` и укажите токен T-Bank Invest API и другие параметры.

Переменные окружения используют префикс `APP_`, вложенные поля разделяются `__`:

```
APP_APP__ENV=local
APP_TINKOFF_INVEST_API__TOKEN=your_token_here
```

`.env.local` подхватывается автоматически только в окружении `local`.

---

## Запуск

### HTTP-сервис (finsight-api)

```bash
make finsight-api-start   # обычный режим
make finsight-api-dev     # с автообновлением (--reload)
```

Сервис доступен по адресу `http://127.0.0.1:8000`.

### Celery-воркер (finsight-worker)

Требует запущенный Redis (broker).

```bash
make finsight-worker-start
```

---

## Примеры запросов

### Проверка состояния сервиса

```bash
curl http://localhost:8000/system/startup
curl http://localhost:8000/system/readiness
curl http://localhost:8000/system/liveness
```

### Список счётов

```bash
curl http://localhost:8000/api/v1/account/accounts
```

### Портфель по счёту

```bash
curl http://localhost:8000/api/v1/account/{account_id}/portfolio
```

---

## Тестирование

```bash
make test                # запустить тесты
make test-with-coverage  # с отчётом о покрытии
```

Поддерживается передача аргументов pytest через `ARGS`:

```bash
make test ARGS="-k test_portfolio"
make test ARGS="-m unit"
```

Маркеры: `unit`, `integration`, `api`, `slow`, `critical`.

---

## Качество кода

```bash
make lint        # ruff check .
make lint-fix    # ruff check . --fix
make lint-format # ruff format .
make type-check  # mypy --config-file=mypy.ini
make pre-commit  # все хуки pre-commit
```

---

## Технологический стек

- Python 3.13
- uv workspace
- FastAPI, Pydantic v2
- Celery, Redis
- T-Bank Invest API
- structlog
- dependency-injector
- Ruff, Mypy strict
- pytest
- Docker, GitHub Actions

---

## Лицензия

MIT License © 2025 @therealalexmois

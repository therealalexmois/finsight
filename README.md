# finsight-api

📈 **FinSight API** — REST API на базе FastAPI для интеграции с Tinkoff Invest API и предсказаний краткосрочного движения акций по ISIN.

Проект демонстрирует:
- Интеграцию с Tinkoff Invest API
- Предсказания ML модели (KNN) через REST API
- Чистую архитектуру Python-проекта с использованием `src/`-структуры
- Структурированное логирование с `structlog` и трассировкой запросов
- Загрузку конфигурации через `.env` с помощью Pydantic Settings
- Готовность к расширению (база данных, кэш, фоновые задачи)

---

## 📦 Возможности

- ✅ REST API для отображения финансовых данных и инференса модели
- 🔐 Подключение к инвестиционному счёту Tinkoff
- 🧠 ML модель (KNN) для прогноза движения акций
- 📊 Визуализация данных (в перспективе)
- ⚙️ Настройки окружения через `.env.local` и переменные `APP_ENV`
- 📂 Современная структура проекта (`src/`, Poetry, Ruff, Mypy)

---

## 🚀 Быстрый старт

### 1. Клонировать репозиторий

```bash
git clone https://github.com/your-username/finsight-api
cd finsight-api
```

### 2. Установить зависимости

```bash
make install
```

Для установки зависимостей разработчика:

```bash
make install-dev
```

### 3. Создать .env.local

```bash
cp .env.local.sample .env.local
```

Отредактируйте файл, указав токен доступа Tinkoff и другие параметры.

### 4. Запустить приложение

Для запуска в обычном режиме:

```bash
make start
```

Приложение будет доступно по адресу http://127.0.0.1:8000

#### 🔁 Локальная разработка с автообновлением (hot reload)

```bash
make dev
```

Также можно передать дополнительные параметры через ARGS, например:

```bash
make dev ARGS="--port 5000"
```

---

## 📊 Примеры запросов

### Получить сводку по счёту

```bash
curl -X GET http://localhost:8000/account/summary
```

### Прогноз по ISIN

```bash
curl -X GET "http://localhost:8000/predict?isin=RU000A0JX0J2"
```

---

## 🧪 Тестирование

```bash
make test
```

С покрытием:

```bash
make test-with-coverage
```

---

## 🧹 Проверка качества кода

```bash
make lint        # Линтинг Ruff
make type-check  # Проверка типов Mypy
make pre-commit  # Все хуки pre-commit
```

---

## 🛠 Стек технологий

- FastAPI
- Pydantic v2
- Poetry
- Tinkoff Invest API
- Scikit-learn
- Structlog
- PostgreSQL (в перспективе)
- Redis (опционально)
- Docker / Make / GitHub Actions

---

📄 Лицензия
MIT License © 2025 @therealalexmois

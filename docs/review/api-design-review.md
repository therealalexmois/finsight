# API Design Review — finsight-api

**Дата:** 2026-06-07  
**Область:** `packages/finsight-api`  
**Ревьюер:** Claude Code (api-design-reviewer skill)

> **Статус:** snapshot-ревью. Зафиксированные проблемы — точки улучшения, не текущий контракт API. Реализованные исправления отражены в коде и не удаляются из этого документа.

---

## Карта эндпоинтов (текущее состояние)

```
GET /system/startup        → SystemStatusResponse
GET /system/readiness      → SystemStatusResponse
GET /system/liveness       → SystemStatusResponse
GET /api/v1/account/accounts                  → AccountsResponse
GET /api/v1/account/{account_id}/portfolio    → PortfolioResponse
```

---

## 🔴 Критические проблемы

### 1. URL `/account/accounts` — дублирование сегмента пути

Оба роутера объявлены с `prefix='/account'`, поэтому endpoint accounts регистрируется как `/api/v1/account/accounts`. REST-ресурс должен быть плоским и во множественном числе:

```
❌ GET /api/v1/account/accounts
✅ GET /api/v1/accounts
✅ GET /api/v1/accounts/{account_id}/portfolio
```

Сейчас router `account` и router `portfolio` имеют одинаковый `prefix='/account'` — это технически работает, но ресурсный путь `/account` (singular) смешан с коллекцией `/accounts`.

### 2. `ticker` маппится из `figi` — семантически неверно

```python
# mappers.py
ticker=position.figi,  # FIGI: "BBG004730N88", тикер: "SBER"
```

FIGI (Financial Instrument Global Identifier) — это глобальный идентификатор (например `BBG004730N88`), не тикер (`SBER`, `YNDX`). Поле называется `ticker`, но содержит FIGI. Это ломает контракт с клиентом.

**Варианты исправления:**
- переименовать поле в `figi`, если тикер недоступен из Tinkoff API в текущем flow;
- получать тикер через instruments-порт и заполнять правильно.

### 3. `instrument_name` и `currency` всегда `'UNKNOWN'`

```python
instrument_name='UNKNOWN',  # Заглушка
currency='UNKNOWN',         # Заглушка
```

Поля присутствуют в схеме и примере (`PortfolioResponse.json_schema_extra`), но никогда не заполняются. Клиент видит `"Сбербанк"` в документации и `"UNKNOWN"` в реальном ответе — это нарушение контракта. Поля должны либо заполняться, либо быть помечены `instrument_name: str | None = None` и убраны из примера.

---

## 🟠 Значимые проблемы

### 4. Нет аутентификации на бизнес-эндпоинтах

`build_unauthorized_exception` определён в `error_handler.py`, но нигде не используется. `/api/v1/accounts` и `/api/v1/account/{account_id}/portfolio` открыты без какой-либо проверки. Данные Tinkoff — финансовая информация пользователя.

### 5. `float` для денежных значений

```python
class Position(BaseModel):
    balance: float
    current_price: float
```

Использование `float` для финансовых данных — классический антипаттерн (проблемы с точностью IEEE 754). Должен быть `Decimal`. Pydantic v2 поддерживает `Decimal` напрямую.

### 6. `AppContainer()` создаётся на каждый запрос

```python
# get_accounts_use_case.py
def get_accounts_use_case() -> GetAccountsUseCase:
    container = AppContainer()          # новый экземпляр на каждый запрос
    return GetAccountsUseCase(invest=container.tinkoff_invest())
```

Контейнер должен быть singleton. Текущая реализация создаёт новый контейнер (и потенциально новый HTTP-клиент к Tinkoff) на каждый вызов. Стандартный паттерн — держать `app_container` как модульный singleton и обращаться к нему в dependency-функции.

### 7. Несогласованный формат ошибок

Разные пути дают разную структуру:

```json
// BaseAppError
{"detail": "Ошибка бизнес-логики"}

// RequestValidationError
{"detail": [{"loc": ["body", "field"], "msg": "...", "type": "..."}]}
```

Нет единой обёртки, нет `code` (machine-readable), нет `request_id` в теле (только в заголовке). Клиент должен обрабатывать два разных формата `detail`.

Минимальная стандартная структура:
```json
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "...",
        "request_id": "abc-123"
    }
}
```

### 8. Отсутствие `responses` в OpenAPI описании эндпоинтов

```python
@router.get(
    '/{account_id}/portfolio',
    status_code=HTTPStatus.OK,
    # Нет: responses={404: ..., 401: ..., 422: ..., 500: ...}
)
```

В сгенерированной OpenAPI схеме будет только `200`. Клиенты и документация не знают об ошибочных кодах.

---

## 🟡 Улучшения

### 9. Health check пути нестандартны

```
❌ /system/startup    /system/readiness    /system/liveness
✅ /health            /health/ready        /health/live
   (или /healthz, /readyz, /livez для k8s)
```

Kubernetes и большинство proxy/load balancer ищут `/health` или `/healthz`. `/system/startup` не является общепринятым именем для startup probe.

### 10. `accounts_count` — избыточное поле

```python
class AccountsResponse(BaseModel):
    accounts_count: int          # клиент может сам: len(response.accounts)
    accounts: list[AccountResponse]
```

Поле имеет смысл только если оно отражает `total` при пагинации (общее кол-во в БД, а не в текущей странице). Пока пагинации нет — поле избыточно.

### 11. `AccountResponse.type` и `status` как голые `str`

```python
class AccountResponse(BaseModel):
    type: str     # "ACCOUNT_TYPE_TINKOFF", "ACCOUNT_TYPE_IIS", ...
    status: str   # "ACCOUNT_STATUS_OPEN", "ACCOUNT_STATUS_CLOSED", ...
```

Tinkoff API возвращает enum-значения. В схеме ответа это должны быть `Literal` или `Enum`, чтобы клиент знал допустимые значения и OpenAPI генерировал корректные схемы.

### 12. Пагинация не предусмотрена

`/api/v1/accounts` и `/api/v1/account/{account_id}/portfolio` не имеют параметров `limit`/`offset`/`cursor`. Позиций в портфеле может быть десятки. Добавить сейчас дешевле, чем вводить как breaking change позже.

### 13. Swagger UI отключён без явной причины

```python
FastAPI(docs_url=None, redoc_url='/')
```

ReDoc доступен на `/`, Swagger UI отключён. OpenAPI JSON недоступен напрямую. Это осложняет интеграцию и тестирование через браузер. Рекомендуется включить `/docs` хотя бы для `local`/`dev` окружений.

---

## Итоговая оценка

| Категория | Оценка | Основание |
|---|---|---|
| Именование URL | D | `/account/accounts`, singular prefix |
| Корректность данных | D | `ticker=figi`, `UNKNOWN` поля в ответе |
| Аутентификация | F | Финансовые данные без защиты |
| Формат ошибок | C | Частично стандартный, нет единой обёртки |
| Документация | C | ReDoc есть, но `responses` не описаны |
| Типизация | C | `float` для денег, `str` для enum |
| DI / архитектура | C | AppContainer per-request |
| **Итого** | **C−** | |

---

## Приоритетный план исправлений

1. Исправить URL (`/accounts`, `/accounts/{id}/portfolio`) — иначе всё последующее накапливает долг на неправильном контракте.
2. `ticker` → `figi` или получить настоящий тикер; убрать/заполнить `UNKNOWN` поля.
3. Добавить аутентификацию (Bearer token через dependency).
4. `float` → `Decimal` в `Position`.
5. Единый формат ошибок, `responses` в роутах, health check пути.

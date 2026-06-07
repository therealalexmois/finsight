# Аудит: env & secrets hygiene

**Дата:** 2026-06-07
**Инструмент:** env-secrets-manager skill
**Область:** `.env`-файлы, git-история, pre-commit, CI/CD, конфигурация

---

## CRITICAL

### Реальный токен Tinkoff Invest API в `.env.local`

`.env.local:9` содержит живой read-only токен Tinkoff Invest API.

**Статус:** файл правильно добавлен в `.gitignore` (`*.env.local`) и **никогда не коммитился** в git-историю — проверено через `git log -S`. Прямой угрозы утечки через репозиторий нет.

**Риск:** живой credential хранится в плоском файле. Токен Tinkoff истекает через 3 месяца с последнего использования, ротация не отслеживается.

**Действие:** ротировать токен, если он передавался третьим лицам или проходил через буфер обмена / IDE-логи / shell history.

---

## HIGH

### `token: str` вместо `SecretStr` в `TinkoffInvestApiSettings`

**Файл:** `packages/finsight-api/finsight_api/infrastructure/config.py:121`

```python
# сейчас — значение попадёт в repr() и model_dump()
token: str = Field(...)

# нужно
token: SecretStr = Field(...)
```

Pydantic `SecretStr` маскирует значение как `**********` в `repr()` и `model_dump()`. Без этого токен утекает в structlog-логи при дампе настроек или трейсе исключения.

---

## MEDIUM

### Нет pre-commit-хука для Tinkoff-специфичного паттерна

**Файл:** `.pre-commit-config.yaml`

`detect-private-key` ловит RSA/SSH private keys, но не JWT-подобные токены формата `t.*`. Если токен окажется в коде — хук его пропустит.

Рекомендация — добавить `gitleaks` с кастомным правилом:

```toml
# .gitleaks.toml
[extend]
useDefault = true

[[rules]]
id = "tinkoff-invest-token"
description = "Tinkoff Invest API token"
regex = '''t\.[A-Za-z0-9_-]{80,}'''
```

```yaml
# .pre-commit-config.yaml
- repo: https://github.com/gitleaks/gitleaks
  rev: v8.21.2
  hooks:
    - id: gitleaks
```

### Закомментированный sandbox-токен в `.env.local`

`.env.local:10` содержит закомментированный живой credential sandbox-токена. Лучше убрать из файла и хранить отдельно при необходимости.

### `.env.local.sample` устарел

`.env.local.sample` использует старые ключи:
- `APP_TINKOFF_INVEST_API_READONLY_TOKEN` → должно быть `APP_TINKOFF_INVEST_API__TOKEN`
- `APP_TINKOFF_INVEST_API_SANDBOX_TOKEN` → должно быть `APP_TINKOFF_INVEST_API__SANDBOX_TOKEN`

При онбординге новый разработчик получит неработающую конфигурацию.

---

## LOW / INFO

### `deploy.yml` пуст

`.github/workflows/deploy.yml` содержит одну пустую строку — файл-заглушка. Не критично, но вводит в заблуждение.

---

## Хорошее

- `.env.local` отсутствует в git-истории во всех ветках
- `scratch/` правильно gitignored; токенов в JSON-выгрузках не обнаружено
- CI workflow чистый, секреты не хардкодированы
- Конфиг читается только из env, нет fallback-значений для токена
- pre-commit покрывает форматирование, типы и критические тесты

---

## Приоритетные действия

| # | Действие | Приоритет |
|---|----------|-----------|
| 1 | `token: str` → `SecretStr` в `TinkoffInvestApiSettings` | HIGH |
| 2 | Обновить `.env.local.sample` под текущую схему ключей | MEDIUM |
| 3 | Добавить `gitleaks` с правилом для Tinkoff-токена в pre-commit | MEDIUM |
| 4 | Убрать закомментированный sandbox-токен из `.env.local` | MEDIUM |
| 5 | Удалить или наполнить `deploy.yml` | LOW |

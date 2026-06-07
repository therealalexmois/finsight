# Документация FinSight

FinSight — REST API (FastAPI) для интеграции с Tinkoff Invest API и предсказания
краткосрочного движения акций. Репозиторий — uv workspace из трёх пакетов:
`finsight_api` (HTTP-сервис), `finsight_worker` (Celery-воркер) и `finsight_core`
(общий код).

## Содержание

- [Архитектура](architecture.md) — фактическая структура кода: workspace,
  слои clean architecture, поток запроса, DI, интеграция с Tinkoff.
- [RFC: Проектирование системы](rfc/system_design.md) — высокоуровневый замысел
  системы: контекст, проблематика, терминология, целевые проектные решения.

## Ревью и планы

Датированные срезы состояния (snapshot на дату ревью, не живая документация):

- [API Design Review](review/api-design-review.md) — анализ контракта REST API
  `finsight-api`.
- [Architecture Review](specs/architecture-review.md) — точки углубления
  архитектуры (*deepening*).
- [Test Plan](plans/test-plan.md) — текущее покрытие и приоритеты тестов.

## С чего начать

- Замысел и мотивация системы — [RFC](rfc/system_design.md).
- Как устроен код и где что лежит — [Архитектура](architecture.md).

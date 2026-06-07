"""Команда построения снапшота портфеля.

Команда строит снапшот через Use Case и выводит JSON в stdout или в файл.
"""

import asyncio
import json
from dataclasses import asdict
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING

import typer
from rich import print as rprint

from finsight_api.application.use_cases.build_portfolio_snapshot import (
    BuildPortfolioSnapshotInput,
    BuildPortfolioSnapshotOutput,
    BuildPortfolioSnapshotUseCase,
)
from finsight_api.infrastructure.container import app_container
from finsight_api.presentation.cli.utils import write_json_file

if TYPE_CHECKING:
    from typing import Any

app = typer.Typer(help='Build and save an investment profile snapshot.')


def _json_normalize(value: 'Any') -> 'Any':
    """Нормализует структуру для JSON сериализации.

    Args:
        value: Любое значение.

    Returns:
        Any: JSON-совместимое значение.
    """
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, (list, tuple)):
        return [_json_normalize(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _json_normalize(v) for k, v in value.items()}
    return value


def snapshot_to_json_dict(output: BuildPortfolioSnapshotOutput) -> dict[str, object]:
    """Преобразует результат UC в JSON-совместимый словарь.

    Особенности:
        - Decimal сериализуется как строка для сохранения точности.
        - datetime сериализуется в ISO 8601.

    Args:
        output: Результат Use Case.

    Returns:
        dict[str, object]: JSON-совместимое представление.
    """
    raw = asdict(output)
    return _json_normalize(raw)


def _parse_date(value: str | None) -> date | None:
    """Парсит дату YYYY-MM-DD.

    Args:
        value: Строка даты.

    Returns:
        date | None: Дата или None.

    Raises:
        ValueError: Если формат даты некорректный.
    """
    if value is None:
        return None
    return date.fromisoformat(value)


@app.command('build')
def build(
    account_id: str = typer.Argument(..., help='Идентификатор счёта'),
    output: Path | None = typer.Option(None, '--output', '-o', help='Путь до JSON-файла результата'),
    depth: int = typer.Option(1, '--depth', help='Глубина стакана'),
    coupons_from: str | None = typer.Option(None, '--coupons-from', help='YYYY-MM-DD нижняя граница купонов'),
    coupons_to: str | None = typer.Option(None, '--coupons-to', help='YYYY-MM-DD верхняя граница купонов'),
    pretty: bool = typer.Option(True, '--pretty/--no-pretty', help='Pretty print JSON'),
) -> None:
    """Строит снапшот портфеля по счёту и выводит JSON.

    При отсутствии `output` JSON печатается в stdout, иначе сохраняется в файл.

    Raises:
        typer.Exit: При ошибке построения снапшота или записи файла (код 1).
    """
    tinkoff = app_container.tinkoff_invest()
    logger = app_container.logger()

    uc = BuildPortfolioSnapshotUseCase(tinkoff=tinkoff, logger=logger)
    data = BuildPortfolioSnapshotInput(
        account_id=account_id,
        order_book_depth=depth,
        coupons_from_date=_parse_date(coupons_from),
        coupons_to_date=_parse_date(coupons_to),
    )

    try:
        result = asyncio.run(uc.execute(data))
    except Exception as exc:
        logger.error(f'Failed to build portfolio snapshot: {exc!r}')
        raise typer.Exit(code=1) from exc

    payload: dict[str, Any] = snapshot_to_json_dict(result)
    text = json.dumps(payload, ensure_ascii=False, indent=2 if pretty else None)

    if output is None:
        rprint(text)
        return

    try:
        write_json_file(obj=payload, path=output)
    except Exception as exc:
        logger.error(f'Failed to write snapshot JSON file: {exc!r}')
        raise typer.Exit(code=1) from exc

    rprint(f'Snapshot saved to: {output}')


if __name__ == '__main__':
    app()

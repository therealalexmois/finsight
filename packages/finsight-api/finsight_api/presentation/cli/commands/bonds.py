"""Команды поиска облигаций по идентификаторам.

Команды получают данные по облигациям через Use Case и выводят JSON в stdout или в файл.
"""

import asyncio
import json
from dataclasses import asdict
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING

import typer
from rich import print as rprint

from finsight_api.application.use_cases.get_bond_by_isin import (
    GetBondByIsinInput,
    GetBondByIsinUseCase,
)
from finsight_api.application.use_cases.get_bonds_by_isin import (
    GetBondsByIsinInput,
    GetBondsByIsinUseCase,
)
from finsight_api.domain.value_objects.isin import ISIN
from finsight_api.infrastructure.container import app_container
from finsight_api.presentation.cli.utils import write_json_file

if TYPE_CHECKING:
    from typing import Any


app = typer.Typer(help='Fetch bond metadata by ISIN.')


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


def _dump(payload: dict[str, 'Any'], *, pretty: bool) -> str:
    """Сериализует payload в JSON-текст.

    Args:
        payload: JSON-совместимый словарь.
        pretty: Флаг pretty print.

    Returns:
        str: JSON-текст.
    """
    return json.dumps(payload, ensure_ascii=False, indent=2 if pretty else None)


@app.command('get')
def get(
    isin: str = typer.Option(..., '--isin', help='Bond ISIN'),
    output: Path | None = typer.Option(None, '--output', '-o', help='Path to JSON output file'),
    pretty: bool = typer.Option(True, '--pretty/--no-pretty', help='Pretty print JSON'),
) -> None:
    """Получает данные по одной облигации по ISIN и выводит JSON.

    При отсутствии `output` JSON печатается в stdout, иначе сохраняется в файл.

    Raises:
        typer.Exit: При невалидном ISIN (код 2) или ошибке Use Case (код 1).
    """
    logger = app_container.logger()
    tinkoff = app_container.tinkoff_invest()

    try:
        isin_vo = ISIN(value=isin)
    except Exception as exc:
        logger.error(f'Invalid ISIN provided: {exc!r}')
        raise typer.Exit(code=2) from exc

    uc = GetBondByIsinUseCase(tinkoff=tinkoff, logger=logger)

    try:
        result = asyncio.run(uc.execute(GetBondByIsinInput(isin=isin_vo)))
    except Exception as exc:
        logger.error(f'Failed to run GetBondByIsinUseCase: {exc!r}')
        raise typer.Exit(code=1) from exc

    payload = _json_normalize(asdict(result))
    text = _dump(payload, pretty=pretty)

    if output is None:
        rprint(text)
        return

    write_json_file(obj=payload, path=output)
    rprint(f'Snapshot saved to: {output}')


@app.command('bulk')
def bulk(
    isin: list[str] = typer.Option(..., '--isin', help='Bond ISIN (repeatable)'),
    concurrency: int = typer.Option(5, '--concurrency', help='Max parallel requests'),
    output: Path | None = typer.Option(None, '--output', '-o', help='Path to JSON output file'),
    pretty: bool = typer.Option(True, '--pretty/--no-pretty', help='Pretty print JSON'),
) -> None:
    """Получает данные по нескольким облигациям по списку ISIN и выводит JSON.

    Запросы выполняются параллельно с ограничением `concurrency`. При отсутствии
    `output` JSON печатается в stdout, иначе сохраняется в файл.

    Raises:
        typer.Exit: При невалидном ISIN (код 2) или ошибке Use Case (код 1).
    """
    logger = app_container.logger()
    tinkoff = app_container.tinkoff_invest()

    isins: list[ISIN] = []
    for raw in isin:
        try:
            isins.append(ISIN(value=raw))
        except Exception as exc:
            logger.error(f'Invalid ISIN provided: {raw!r}, error={exc!r}')
            raise typer.Exit(code=2) from exc

    uc = GetBondsByIsinUseCase(tinkoff=tinkoff, logger=logger)

    try:
        result = asyncio.run(uc.execute(GetBondsByIsinInput(isins=tuple(isins), concurrency=concurrency)))
    except Exception as exc:
        logger.error(f'Failed to run GetBondsByIsinUseCase: {exc!r}')
        raise typer.Exit(code=1) from exc

    payload = _json_normalize(asdict(result))
    text = _dump(payload, pretty=pretty)

    if output is None:
        rprint(text)
        return

    write_json_file(obj=payload, path=output)
    rprint(f'Snapshot saved to: {output}')

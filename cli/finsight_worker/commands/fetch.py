"""CLI-команда для загрузки исторических данных."""

from datetime import date
from typing import Annotated  # noqa: TC003

import typer

from src.finsight_worker.domain.value_objects import CandleInterval
from src.finsight_worker.infrastructure.tasks.download_historical_data import register_tasks
from src.finsight_worker.main import celery_app

cli = typer.Typer(no_args_is_help=True)


@cli.command('historical')
def trigger_historical_data_download(
    isin: Annotated[str, typer.Argument(help='ISIN инструмента')],
    from_date: Annotated[str, typer.Argument(help='Дата начала в формате YYYY-MM-DD')],
    to_date: Annotated[str, typer.Argument(help='Дата окончания в формате YYYY-MM-DD')],
    interval: Annotated[CandleInterval, typer.Option(help='Интервал между свечами')] = CandleInterval.DAY,
) -> None:
    """Запускает задачу на загрузку исторических данных по инструменту."""
    try:
        date.fromisoformat(from_date)
        date.fromisoformat(to_date)
    except ValueError as error:
        typer.echo('❌ Неверный формат даты. Используйте YYYY-MM-DD.')
        raise typer.Exit(code=1) from error

    register_tasks(celery_app)

    task = celery_app.send_task(
        name='download_historical_data',
        args=[isin, from_date, to_date, interval.value],
    )

    typer.echo(f'✅ Задача отправлена: task_id={task.id}')

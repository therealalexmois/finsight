"""CLI-команда для загрузки исторических данных."""

from datetime import date
from typing import Annotated  # noqa: TC003

import typer

from finsight_worker.domain.value_objects import CandleInterval
from finsight_worker.infrastructure.tasks.download_historical_data import register_tasks
from finsight_worker.main import celery_app

cli = typer.Typer(no_args_is_help=True)


@cli.command('historical')
def trigger_historical_data_download(
    isin: Annotated[str, typer.Argument(help='ISIN инструмента')],
    from_date: Annotated[str, typer.Argument(help='Дата начала в формате YYYY-MM-DD')],
    to_date: Annotated[str, typer.Argument(help='Дата окончания в формате YYYY-MM-DD')],
    interval: Annotated[CandleInterval, typer.Option(help='Интервал между свечами')] = CandleInterval.DAY,
) -> None:
    """Ставит в очередь Celery-задачу загрузки исторических данных по инструменту.

    Проверяет формат дат, регистрирует задачи в celery_app и отправляет задачу
    download_historical_data.

    Args:
        isin: ISIN инструмента.
        from_date: Дата начала в формате YYYY-MM-DD.
        to_date: Дата окончания в формате YYYY-MM-DD.
        interval: Интервал между свечами.

    Raises:
        typer.Exit: Если формат даты не соответствует YYYY-MM-DD.
    """
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

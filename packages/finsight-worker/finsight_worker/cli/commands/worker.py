"""Команды управления Celery воркером."""

import subprocess
import sys

import typer

cli = typer.Typer(no_args_is_help=True)


@cli.command('start')
def start_worker() -> None:
    """Запускает Celery-воркер для приложения finsight_worker в дочернем процессе.

    Raises:
        typer.Exit: С кодом возврата процесса celery worker.
    """
    typer.echo('🚀 Starting Celery worker...')

    exit_code = subprocess.call(
        [
            sys.executable,
            '-m',
            'celery',
            '-A',
            'finsight_worker.main',
            'worker',
            '--loglevel=info',
        ]
    )

    raise typer.Exit(code=exit_code)

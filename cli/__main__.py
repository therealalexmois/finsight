"""CLI для запуска сервисов FinSight."""

import click


@click.group()
def cli() -> None:
    """Командная оболочка для запуска сервисов FinSight."""
    pass


@cli.command()
def start_api() -> None:
    """Запускает FastAPI-приложение FinSight."""
    # TODO: Replace with actual app startup (e.g., import start_app)
    click.echo('Starting FastAPI application...')


@cli.command()
def start_worker() -> None:
    """Запускает воркер Celery для FinSight."""
    # TODO: Replace with actual Celery worker bootstrapping
    click.echo('Starting Celery worker...')


@cli.command()
@click.argument('isin')
@click.argument('from_date')
@click.argument('to_date')
@click.option('--interval', default='day', help='Candle interval (e.g., day, hour, month)')
def download_historical_data(isin: str, from_date: str, to_date: str, interval: str) -> None:
    """Выгружает исторические свечи для указанного ISIN и диапазона дат."""
    # TODO: Replace with real use case trigger
    click.echo(f'Downloading data for {isin} from {from_date} to {to_date} at {interval} interval...')


if __name__ == '__main__':
    cli()

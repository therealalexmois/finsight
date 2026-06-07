"""Главная точка входа CLI (Command Groups)."""

import typer

from finsight_api.presentation.cli.commands import bonds, portfolio

app = typer.Typer(no_args_is_help=True)

app.add_typer(portfolio, name='portfolio', help='Portfolio utilities and snapshot commands.')
app.add_typer(bonds, name='bonds', help='Fetch bond metadata by identifiers.')


if __name__ == '__main__':
    app()

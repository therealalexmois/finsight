"""CLI команды finsight_api."""

from .portfolio import app as portfolio
from .bonds import app as bonds

__all__ = [
    'bonds',
    'portfolio',
]

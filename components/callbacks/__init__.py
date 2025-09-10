"""
Callbacks package for the investment board application.
"""

from .portfolio_mode import (
    table_control_callbacks,
    alerts_modal_callbacks,
    portfolio_table_callbacks,
    insert_row_callbacks,
)
from . import routing

__all__ = [
    "table_control_callbacks",
    "alerts_modal_callbacks",
    "portfolio_table_callbacks",
    "insert_row_callbacks",
    "routing",
]

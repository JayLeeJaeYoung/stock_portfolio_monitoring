"""
Layouts package for the investment board application.
"""

from .misc_layouts import logo_and_title_layout
from .auth_layouts import login_layout
from .portfolio_mode import (
    table_control_layout,
    alerts_modal,
    portfolio_table_layout,
    insert_row,
)
from .main_layouts import main_app_layout

__all__ = [
    "logo_and_title_layout",
    "login_layout",
    "table_control_layout",
    "alerts_modal",
    "portfolio_table_layout",
    "insert_row",
    "main_app_layout",
]

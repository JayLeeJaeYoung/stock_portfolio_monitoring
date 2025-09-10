import dash_mantine_components as dmc
from utils.enums import FreqMode
from .portfolio_mode import (
    table_control_layout,
    alerts_modal,
    portfolio_table_layout,
    insert_row,
)
from .footer_layouts import footer_layout


def main_app_layout():
    return (
        dmc.Container(
            fluid=True,
            className="no-margin-padding",
            children=[
                dmc.Card(
                    id="main-card",
                    withBorder=True,
                    shadow="sm",
                    radius="md",
                    children=[
                        dmc.Stack(
                            gap="xs",
                            mb=50,
                            children=[
                                table_control_layout(FreqMode.DAILY),
                                portfolio_table_layout(FreqMode.DAILY),
                                insert_row(FreqMode.DAILY),
                                alerts_modal(FreqMode.DAILY),
                            ],
                        ),
                        dmc.Stack(
                            gap="xs",
                            mb=50,
                            children=[
                                table_control_layout(FreqMode.WEEKLY),
                                portfolio_table_layout(FreqMode.WEEKLY),
                                insert_row(FreqMode.WEEKLY),
                                alerts_modal(FreqMode.WEEKLY),
                            ],
                        ),
                        dmc.Stack(
                            gap="xs",
                            mb=50,
                            children=[
                                table_control_layout(FreqMode.MONTHLY),
                                portfolio_table_layout(FreqMode.MONTHLY),
                                insert_row(FreqMode.MONTHLY),
                                alerts_modal(FreqMode.MONTHLY),
                            ],
                        ),
                    ],
                ),
                footer_layout(),
            ],
        ),
    )

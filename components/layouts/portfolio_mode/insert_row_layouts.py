import dash_mantine_components as dmc
from dash import dcc
from utils.enums import FreqMode
from dash_iconify import DashIconify


def insert_row(mode: FreqMode = FreqMode.DAILY):
    return dmc.Stack(
        gap="xs",
        children=[
            # Store component for undo button states across all modes
            dcc.Store(id={"type": "undo-buttons-store", "mode": mode.value}, data=None),
            dmc.Group(
                dmc.Button(
                    id={"type": "insert-row-button", "mode": mode.value},
                    size="xs",
                    radius="md",
                    variant="filled",
                    n_clicks=0,
                    leftSection=DashIconify(
                        icon="fluent-mdl2:insert-rows-below", width=20, height=20
                    ),
                    children=dmc.Text("Insert Row", size="xs"),
                    className="dramatic-hover",
                ),
            ),
            dmc.Collapse(
                opened=False,
                transitionDuration=100,
                id={"type": "insert-row-collapse", "mode": mode.value},
                children=[
                    dmc.Card(
                        id={"type": "insert-row-card", "mode": mode.value},
                        withBorder=True,
                        radius="md",
                        shadow="sm",
                        ml=20,
                        mt=10,
                        mb=10,
                        padding="sm",
                        children=[
                            dmc.Stack(
                                children=[
                                    dmc.Autocomplete(
                                        id={
                                            "type": "insert-row-ticker-search",
                                            "mode": mode.value,
                                        },
                                        label="Search for Ticker",
                                        placeholder="Start typing a company name or ticker ...",
                                        style={"width": 500},
                                        data=[],
                                        rightSection=DashIconify(
                                            icon="tabler:search", width=20
                                        ),
                                        limit=20,
                                        value="",
                                    ),
                                    dmc.Group(
                                        gap="xs",
                                        children=[
                                            dmc.ChipGroup(
                                                id={
                                                    "type": "watch-or-own-chip-group",
                                                    "mode": mode.value,
                                                },
                                                value="watch",
                                                children=[
                                                    dmc.Chip(
                                                        "Watch",
                                                        id={
                                                            "type": "watch-chip",
                                                            "mode": mode.value,
                                                        },
                                                        value="watch",
                                                        icon=DashIconify(
                                                            icon="mdi:eye-outline",
                                                        ),
                                                        disabled=True,
                                                    ),
                                                    dmc.Chip(
                                                        "Own",
                                                        id={
                                                            "type": "own-chip",
                                                            "mode": mode.value,
                                                        },
                                                        value="own",
                                                        icon=DashIconify(
                                                            icon="mdi:briefcase-outline",
                                                        ),
                                                        disabled=True,
                                                    ),
                                                ],
                                            )
                                        ],
                                    ),
                                    dmc.Collapse(
                                        id={
                                            "type": "holding-info-collapse",
                                            "mode": mode.value,
                                        },
                                        opened=False,
                                        transitionDuration=100,
                                        children=[
                                            dmc.Fieldset(
                                                id={
                                                    "type": "holding-info-fieldset",
                                                    "mode": mode.value,
                                                },
                                                legend="Holding Info (Required)",
                                                disabled=True,
                                                children=[
                                                    dmc.Group(
                                                        children=[
                                                            dmc.NumberInput(
                                                                id={
                                                                    "type": "avg-buy-price",
                                                                    "mode": mode.value,
                                                                },
                                                                label="Average Buy Price",
                                                                decimalScale=3,
                                                                min=0.001,
                                                                step=0.001,
                                                                # description="(Required)",
                                                                # style={"width": 200},
                                                            ),
                                                            dmc.NumberInput(
                                                                id={
                                                                    "type": "position-quantity",
                                                                    "mode": mode.value,
                                                                },
                                                                label="Position Quantity",
                                                                min=1,
                                                                step=1,
                                                                # description="(Required)",
                                                                # style={"width": 200},
                                                            ),
                                                        ]
                                                    )
                                                ],
                                            )
                                        ],
                                    ),
                                    dmc.Group(
                                        gap="md",
                                        children=[
                                            dmc.Fieldset(
                                                id={
                                                    "type": "personal-preference-fieldset",
                                                    "mode": mode.value,
                                                },
                                                legend="Personal Preference (Optional)",
                                                disabled=True,
                                                children=[
                                                    dmc.Group(
                                                        gap="md",
                                                        children=[
                                                            dmc.NumberInput(
                                                                id={
                                                                    "type": "priority-input",
                                                                    "mode": mode.value,
                                                                },
                                                                label="Priority (0 ~ 100)",
                                                                min=0,
                                                                max=100,
                                                                step=1,
                                                            ),
                                                            dmc.NumberInput(
                                                                id={
                                                                    "type": "price-upper-target-input",
                                                                    "mode": mode.value,
                                                                },
                                                                label="Price Upper Target",
                                                                min=0.01,
                                                                step=0.01,
                                                            ),
                                                            dmc.NumberInput(
                                                                id={
                                                                    "type": "price-lower-target-input",
                                                                    "mode": mode.value,
                                                                },
                                                                label="Price Lower Target",
                                                                min=0.01,
                                                                step=0.01,
                                                            ),
                                                        ],
                                                    )
                                                ],
                                            ),
                                        ],
                                    ),
                                    dmc.Group(
                                        children=[
                                            dmc.Button(
                                                "Submit",
                                                disabled=True,
                                                n_clicks=0,
                                                id={
                                                    "type": "insert-row-submit-button",
                                                    "mode": mode.value,
                                                },
                                            ),
                                            dmc.Button(
                                                "Cancel",
                                                n_clicks=0,
                                                color="red",
                                                variant="outline",
                                                id={
                                                    "type": "insert-row-cancel-button",
                                                    "mode": mode.value,
                                                },
                                            ),
                                        ]
                                    ),
                                ]
                            )
                        ],
                    )
                ],
            ),
        ],
    )

import dash_mantine_components as dmc
from utils.enums import FreqMode
from dash_iconify import DashIconify
from components.layouts.misc_layouts import logo_and_title_layout


def table_control_layout(mode: FreqMode = FreqMode.DAILY):

    table_title = mode.name.capitalize() + " Portfolio"

    return dmc.Group(
        gap="xs",
        mt="xs",
        ml=20,
        mr=100,
        justify="space-between",
        children=[
            dmc.Group(
                gap="xs",
                mr=100,
                children=[
                    dmc.Button(
                        id={"type": "reload-button", "mode": mode.value},
                        size="xs",
                        radius="md",
                        variant="filled",
                        n_clicks=0,
                        leftSection=DashIconify(
                            icon="subway:cloud-reload", width=20, height=20
                        ),
                        children=dmc.Text("Reload", size="xs"),
                        className="dramatic-hover",
                    ),
                    dmc.Button(
                        id={"type": "undo-button", "mode": mode.value},
                        size="xs",
                        radius="md",
                        variant="filled",
                        disabled=True,
                        n_clicks=0,
                        leftSection=DashIconify(
                            icon="solar:undo-left-round-square-outline",
                            width=20,
                            height=20,
                        ),
                        children=dmc.Text("Undo", size="xs"),
                        className="dramatic-hover",
                    ),
                    dmc.Button(
                        id={"type": "clear-sort-button", "mode": mode.value},
                        size="xs",
                        radius="md",
                        variant="filled",
                        n_clicks=0,
                        leftSection=DashIconify(
                            icon="material-symbols:restart-alt-rounded",
                            width=20,
                            height=20,
                        ),
                        disabled=True,
                        children=dmc.Text("Clear Sort", size="xs"),
                        className="dramatic-hover",
                    ),
                ],
            ),
            dmc.Title(
                table_title,
                order=3,
                className="title-font",
            ),
            logo_and_title_layout("small"),
        ],
    )

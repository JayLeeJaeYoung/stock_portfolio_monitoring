import dash_mantine_components as dmc
from components.layouts.misc_layouts import logo_and_title_layout
from dash_iconify import DashIconify


def footer_layout():
    return dmc.Group(
        mt=50,
        mb=50,
        mr=100,
        children=[
            dmc.Card(
                id="app-title-card",
                withBorder=True,
                radius="md",
                shadow="sm",
                ml=20,
                mt=10,
                mb=10,
                padding="sm",
                children=[logo_and_title_layout("large")],
            ),
            dmc.Button(
                "Logout",
                id="logout-button",
                leftSection=DashIconify(icon="tabler:logout", width=20, height=20),
                n_clicks=0,
                className="dramatic-hover",
            ),
        ],
    )

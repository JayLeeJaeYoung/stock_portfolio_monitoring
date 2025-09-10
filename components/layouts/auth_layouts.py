import dash_mantine_components as dmc
from components.layouts.misc_layouts import logo_and_title_layout
from dash_iconify import DashIconify


def login_layout():
    return dmc.Container(
        size=400,
        children=dmc.Stack(
            # align="center",
            children=[
                logo_and_title_layout("large"),
                dmc.TextInput(id="username", label="Username", required=True),
                dmc.PasswordInput(id="password", label="Password", required=True),
                dmc.Button(
                    "Login",
                    id="login-button",
                    n_clicks=0,
                    disabled=True,
                    style={"marginTop": 5},
                    leftSection=DashIconify(icon="tabler:login", width=20, height=20),
                ),
                dmc.Text(id="login-error-message", c="red", fw=600),
            ]
        ),
        style={"marginTop": 100},
    )

from components.callbacks.portfolio_mode import (
    alerts_modal_callbacks,
    insert_row_callbacks,
    portfolio_table_callbacks,
    table_control_callbacks,
)
from components.callbacks import routing
from components.layouts.mantine_theme import mantine_theme

from dash import Dash, dcc
import dash_mantine_components as dmc
import flask
from datetime import timedelta
import os
from dotenv import load_dotenv
from utils.cache_setup import background_callback_manager


# load env variables
load_dotenv()


flask_server = flask.Flask(__name__)
flask_server.secret_key = os.getenv("FLASK_SECRET_KEY")
flask_server.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=365 * 100)

app = Dash(
    __name__,
    server=flask_server,
    title="Investment Board",
    suppress_callback_exceptions=True,
    external_stylesheets=[dmc.styles.ALL],
    prevent_initial_callbacks=True,
    background_callback_manager=background_callback_manager,
)


app.layout = dmc.MantineProvider(
    theme=mantine_theme,
    children=[
        dcc.Location(id="url", refresh=True),
        dmc.Container(className="no-margin-padding", fluid=True, id="app-content"),
    ],
)

server = app.server


if __name__ == "__main__":
    app.run(debug=True)

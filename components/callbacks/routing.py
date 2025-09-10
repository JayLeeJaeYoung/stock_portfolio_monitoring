from components.layouts import main_app_layout, login_layout
from dash import callback, Output, Input, State, no_update
from dash.exceptions import PreventUpdate
import flask
import bcrypt
from models.models import get_data_list, get_alert_list
from models.database import get_db_connection
from utils.enums import FreqMode


mongodb = get_db_connection()


@callback(
    Output("login-button", "disabled", allow_duplicate=True),
    Output("login-error-message", "children", allow_duplicate=True),
    Input("username", "value"),
    Input("password", "value"),
    prevent_initial_call=True,
)
def login_button_disabled(username, password):
    return not (username and password), ""


def _authenticate_user(username, password):
    try:
        users_collection = mongodb["users"]
        user = users_collection.find_one({"username": username})
        if user is None:
            return False
        result = bcrypt.checkpw(password.encode("utf-8"), user["password_hash"])
        return result
    except Exception as e:
        print(f"Authentication error: {e}")
        raise e


@callback(
    Output("url", "pathname", allow_duplicate=True),
    Output("login-error-message", "children", allow_duplicate=True),
    Input("login-button", "n_clicks"),
    State("username", "value"),
    State("password", "value"),
    prevent_initial_call=True,
)
def login_submit(n_clicks, username, password):
    """Handle user login: authenticate credentials and create session"""
    if n_clicks == 0:
        raise PreventUpdate

    try:
        if _authenticate_user(username, password):
            flask.session["user"] = username
            flask.session.permanent = True
            return "/main", ""
        else:
            return no_update, "Invalid username or password"
    except Exception as e:
        print(f"Login error: {e}")
        return no_update, f"Login error: {str(e)}"


@callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("logout-button", "n_clicks"),
    prevent_initial_call=True,
)
def logout_submit(n_clicks):
    """Handle user logout: clear cache and session, redirect to login"""
    if n_clicks == 0:
        raise PreventUpdate

    try:
        from utils.cache_setup import cache
        cache.clear()
    except Exception as e:
        print(f"[LOGOUT] Error clearing cache: {e}")

    flask.session.clear()
    return "/"


@callback(
    Output("app-content", "children", allow_duplicate=True),
    Output("url", "pathname", allow_duplicate=True),
    Input("url", "pathname"),
    prevent_initial_call=True,
)
def render_routes(pathname):
    if flask.session.get("user"):
        if pathname == "/main":
            username = flask.session.get("user")
            dl = get_data_list(FreqMode.DAILY)
            al = get_alert_list(FreqMode.DAILY)
            dl.update_username(username)
            al.update_username(username)
            return main_app_layout(), no_update
        else:
            return no_update, "/main"

    else:
        if pathname == "/":
            return login_layout(), no_update
        else:
            return no_update, "/"

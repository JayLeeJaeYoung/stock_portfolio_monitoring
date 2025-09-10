from dash import callback, Output, Input, State, MATCH, Patch
from dash.exceptions import PreventUpdate
from models.models import get_data_list
from utils.enums import FreqMode


@callback(
    Output({"type": "portfolio-table", "mode": MATCH}, "rowData", allow_duplicate=True),
    Input({"type": "reload-button", "mode": MATCH}, "n_clicks"),
    State({"type": "reload-button", "mode": MATCH}, "id"),
    prevent_initial_call=True,
    allow_duplicate=True,
)
def reload_button_click(n_clicks, component_id):
    mode = component_id["mode"]

    if n_clicks == 0:
        raise PreventUpdate

    rowData = get_data_list(FreqMode(mode)).refresh_all()
    return rowData


@callback(
    Output({"type": "reload-button", "mode": MATCH}, "disabled", allow_duplicate=True),
    Input({"type": "portfolio-table", "mode": MATCH}, "rowData"),
    prevent_initial_call=True,
    allow_duplicate=True,
)
def reload_button_disabled(rowData):
    return False if rowData else True


@callback(
    Output({"type": "portfolio-table", "mode": MATCH}, "rowData", allow_duplicate=True),
    Output({"type": "undo-button", "mode": MATCH}, "disabled", allow_duplicate=True),
    Input({"type": "undo-button", "mode": MATCH}, "n_clicks"),
    State({"type": "undo-button", "mode": MATCH}, "id"),
    prevent_initial_call=True,
    allow_duplicate=True,
)
def undo_button_click(n_clicks, component_id):
    mode = component_id["mode"]

    if n_clicks == 0:
        raise PreventUpdate

    dl = get_data_list(FreqMode(mode))
    new_row = dl.restore_latest_ticker()
    rowData = Patch()
    rowData.append(new_row)

    undo_disabled = dl.is_trash_empty()

    return rowData, undo_disabled


@callback(
    Output(
        {"type": "clear-sort-button", "mode": MATCH}, "disabled", allow_duplicate=True
    ),
    Input({"type": "portfolio-table", "mode": MATCH}, "columnState"),
    prevent_initial_call=True,
    allow_duplicate=True,
)
def clear_sort_button_disabled(col_state):
    for col in col_state:
        if col.get("sort", None) is not None or col.get("sortIndex", None) is not None:
            return False
    return True


@callback(
    Output(
        {"type": "portfolio-table", "mode": MATCH}, "columnState", allow_duplicate=True
    ),
    Input({"type": "clear-sort-button", "mode": MATCH}, "n_clicks"),
    State({"type": "portfolio-table", "mode": MATCH}, "columnState"),
    prevent_initial_call=True,
    allow_duplicate=True,
)
def clear_sort(n_clicks, col_state):
    if n_clicks == 0:
        raise PreventUpdate

    for col in col_state:
        col["sort"] = None
        col["sortIndex"] = None

    return col_state

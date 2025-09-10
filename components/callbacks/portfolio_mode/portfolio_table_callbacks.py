from dash import callback, Output, Input, State, no_update, MATCH
from dash.exceptions import PreventUpdate
from models.models import get_data_list, get_alert_list
from .alerts_modal_callbacks import create_alert_card
from utils.enums import FreqMode

# Database access now goes through models.py
# No need for direct database imports or get_db_connection calls


@callback(
    Output({"type": "portfolio-table", "mode": MATCH}, "rowData", allow_duplicate=True),
    Input({"type": "portfolio-table", "mode": MATCH}, "cellValueChanged"),
    State({"type": "portfolio-table", "mode": MATCH}, "rowData"),
    State({"type": "portfolio-table", "mode": MATCH}, "id"),
    prevent_initial_call=True,
    allow_duplicate=True,
)
def user_edit_cell(event, rowData, component_id):
    mode = component_id["mode"]

    if event is None:
        raise PreventUpdate

    output = event[0]["data"]
    ticker = output["ticker"]
    key_to_update = event[0]["colId"]
    new_value = event[0]["value"]

    dl = get_data_list(FreqMode(mode))
    new_row = dl.update_user_input(ticker, key_to_update, new_value)

    for i, item in enumerate(rowData):
        if item.get("ticker") == ticker:
            rowData[i] = new_row
            break

    return rowData


@callback(
    Output({"type": "portfolio-table", "mode": MATCH}, "rowData", allow_duplicate=True),
    Output({"type": "undo-button", "mode": MATCH}, "disabled", allow_duplicate=True),
    Output({"type": "alert-modal", "mode": MATCH}, "opened", allow_duplicate=True),
    Output(
        {"type": "alert-modal-header", "mode": MATCH}, "children", allow_duplicate=True
    ),
    Output(
        {"type": "alert-modal-exiting-alerts", "mode": MATCH},
        "children",
        allow_duplicate=True,
    ),
    Input({"type": "portfolio-table", "mode": MATCH}, "cellRendererData"),
    State({"type": "portfolio-table", "mode": MATCH}, "rowData"),
    State({"type": "portfolio-table", "mode": MATCH}, "id"),
    prevent_initial_call=True,
    allow_duplicate=True,
)
def table_action_button_clicked(event, rowData, component_id):
    """Handle clicks on table action buttons (refresh, trash, alert)"""
    mode = component_id["mode"]

    if event["value"]["n_clicks"] == 0:
        raise PreventUpdate

    ticker = event["rowId"]

    dl = get_data_list(FreqMode(mode))
    al = get_alert_list(FreqMode(mode))

    if event["colId"] == "refreshButton":
        new_row = dl.refresh_one_ticker(ticker)
        rowData = [new_row if row.get("ticker") == ticker else row for row in rowData]
        return rowData, no_update, no_update, no_update, no_update
    elif event["colId"] == "trashButton":
        dl.delete(ticker)
        rowData = [row for row in rowData if row.get("ticker") != ticker]
        undo_disabled = dl.is_trash_empty()
        return rowData, undo_disabled, no_update, no_update, no_update

    elif event["colId"] == "alertButton":
        alert_header = f"Alerts: {ticker}"
        alert_data_list = al.read(ticker)
        cards = [create_alert_card(alert, mode) for alert in alert_data_list]

        return no_update, no_update, True, alert_header, cards
    else:
        raise PreventUpdate

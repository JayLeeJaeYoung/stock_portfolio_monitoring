import dash_mantine_components as dmc
from dash import callback, Output, Input, State, ALL, no_update, ctx, MATCH
from dash.exceptions import PreventUpdate
from models.models import get_data_list, get_alert_list
from utils.enums import FreqMode

# Database access now goes through models.py
# No need for direct database imports or get_db_connection calls


def create_alert_card(alert, mode):
    alert_id = str(alert["_id"])
    created_time = alert.get("created_time")
    alert_description = alert.get("alert_description")
    lower_price = alert.get("lower_alert_price", "—")
    lower_note = alert.get("lower_alert_note", "—")
    upper_price = alert.get("upper_alert_price", "—")
    upper_note = alert.get("upper_alert_note", "—")
    triggered_date = alert.get("triggered_date")

    created_time = created_time.strftime("%Y-%m-%d %H:%M:%S")

    if triggered_date:
        triggered_date = triggered_date.strftime("%Y-%m-%d %H:%M:%S")
        border_color = "#FF6B6B"

    else:
        triggered_date = "Not triggered"
        border_color = "#228BE6"

    return dmc.Card(
        id={"type": "alert-data-card", "index": alert_id, "mode": mode},
        withBorder=True,
        shadow="sm",
        radius="md",
        style={"border": f"2px solid {border_color}"},
        children=[
            dmc.Fieldset(
                legend=f"Created at: {created_time}",
                children=[
                    dmc.Text("Description", size="sm"),
                    dmc.Text(alert_description, size="xs"),
                    dmc.Group(
                        grow=True,
                        children=[
                            dmc.NumberInput(
                                label="Trigger below",
                                value=lower_price,
                                disabled=True,
                                className="input-width",
                            ),
                            dmc.TextInput(
                                label="Note",
                                value=lower_note,
                                disabled=True,
                                className="textinput-width",
                            ),
                        ],
                    ),
                    dmc.Group(
                        grow=True,
                        children=[
                            dmc.NumberInput(
                                label="Trigger above",
                                value=upper_price,
                                disabled=True,
                                className="input-width",
                            ),
                            dmc.TextInput(
                                label="Note",
                                value=upper_note,
                                disabled=True,
                                className="textinput-width",
                            ),
                        ],
                    ),
                    dmc.Text(f"Triggered at: {triggered_date}", mt="sm"),
                    dmc.Button(
                        "Remove",
                        id={
                            "type": "alert-data-remove-button",
                            "index": alert_id,
                            "mode": mode,
                        },
                        color="red",
                        mt=10,
                        n_clicks=0,
                    ),
                ],
            )
        ],
    )


@callback(
    Output(
        {"type": "alert-modal-exiting-alerts", "mode": MATCH}, "children", allow_duplicate=True,
    ),
    Output({"type": "portfolio-table", "mode": MATCH}, "rowData", allow_duplicate=True),
    Output(
        {"type": "portfolio-table", "mode": MATCH},
        "dashGridOptions",
        allow_duplicate=True,
    ),
    Input(
        {"type": "alert-data-remove-button", "index": ALL, "mode": MATCH}, "n_clicks"
    ),
    State({"type": "portfolio-table", "mode": MATCH}, "rowData"),
    # needed to force re-render AlertIcon when rowData changes
    State({"type": "portfolio-table", "mode": MATCH}, "dashGridOptions"),
    State({"type": "alert-data-remove-button", "index": ALL, "mode": MATCH}, "id"),
    prevent_initial_call=True,
    allow_duplicate=True,
)
def delete_alert(n_clicks_list, rowData, grid_options, component_ids):
    """Delete an alert and update portfolio table alert count"""
    mode = component_ids[0]["mode"] if component_ids else 1

    if all(x == 0 for x in n_clicks_list):
        raise PreventUpdate

    if not ctx.triggered:
        raise PreventUpdate

    triggered_id = ctx.triggered_id
    if (
        not isinstance(triggered_id, dict)
        or "index" not in triggered_id
        or triggered_id["type"] != "alert-data-remove-button"
    ):
        raise PreventUpdate

    alert_id = triggered_id["index"]
    al = get_alert_list(FreqMode(mode))
    ticker, alert_data_list = al.delete_one_alert(alert_id)
    cards = [create_alert_card(alert, mode) for alert in alert_data_list]

    alert_count = len(alert_data_list)
    dl = get_data_list(FreqMode(mode))
    new_row = dl.update_alert_count(ticker, alert_count)

    for i, item in enumerate(rowData):
        if item.get("ticker") == ticker:
            rowData[i] = new_row
            break

    # Force grid to refresh by toggling a grid option
    updated_options = grid_options.copy()
    updated_options["suppressPropertyNamesCheck"] = not updated_options.get(
        "suppressPropertyNamesCheck", False
    )

    return cards, rowData, updated_options


@callback(
    Output({"type": "alert-modal", "mode": MATCH}, "opened", allow_duplicate=True),
    Output({"type": "alert-description-input", "mode": MATCH}, "value"),
    Output({"type": "trigger-below-input", "mode": MATCH}, "value"),
    Output({"type": "trigger-below-note", "mode": MATCH}, "value"),
    Output({"type": "trigger-above-input", "mode": MATCH}, "value"),
    Output({"type": "trigger-above-note", "mode": MATCH}, "value"),
    Output(
        {"type": "alert-modal-exiting-alerts", "mode": MATCH},
        "children",
        allow_duplicate=True,
    ),
    Output({"type": "portfolio-table", "mode": MATCH}, "rowData", allow_duplicate=True),
    Output(
        {"type": "portfolio-table", "mode": MATCH},
        "dashGridOptions",
        allow_duplicate=True,
    ),
    Input({"type": "alert-modal-submit-button", "mode": MATCH}, "n_clicks"),
    Input({"type": "alert-modal-cancel-button", "mode": MATCH}, "n_clicks"),
    State({"type": "alert-description-input", "mode": MATCH}, "value"),
    State({"type": "trigger-below-input", "mode": MATCH}, "value"),
    State({"type": "trigger-below-note", "mode": MATCH}, "value"),
    State({"type": "trigger-above-input", "mode": MATCH}, "value"),
    State({"type": "trigger-above-note", "mode": MATCH}, "value"),
    State({"type": "alert-modal-header", "mode": MATCH}, "children"),
    State({"type": "portfolio-table", "mode": MATCH}, "rowData"),
    State({"type": "portfolio-table", "mode": MATCH}, "dashGridOptions"),
    State({"type": "alert-modal-submit-button", "mode": MATCH}, "id"),
    prevent_initial_call=True,
    allow_duplicate=True,
)
def alert_modal_submit(
    submit_clicked,
    cancel_clicked,
    alert_description,
    lower_trigger,
    lower_trigger_note,
    upper_trigger,
    upper_trigger_note,
    alert_header,
    rowData,
    grid_options,
    component_id,
):
    """Handle alert modal submission: create new alert and update portfolio table"""
    mode = component_id["mode"]

    if not ctx.triggered:
        raise PreventUpdate

    if submit_clicked == 0 and cancel_clicked == 0:
        raise PreventUpdate

    if ctx.triggered_id["type"] == "alert-modal-cancel-button":
        return False, "", "", "", "", "", no_update, no_update, no_update

    ticker = alert_header.split("Alerts:")[1].strip()

    al = get_alert_list(FreqMode(mode))
    alert_data_list = al.append(
        ticker,
        alert_description,
        lower_trigger,
        lower_trigger_note,
        upper_trigger,
        upper_trigger_note,
    )

    cards = [create_alert_card(alert, mode) for alert in alert_data_list]

    alert_count = len(alert_data_list)
    dl = get_data_list(FreqMode(mode))
    new_row = dl.update_alert_count(ticker, alert_count)

    for i, item in enumerate(rowData):
        if item.get("ticker") == ticker:
            rowData[i] = new_row
            break

    # Force grid to refresh by toggling a grid option
    updated_options = grid_options.copy()
    updated_options["suppressPropertyNamesCheck"] = not updated_options.get(
        "suppressPropertyNamesCheck", False
    )

    return True, "", "", "", "", "", cards, rowData, updated_options


@callback(
    Output(
        {"type": "alert-modal-submit-button", "mode": MATCH},
        "disabled",
        allow_duplicate=True,
    ),
    Input({"type": "trigger-below-input", "mode": MATCH}, "value"),
    Input({"type": "trigger-above-input", "mode": MATCH}, "value"),
    prevent_initial_call=True,
    allow_duplicate=True,
)
def toggle_modal_submit_enable(lower_trigger, upper_trigger):
    return not (
        (isinstance(lower_trigger, (int, float)) and lower_trigger > 0)
        or (isinstance(upper_trigger, (int, float)) and upper_trigger > 0)
    )


@callback(
    Output({"type": "alert-modal", "mode": MATCH}, "opened", allow_duplicate=True),
    Input({"type": "alert-modal-cancel-button", "mode": MATCH}, "n_clicks"),
    prevent_initial_call=True,
    allow_duplicate=True,
)
def close_alert_modal(n_clicks):
    if n_clicks == 0:
        raise PreventUpdate

    return False

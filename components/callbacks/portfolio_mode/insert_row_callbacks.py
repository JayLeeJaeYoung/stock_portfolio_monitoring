from utils.reference import YAHOO_SEARCH_URL
import requests
from dash import callback, Output, Input, State, ctx, MATCH, ALL
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from models.models import get_data_list
from utils.enums import FreqMode

# Database access now goes through models.py
# No need for direct database imports or get_db_connection calls


@callback(
    Output(
        {"type": "insert-row-ticker-search", "mode": MATCH},
        "data",
        allow_duplicate=True,
    ),
    Input({"type": "insert-row-ticker-search", "mode": MATCH}, "value"),
    prevent_initial_call=True,
    allow_duplicate=True,
)
def update_ticker_suggestions(search_value):
    if not search_value or len(search_value) < 2:
        return []
    try:
        url = f"{YAHOO_SEARCH_URL}{search_value}"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        quotes = r.json().get("quotes", [])

        suggestions = []
        seen = set()

        for q in quotes:
            if "symbol" in q:
                exch = q.get("exchDisp", "No Exchange")
                name = q.get("shortname", "")
                suggestion = f"{q['symbol']} ({exch}): {name}"
                if suggestion not in seen:
                    seen.add(suggestion)
                    suggestions.append(suggestion)

        return suggestions

    except:
        return []


@callback(
    Output(
        {"type": "insert-row-ticker-search", "mode": MATCH},
        "error",
        allow_duplicate=True,
    ),
    Output(
        {"type": "insert-row-ticker-search", "mode": MATCH},
        "rightSection",
        allow_duplicate=True,
    ),
    Output(
        {"type": "insert-row-ticker-search", "mode": MATCH}, "sx", allow_duplicate=True
    ),
    Output({"type": "watch-chip", "mode": MATCH}, "disabled", allow_duplicate=True),
    Output({"type": "own-chip", "mode": MATCH}, "disabled", allow_duplicate=True),
    Output(
        {"type": "holding-info-fieldset", "mode": MATCH},
        "disabled",
        allow_duplicate=True,
    ),
    Output(
        {"type": "personal-preference-fieldset", "mode": MATCH},
        "disabled",
        allow_duplicate=True,
    ),
    Input({"type": "insert-row-ticker-search", "mode": MATCH}, "value"),
    State({"type": "insert-row-ticker-search", "mode": MATCH}, "data"),
    State({"type": "insert-row-ticker-search", "mode": MATCH}, "id"),
    prevent_initial_call=True,
    allow_duplicate=True,
)
def validate_ticker(value, suggestions, component_id):
    """Validate ticker input and enable/disable form fields accordingly"""
    mode = component_id["mode"]

    if not value:
        placeholder_icon = DashIconify(icon="tabler:search", width=20)
        return "", placeholder_icon, {}, True, True, True, True

    is_valid = suggestions and (value in suggestions)
    x_icon = DashIconify(icon="tabler:circle-x", width=20)

    if not is_valid:
        return "Invalid Ticker", x_icon, {}, True, True, True, True

    ticker = value.split(" ", 1)[0]

    # ticker cannot be duplicated
    dl = get_data_list(FreqMode(mode))
    if dl.is_duplicate(ticker):
        return "Duplicate Ticker", x_icon, {}, True, True, True, True

    check_icon = DashIconify(icon="tabler:check", width=20)
    teal_hex = "#12B886"

    return (
        "",
        check_icon,
        {
            "& .mantine-Autocomplete-input": {"borderColor": f"{teal_hex} !important"},
        },
        False,
        False,
        False,
        False,
    )


@callback(
    Output(
        {"type": "holding-info-collapse", "mode": MATCH}, "opened", allow_duplicate=True
    ),
    Input({"type": "watch-or-own-chip-group", "mode": MATCH}, "value"),
    prevent_initial_call=True,
    allow_duplicate=True,
)
def toggle_position_fieldset(value):
    return value == "own"


@callback(
    Output(
        {"type": "insert-row-submit-button", "mode": MATCH},
        "disabled",
        allow_duplicate=True,
    ),
    Input({"type": "watch-chip", "mode": MATCH}, "disabled"),
    Input({"type": "own-chip", "mode": MATCH}, "disabled"),
    Input({"type": "watch-or-own-chip-group", "mode": MATCH}, "value"),
    Input({"type": "avg-buy-price", "mode": MATCH}, "value"),
    Input({"type": "position-quantity", "mode": MATCH}, "value"),
    prevent_initial_call=True,
    allow_duplicate=True,
)
def toggle_submit_enable(watch_disabled, own_disabled, chip_value, avg_price, quantity):
    if watch_disabled and own_disabled:
        return True

    if chip_value == "own":
        try:
            avg_price = float(avg_price)
            quantity = int(quantity)
        except (ValueError, TypeError):
            return True

        if avg_price <= 0 or quantity <= 0:
            return True
    return False


@callback(
    Output(
        {"type": "insert-row-button", "mode": MATCH}, "disabled", allow_duplicate=True
    ),
    Output(
        {"type": "insert-row-collapse", "mode": MATCH}, "opened", allow_duplicate=True
    ),
    Input({"type": "insert-row-button", "mode": MATCH}, "n_clicks"),
    Input({"type": "insert-row-cancel-button", "mode": MATCH}, "n_clicks"),
    prevent_initial_call=True,
    allow_duplicate=True,
)
def toggle_insert_row_input(insert_row_clicks, cancel_clicks):
    if not ctx.triggered:
        raise PreventUpdate

    if insert_row_clicks == 0 and cancel_clicks == 0:
        raise PreventUpdate

    if ctx.triggered_id["type"] == "insert-row-button":
        return True, True
    return False, False


def parse_number(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


@callback(
    Output(
        {"type": "insert-row-button", "mode": MATCH}, "disabled", allow_duplicate=True
    ),
    Output(
        {"type": "insert-row-collapse", "mode": MATCH}, "opened", allow_duplicate=True
    ),
    Output({"type": "portfolio-table", "mode": MATCH}, "rowData", allow_duplicate=True),
    Output(
        {"type": "insert-row-ticker-search", "mode": MATCH},
        "value",
        allow_duplicate=True,
    ),
    Output({"type": "avg-buy-price", "mode": MATCH}, "value", allow_duplicate=True),
    Output({"type": "position-quantity", "mode": MATCH}, "value", allow_duplicate=True),
    Output({"type": "priority-input", "mode": MATCH}, "value", allow_duplicate=True),
    Output(
        {"type": "price-upper-target-input", "mode": MATCH},
        "value",
        allow_duplicate=True,
    ),
    Output(
        {"type": "price-lower-target-input", "mode": MATCH},
        "value",
        allow_duplicate=True,
    ),
    Output({"type": "undo-buttons-store", "mode": MATCH}, "data", allow_duplicate=True),
    Input({"type": "insert-row-submit-button", "mode": MATCH}, "n_clicks"),
    State({"type": "insert-row-ticker-search", "mode": MATCH}, "value"),
    State({"type": "watch-or-own-chip-group", "mode": MATCH}, "value"),
    State({"type": "avg-buy-price", "mode": MATCH}, "value"),
    State({"type": "position-quantity", "mode": MATCH}, "value"),
    State({"type": "priority-input", "mode": MATCH}, "value"),
    State({"type": "price-upper-target-input", "mode": MATCH}, "value"),
    State({"type": "price-lower-target-input", "mode": MATCH}, "value"),
    State({"type": "portfolio-table", "mode": MATCH}, "rowData"),
    State({"type": "insert-row-submit-button", "mode": MATCH}, "id"),
    prevent_initial_call=True,
    allow_duplicate=True,
)
def handle_insert_row_submit(
    n_clicks,
    ticker_value,
    chip_value,
    avg_price,
    quantity,
    priority,
    price_upper_target,
    price_lower_target,
    rowData,
    component_id,
):
    """Process form submission and add new ticker to portfolio table"""
    if n_clicks == 0:
        raise PreventUpdate

    mode = component_id["mode"]
    dl = get_data_list(FreqMode(mode))

    ticker = ticker_value.split(" ")[0]
    user_input = {
        "ticker": ticker,
        "priority": parse_number(priority),
        "priceUpperTarget": parse_number(price_upper_target),
        "priceLowerTarget": parse_number(price_lower_target),
    }

    if chip_value == "own":
        user_input.update(
            {
                "averageBuyPrice": parse_number(avg_price),
                "positionQuantity": parse_number(quantity),
            }
        )

    rowData.append(dl.append(user_input))

    # Get undo button states for all modes and store them
    undo_states = dl.is_all_trash_empty()

    return False, False, rowData, "", "", "", "", "", "", undo_states


@callback(
    Output({"type": "undo-button", "mode": ALL}, "disabled", allow_duplicate=True),
    Input({"type": "undo-buttons-store", "mode": ALL}, "data"),
    prevent_initial_call=True,
    allow_duplicate=True,
)
def update_all_undo_buttons_from_store(undo_states_list):
    """Update all undo buttons based on stored data from any mode"""
    if not undo_states_list or not any(undo_states_list):
        raise PreventUpdate

    # Get the first non-None undo_states from any mode
    undo_states = None
    for states in undo_states_list:
        if states is not None:
            undo_states = states
            break

    if undo_states is None:
        raise PreventUpdate

    return undo_states

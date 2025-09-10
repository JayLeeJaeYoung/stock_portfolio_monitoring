import dash_mantine_components as dmc
from utils.enums import FreqMode


def alerts_modal(mode: FreqMode = FreqMode.DAILY):
    return dmc.Modal(
        id={"type": "alert-modal", "mode": mode.value},
        centered=True,
        size="700px",
        opened=False,
        withCloseButton=False,
        closeOnClickOutside=False,
        closeOnEscape=False,
        children=[
            dmc.Text(
                id={"type": "alert-modal-header", "mode": mode.value},
                children="Ticker: ---",  # to be updated via callback
                size="lg",
                mb="md",
                fw=800,
            ),
            dmc.Card(
                withBorder=True,
                shadow="sm",
                radius="md",
                children=[
                    # Placeholder for extra Stack (empty for now)
                    dmc.Stack(
                        id={"type": "alert-modal-exiting-alerts", "mode": mode.value},
                        children=[],
                        mb="md",
                    ),
                    dmc.Stack(
                        children=[
                            dmc.Fieldset(
                                legend="Add New Alert",
                                children=[
                                    dmc.TextInput(
                                        id={
                                            "type": "alert-description-input",
                                            "mode": mode.value,
                                        },
                                        label="Alert Description",
                                        placeholder="Enter a description for the alert...",
                                        style={"width": "100%"},
                                    ),
                                    dmc.Group(
                                        grow=True,
                                        children=[
                                            dmc.NumberInput(
                                                id={
                                                    "type": "trigger-below-input",
                                                    "mode": mode.value,
                                                },
                                                label="Trigger below",
                                                decimalScale=2,
                                                min=0.01,
                                                step=0.01,
                                                className="input-width",
                                            ),
                                            dmc.TextInput(
                                                id={
                                                    "type": "trigger-below-note",
                                                    "mode": mode.value,
                                                },
                                                label="Note",
                                                className="textinput-width",
                                            ),
                                        ],
                                    ),
                                    dmc.Group(
                                        grow=True,
                                        children=[
                                            dmc.NumberInput(
                                                id={
                                                    "type": "trigger-above-input",
                                                    "mode": mode.value,
                                                },
                                                label="Trigger above",
                                                decimalScale=2,
                                                min=0.01,
                                                step=0.01,
                                                className="input-width",
                                            ),
                                            dmc.TextInput(
                                                id={
                                                    "type": "trigger-above-note",
                                                    "mode": mode.value,
                                                },
                                                label="Note",
                                                className="textinput-width",
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            dmc.Group(
                                children=[
                                    dmc.Button(
                                        "Submit",
                                        id={
                                            "type": "alert-modal-submit-button",
                                            "mode": mode.value,
                                        },
                                        n_clicks=0,
                                        disabled=True,
                                    ),
                                    dmc.Button(
                                        "Exit",
                                        id={
                                            "type": "alert-modal-cancel-button",
                                            "mode": mode.value,
                                        },
                                        n_clicks=0,
                                        color="red",
                                        variant="outline",
                                    ),
                                ]
                            ),
                        ]
                    ),
                ],
            ),
        ],
    )

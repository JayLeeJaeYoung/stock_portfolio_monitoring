import pandas as pd

dataTypeDefinitions = {
    "number_mil": {
        "extendsDataType": "number",
        "baseDataType": "number",
        "valueFormatter": {
            "function": "params.value == null ? '' : d3.format(',.0f')(params.value / 1000000) + 'M'"
        },
    },
    "number_integer": {
        "extendsDataType": "number",
        "baseDataType": "number",
        "valueFormatter": {
            "function": "params.value == null ? '' : d3.format(',.0f')(params.value)"
        },
    },
    "number3d": {
        "extendsDataType": "number",
        "baseDataType": "number",
        "valueFormatter": {
            "function": "params.value == null ? '' : d3.format(',.3f')(params.value)"
        },
    },
    "number2d": {
        "extendsDataType": "number",
        "baseDataType": "number",
        "valueFormatter": {
            "function": "params.value == null ? '' : d3.format(',.2f')(params.value)"
        },
    },
    "number1d": {
        "extendsDataType": "number",
        "baseDataType": "number",
        "valueFormatter": {
            "function": "params.value == null ? '' : d3.format(',.1f')(params.value)"
        },
    },
    "percent2d": {
        "extendsDataType": "number",
        "baseDataType": "number",
        "valueFormatter": {
            "function": "params.value == null ? '' : d3.format(',.2%')(params.value)"
        },
    },
    "percent1d": {
        "extendsDataType": "number",
        "baseDataType": "number",
        "valueFormatter": {
            "function": "params.value == null ? '' : d3.format(',.1%')(params.value)"
        },
    },
}

columnTypes = {
    "note_string_col": {
        "cellEditor": "agLargeTextCellEditor",
        "cellEditorPopup": True,
        "cellEditorParams": {"maxLength": 1000, "rows": 10, "cols": 50},
        "cellStyle": {
            "whiteSpace": "normal",
            "wordBreak": "break-word",
            "lineHeight": "1.5",
        },
    },
    "priority_integer_col": {
        # "minWidth": 130,
        "filter": "agNumberColumnFilter",
        "filterParams": {
            "buttons": ["apply", "reset"],
            "closeOnApply": True,
        },
        "cellEditor": "agNumberCellEditor",
        "cellEditorParams": {
            "precision": 0,
            "step": 1,
            "showStepperButtons": True,
            "min": 0,
            "max": 100,
        },
        "cellStyle": {"textAlign": "right"},
    },
    "positive_integer_col": {
        # "minWidth": 130,
        "filter": "agNumberColumnFilter",
        "filterParams": {
            "buttons": ["apply", "reset"],
            "closeOnApply": True,
        },
        "cellEditor": "agNumberCellEditor",
        "cellEditorParams": {
            "precision": 0,
            "step": 1,
            "showStepperButtons": True,
            "min": 0,
        },
        "cellStyle": {"textAlign": "right"},
    },
    "integer_col": {
        # "minWidth": 130,
        "filter": "agNumberColumnFilter",
        "filterParams": {
            "buttons": ["apply", "reset"],
            "closeOnApply": True,
        },
        "cellEditor": "agNumberCellEditor",
        "cellEditorParams": {
            "precision": 0,
            "step": 1,
            "showStepperButtons": True,
        },
        "cellStyle": {"textAlign": "right"},
    },
    "positive_number3d_col": {
        # "minWidth": 130,
        "filter": "agNumberColumnFilter",
        "filterParams": {
            "buttons": ["apply", "reset"],
            "closeOnApply": True,
        },
        "cellEditor": "agNumberCellEditor",
        "cellEditorParams": {
            "precision": 3,
            "step": 0.001,
            "showStepperButtons": True,
            "min": 0.00,
        },
        "cellStyle": {"textAlign": "right"},
    },
    "positive_number2d_col": {
        # "minWidth": 130,
        "filter": "agNumberColumnFilter",
        "filterParams": {
            "buttons": ["apply", "reset"],
            "closeOnApply": True,
        },
        "cellEditor": "agNumberCellEditor",
        "cellEditorParams": {
            "precision": 2,
            "step": 0.01,
            "showStepperButtons": True,
            "min": 0.00,
        },
        "cellStyle": {"textAlign": "right"},
    },
    "number2d_col": {
        # "minWidth": 130,
        "filter": "agNumberColumnFilter",
        "filterParams": {
            "buttons": ["apply", "reset"],
            "closeOnApply": True,
        },
        "cellEditor": "agNumberCellEditor",
        "cellEditorParams": {
            "precision": 2,
            "step": 0.01,
            "showStepperButtons": True,
        },
        "cellStyle": {"textAlign": "right"},
    },
    "number1d_col": {
        # "minWidth": 130,
        "filter": "agNumberColumnFilter",
        "filterParams": {
            "buttons": ["apply", "reset"],
            "closeOnApply": True,
        },
        "cellEditor": "agNumberCellEditor",
        "cellEditorParams": {
            "precision": 1,
            "step": 0.1,
            "showStepperButtons": True,
        },
        "cellStyle": {"textAlign": "right"},
    },
    "percent2d_col": {
        # "minWidth": 130,
        "filter": "agNumberColumnFilter",
        "filterParams": {
            "buttons": ["apply", "reset"],
            "closeOnApply": True,
        },
        "cellEditor": "agNumberCellEditor",
        "cellEditorParams": {
            "precision": 4,
            "step": 0.0001,
            "showStepperButtons": True,
        },
        "cellStyle": {"textAlign": "right"},
    },
    "percent1d_col": {
        # "minWidth": 130,
        "filter": "agNumberColumnFilter",
        "filterParams": {
            "buttons": ["apply", "reset"],
            "closeOnApply": True,
        },
        "cellEditor": "agNumberCellEditor",
        "cellEditorParams": {
            "precision": 3,
            "step": 0.001,
            "showStepperButtons": True,
        },
        "cellStyle": {"textAlign": "right"},
    },
}

portfolio_table_default_col_def = {
    "resizable": True,
    "sortable": True,
    "filter": True,
    "autoSizeColumns": True,
    "wrapText": True,
    "headerClass": "wrap-header",
    "autoSizeStrategy": {"type": "fitCellContents", "excludeHeader": True},
    "wrapHeaderText": True,
    "autoHeaderHeight": True,
    # "flex": 1,  # This allows columns to flex and take up available space
    "useValueFormatterForExport": True,
    # "menuTabs": ["generalMenuTab", 'valueAggMenuTab', 'chartMenuTab', 'columnsMenuTab', 'filterMenuTab', 'setFilterMenuTab'],
}

portfolio_table_dash_grid_options = {
    # "pagination": True,
    "dataTypeDefinitions": dataTypeDefinitions,
    "columnTypes": columnTypes,
    "animateRows": True,
    "alwaysMultiSort": True,
    "rowSelection": "multiple",
    "rowMultiSelectWithClick": True,
    "suppressRowClickSelection": True,
    "domLayout": "normal",
    "enableCellTextSelection": False,
    "suppressMovableColumns": True,
    # "rowHeight": 60,
    "maintainColumnOrder": True,
    "skipHeaderOnAutoSize": True,
    "rowDragManaged": True,
    "rowDragMultiRow": "multi",
    "suppressMaintainUnsortedOrder": True,
    # "stopEditingWhenCellsLoseFocus": True,
    "undoRedoCellEditing": True,
    "undoRedoCellEditingLimit": 20,
    "defaultColGroupDef": {"marryChildren": True},
    "suppressClickEdit": False,
}

portfolio_table_persisted_props = [
    "filterModel",
    "sortModel",
    "columnState",
    "columnGroupState",
    "paginationModel",
    "selectedRows",
]


def create_portfolio_table_col_defs(col_def):
    portfolio_table_cols_df = (
        col_def[col_def["display"] == True]
        .drop(columns=["source", "calculation_note", "dependency", "display"])
        .rename(columns={"label": "headerName"})
        .copy()
    )

    for col in ["editable", "rowDrag", "sortable", "filter", "is_neg_red"]:
        if portfolio_table_cols_df[col].dtype != bool:
            raise ValueError(f"{col} must be bool")

    columnDefs = []
    for group in portfolio_table_cols_df["group"].unique():
        group_id = group.strip().lower().replace(" ", "_")

        col_defs = portfolio_table_cols_df[
            portfolio_table_cols_df["group"] == group
        ].to_dict(orient="records")

        for i, record in enumerate(col_defs):
            record = {k: v for k, v in record.items() if pd.notna(v)}

            if record.get("cellRenderer", False) == "IconButton":
                icon = record.pop("icon", None)
                record.update(
                    {
                        "cellRendererParams": {"icon": icon},
                        "cellStyle": {
                            "padding": 0,
                        },
                    }
                )

            if record.get("cellRenderer", False) == "AlertButton":
                icon = record.pop("icon", None)
                record.update(
                    {
                        "cellRendererParams": {"icon": icon},
                        "cellStyle": {
                            "padding": 0,
                        },
                    }
                )

            # elif record.get('cellRenderer', False) == 'EditButton':
            #     no_decimal = record.pop('no_decimal', None)
            #     record.update({
            #         "cellRendererParams": {'no_decimal': int(no_decimal)},
            #     })

            if record.pop("is_neg_red", False):
                record["cellClassRules"] = {"ag-red-cell": "params.value < 0"}

            col_defs[i] = record

        group_def = {"headerName": group, "groupId": group_id, "children": col_defs}
        columnDefs.append(group_def)

    return columnDefs

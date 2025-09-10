from utils.portfolio_table_inputs import (
    create_portfolio_table_col_defs,
    portfolio_table_default_col_def,
    portfolio_table_dash_grid_options,
    portfolio_table_persisted_props,
)
from utils.reference import INPUT_FIELDS_FILE_PATH
import dash_ag_grid as dag
import pandas as pd
from utils.enums import FreqMode
from models.models import get_data_list

# Load column definitions from Excel file
col_def = pd.read_excel(INPUT_FIELDS_FILE_PATH, sheet_name="col_def")


def portfolio_table_layout(mode: FreqMode = FreqMode.DAILY):
    return dag.AgGrid(
        id={"type": "portfolio-table", "mode": mode.value},
        className="ag-theme-quartz",
        rowData=get_data_list(mode).read_all(),
        columnDefs=create_portfolio_table_col_defs(col_def),
        getRowId="params.data.ticker",
        defaultColDef=portfolio_table_default_col_def,
        style={"width": "100%", "height": "75vh"},
        dashGridOptions=portfolio_table_dash_grid_options,
        columnSize="autoSize",
        persistence=True,
        persistence_type="session",
        persisted_props=portfolio_table_persisted_props,
    )

import pytz
from datetime import datetime
import pandas as pd
from utils.enums import FreqMode
from models.models import get_data_list, get_alert_list
from html import escape
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def create_daily_tables(chosen_user_name):
    # Database access now goes through models.py
    dl = get_data_list(FreqMode.DAILY)
    dl.update_username(chosen_user_name)
    data_list = dl.refresh_all()
    # data_list = dl.read_all()

    if not data_list:
        print("⚠️ No tickers found. Exiting early.\n")
        return pd.DataFrame(), pd.DataFrame()

    al = get_alert_list(FreqMode.DAILY)
    al.update_username(chosen_user_name)
    alert_list = al.read_all()
    print(f"# of alerts: {len(alert_list)}\n")

    # delete all alerts other than chosen_user_name because by design, I only want main user in this app and won't allow other users to use alerts.
    deleted = al.delete_other_alerts(chosen_user_name)
    if deleted > 0:
        print(f"{deleted} alerts deleted by non-main users\n")

    # delete orphaned tickers where users have created alerts but deleted the ticker from table
    tickers_to_delete = list(
        set([alert["ticker"] for alert in alert_list])
        - set([x["ticker"] for x in data_list])
    )
    deleted = al.delete_orphaned_tickers(tickers_to_delete)
    if deleted > 0:
        print(f"{deleted} orphaned alerts deleted\n")

    # alert_df is helpful dataframe to find alerts that need to be triggered
    if alert_list:
        alert_df = pd.DataFrame(alert_list)[
            [
                "_id",
                "ticker",
                "lower_alert_price",
                "upper_alert_price",
                "triggered_date",
            ]
        ].merge(
            pd.DataFrame(data_list)[
                [
                    "ticker",
                    "regularMarketDayHigh",
                    "regularMarketDayLow",
                    "regularMarketPrice",
                ]
            ],
            how="left",
            on="ticker",
        )
        alert_df["lower_alert_price"] = pd.to_numeric(
            alert_df["lower_alert_price"], errors="coerce"
        )
        alert_df["upper_alert_price"] = pd.to_numeric(
            alert_df["upper_alert_price"], errors="coerce"
        )

        # For exchanges other than NYSE, DayH and DayL may be zero
        alert_df.loc[alert_df["regularMarketDayHigh"] == 0, "regularMarketDayHigh"] = (
            alert_df.loc[alert_df["regularMarketDayHigh"] == 0, "regularMarketPrice"]
        )
        alert_df.loc[alert_df["regularMarketDayLow"] == 0, "regularMarketDayLow"] = (
            alert_df.loc[alert_df["regularMarketDayLow"] == 0, "regularMarketPrice"]
        )

        alert_df["is_new_trigger"] = (
            (alert_df["upper_alert_price"] < alert_df["regularMarketDayHigh"])
            | (alert_df["lower_alert_price"] > alert_df["regularMarketDayLow"])
        ) & alert_df["triggered_date"].isna()

        updated_alert_list = al.update_triggered_date(
            alert_df[alert_df["is_new_trigger"]]["_id"].tolist()
        )
    else:
        updated_alert_list = []

    # create daily_change_df to be emailed
    if data_list:
        daily_change_df = pd.DataFrame(data_list)[
            [
                "latestMarketTimeWithTimeZone",
                "companyName",
                "ticker",
                "regularMarketPrice",
                "percent1D",
                "percent1W",
                "percent1M",
            ]
        ]
        daily_change_df["percent1D"] = daily_change_df["percent1D"] * 100
        daily_change_df["percent1W"] = daily_change_df["percent1W"] * 100
        daily_change_df["percent1M"] = daily_change_df["percent1M"] * 100
        daily_change_df = daily_change_df.sort_values(by=["percent1D"], ascending=False)
    else:
        daily_change_df = pd.DataFrame()

    # create updated_alert_df to be emailed
    if updated_alert_list and data_list:
        updated_alert_df = pd.DataFrame(updated_alert_list).merge(
            daily_change_df[["ticker", "companyName", "regularMarketPrice"]],
            how="left",
            on="ticker",
        )[
            [
                "created_time",
                "companyName",
                "ticker",
                "alert_description",
                "regularMarketPrice",
                "lower_alert_price",
                "upper_alert_price",
                "lower_alert_note",
                "upper_alert_note",
                "triggered_date",
            ]
        ]

        updated_alert_df[["created_time", "triggered_date"]] = (
            updated_alert_df[["created_time", "triggered_date"]]
            .apply(pd.to_datetime, errors="coerce")
            .apply(
                lambda col: col.dt.tz_localize("UTC")
                .dt.tz_convert("US/Eastern")
                .dt.strftime("%Y/%m/%d %I:%M %p (%Z)")
            )
        )

    else:
        updated_alert_df = pd.DataFrame()

    return daily_change_df, updated_alert_df


def create_lt_duration_tables(chosen_user_name, mode):
    # Database access now goes through models.py

    if mode == FreqMode.WEEKLY:
        high_price_field = "price1W_high"
        low_price_field = "price1W_low"
        sort_by_field = "percent1W"
    elif mode == FreqMode.MONTHLY:
        high_price_field = "price1M_high"
        low_price_field = "price1M_low"
        sort_by_field = "percent1M"
    else:
        raise ValueError(f"Invalid mode: {mode}. Must be FreqMode.WEEKLY or FreqMode.MONTHLY")

    dl = get_data_list(mode)
    dl.update_username(chosen_user_name)
    # data_list = dl.refresh_all()
    data_list = dl.read_all()

    if not data_list:
        print("⚠️ No tickers found. Exiting early.\n")
        return pd.DataFrame(), pd.DataFrame()

    al = get_alert_list(mode)
    al.update_username(chosen_user_name)
    alert_list = al.read_all()
    print(f"# of alerts: {len(alert_list)}\n")

    # delete all alerts other than chosen_user_name because by design, I only want main user in this app and won't allow other users to use alerts.
    deleted = al.delete_other_alerts(chosen_user_name)
    if deleted > 0:
        print(f"{deleted} alerts deleted by non-main users\n")

    # delete orphaned tickers where users have created alerts but deleted the ticker from table
    tickers_to_delete = list(
        set([alert["ticker"] for alert in alert_list])
        - set([x["ticker"] for x in data_list])
    )
    deleted = al.delete_orphaned_tickers(tickers_to_delete)
    if deleted > 0:
        print(f"{deleted} orphaned alerts deleted\n")

    # alert_df is helpful dataframe to find alerts that need to be triggered
    if alert_list:
        alert_df = pd.DataFrame(alert_list)[
            [
                "_id",
                "ticker",
                "lower_alert_price",
                "upper_alert_price",
                "triggered_date",
            ]
        ].merge(
            pd.DataFrame(data_list)[
                [
                    "ticker",
                    "regularMarketPrice",
                    high_price_field,
                    low_price_field,
                ]
            ],
            how="left",
            on="ticker",
        )
        alert_df["lower_alert_price"] = pd.to_numeric(
            alert_df["lower_alert_price"], errors="coerce"
        )
        alert_df["upper_alert_price"] = pd.to_numeric(
            alert_df["upper_alert_price"], errors="coerce"
        )

        alert_df["is_new_trigger"] = (
            (alert_df["upper_alert_price"] < alert_df[high_price_field])
            | (alert_df["lower_alert_price"] > alert_df[low_price_field])
        ) & alert_df["triggered_date"].isna()

        updated_alert_list = al.update_triggered_date(
            alert_df[alert_df["is_new_trigger"]]["_id"].tolist()
        )
    else:
        updated_alert_list = []

    # create lt_change_df to be emailed
    if data_list:
        lt_change_df = pd.DataFrame(data_list)[
            [
                "latestMarketTimeWithTimeZone",
                "companyName",
                "ticker",
                "regularMarketPrice",
                "percent1D",
                "percent1W",
                "percent1M",
                'percent1Y',
                'percent5Y',

            ]
        ]
        # Ensure all percent columns are consistent decimals (not strings with % signs)
        for col in ["percent1D", "percent1W", "percent1M", "percent1Y", "percent5Y"]:
            if col in lt_change_df.columns:
                # Convert to numeric, removing any % signs, then multiply by 100
                lt_change_df[col] = pd.to_numeric(lt_change_df[col].astype(
                    str).str.replace('%', ''), errors='coerce') * 100

        lt_change_df = lt_change_df.sort_values(by=[sort_by_field], ascending=False)
    else:
        lt_change_df = pd.DataFrame()

    # create updated_alert_df to be emailed
    if updated_alert_list and data_list:
        updated_alert_df = pd.DataFrame(updated_alert_list).merge(
            lt_change_df[["ticker", "companyName", "regularMarketPrice"]],
            how="left",
            on="ticker",
        )[
            [
                "created_time",
                "companyName",
                "ticker",
                "alert_description",
                "regularMarketPrice",
                "lower_alert_price",
                "upper_alert_price",
                "lower_alert_note",
                "upper_alert_note",
                "triggered_date",
            ]
        ]

        updated_alert_df[["created_time", "triggered_date"]] = (
            updated_alert_df[["created_time", "triggered_date"]]
            .apply(pd.to_datetime, errors="coerce")
            .apply(
                lambda col: col.dt.tz_localize("UTC")
                .dt.tz_convert("US/Eastern")
                .dt.strftime("%Y/%m/%d %I:%M %p (%Z)")
            )
        )

    else:
        updated_alert_df = pd.DataFrame()

    return lt_change_df, updated_alert_df


def create_daily_email_body(daily_change_df, updated_alert_df):
    def fmt_fixed2(x):
        if pd.isna(x):
            return ""
        return f"{x:,.2f}"

    def fmt_percent_fixed2(x):
        if pd.isna(x):
            return ""
        return f"{x:.2f}%"

    def break_ticker(ticker):
        # Insert zero-width space after every '.' to break Gmail auto-linking
        if isinstance(ticker, str):
            return ticker.replace(".", ".\u200b")
        return ticker

    def build_table(df, title):
        # Define columns alignment
        right_cols = set()
        left_cols = set()
        formatters = {}

        if title.startswith("📈 Daily Change"):
            if "regularMarketPrice" in df.columns:
                formatters["regularMarketPrice"] = fmt_fixed2
                right_cols.add("regularMarketPrice")
            for col in ["percent1D", "percent1W", "percent1M"]:
                if col in df.columns:
                    formatters[col] = fmt_percent_fixed2
                    right_cols.add(col)
            for col in ["latestMarketTimeWithTimeZone", "companyName", "ticker"]:
                if col in df.columns:
                    left_cols.add(col)

        if title.startswith("📊 Alerts"):
            for col in [
                "ticker",
                "companyName",
                "alert_description",
                "lower_alert_note",
                "upper_alert_note",
            ]:
                if col in df.columns:
                    left_cols.add(col)
            for col in ["regularMarketPrice", "lower_alert_price", "upper_alert_price"]:
                if col in df.columns:
                    formatters[col] = fmt_fixed2
                    right_cols.add(col)

        # Start building HTML string
        html = []
        html.append(
            '<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; font-family: Arial, sans-serif;">'
        )
        html.append(
            f'<caption style="text-align: left; font-size: 1.2em; font-weight: bold; margin-bottom: 5px;">{escape(title)}</caption>'
        )

        # Header row
        html.append("<thead><tr>")
        # Blank corner cell (index header)
        html.append(
            '<th style="background-color: #f2f2f2; text-align: center; padding: 5px;">&nbsp;</th>'
        )
        for col in df.columns:
            html.append(
                f'<th style="background-color: #f2f2f2; text-align: center; padding: 5px;">{escape(col)}</th>'
            )
        html.append("</tr></thead>")

        # Body rows
        html.append("<tbody>")
        for idx, row in df.iterrows():
            # Row header with index, left aligned
            html.append(
                f'<tr><th style="text-align: left; padding: 5px;">{escape(str(idx))}</th>'
            )
            for col in df.columns:
                val = row[col]
                # Apply formatting
                if col in formatters:
                    val = formatters[col](val)
                else:
                    val = "" if pd.isna(val) else str(val)
                # Break ticker dots
                if col == "ticker":
                    val = break_ticker(val)
                # Decide alignment
                align = (
                    "left"
                    if col in left_cols
                    else ("right" if col in right_cols else "left")
                )
                # Escape HTML inside cell text
                val_escaped = escape(val)
                html.append(
                    f'<td style="text-align: {align}; padding: 5px;">{val_escaped}</td>'
                )
            html.append("</tr>")
        html.append("</tbody>")
        html.append("</table><br>")

        return "".join(html)

    html_parts = []
    html_parts.append(build_table(daily_change_df, "📈 Daily Change"))

    if not updated_alert_df.empty:
        html_parts.append(build_table(updated_alert_df, "📊 Alerts"))

    email_body = "<html><body>" + "".join(html_parts) + "</body></html>"
    return email_body


def create_email_body_lt(lt_change_df, updated_alert_df, mode):
    def fmt_fixed2(x):
        if pd.isna(x):
            return ""
        return f"{x:,.2f}"

    def fmt_percent_fixed2(x):
        if pd.isna(x):
            return ""
        return f"{x:.2f}%"

    def break_ticker(ticker):
        # Insert zero-width space after every '.' to break Gmail auto-linking
        if isinstance(ticker, str):
            return ticker.replace(".", ".\u200b")
        return ticker

    def build_table(df, title):
        # Define columns alignment
        right_cols = set()
        left_cols = set()
        formatters = {}

        # Determine mode-specific title and columns
        if title.startswith("📈"):
            if "regularMarketPrice" in df.columns:
                formatters["regularMarketPrice"] = fmt_fixed2
                right_cols.add("regularMarketPrice")

            # Handle different percent columns based on mode
            for col in ["percent1D", "percent1W", "percent1M", "percent1Y", "percent5Y"]:
                if col in df.columns:
                    formatters[col] = fmt_percent_fixed2
                    right_cols.add(col)

            for col in ["latestMarketTimeWithTimeZone", "companyName", "ticker"]:
                if col in df.columns:
                    left_cols.add(col)

        if title.startswith("📊 Alerts"):
            for col in [
                "ticker",
                "companyName",
                "alert_description",
                "lower_alert_note",
                "upper_alert_note",
            ]:
                if col in df.columns:
                    left_cols.add(col)
            for col in ["regularMarketPrice", "lower_alert_price", "upper_alert_price"]:
                if col in df.columns:
                    formatters[col] = fmt_fixed2
                    right_cols.add(col)

        # Start building HTML string
        html = []
        html.append(
            '<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; font-family: Arial, sans-serif;">'
        )
        html.append(
            f'<caption style="text-align: left; font-size: 1.2em; font-weight: bold; margin-bottom: 5px;">{escape(title)}</caption>'
        )

        # Header row
        html.append("<thead><tr>")
        # Blank corner cell (index header)
        html.append(
            '<th style="background-color: #f2f2f2; text-align: center; padding: 5px;">&nbsp;</th>'
        )
        for col in df.columns:
            html.append(
                f'<th style="background-color: #f2f2f2; text-align: center; padding: 5px;">{escape(col)}</th>'
            )
        html.append("</tr></thead>")

        # Body rows
        html.append("<tbody>")
        for idx, row in df.iterrows():
            # Row header with index, left aligned
            html.append(
                f'<tr><th style="text-align: left; padding: 5px;">{escape(str(idx))}</th>'
            )
            for col in df.columns:
                val = row[col]
                # Apply formatting
                if col in formatters:
                    val = formatters[col](val)
                else:
                    val = "" if pd.isna(val) else str(val)
                # Break ticker dots
                if col == "ticker":
                    val = break_ticker(val)
                # Decide alignment
                align = (
                    "left"
                    if col in left_cols
                    else ("right" if col in right_cols else "left")
                )
                # Escape HTML inside cell text
                val_escaped = escape(val)
                html.append(
                    f'<td style="text-align: {align}; padding: 5px;">{val_escaped}</td>'
                )
            html.append("</tr>")
        html.append("</tbody>")
        html.append("</table><br>")

        return "".join(html)

    # Determine mode-specific title
    if mode == FreqMode.WEEKLY:
        change_title = "📈 Weekly Change"
    elif mode == FreqMode.MONTHLY:
        change_title = "📈 Monthly Change"
    else:
        change_title = "📈 Change"

    html_parts = []
    html_parts.append(build_table(lt_change_df, change_title))

    if not updated_alert_df.empty:
        html_parts.append(build_table(updated_alert_df, "📊 Alerts"))

    email_body = "<html><body>" + "".join(html_parts) + "</body></html>"
    return email_body


def daily_cron_job(chosen_user_name):
    daily_change_df, updated_alert_df = create_daily_tables(chosen_user_name)
    email_body = create_daily_email_body(daily_change_df, updated_alert_df)
    return email_body


def weekly_cron_job(chosen_user_name):
    lt_change_df, updated_alert_df = create_lt_duration_tables(chosen_user_name, FreqMode.WEEKLY)
    email_body = create_email_body_lt(lt_change_df, updated_alert_df, FreqMode.WEEKLY)
    return email_body


def monthly_cron_job(chosen_user_name):
    lt_change_df, updated_alert_df = create_lt_duration_tables(chosen_user_name, FreqMode.MONTHLY)
    email_body = create_email_body_lt(lt_change_df, updated_alert_df, FreqMode.MONTHLY)
    return email_body

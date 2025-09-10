from datetime import datetime
from utils.reference import YAHOO_BASE_URL, INPUT_FIELDS_FILE_PATH
from models.database import *
from utils.enums import FreqMode

import pandas as pd
import requests
from pymongo import ReturnDocument
from bson import ObjectId
import pytz
from utils.cache_setup import cache

# Yahoo Finance API inputs for 5 year chart
chart_5y_df = pd.read_excel(
    INPUT_FIELDS_FILE_PATH, sheet_name="v8_finance_chart_5y"
).drop(columns=["sample_data", "comment"])

mongodb = get_db_connection()

raw_data_collection = mongodb["raw_data"]
alert_data_collection = mongodb["alert_data"]


def _perc_chg(output, num_key, den_key):
    try:
        return float(output[num_key] / output[den_key] - 1)
    except Exception:
        return None


class RawDataList:
    """
    RawDataList represents a list of raw_data
    raw_data is made up of
        (1) user_input: input entered by user
        (2) raw_output: output from api queries

    primary key: (1) username (2) ticker (3) freq_mode

    Document structure:
    {
        # primary keys
        'username': 'user123',
        'ticker': '^GSPC',
        'freq_mode': 1,

        # user_input
        'priority': 1.0,
        'personal_note': 'my note',
        'averageBuyPrice': 30.23,
        'positionQuantity': 30,
        'priceUpperTarget': 40.20,
        'priceLowerTarget': 20.23,

        # raw_output
        'shortName': 'S&P 500',
        'regularMarketPrice': 4183.34,
        ...
    }
    """

    def __init__(self, raw_data_collection, freq_mode: FreqMode = FreqMode.DAILY):
        self.username = None
        self.freq_mode = freq_mode
        self.collection = raw_data_collection

        # Create index for faster queries - now includes freq_mode
        self.collection.create_index(
            [("username", 1), ("ticker", 1), ("freq_mode", 1)], unique=True
        )

    def update_username(self, username):
        self.username = username

    def update_freq_mode(self, freq_mode: FreqMode):
        self.freq_mode = freq_mode

    def is_trash_empty(self):
        """checks if trash is empty for the current user and freq_mode"""
        user_cache = cache.get(self.username, {})
        mode_trash = user_cache.get(f"mode_{self.freq_mode.value}", {}).get("trash", [])
        return not bool(mode_trash)

    def is_all_trash_empty(self) -> list[bool]:
        """
        Check if trash is empty for ALL frequency modes for the current user.

        Returns:
            list[bool]: List of boolean values indicating trash status for each mode.
                       True = trash is empty (nothing to undo)
                       False = trash has items (can undo)
                       Order: Follows FreqMode enum order (DAILY=1, WEEKLY=2, MONTHLY=3)
        """
        undo_states = []
        user_cache = cache.get(self.username, {})

        for freq_mode in FreqMode:
            mode_trash = user_cache.get(f"mode_{freq_mode.value}", {}).get("trash", [])
            undo_states.append(not bool(mode_trash))

        return undo_states

    def _query_5y_one_ticker(self, ticker):
        """
        queries 5y data from Yahoo Finance
        """
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/113.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json",
            "Connection": "keep-alive",
        }
        url = f"{YAHOO_BASE_URL}/redacted_path/{ticker}?range=5y&interval=1d"

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise RuntimeError(
                f"Yahoo API error for {ticker}: HTTP {response.status_code} - {response.text.strip()}"
            )

        try:
            res = response.json()
        except Exception:
            raise RuntimeError(
                f"Failed to parse JSON for {ticker}: {response.text.strip()}"
            )

        if res["chart"]["error"]:
            raise RuntimeError(f"Yahoo API returned an error: {res['chart']['error']}")

        # parse to raw_output
        base = res["chart"]["result"][0]
        raw_output = {"ticker": ticker}  # ticker is primary key
        for row in chart_5y_df.itertuples(index=False):
            if not row.include:
                continue

            try:
                if pd.notna(row.api_key3):
                    value = base[row.api_key1][row.api_key2][0][row.api_key3]
                elif pd.notna(row.api_key2):
                    value = base[row.api_key1][row.api_key2]
                elif pd.notna(row.api_key1):
                    value = base[row.api_key1]
                else:
                    # this won't happen unless chart_5y_df has errors
                    raise RuntimeError("chart_5y_df has errors")

                raw_output[row.field] = value
            except (KeyError, IndexError, TypeError):
                # Field doesn't exist in API response, set to None
                raw_output[row.field] = None
                print(f"[WARNING] Missing field '{row.field}' for ticker {ticker}")

        # clean raw_output
        raw_output["companyName"] = raw_output.get("shortName") or raw_output.get(
            "longName"
        )
        raw_output.pop("shortName", None)
        raw_output.pop("longName", None)

        # Safely expand time series data with error handling
        try:
            closing_time_offset = (
                raw_output["currentTradingPeriod"]["regular"]["end"]
                - raw_output["currentTradingPeriod"]["regular"]["start"]
            )

            df = pd.DataFrame(
                {"date": raw_output["5y_timestamp"], "price": raw_output["5y_adjclose"], "low": res['chart']['result'][0]
                    ['indicators']['quote'][0]['low'], "high": res['chart']['result'][0]['indicators']['quote'][0]['high']}
            )
            # date's hour shows opening time, not closing time for all dates except latest date
            df.at[df.index[-1], "date"] = df.at[df.index[-1], "date"] - closing_time_offset
            df["date"] = (
                pd.to_datetime(df["date"] + closing_time_offset, unit="s", utc=True)
                .dt.tz_convert(raw_output["exchangeTimezoneName"])
                .dt.tz_localize(None)
            )

            # fix the date for the latest date - for some tickers, latest time after hours keep increasing while the price remains at closing price. This date messes up 1D percent calculation.
            t2 = df.iloc[-2]["date"]
            t1 = df.iloc[-1]["date"]
            # compare only time-of-day (ignoring date)
            if t1.time() > t2.time():
                # replace the time-of-day of t1 with t2's, keep the date of t1
                new_time = pd.Timestamp.combine(t1.date(), t2.time())
                df.at[df.index[-1], "date"] = new_time

            date_prefix_map = {
                "1D": pd.DateOffset(days=1),
                "1W": pd.DateOffset(weeks=1),
                "1M": pd.DateOffset(months=1),
                "1Y": pd.DateOffset(years=1),
                "5Y": pd.DateOffset(years=5),
            }

            latest_date = df.iloc[-1]["date"]
            first_date = df.iloc[0]["date"]

            for label, offset in date_prefix_map.items():
                price_key = f"price{label}"
                percent_key = f"percent{label}"
                low_key = f"price{label}_low"
                high_key = f"price{label}_high"

                if label == "5Y":
                    prior_date = first_date
                else:
                    prior_date = latest_date - offset

                # Get the date range for this period
                period_df = df[df["date"] >=
                               prior_date] if first_date <= prior_date else pd.DataFrame()

                raw_output[price_key] = (
                    float(period_df.iloc[0]["price"])
                    if not period_df.empty
                    else None
                )
                raw_output[percent_key] = _perc_chg(
                    raw_output, "regularMarketPrice", price_key
                )

                # Calculate low and high for this period
                if not period_df.empty:
                    raw_output[low_key] = float(period_df["low"].min())
                    raw_output[high_key] = float(period_df["high"].max())
                else:
                    raw_output[low_key] = None
                    raw_output[high_key] = None

            raw_output["percentFromDayHigh"] = _perc_chg(
                raw_output, "regularMarketPrice", "regularMarketDayHigh"
            )
            raw_output["percentFromDayLow"] = _perc_chg(
                raw_output, "regularMarketPrice", "regularMarketDayLow"
            )
            raw_output["percentFrom52wHigh"] = _perc_chg(
                raw_output, "regularMarketPrice", "fiftyTwoWeekHigh"
            )
            raw_output["percentFrom52wLow"] = _perc_chg(
                raw_output, "regularMarketPrice", "fiftyTwoWeekLow"
            )

            raw_output.pop("5y_timestamp", None)
            raw_output.pop("5y_adjclose", None)
            raw_output.pop("currentTradingPeriod", None)

        except (KeyError, TypeError, AttributeError) as e:
            print(f"[WARNING] Could not process time series data for {ticker}: {e}")
            # Set default values for missing fields
            for label in ["1D", "1W", "1M", "1Y", "5Y"]:
                raw_output[f"price{label}"] = None
                raw_output[f"percent{label}"] = None
                raw_output[f"price{label}_low"] = None
                raw_output[f"price{label}_high"] = None

            raw_output["percentFromDayHigh"] = None
            raw_output["percentFromDayLow"] = None
            raw_output["percentFrom52wHigh"] = None
            raw_output["percentFrom52wLow"] = None

        return raw_output

    def _query_one_ticker(self, ticker):
        """
        Run all api queries
        """
        try:
            five_year_output = self._query_5y_one_ticker(ticker)
        except Exception as e:
            raise RuntimeError(f"Error: {ticker}: {e}")

        raw_output = five_year_output.copy()
        return raw_output

    def read_all(self):
        raw_data_list = list(
            self.collection.find(
                {"username": self.username, "freq_mode": self.freq_mode},
                projection={"_id": 0},
            )
        )
        return raw_data_list

    def delete(self, ticker):
        trash = self.collection.find_one_and_delete(
            {"username": self.username, "ticker": ticker, "freq_mode": self.freq_mode},
            projection={"_id": 0},
        )
        if not trash:
            raise KeyError(f"No ticker to delete: {ticker}")

        # Add to cache trash
        user_cache = cache.get(self.username, {})
        mode_trash = user_cache.get(f"mode_{self.freq_mode.value}", {}).get("trash", [])
        mode_trash.append(trash)
        user_cache[f"mode_{self.freq_mode.value}"] = {"trash": mode_trash}
        cache.set(self.username, user_cache)

    def is_duplicate(self, ticker):
        """
        Check if a ticker already exists for the current user across ALL frequency modes.

        This method prevents users from adding the same stock ticker multiple times
        regardless of which portfolio mode (daily, weekly, monthly) they're using.

        Args:
            ticker (str): The stock ticker symbol to check (e.g., "AAPL", "TSLA")

        Returns:
            bool: True if the ticker already exists for this user in any mode,
                  False if the ticker is new for this user
        """
        return (
            self.collection.count_documents(
                {
                    "username": self.username,
                    "ticker": ticker,
                    # freq_mode filter removed to prevent duplicates across ALL modes
                    # This ensures one ticker per user across daily/weekly/monthly portfolios
                }
            )
            > 0
        )

    def append(self, user_input: dict):
        """Add new ticker to database after checking duplicates and clearing from trash"""
        # user_input won't have a username
        ticker = user_input["ticker"]

        # Check for duplicate
        if self.is_duplicate(ticker):
            raise KeyError(f"Duplicated Ticker: {ticker}")

        # Remove from trash if exists in ANY mode for this user
        # Get all cache keys for this user and check each one
        user_cache = cache.get(self.username, {})
        for mode_key in user_cache.keys():
            if mode_key.startswith("mode_"):
                current_trash = user_cache[mode_key]["trash"]

                # Find and remove the ticker if it exists in this mode's trash
                for i, row in enumerate(current_trash):
                    if row["ticker"] == ticker:
                        current_trash.pop(i)
                        user_cache[mode_key]["trash"] = current_trash
                        cache.set(self.username, user_cache)
                        break

        try:
            raw_output = self._query_one_ticker(ticker)
            raw_data = {
                "username": self.username,
                "freq_mode": self.freq_mode,
                **user_input,
                **raw_output,
            }
            # insert_one will mutate and add _id
            self.collection.insert_one(raw_data.copy())
            return raw_data

        except Exception as e:
            raise RuntimeError(f"Error appending ticker {ticker}: {e}")

    def update_user_input(self, ticker, key, new_value):
        if key == "ticker":
            raise KeyError("Updating ticker is not allowed")

        raw_data = self.collection.find_one_and_update(
            {"username": self.username, "ticker": ticker, "freq_mode": self.freq_mode},
            {"$set": {key: new_value}},
            projection={"_id": 0},
            return_document=ReturnDocument.AFTER,
        )
        if raw_data is None:
            raise KeyError(f"No ticker found to update: {ticker}")

        return raw_data

    def update_alert_count(self, ticker, alert_count):
        raw_data = self.collection.find_one_and_update(
            {"username": self.username, "ticker": ticker, "freq_mode": self.freq_mode},
            {"$set": {"alertCount": alert_count}},
            projection={"_id": 0},
            return_document=ReturnDocument.AFTER,
        )
        if raw_data is None:
            raise KeyError(f"No ticker found to update: {ticker}")

        return raw_data

    def refresh_raw_output(self, ticker):
        raw_data = self.collection.find_one_and_delete(
            {"username": self.username, "ticker": ticker, "freq_mode": self.freq_mode},
            projection={"_id": 0},
        )

        try:
            raw_output = self._query_one_ticker(ticker)
            raw_data.update(raw_output)
            self.collection.insert_one(raw_data.copy())
            return raw_data

        except Exception as e:
            raise RuntimeError(f"Error updating ticker {ticker}: {e}")

    def refresh_all(self):
        raw_data_list = self.read_all()

        new_data_list = []
        for i, raw_data in enumerate(raw_data_list):
            ticker = raw_data["ticker"]
            new_raw_data = self._query_one_ticker(ticker)
            raw_data_list[i] = {**raw_data, **new_raw_data}
            new_data_list.append(raw_data_list[i].copy())

        self.collection.delete_many(
            {"username": self.username, "freq_mode": self.freq_mode}
        )

        # Only insert if there are documents to insert
        if raw_data_list:
            self.collection.insert_many(raw_data_list)

        return new_data_list

    def restore(self):
        user_cache = cache.get(self.username, {})
        mode_trash = user_cache.get(f"mode_{self.freq_mode.value}", {}).get("trash", [])
        if not mode_trash:
            raise IndexError("Trash is empty")

        raw_data = mode_trash.pop()
        self.collection.insert_one(raw_data.copy())

        # Update the cache with the modified trash list
        user_cache[f"mode_{self.freq_mode.value}"] = {"trash": mode_trash}
        cache.set(self.username, user_cache)

        return raw_data


class DataList:
    """
    DataList represents rowData attribute in dash-ag-grid table
    It starts from RawDataList and adds calculated fields
    """

    def __init__(self, raw_data_collection, freq_mode: FreqMode = FreqMode.DAILY):
        self.username = None
        self.freq_mode = freq_mode
        self.rdl = RawDataList(raw_data_collection, freq_mode)

    def update_username(self, username):
        self.username = username
        self.rdl.update_username(username)

    def update_freq_mode(self, freq_mode: FreqMode):
        self.freq_mode = freq_mode
        self.rdl.update_freq_mode(freq_mode)

    def is_trash_empty(self):
        """checks if trash is empty for the current user and freq_mode"""
        return self.rdl.is_trash_empty()

    def is_all_trash_empty(self) -> list[bool]:
        """Check if trash is empty for ALL frequency modes for the current user"""
        return self.rdl.is_all_trash_empty()

    def is_duplicate(self, ticker):
        return self.rdl.is_duplicate(ticker)

    def _mutate_data_on_5y(self, data):
        """mutates data"""
        data["ipo"] = (
            pd.to_datetime(data["firstTradeDate"], unit="s", utc=True)
            .tz_convert(data["exchangeTimezoneName"])
            .strftime("%Y/%m/%d")
        )
        data.pop("firstTradeDate", None)

        data["latestMarketTimeWithTimeZone"] = (
            pd.to_datetime(data["regularMarketTime"], unit="s", utc=True)
            .tz_convert(data["exchangeTimezoneName"])
            .strftime("%Y/%m/%d %I:%M %p")
            + f" ({data.get('timezone')})"
        )

        data.pop("regularMarketTime", None)
        data.pop("exchangeTimezoneName", None)
        data.pop("timezone", None)

    def _mutate_data_on_user(self, data):
        data["percentFromUpperTarget"] = _perc_chg(
            data, "regularMarketPrice", "priceUpperTarget"
        )
        data["percentFromLowerTarget"] = _perc_chg(
            data, "regularMarketPrice", "priceLowerTarget"
        )
        data["positionCost"] = (
            data["averageBuyPrice"] * data["positionQuantity"]
            if all(
                isinstance(data.get(k), (int, float))
                for k in ["averageBuyPrice", "positionQuantity"]
            )
            else None
        )
        data["positionFMV"] = (
            data["regularMarketPrice"] * data["positionQuantity"]
            if all(
                isinstance(data.get(k), (int, float))
                for k in ["regularMarketPrice", "positionQuantity"]
            )
            else None
        )
        data["unrealizedGainLoss"] = (
            data["positionFMV"] - data["positionCost"]
            if all(
                isinstance(data.get(k), (int, float))
                for k in ["positionFMV", "positionCost"]
            )
            else None
        )
        data["positionReturn"] = _perc_chg(
            data, "regularMarketPrice", "averageBuyPrice"
        )

    def read_all(self):
        data_list = self.rdl.read_all()
        for data in data_list:
            self._mutate_data_on_5y(data)
            self._mutate_data_on_user(data)
        return data_list

    def delete(self, ticker):
        self.rdl.delete(ticker)

    def append(self, user_input: dict):
        data = self.rdl.append(user_input)
        self._mutate_data_on_5y(data)
        self._mutate_data_on_user(data)

        return data

    def update_user_input(self, ticker, key, new_value):
        data = self.rdl.update_user_input(ticker, key, new_value)
        # Note: not executing self._mutate_data_on_5y(data)
        self._mutate_data_on_user(data)
        return data

    def update_alert_count(self, ticker, alert_count):
        data = self.rdl.update_alert_count(ticker, alert_count)
        return data

    def refresh_one_ticker(self, ticker):
        data = self.rdl.refresh_raw_output(ticker)
        self._mutate_data_on_5y(data)
        self._mutate_data_on_user(data)
        return data

    def refresh_all(self):
        data_list = self.rdl.refresh_all()
        for data in data_list:
            self._mutate_data_on_5y(data)
            self._mutate_data_on_user(data)
        return data_list

    def restore_latest_ticker(self):
        data = self.rdl.restore()
        self._mutate_data_on_5y(data)
        self._mutate_data_on_user(data)
        return data


class AlertList:
    """
    AlertList represents a list of alert_data
    Alerts have a composite primary key of
        (1) username
        (2) ticker
        (3) freq_mode
        (4) created_time

    Given a (1) username, there is a (2) ticker, for which an alert is created at (4) created_time
    A user can create multiple alerts for a ticker in different modes, thus we need (3) freq_mode and (4) created_time as additional primary keys

    Each alert will also contain
        - alert_description: description of the alert
        - lower_alert_price: a positive float with 2 decimal points
        - lower_alert_note: a text string
        - upper_alert_price: a positive float with 2 decimal points
        - upper_alert_note: a text string
        - triggered_date: a time representation that is compatible with mongoDB which
            signifies whether the alert is triggered or not in a cron job. This will be initially None
            but will have a specific date if it is triggered
    """

    def __init__(self, alert_data_collection, freq_mode: FreqMode = FreqMode.DAILY):
        self.username = None
        self.freq_mode = freq_mode
        self.collection = alert_data_collection

        # Create index for faster queries - now includes freq_mode
        self.collection.create_index(
            [("username", 1), ("ticker", 1), ("freq_mode", 1), ("created_time", 1)],
            unique=True,
        )

    def update_username(self, username):
        self.username = username

    def update_freq_mode(self, freq_mode: FreqMode):
        self.freq_mode = freq_mode

    def read(self, ticker):
        """returns all the alerts for a user and ticker"""
        alert_data_list = list(
            self.collection.find(
                {
                    "username": self.username,
                    "ticker": ticker,
                    "freq_mode": self.freq_mode,
                },
                # projection={"_id": 0}
            )
        )
        return alert_data_list

    def read_all(self):
        """returns all the alerts for a user across all tickers"""
        alert_data_list = list(
            self.collection.find(
                {"username": self.username, "freq_mode": self.freq_mode},
                # projection={"_id": 0}
            )
        )
        return alert_data_list

    def delete_one_alert(self, alert_id):
        """
        Deletes the alert with the specified alert_id (MongoDB _id as string)
        and returns all the alert_list for that user and ticker, excluding the one just deleted
        """
        try:
            object_id = ObjectId(alert_id)
        except:
            raise ValueError(f"Invalid alert_id format: {alert_id}")

        # Find and delete the alert
        trash = self.collection.find_one_and_delete(
            {"_id": object_id}, projection={"_id": 0}
        )

        if not trash:
            raise KeyError(f"No alert to delete with id: {alert_id}")

        ticker = trash.get("ticker")

        return ticker, self.read(ticker)

    def append(
        self,
        ticker,
        alert_description,
        lower_alert_price,
        lower_alert_note,
        upper_alert_price,
        upper_alert_note,
    ):
        """appends a new alert and returns all the alert_list for that user and ticker, including the one just appended"""
        # Create a new alert with current timestamp and triggered_date as None
        new_alert = {
            "username": self.username,
            "ticker": ticker,
            "freq_mode": self.freq_mode,
            "created_time": datetime.now(tz=pytz.UTC),
            "alert_description": alert_description,
            "lower_alert_price": lower_alert_price,
            "lower_alert_note": lower_alert_note,
            "upper_alert_price": upper_alert_price,
            "upper_alert_note": upper_alert_note,
            "triggered_date": None,
        }

        self.collection.insert_one(new_alert)
        return self.read(ticker)

    def update_triggered_date(self, alert_ids):
        """Update triggered_date for a list of alert_ids (ObjectId instances)"""

        if not alert_ids:
            return list()

        result = self.collection.update_many(
            {"_id": {"$in": alert_ids}},
            {"$set": {"triggered_date": datetime.now(tz=pytz.UTC)}},
        )

        if result.matched_count == 0:
            raise KeyError(
                f"No matching alerts found for the given _ids and user: {self.username}"
            )

        updated_alerts = list(self.collection.find({"_id": {"$in": alert_ids}}))

        return updated_alerts

    def delete_other_alerts(self, username_to_keep):
        """Delete all alerts for all users except the specified username_to_keep.
        This is used to delete all alerts for all users except the main user - by design, I only want main user in this app and won't allow other users to use alerts.
        """
        result = self.collection.delete_many({"username": {"$ne": username_to_keep}})
        return result.deleted_count

    def delete_orphaned_tickers(self, tickers_to_delete):
        """Delete all alerts for self.username where the ticker is in tickers_to_delete."""
        if not tickers_to_delete:
            return 0

        result = self.collection.delete_many(
            {
                "username": self.username,
                "freq_mode": self.freq_mode,
                "ticker": {"$in": tickers_to_delete},
            }
        )

        return result.deleted_count


_data_list = None


def get_data_list(freq_mode: FreqMode = FreqMode.DAILY):
    """Get or create global DataList instance for the specified frequency mode"""
    global _data_list
    if _data_list is None:
        _data_list = DataList(raw_data_collection, freq_mode)
    else:
        # Update freq_mode if it's different
        _data_list.update_freq_mode(freq_mode)
    return _data_list


_alert_list = None


def get_alert_list(freq_mode: FreqMode = FreqMode.DAILY):
    """Get or create global AlertList instance for the specified frequency mode"""
    global _alert_list
    if _alert_list is None:
        _alert_list = AlertList(alert_data_collection, freq_mode)
    else:
        # Update freq_mode if it's different
        _alert_list.update_freq_mode(freq_mode)
    return _alert_list

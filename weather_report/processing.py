"""Clean, combine and aggregate the raw daily weather data with pandas.

This module turns the raw tables loaded by storage.py into tables that
are ready for the analysis: dates as index, one table for all cities,
monthly and yearly values. It does not compute statistics or draw plots.
"""

import pandas as pd


def clean_city(df: pd.DataFrame) -> pd.DataFrame:
    """Turn the raw daily data of one city into a clean time series.

    The "time" column is converted to dates and used as the index.
    Rows are sorted by date, duplicated dates are dropped (the first
    one is kept) and missing days are added as rows of NaN, so that
    there is exactly one row per day.

    Parameters
    ----------
    df : pandas.DataFrame
        Raw daily data of one city, as returned by ``load_raw``.

    Returns
    -------
    pandas.DataFrame
        Daily data indexed by date (``DatetimeIndex`` with daily
        frequency), one column for each daily variable.
    """
    # Text to dates, then dates as the index
    cleaned = df.assign(time=pd.to_datetime(df["time"], format="%Y-%m-%d"))
    cleaned = cleaned.set_index("time").sort_index()

    # Drop repeated dates, keeping the first occurrence
    cleaned = cleaned[~cleaned.index.duplicated(keep="first")]

    # One row per day: missing days become rows of NaN
    return cleaned.asfreq("D")
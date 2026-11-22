"""Save and load the raw weather data as CSV files (local cache).

Each city is stored in data/raw/ as one CSV file, exactly as received
from the API. Cleaning and transforming the data are done elsewhere.
"""

from pathlib import Path

import pandas as pd

from weather_report.config import END_DATE, RAW_DATA_DIR, START_DATE
from weather_report.models import City


def response_to_dataframe(data: dict) -> pd.DataFrame:
    """Convert the "daily" block of an API response into a DataFrame.

    Parameters
    ----------
    data : dict
        API response returned by ``fetch_daily_weather``.

    Returns
    -------
    pandas.DataFrame
        One row per day: the "time" column with the dates as text
        and one column for each daily variable.
    """
    return pd.DataFrame(data["daily"])


def raw_path(
    city: City,
    start_date: str = START_DATE,
    end_date: str = END_DATE,
) -> Path:
    """Return the path of the raw CSV file for a city and a period.

    The period is part of the file name, so files of different
    requests never get mixed up (e.g. a short test and the full
    download).

    Parameters
    ----------
    city : City
        The city the data refers to.
    start_date : str, optional
        First day in ISO format "YYYY-MM-DD" (default: START_DATE).
    end_date : str, optional
        Last day in ISO format "YYYY-MM-DD" (default: END_DATE).

    Returns
    -------
    pathlib.Path
        For example data/raw/milan_1940-01-01_2025-12-31.csv
    """
    return RAW_DATA_DIR / f"{city.slug}_{start_date}_{end_date}.csv"
"""Save and load the raw weather data as CSV files (local cache).

Each city is stored in data/raw/ as one CSV file, exactly as received
from the API. Cleaning and transforming the data are done elsewhere.
"""

from pathlib import Path

import pandas as pd

from weather_report.config import (
     DAILY_VARIABLES,
     END_DATE,
    RAW_DATA_DIR,
    START_DATE,
)    
from weather_report.models import City

class StorageError(Exception):
    """Raised when a raw data file cannot be read."""


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


def save_raw(df: pd.DataFrame, path: Path) -> None:
    """Save raw daily data as a CSV file.

    The destination folder is created if it does not exist yet.

    Parameters
    ----------
    df : pandas.DataFrame
        Raw daily data, as returned by ``response_to_dataframe``.
    path : pathlib.Path
        Destination file, usually given by ``raw_path``.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def load_raw(path: Path) -> pd.DataFrame:
    """Load a raw CSV file saved by ``save_raw``.

    Parameters
    ----------
    path : pathlib.Path
        File to read, usually given by ``raw_path``.

    Returns
    -------
    pandas.DataFrame
        The raw daily data, with the same columns as the API response.

    Raises
    ------
    StorageError
        If the file does not exist, is empty or misses expected columns.
    """
    try:
        df = pd.read_csv(path)
    except FileNotFoundError as error:
        raise StorageError(f"Raw data file not found: {path}") from error
    except pd.errors.EmptyDataError as error:
        raise StorageError(f"Raw data file is empty: {path}") from error

    # The file must contain the date column and every daily variable
    expected = ("time", *DAILY_VARIABLES)
    missing = [col for col in expected if col not in df.columns]
    if missing:
        raise StorageError(f"Columns {missing} missing in {path}")
    return df
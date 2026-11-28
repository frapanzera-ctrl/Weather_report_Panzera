"""Save and load the project files: raw CSV cache, tables and figures.

Raw data are downloaded only when their CSV file is missing. Cleaning
and analysis happen in processing.py and analysis.py.
"""

import time
from pathlib import Path

import pandas as pd
# Figure is only used as a type hint in save_figure
from matplotlib.figure import Figure

from weather_report.api import fetch_daily_weather
from weather_report.config import (
    CITIES,
    END_DATE,
    FIGURES_DIR,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
    TABLES_DIR,
    REQUEST_PAUSE,
    START_DATE,
)
from weather_report.models import City


class StorageError(Exception):
    """Raised when a raw CSV file cannot be read."""


def response_to_dataframe(data: dict) -> pd.DataFrame:
    """Turn the "daily" block of an API answer into a DataFrame."""
    # Each key of "daily" (time, temperatures....) becomes a column
    return pd.DataFrame(data["daily"])


def raw_path(
    city: City,
    start_date: str = START_DATE,
    end_date: str = END_DATE,
) -> Path:
    """Return the path of the raw CSV file of a city for a period.

    The period is in the file name, so different downloads never mix.
    """
    # e.g. data/raw/milan_1940-01-01_2025-12-31.csv
    return RAW_DATA_DIR / f"{city.slug}_{start_date}_{end_date}.csv"


def save_raw(df: pd.DataFrame, path: Path) -> None:
    """Save raw daily data as a CSV file, creating the folder if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    # index=False: the row numbers 0, 1, 2... are not saved
    df.to_csv(path, index=False)


def load_raw(path: Path) -> pd.DataFrame:
    """Read a raw CSV file; raise StorageError if it is missing or empty."""
    # Turn the 2 pandas errors into one project error
    try:
        df = pd.read_csv(path)
    except FileNotFoundError as error:
        raise StorageError(f"Raw data file not found: {path}") from error
    except pd.errors.EmptyDataError as error:
        raise StorageError(f"Raw data file is empty: {path}") from error

    return df


def load_all_cities(
    cities: tuple[City, ...] = CITIES,
    start_date: str = START_DATE,
    end_date: str = END_DATE,
    pause: float = REQUEST_PAUSE,
) -> dict[str, pd.DataFrame]:
    """Load the raw data of every city, downloading only the missing files.

    Returns a dict {slug: DataFrame}. Waits ``pause`` seconds between two
    downloads to respect the API rate limit.
    """
    frames = {}
    downloaded = False
    for city in cities:
        # Cache: read the file if it exists, otherwise download it
        path = raw_path(city, start_date, end_date)
        if path.exists():
            print(f"{city.name}: loaded from {path.name}")
        else:
            if downloaded:
                time.sleep(pause)  # respect the API rate limit
            print(f"{city.name}: downloading...")
            data = fetch_daily_weather(city, start_date, end_date)
            save_raw(response_to_dataframe(data), path)
            downloaded = True
        # Always read from the file: same types for cached and new data
        frames[city.slug] = load_raw(path)
    return frames


def save_processed(df: pd.DataFrame, name: str) -> Path:
    """Save a processed table in data/processed/ and return its path."""
    path = PROCESSED_DATA_DIR / f"{name}.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    # The index (the dates) is saved as first column
    df.to_csv(path)
    return path


def save_table(df: pd.DataFrame, name: str) -> Path:
    """Save a results table in outputs/tables/ and return its path."""
    path = TABLES_DIR / f"{name}.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    # The index (city or years) is saved as firts column
    df.to_csv(path)
    return path


def save_figure(fig: Figure, name: str) -> Path:
    """Save a figure as PNG in outputs/figures/ and return its path."""
    path = FIGURES_DIR / f"{name}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    # dpi=150: sharp image; bbox_inches="tight": no extra white margins
    fig.savefig(path, dpi=150, bbox_inches="tight")
    return path

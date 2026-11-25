"""Clean, combine and aggregate the raw daily data with pandas.

Turns the raw tables of storage.py into the daily, monthly and yearly
tables used by analysis.py and plots.py.
"""

import pandas as pd

from weather_report.config import AGGREGATIONS, CITIES
from weather_report.storage import load_all_cities, save_processed
from weather_report.models import City


def clean_city(df: pd.DataFrame) -> pd.DataFrame:
    """Turn the raw data of one city into a daily series indexed by date.

    Missing days are added as rows of NaN: exactly one row per day.
    """
    # Text to dates, then dates as the index (assign returns a copy,
    # so the raw table is not modified)
    cleaned = df.assign(time=pd.to_datetime(df["time"], format="%Y-%m-%d"))
    cleaned = cleaned.set_index("time").sort_index()


    # One row per day: missing days become rows of NaN
    return cleaned.asfreq("D")


def combine_cities(
    frames: dict[str, pd.DataFrame],
    cities: tuple[City, ...] = CITIES,
) -> pd.DataFrame:
    """Clean every city and stack them in one long-format table.

    A "city" column tells which city each row belongs to.
    """
    # From slug to readable name, e.g. "milan" -> "Milan"
    names = {city.slug: city.name for city in cities}

    # Clean every city and add a column with its name
    cleaned = [
        clean_city(df).assign(city=names[slug])
        for slug, df in frames.items()
    ]

    # Stack the tables one under the other: dates stay as index
    return pd.concat(cleaned)


# Leading underscore: internal helper, used by to_monthly and to_annual
def _aggregate(daily: pd.DataFrame, freq: str) -> pd.DataFrame:
    """Aggregate the daily data of each city by period ("MS" or "YS").

    Temperatures are averaged and precipitation summed (see AGGREGATIONS).
    """
    # Group by city and by period at the same time
    grouped = daily.groupby(["city", pd.Grouper(level="time", freq=freq)])
    # reset_index: "City" goes back from the index to a normal column
    return grouped.agg(AGGREGATIONS).reset_index(level="city")


# "MS" / "YS" = month start / year start: each period is labelled
# by its first day (e.g. 1961-01-01 for the year 1961)
def to_monthly(daily: pd.DataFrame) -> pd.DataFrame:
    """Return monthly values of each city (see ``_aggregate``)."""
    return _aggregate(daily, "MS")


def to_annual(daily: pd.DataFrame) -> pd.DataFrame:
    """Return yearly values of each city (see ``_aggregate``)."""
    return _aggregate(daily, "YS")


def monthly_pivot(
    monthly: pd.DataFrame,
    city: str,
    variable: str = "temperature_2m_mean",
) -> pd.DataFrame:
    """Reshape the monthly data of one city into a year x month table.

    Raises ValueError if the city is not in the table.
    """
    # Keep only the rows of the chosen city (boolean mask)
    data = monthly[monthly["city"] == city]
    if data.empty:
        raise ValueError(f"No monthly data for city {city!r}")

    # Year and month from the dates, then one row per year
    data = data.assign(year=data.index.year, month=data.index.month)
    return data.pivot(index="year", columns="month", values=variable)


def build_tables(save: bool = True) -> dict[str, pd.DataFrame]:
    """Run the whole pipeline: return the daily, monthly and yearly tables.

    If ``save`` is True the tables are also written to data/processed/.
    """
    # Load (or download), clean and join the data of all cities
    daily = combine_cities(load_all_cities())
    tables = {
        "daily": daily,
        "monthly": to_monthly(daily),
        "annual": to_annual(daily),
    }
    # Save each table as a CSV file, if requested
    if save:
        for name, table in tables.items():
            path = save_processed(table, name)
            print(f"{name}: saved to {path.name}")
    return tables
"""Clean, combine and aggregate the raw daily weather data with pandas.

This module turns the raw tables loaded by storage.py into tables that
are ready for the analysis: dates as index, one table for all cities,
monthly and yearly values. It does not compute statistics or draw plots.
"""

import pandas as pd

from weather_report.config import AGGREGATIONS, CITIES, MIN_VALID_FRACTION
from weather_report.storage import load_all_cities, save_processed
from weather_report.models import City


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

def combine_cities(
    frames: dict[str, pd.DataFrame],
    cities: tuple[City, ...] = CITIES,
) -> pd.DataFrame:
    """Clean the data of several cities and join them in one long table.

    Each raw table is cleaned with ``clean_city`` and the tables are
    stacked one under the other. A "city" column with the city name
    tells which city each row belongs to (long format).

    Parameters
    ----------
    frames : dict of str to pandas.DataFrame
        Raw daily data keyed by city slug, as returned by
        ``load_all_cities``.
    cities : tuple of City, optional
        Cities used to turn slugs into names (default: CITIES).

    Returns
    -------
    pandas.DataFrame
        Daily data of all cities indexed by date, with a "city" column
        and one column for each daily variable.
    """
    # From slug to readable name, e.g. "milan" -> "Milan"
    names = {city.slug: city.name for city in cities}

    # Clean every city, keyed by its name
    cleaned = {names[slug]: clean_city(df) for slug, df in frames.items()}

    # Stack the tables: the keys become the "city" level of the index
    combined = pd.concat(cleaned, names=["city", "time"])

    # Move "city" from the index to a column: only dates stay as index
    return combined.reset_index(level="city")

def _aggregate(
    daily: pd.DataFrame,
    freq: str,
    min_fraction: float = MIN_VALID_FRACTION,
) -> pd.DataFrame:
    """Aggregate the daily data of each city over periods of time.

    Temperatures are averaged and precipitation is summed, following
    AGGREGATIONS. A value becomes NaN if less than ``min_fraction`` of
    the days in its period have data.

    Parameters
    ----------
    daily : pandas.DataFrame
        Daily data of all cities, as returned by ``combine_cities``.
    freq : str
        pandas frequency of the periods, e.g. "MS" (months) or "YS"
        (years).
    min_fraction : float, optional
        Minimum share of valid days, between 0 and 1
        (default: MIN_VALID_FRACTION).

    Returns
    -------
    pandas.DataFrame
        One row per city and period, indexed by the first day of the
        period, with a "city" column.
    """
    # Group by city and by period at the same time
    grouped = daily.groupby(["city", pd.Grouper(level="time", freq=freq)])
    values = grouped.agg(AGGREGATIONS)

    # Share of days with data: valid days / days in the period
    fraction = grouped.count().div(grouped.size(), axis=0)

    # Hide the values of incomplete periods
    values = values.where(fraction >= min_fraction)
    return values.reset_index(level="city")


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

    Parameters
    ----------
    monthly : pandas.DataFrame
        Monthly data of all cities, as returned by ``to_monthly``.
    city : str
        Name of the city, e.g. "Milan".
    variable : str, optional
        Column to put in the table (default: "temperature_2m_mean").

    Returns
    -------
    pandas.DataFrame
        One row per year and one column per month (1 to 12).

    Raises
    ------
    ValueError
        If there are no data for the given city.
    """
    data = monthly[monthly["city"] == city]
    if data.empty:
        raise ValueError(f"No monthly data for city {city!r}")

    # Year and month from the dates, then one row per year
    data = data.assign(year=data.index.year, month=data.index.month)
    return data.pivot(index="year", columns="month", values=variable)

def build_tables(save: bool = True) -> dict[str, pd.DataFrame]:
    """Run the whole processing and return the daily, monthly and yearly tables.

    Raw data are loaded (or downloaded if missing), cleaned, joined and
    aggregated. If ``save`` is True each table is also written to
    data/processed/.

    Parameters
    ----------
    save : bool, optional
        Whether to save the tables as CSV files (default: True).

    Returns
    -------
    dict of str to pandas.DataFrame
        The tables keyed by name: "daily", "monthly" and "annual".
    """
    daily = combine_cities(load_all_cities())
    tables = {
        "daily": daily,
        "monthly": to_monthly(daily),
        "annual": to_annual(daily),
    }
    if save:
        for name, table in tables.items():
            path = save_processed(table, name)
            print(f"{name}: saved to {path.name}")
    return tables
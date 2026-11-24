"""Compute statistics on the processed weather tables with numpy and scipy.

Every function receives a table built by processing.py and returns a
new table or a small dictionary of numbers. It does not draw plots.
"""

import pandas as pd
from scipy import stats

from weather_report.config import REFERENCE_PERIOD


def city_summary(
    daily: pd.DataFrame,
    variable: str = "temperature_2m_mean",
) -> pd.DataFrame:
    """Descriptive statistics of one daily variable for each city.

    Parameters
    ----------
    daily : pandas.DataFrame
        Daily data of all cities, as returned by ``combine_cities``.
    variable : str, optional
        Column to describe (default: "temperature_2m_mean").

    Returns
    -------
    pandas.DataFrame
        One row per city, columns "mean", "std", "min" and "max".
    """
    # Split by city, compute the four statistics, round for reading
    summary = daily.groupby("city")[variable].agg(["mean", "std", "min", "max"])
    return summary.round(2)

def annual_anomalies(
    annual: pd.DataFrame,
    variable: str = "temperature_2m_mean",
    period: tuple[int, int] = REFERENCE_PERIOD,
) -> pd.DataFrame:
    """Difference between each yearly value and the city's climate normal.

    The climate normal is the mean of the variable over the reference
    period (default: 1961-1990). Anomalies put all cities on the same
    scale, centred on zero.

    Parameters
    ----------
    annual : pandas.DataFrame
        Yearly data of all cities, as returned by ``to_annual``.
    variable : str, optional
        Column to use (default: "temperature_2m_mean").
    period : tuple of int, optional
        First and last year of the reference period
        (default: REFERENCE_PERIOD).

    Returns
    -------
    pandas.DataFrame
        Indexed by the first day of each year, with a "city" column
        and an "anomaly" column.
    """
    # Keep only the years of the reference period (boolean mask)
    start, end = period
    years = annual.index.year
    in_period = (years >= start) & (years <= end)

    # Climate normal of each city, then subtract it row by row
    normals = annual[in_period].groupby("city")[variable].mean()
    anomaly = annual[variable] - annual["city"].map(normals)
    return annual.assign(anomaly=anomaly.round(2))[["city", "anomaly"]]
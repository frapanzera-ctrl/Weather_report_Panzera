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
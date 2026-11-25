"""Compute statistics on the processed weather tables with numpy and scipy.

Every function receives a table built by processing.py and returns a
new table or a small dictionary of numbers. It does not draw plots.
"""

import pandas as pd
from scipy import stats

from weather_report.config import (
    HOT_DAY_THRESHOLD,
    RECENT_PERIOD,
    REFERENCE_PERIOD,
)

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

def linear_trend(
    annual: pd.DataFrame,
    city: str,
    variable: str = "temperature_2m_mean",
) -> dict:
    """Fit a straight line to the yearly values of one city.

    The slope is given per decade. The p-value tests the null
    hypothesis that there is no trend (slope equal to zero).

    Parameters
    ----------
    annual : pandas.DataFrame
        Yearly data of all cities, as returned by ``to_annual``.
    city : str
        Name of the city, e.g. "Milan".
    variable : str, optional
        Column to use (default: "temperature_2m_mean").

    Returns
    -------
    dict
        Keys "city", "slope_per_decade", "r_squared" and "p_value".
    """
    data = annual[annual["city"] == city]

    # Years on x, values on y, as numpy arrays
    years = data.index.year.to_numpy()
    values = data[variable].to_numpy()
    result = stats.linregress(years, values)

    return {
        "city": city,
        "slope_per_decade": round(float(result.slope) * 10, 3),
        "r_squared": round(float(result.rvalue) ** 2, 3),
        "p_value": float(result.pvalue),
    }


def trend_table(
    annual: pd.DataFrame,
    variable: str = "temperature_2m_mean",
) -> pd.DataFrame:
    """Linear trend of every city in one table (see ``linear_trend``).

    Parameters
    ----------
    annual : pandas.DataFrame
        Yearly data of all cities, as returned by ``to_annual``.
    variable : str, optional
        Column to use (default: "temperature_2m_mean").

    Returns
    -------
    pandas.DataFrame
        One row per city, columns "slope_per_decade", "r_squared"
        and "p_value".
    """
    rows = [linear_trend(annual, city, variable)
            for city in annual["city"].unique()]
    return pd.DataFrame(rows).set_index("city")

def compare_periods(
    annual: pd.DataFrame,
    city: str,
    variable: str = "temperature_2m_mean",
    early: tuple[int, int] = REFERENCE_PERIOD,
    late: tuple[int, int] = RECENT_PERIOD,
) -> dict:
    """Compare the mean of two periods of one city with Welch's t-test.

    The null hypothesis is that the two periods have the same mean.
    Welch's version does not assume equal variances.

    Parameters
    ----------
    annual : pandas.DataFrame
        Yearly data of all cities, as returned by ``to_annual``.
    city : str
        Name of the city, e.g. "Milan".
    variable : str, optional
        Column to use (default: "temperature_2m_mean").
    early : tuple of int, optional
        First and last year of the first period
        (default: REFERENCE_PERIOD).
    late : tuple of int, optional
        First and last year of the second period
        (default: RECENT_PERIOD).

    Returns
    -------
    dict
        Keys "city", "early_mean", "late_mean", "difference",
        "t_statistic" and "p_value".
    """
    data = annual[annual["city"] == city]
    years = data.index.year

    # Yearly values of the two periods (boolean masks)
    first = data.loc[(years >= early[0]) & (years <= early[1]), variable]
    second = data.loc[(years >= late[0]) & (years <= late[1]), variable]

    t_statistic, p_value = stats.ttest_ind(second, first, equal_var=False)

    return {
        "city": city,
        "early_mean": round(float(first.mean()), 2),
        "late_mean": round(float(second.mean()), 2),
        "difference": round(float(second.mean() - first.mean()), 2),
        "t_statistic": round(float(t_statistic), 2),
        "p_value": float(p_value),
    }


def comparison_table(
    annual: pd.DataFrame,
    variable: str = "temperature_2m_mean",
    early: tuple[int, int] = REFERENCE_PERIOD,
    late: tuple[int, int] = RECENT_PERIOD,
) -> pd.DataFrame:
    """Period comparison of every city in one table (see ``compare_periods``).

    Parameters
    ----------
    annual : pandas.DataFrame
        Yearly data of all cities, as returned by ``to_annual``.
    variable : str, optional
        Column to use (default: "temperature_2m_mean").
    early : tuple of int, optional
        First and last year of the first period
        (default: REFERENCE_PERIOD).
    late : tuple of int, optional
        First and last year of the second period
        (default: RECENT_PERIOD).

    Returns
    -------
    pandas.DataFrame
        One row per city, columns "early_mean", "late_mean",
        "difference", "t_statistic" and "p_value".
    """
    rows = [compare_periods(annual, city, variable, early, late)
            for city in annual["city"].unique()]
    return pd.DataFrame(rows).set_index("city")


def hot_days_per_year(
    daily: pd.DataFrame,
    threshold: float = HOT_DAY_THRESHOLD,
) -> pd.DataFrame:
    """Count the days of each year with a maximum temperature above a threshold.

    Parameters
    ----------
    daily : pandas.DataFrame
        Daily data of all cities, as returned by ``combine_cities``.
    threshold : float, optional
        Minimum daily maximum temperature in °C
        (default: HOT_DAY_THRESHOLD).

    Returns
    -------
    pandas.DataFrame
        One row per year and one column per city.
    """
    # True for every hot day: summing booleans counts them
    hot = daily["temperature_2m_max"] >= threshold
    year = daily.index.year.rename("year")
    counts = hot.groupby([daily["city"], year]).sum()

    # Cities from the rows to the columns (wide format)
    return counts.unstack(level="city")
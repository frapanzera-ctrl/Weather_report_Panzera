"""Compute statistics on the processed tables with pandas and scipy.

Every function takes a table from processing.py and returns a new
table or a dict of numbers. It does not draw plots.
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
    """Mean, standard deviation, min and max of one variable per city."""
    # Split by city, compute the four statistics, round for reading
    summary = daily.groupby("city")[variable].agg(["mean", "std", "min", "max"])
    return summary.round(2)


def annual_anomalies(
    annual: pd.DataFrame,
    variable: str = "temperature_2m_mean",
    period: tuple[int, int] = REFERENCE_PERIOD,
) -> pd.DataFrame:
    """Difference between each yearly value and the city's climate normal.

    The normal is the mean over the reference period (default 1961-1990).
    """
    # Keep only the years of the reference period (boolean mask)
    start, end = period
    years = annual.index.year
    in_period = (years >= start) & (years <= end)

    # Climate normal of each city, then subtract it row by row
    # (map gives each row the normal of its own city)
    normals = annual[in_period].groupby("city")[variable].mean()
    anomaly = annual[variable] - annual["city"].map(normals)
    # Keep only the city and the anomaly columns 
    return annual.assign(anomaly=anomaly.round(2))[["city", "anomaly"]]


def linear_trend(
    annual: pd.DataFrame,
    city: str,
    variable: str = "temperature_2m_mean",
) -> dict:
    """Fit a straight line to the yearly values of one city.

    Returns slope per decade, R² and p-value (H0: slope equal to zero).
    """
    # Keep only the rows of the chosen city
    data = annual[annual["city"] == city]

    # Years on x, values on y, as numpy arrays
    years = data.index.year.to_numpy()
    values = data[variable].to_numpy()
    result = stats.linregress(years, values)

    # slope is in °C per year, multiply by 10 for °C per decade
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
    """Run ``linear_trend`` for every city and return one table."""
    # One dict per city, then one row per dict
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

    H0: same mean in both periods. Welch does not assume equal variances.
    """
    data = annual[annual["city"] == city]
    years = data.index.year

    # Yearly values of the two periods (boolean masks)
    first = data.loc[(years >= early[0]) & (years <= early[1]), variable]
    second = data.loc[(years >= late[0]) & (years <= late[1]), variable]

    # Recent minus early: a positive t means the recent period is warmer
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
    """Run ``compare_periods`` for every city and return one table."""
    # One dict per city, then one row per dict
    rows = [compare_periods(annual, city, variable, early, late)
            for city in annual["city"].unique()]
    return pd.DataFrame(rows).set_index("city")


def hot_days_per_year(
    daily: pd.DataFrame,
    threshold: float = HOT_DAY_THRESHOLD,
) -> pd.DataFrame:
    """Count the days of each year with maximum temperature >= threshold.

    Returns one row per year and one column per city.
    """
    # True for every hot day: summing booleans counts them
    hot = daily["temperature_2m_max"] >= threshold
    year = daily.index.year.rename("year")
    # Group by city and year, then add up the True values
    counts = hot.groupby([daily["city"], year]).sum()

    # Cities from the rows to the columns (wide format)
    return counts.unstack(level="city")


def hot_days_by_period(
    hot: pd.DataFrame,
    early: tuple[int, int] = REFERENCE_PERIOD,
    late: tuple[int, int] = RECENT_PERIOD,
) -> pd.DataFrame:
    """Mean number of hot days per year in two periods, for every city."""
    # The index holds the years, so .loc can slice by year
    table = pd.DataFrame({
        "early_mean": hot.loc[early[0]:early[1]].mean(),
        "late_mean": hot.loc[late[0]:late[1]].mean(),
    })
    # One decimal is enough for a number of days
    return table.round(1)
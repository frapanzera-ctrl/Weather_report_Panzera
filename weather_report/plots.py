"""Draw the results of the analysis with matplotlib and seaborn.

Every function receives a table built by processing.py or analysis.py
and returns a matplotlib Figure. It does not compute statistics and
does not save files (see storage.save_figure).
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure

from weather_report.config import END_YEAR, HOT_DAY_THRESHOLD, START_YEAR
from weather_report.processing import monthly_pivot

# One fixed color per city, the same in every plot
CITY_COLORS = {
    "Milan": "#2a78d6",
    "Palermo": "#eb6834",
    "Berlin": "#1baf7a",
    "London": "#eda100",
    "Madrid": "#e87ba4",
}


def plot_anomalies(anomalies: pd.DataFrame) -> Figure:
    """Line plot of the yearly temperature anomaly of every city.

    Parameters
    ----------
    anomalies : pandas.DataFrame
        Output of ``annual_anomalies``.

    Returns
    -------
    matplotlib.figure.Figure
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    for city, color in CITY_COLORS.items():
        data = anomalies[anomalies["city"] == city]
        ax.plot(data.index.year, data["anomaly"], color=color, label=city)

    # Zero line: the climate normal
    ax.axhline(0, color="gray", linewidth=1)
    ax.set_xlabel("Year")
    ax.set_ylabel("Anomaly (°C)")
    ax.set_title("Yearly temperature anomaly compared with 1961-1990")
    ax.legend()
    return fig

def plot_trends(trends: pd.DataFrame) -> Figure:
    """Horizontal bar chart of the temperature trend of every city.

    Parameters
    ----------
    trends : pandas.DataFrame
        Output of ``trend_table``.

    Returns
    -------
    matplotlib.figure.Figure
    """
    # Ascending order: barh draws the first bar at the bottom,
    # so the fastest-warming city ends up at the top
    data = trends.sort_values("slope_per_decade")
    colors = [CITY_COLORS[city] for city in data.index]

    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.barh(data.index, data["slope_per_decade"], color=colors)
    ax.bar_label(bars, fmt="%.2f", padding=3)  # value at the end of each bar
    ax.set_xlabel("Trend (°C per decade)")
    ax.set_title(f"Temperature trend {START_YEAR}-{END_YEAR}")
    return fig

def plot_hot_days(hot: pd.DataFrame) -> Figure:
    """Line plot of the number of hot days per year in every city.

    Parameters
    ----------
    hot : pandas.DataFrame
        Output of ``hot_days_per_year``.

    Returns
    -------
    matplotlib.figure.Figure
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    for city, color in CITY_COLORS.items():
        ax.plot(hot.index, hot[city], color=color, label=city)

    title = f"Hot days per year (maximum ≥ {HOT_DAY_THRESHOLD:g} °C)"
    ax.set_xlabel("Year")
    ax.set_ylabel("Days")
    ax.set_title(title)
    ax.legend()
    return fig

def plot_warming_stripes(anomalies: pd.DataFrame, city: str) -> Figure:
    """Warming stripes of one city: one colored stripe per year.

    Blue years are colder and red years warmer than the climate normal.

    Parameters
    ----------
    anomalies : pandas.DataFrame
        Output of ``annual_anomalies``.
    city : str
        Name of the city, e.g. "Milan".

    Returns
    -------
    matplotlib.figure.Figure
    """
    data = anomalies[anomalies["city"] == city]
    years = data.index.year
    values = data["anomaly"].to_numpy()

    # Same limit on both sides, so that zero is white
    limit = np.abs(values).max()

    fig, ax = plt.subplots(figsize=(10, 2))
    ax.imshow(
        values[np.newaxis, :],  # 1 row x N years, drawn as an image
        cmap="RdBu_r",
        vmin=-limit,
        vmax=limit,
        aspect="auto",
        extent=(years[0], years[-1] + 1, 0, 1),
    )
    ax.set_yticks([])  # the vertical axis has no meaning here
    ax.set_title(f"Warming stripes: {city}")
    return fig


def plot_monthly_heatmap(monthly: pd.DataFrame, city: str) -> Figure:
    """Heatmap of the monthly mean temperature of one city, year by month.

    Parameters
    ----------
    monthly : pandas.DataFrame
        Output of ``to_monthly``.
    city : str
        Name of the city, e.g. "Milan".

    Returns
    -------
    matplotlib.figure.Figure
    """
    table = monthly_pivot(monthly, city)  # one row per year, one per month

    fig, ax = plt.subplots(figsize=(7, 10))
    sns.heatmap(
        table,
        cmap="Reds",
        yticklabels=10,  # one label every 10 years
        cbar_kws={"label": "Mean temperature (°C)"},
        ax=ax,
    )
    ax.set_xlabel("Month")
    ax.set_ylabel("Year")
    ax.set_title(f"Monthly mean temperature: {city}")
    return fig
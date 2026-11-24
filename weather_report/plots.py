"""Draw the results of the analysis with matplotlib and seaborn.

Every function receives a table built by processing.py or analysis.py
and returns a matplotlib Figure. It does not compute statistics and
does not save files (see storage.save_figure).
"""

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

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
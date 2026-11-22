"""Download the daily weather data from the Open-meteo hystorical weather API.

This module only talks to the API: it builds the request, sends it and
checks the answer. Saving and cleaning the data is done somewhere else.
"""
from weather_report.config import (
    DAILY_VARIABLES,
    END_DATE,
    START_DATE,
    TIMEZONE,
    WEATHER_MODEL,
)
from weather_report.models import City

class WeatherAPIError(Exception):
    """Raised when weather data cannot be downloaded from Open-meteo."""

def build_params(
    city: City,
    start_date: str = START_DATE,
    end_date: str = END_DATE,
) -> dict:
    """Build the query parameters of the API request for one city.

    Parameters
    ----------
    city : City
        The city to download data for.
    start_date : str, optional
        First day in ISO format "YYYY-MM-DD" (default: START_DATE).
    end_date : str, optional
        Last day in ISO format "YYYY-MM-DD" (default: END_DATE).

    Returns
    -------
    dict
        Query parameters for the Open-Meteo archive endpoint.
    """
    return {
        "latitude": city.latitude,
        "longitude": city.longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": ",".join(DAILY_VARIABLES),
        "timezone": TIMEZONE,
        "models": WEATHER_MODEL,
    }


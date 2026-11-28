"""Download daily weather data from the Open-Meteo Historical Weather API.

This module only talks to the API. Saving and cleaning the data happen
in storage.py and processing.py.
"""

import requests

from weather_report.config import (
    ARCHIVE_API_URL,
    DAILY_VARIABLES,
    END_DATE,
    REQUEST_TIMEOUT,
    START_DATE,
    TIMEZONE,
    WEATHER_MODEL,
)
from weather_report.models import City


class WeatherAPIError(Exception):
    """Raised when the data of a city cannot be downloaded."""


def build_params(
    city: City,
    start_date: str = START_DATE,
    end_date: str = END_DATE,
) -> dict:
    """Build the query parameters of the request for one city."""
    # Variables are sent as one comma-separated string
    return {
        "latitude": city.latitude,
        "longitude": city.longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": ",".join(DAILY_VARIABLES),
        "timezone": TIMEZONE,
        "models": WEATHER_MODEL,
    }


def fetch_daily_weather(
    city: City,
    start_date: str = START_DATE,
    end_date: str = END_DATE,
) -> dict:
    """Download the daily data of one city and return the JSON as a dict.

    Raises WeatherAPIError if the request fails or the answer has no
    "daily" block.
    """
    params = build_params(city, start_date, end_date)

    # 1. Send the request: network problems, timeouts and HTTP errors
    #    (4xx, 5xx) all become a WeatherAPIError
    try:
        response = requests.get(
            ARCHIVE_API_URL, params=params, timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as error:
        raise WeatherAPIError(
            f"Could not download data for {city.name}: {error}"
        ) from error

    # 2. Read the JSON and check that the "daily" block is there
    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError as error:
        raise WeatherAPIError(
            f"Invalid JSON received for {city.name}"
        ) from error
    if "daily" not in data:
        raise WeatherAPIError(
            f"No daily data in the response for {city.name}"
        )
    return data

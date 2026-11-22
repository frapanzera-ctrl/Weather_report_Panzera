"""Download the daily weather data from the Open-meteo hystorical weather API.

This module only talks to the API: it builds the request, sends it and
checks the answer. Saving and cleaning the data is done somewhere else.
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


def fetch_daily_weather(
    city: City,
    start_date: str = START_DATE,
    end_date: str = END_DATE,
) -> dict:
    """Download daily weather data for one city.

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
        The JSON response as a dictionary. Its "daily" key holds the
        list of dates and one list of values for each variable.

    Raises
    ------
    WeatherAPIError
        If the API cannot be reached, returns an error or sends a
        response without daily data.
    """
    params = build_params(city, start_date, end_date)

    # 1. Send the request: network problems and timeouts end up here
    try:
        response = requests.get(
            ARCHIVE_API_URL, params=params, timeout=REQUEST_TIMEOUT
        )
    except requests.exceptions.RequestException as error:
        raise WeatherAPIError(
            f"Could not reach Open-Meteo for {city.name}: {error}"
        ) from error

    # 2. Check the status code: Open-Meteo explains errors in "reason"
    if response.status_code != 200:
        try:
            reason = response.json().get("reason", response.text)
        except requests.exceptions.JSONDecodeError:
            reason = response.text
        message = (
            f"Open-Meteo error {response.status_code} "
            f"for {city.name}: {reason}"
        )
        if response.status_code == 429:
            message += " (rate limit reached: wait and try again later)"
        raise WeatherAPIError(message)

    # 3. Check the content: the answer must contain the "daily" block
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

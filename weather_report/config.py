"""Project-wide settings: folder paths, API parameters, period and cities.

Every constant lives here, so each value is changed in one place only.
"""

from pathlib import Path

from weather_report.models import City

# Paths: built from this file's location, so they work from any folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
FIGURES_DIR = OUTPUTS_DIR / "figures"
TABLES_DIR = OUTPUTS_DIR / "tables"

# Open-Meteo Historical Weather API
ARCHIVE_API_URL = "https://archive-api.open-meteo.com/v1/archive"
DAILY_VARIABLES = (
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "precipitation_sum",
)
WEATHER_MODEL = "era5"  # one model only: no artificial jumps in the series
TIMEZONE = "auto"  # days follow the local time for each city
REQUEST_TIMEOUT = 60  # seconds
REQUEST_PAUSE = 90  # seconds between cities (API rate limit)

# Time period: complete years and ISO dates
START_YEAR = 1940
END_YEAR = 2025
START_DATE = f"{START_YEAR}-01-01"
END_DATE = f"{END_YEAR}-12-31"

# Reference period for anomalies (climate normal)
REFERENCE_PERIOD = (1961, 1990)
# Recent period compared with the reference period
RECENT_PERIOD = (1996, 2025)
# A "hot day" has a maximum temperature of at least this value (°C)
HOT_DAY_THRESHOLD = 30.0

# Cities: coordinates from the Open-Meteo Geocoding API
CITIES = (
    City("Milan", 45.46427, 9.18951),
    City("Palermo", 38.1166, 13.3636),
    City("Berlin", 52.52437, 13.41053),
    City("London", 51.50853, -0.12574),
    City("Madrid", 40.4165, -3.70256),
)


# Aggregation rule of each daily variable: states (temperatures) are
# averaged, accumulated quantities (precipitation) are summed
AGGREGATIONS = {
    "temperature_2m_max": "mean",
    "temperature_2m_min": "mean",
    "temperature_2m_mean": "mean",
    "precipitation_sum": "sum",
}

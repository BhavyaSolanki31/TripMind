
import json
import time
import threading
from datetime import date as Date, timedelta
from functools import lru_cache
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

TIMEOUT_SECONDS = 15
MAX_ATTEMPTS = 3
MAX_FORECAST_DAYS = 16
CACHE_TTL_SECONDS = 900

WEATHER_FIELDS = (
    "temperature_2m_max,"
    "weather_code,"
    "precipitation_probability_max,"
    "wind_speed_10m_max"
)

_forecast_cache = {}
_cache_lock = threading.Lock()


def _get_json(url):
    """
    Fetch JSON with timeouts and retries.

    HTTP 429 is not retried because repeated requests can
    make rate limiting worse.
    """

    request = Request(
        url,
        headers={"User-Agent": "TripMind-Weather/1.0"}
    )

    for attempt in range(MAX_ATTEMPTS):
        try:
            with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                return json.loads(response.read().decode("utf-8"))

        except HTTPError as error:
            if error.code == 429:
                raise

            if error.code not in (500, 502, 503, 504):
                raise

            if attempt == MAX_ATTEMPTS - 1:
                raise

        except (URLError, TimeoutError, OSError, json.JSONDecodeError):
            if attempt == MAX_ATTEMPTS - 1:
                raise

        time.sleep(1.0 * (attempt + 1))


@lru_cache(maxsize=128)
def _get_coordinates_cached(destination):
    """Cache geocoding results for repeated destination searches."""

    params = {
        "name": destination,
        "count": 1,
        "language": "en",
        "format": "json",
    }

    url = f"{GEOCODING_URL}?{urlencode(params)}"
    data = _get_json(url)

    results = data.get("results", [])

    if not results:
        raise ValueError(f"Could not find destination: {destination}")

    location = results[0]

    return (
        location["latitude"],
        location["longitude"],
        location.get("name", destination),
        location.get("country", ""),
    )


def get_coordinates(destination):
    """Resolve a destination to geographic coordinates."""

    latitude, longitude, name, country = (
        _get_coordinates_cached(destination.strip())
    )

    return {
        "latitude": latitude,
        "longitude": longitude,
        "name": name,
        "country": country,
    }


def weather_code_to_condition(code):
    """Convert Open-Meteo WMO weather codes to readable conditions."""

    weather_codes = {
        0: "Clear Sky",
        1: "Mainly Clear",
        2: "Partly Cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing Rime Fog",
        51: "Light Drizzle",
        53: "Moderate Drizzle",
        55: "Dense Drizzle",
        56: "Light Freezing Drizzle",
        57: "Dense Freezing Drizzle",
        61: "Slight Rain",
        63: "Moderate Rain",
        65: "Heavy Rain",
        66: "Light Freezing Rain",
        67: "Heavy Freezing Rain",
        71: "Slight Snow",
        73: "Moderate Snow",
        75: "Heavy Snow",
        77: "Snow Grains",
        80: "Slight Rain Showers",
        81: "Moderate Rain Showers",
        82: "Violent Rain Showers",
        85: "Slight Snow Showers",
        86: "Heavy Snow Showers",
        95: "Thunderstorm",
        96: "Thunderstorm with Slight Hail",
        99: "Thunderstorm with Heavy Hail",
    }

    return weather_codes.get(code, "Unknown")


def unavailable_weather(destination, date, reason):
    """Return an explicit unavailable result without inventing weather."""

    return {
        "destination": destination,
        "date": date,
        "temperature": None,
        "condition": "Weather unavailable",
        "rain_probability": None,
        "wind": "Unavailable",
        "source": "unavailable",
        "status": "unavailable",
        "message": reason,
    }


def _get_cached_forecast(latitude, longitude, start_date, end_date):
    """Fetch and cache one complete daily forecast date range."""

    cache_key = (
        round(float(latitude), 4),
        round(float(longitude), 4),
        start_date,
        end_date,
    )

    now = time.monotonic()

    with _cache_lock:
        cached = _forecast_cache.get(cache_key)

        if cached and now - cached["time"] < CACHE_TTL_SECONDS:
            return cached["data"]

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": WEATHER_FIELDS,
        "timezone": "auto",
        "start_date": start_date,
        "end_date": end_date,
    }

    url = f"{FORECAST_URL}?{urlencode(params)}"
    data = _get_json(url)

    if not isinstance(data.get("daily"), dict):
        raise ValueError("Weather service returned no daily forecast data.")

    with _cache_lock:
        _forecast_cache[cache_key] = {
            "time": time.monotonic(),
            "data": data,
        }

        # Keep the in-memory cache bounded.
        if len(_forecast_cache) > 128:
            oldest_key = min(
                _forecast_cache,
                key=lambda key: _forecast_cache[key]["time"]
            )
            _forecast_cache.pop(oldest_key, None)

    return data


def _build_daily_weather(destination, requested_date, daily):
    """Convert one date from the API's daily response into TripMind format."""

    dates = daily.get("time", [])

    if not isinstance(dates, list) or requested_date not in dates:
        return unavailable_weather(
            destination,
            requested_date,
            "No forecast is available for the requested date.",
        )

    index = dates.index(requested_date)

    required_fields = (
        "temperature_2m_max",
        "weather_code",
        "precipitation_probability_max",
        "wind_speed_10m_max",
    )

    values = {}

    for field in required_fields:
        series = daily.get(field)

        if not isinstance(series, list) or index >= len(series):
            return unavailable_weather(
                destination,
                requested_date,
                f"The {field} measurement is missing.",
            )

        value = series[index]

        if value is None:
            return unavailable_weather(
                destination,
                requested_date,
                f"The {field} measurement is unavailable.",
            )

        values[field] = value

    temperature = values["temperature_2m_max"]
    weather_code = values["weather_code"]
    rain_probability = values["precipitation_probability_max"]
    wind_speed = values["wind_speed_10m_max"]

    if not isinstance(weather_code, int):
        return unavailable_weather(
            destination,
            requested_date,
            "The weather service returned an invalid weather code.",
        )

    if not 0 <= rain_probability <= 100:
        return unavailable_weather(
            destination,
            requested_date,
            "The rain probability is outside the valid range.",
        )

    if temperature < -100 or temperature > 70 or wind_speed < 0:
        return unavailable_weather(
            destination,
            requested_date,
            "The weather service returned implausible measurements.",
        )

    return {
        "destination": destination,
        "date": requested_date,
        "temperature": temperature,
        "condition": weather_code_to_condition(weather_code),
        "rain_probability": rain_probability,
        "wind": f"{wind_speed} km/h",
        "source": "Open-Meteo forecast API",
        "status": "forecast",
    }


def search_weather_range(destination, start_date, end_date):
    """
    Fetch weather for an entire trip using one forecast API request.

    Dates outside the supported forecast horizon are returned as
    unavailable. Existing response fields are preserved.
    """

    if not isinstance(destination, str) or not destination.strip():
        raise ValueError("Destination must be a non-empty city name.")

    destination = destination.strip()

    try:
        start = Date.fromisoformat(start_date)
        end = Date.fromisoformat(end_date)
    except (TypeError, ValueError):
        raise ValueError("Dates must use YYYY-MM-DD format.")

    if end < start:
        raise ValueError("End date must be after or equal to start date.")

    today = Date.today()
    last_forecast_date = today + timedelta(days=MAX_FORECAST_DAYS)

    daily_weather = []
    current = start

    # Build unavailable entries for past dates and dates beyond
    # the supported forecast horizon.
    while current <= end:
        date_string = current.isoformat()

        if current < today:
            daily_weather.append(
                unavailable_weather(
                    destination,
                    date_string,
                    "Past dates are not supported.",
                )
            )

        elif current > last_forecast_date:
            daily_weather.append(
                unavailable_weather(
                    destination,
                    date_string,
                    f"Forecasts are available for up to "
                    f"{MAX_FORECAST_DAYS} days ahead.",
                )
            )

        else:
            daily_weather.append(None)

        current += timedelta(days=1)

    forecast_dates = [
        (start + timedelta(days=index)).isoformat()
        for index, item in enumerate(daily_weather)
        if item is None
    ]

    if not forecast_dates:
        return daily_weather

    try:
        location = get_coordinates(destination)

        # Fetch all eligible dates together, rather than once per day.
        forecast_start = forecast_dates[0]
        forecast_end = forecast_dates[-1]

        data = _get_cached_forecast(
            location["latitude"],
            location["longitude"],
            forecast_start,
            forecast_end,
        )

        daily_data = data["daily"]

        for index, item in enumerate(daily_weather):
            if item is None:
                daily_weather[index] = _build_daily_weather(
                    destination,
                    forecast_dates[forecast_dates.index(
                        next(
                            date_string
                            for date_string in forecast_dates
                            if date_string == (
                                start + timedelta(days=index)
                            ).isoformat()
                        )
                    )],
                    daily_data,
                )

    except Exception as error:
        print(
            f"Weather range lookup failed for {destination} "
            f"from {forecast_dates[0]} to {forecast_dates[-1]}: {error}"
        )

        for index, item in enumerate(daily_weather):
            if item is None:
                requested_date = (start + timedelta(days=index)).isoformat()

                daily_weather[index] = _build_daily_weather(
                    destination,
                    requested_date,
                    daily_data,
                )

    return daily_weather


def search_weather(destination, date):
    """
    Backward-compatible single-date weather lookup.

    Invalid dates return a structured unavailable response
    instead of crashing the application.
    """

    try:
        results = search_weather_range(destination, date, date)
        return results[0]

    except (TypeError, ValueError) as exc:
        return unavailable_weather(
            destination,
            date,
            str(exc),
        )

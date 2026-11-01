
import json
import os
import time
import threading
from collections import Counter
from datetime import date as Date, datetime, timedelta, timezone
from functools import lru_cache
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


GEOCODING_URL = "https://api.openweathermap.org/geo/1.0/direct"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

TIMEOUT_SECONDS = 15
MAX_ATTEMPTS = 3
MAX_FORECAST_DAYS = 5  # OpenWeather free 5-day / 3-hour forecast.
CACHE_TTL_SECONDS = 3600  # Reuse successful forecasts for one hour.
RATE_LIMIT_COOLDOWN_SECONDS = 300  # Pause Open-Meteo calls after HTTP 429.

OPENWEATHER_API_KEY_ENV = "OPENWEATHER_API_KEY"

_forecast_cache = {}
_cache_lock = threading.Lock()
_provider_cooldown_until = 0.0


def _get_json(url):
    """
    Fetch JSON with timeouts and retries.

    A 429 response starts a shared cooldown for both geocoding
    and forecast requests, preventing repeated calls from making
    provider rate limiting worse.
    """
    global _provider_cooldown_until

    now = time.monotonic()
    with _cache_lock:
        remaining = _provider_cooldown_until - now

    if remaining > 0:
        raise RuntimeError(
            f"Open-Meteo rate-limit cooldown is active "
            f"({int(remaining) + 1} seconds remaining)."
        )

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
                retry_after = error.headers.get("Retry-After")
                try:
                    cooldown = int(retry_after) if retry_after else RATE_LIMIT_COOLDOWN_SECONDS
                except (TypeError, ValueError):
                    cooldown = RATE_LIMIT_COOLDOWN_SECONDS

                # Respect provider guidance, but keep the cooldown bounded.
                cooldown = max(60, min(cooldown, 900))
                with _cache_lock:
                    _provider_cooldown_until = (
                        time.monotonic() + cooldown
                    )
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
    """Resolve and cache destination coordinates using OpenWeather Geocoding."""

    api_key = os.getenv(OPENWEATHER_API_KEY_ENV)
    if not api_key:
        raise RuntimeError(
            f"{OPENWEATHER_API_KEY_ENV} is not configured on the server."
        )

    params = {
        "q": destination,
        "limit": 1,
        "appid": api_key,
    }
    url = f"{GEOCODING_URL}?{urlencode(params)}"
    data = _get_json(url)

    if not isinstance(data, list) or not data:
        raise ValueError(f"Could not find destination: {destination}")

    location = data[0]
    return (
        location["lat"],
        location["lon"],
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
    """Fetch and cache OpenWeather's five-day, three-hour forecast."""

    api_key = os.getenv(OPENWEATHER_API_KEY_ENV)
    if not api_key:
        raise RuntimeError(
            f"{OPENWEATHER_API_KEY_ENV} is not configured on the server."
        )

    cache_key = (
        round(float(latitude), 4),
        round(float(longitude), 4),
    )
    now = time.monotonic()

    with _cache_lock:
        cached = _forecast_cache.get(cache_key)
        if cached and now - cached["time"] < CACHE_TTL_SECONDS:
            return cached["data"]

    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": api_key,
        "units": "metric",
    }
    url = f"{FORECAST_URL}?{urlencode(params)}"
    data = _get_json(url)

    if not isinstance(data.get("list"), list):
        raise ValueError("OpenWeather returned no forecast list.")

    with _cache_lock:
        _forecast_cache[cache_key] = {
            "time": time.monotonic(),
            "data": data,
        }

        if len(_forecast_cache) > 128:
            oldest_key = min(
                _forecast_cache,
                key=lambda key: _forecast_cache[key]["time"]
            )
            _forecast_cache.pop(oldest_key, None)

    return data


def _aggregate_openweather_daily(data):
    """Aggregate OpenWeather's 3-hour forecast records into local calendar days."""

    city = data.get("city") or {}
    timezone_offset = int(city.get("timezone", 0))
    grouped = {}

    for entry in data.get("list", []):
        if not isinstance(entry, dict) or "dt" not in entry:
            continue

        local_datetime = (
            datetime.fromtimestamp(entry["dt"], tz=timezone.utc)
            + timedelta(seconds=timezone_offset)
        )
        day = local_datetime.date().isoformat()
        grouped.setdefault(day, []).append(entry)

    daily = {
        "time": [],
        "temperature_2m_max": [],
        "weather_code": [],
        "precipitation_probability_max": [],
        "wind_speed_10m_max": [],
        "condition": [],
    }

    for day in sorted(grouped):
        entries = grouped[day]
        temperatures = []
        rain_probabilities = []
        wind_speeds = []
        conditions = []

        for entry in entries:
            main = entry.get("main") or {}
            if main.get("temp_max") is not None:
                temperatures.append(float(main["temp_max"]))
            elif main.get("temp") is not None:
                temperatures.append(float(main["temp"]))

            if entry.get("pop") is not None:
                rain_probabilities.append(float(entry["pop"]) * 100)

            wind = entry.get("wind") or {}
            if wind.get("speed") is not None:
                # OpenWeather reports wind speed in m/s; TripMind displays km/h.
                wind_speeds.append(float(wind["speed"]) * 3.6)

            weather_items = entry.get("weather") or []
            if weather_items:
                item = weather_items[0]
                condition = item.get("description") or item.get("main")
                if condition:
                    conditions.append(str(condition).title())

        daily["time"].append(day)
        daily["temperature_2m_max"].append(
            max(temperatures) if temperatures else None
        )
        daily["weather_code"].append(0)  # Compatibility field; condition is used below.
        daily["precipitation_probability_max"].append(
            max(rain_probabilities) if rain_probabilities else None
        )
        daily["wind_speed_10m_max"].append(
            max(wind_speeds) if wind_speeds else None
        )
        daily["condition"].append(
            Counter(conditions).most_common(1)[0][0] if conditions else None
        )

    return daily


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

    condition = daily.get("condition", [None])[index]
    if not condition:
        condition = weather_code_to_condition(weather_code)

    return {
        "destination": destination,
        "date": requested_date,
        "temperature": temperature,
        "condition": condition,
        "rain_probability": rain_probability,
        "wind": f"{wind_speed:.1f} km/h",
        "source": "OpenWeather 5-day forecast API",
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
    last_forecast_date = today + timedelta(days=MAX_FORECAST_DAYS - 1)

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
                    f"{MAX_FORECAST_DAYS}-day forecast window.",
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

        daily_data = _aggregate_openweather_daily(data)

        for index, item in enumerate(daily_weather):
            if item is None:
                requested_date = (
                    start + timedelta(days=index)
                ).isoformat()

                daily_weather[index] = _build_daily_weather(
                    destination,
                    requested_date,
                    daily_data,
                )


    except Exception as error:
        print(
            f"Weather range lookup failed for {destination} "
            f"from {forecast_dates[0]} to {forecast_dates[-1]}: {error}"
        )

        # Weather is optional: preserve the trip plan even if
        # the external weather provider is unavailable.
        for index, item in enumerate(daily_weather):
            if item is None:
                requested_date = (
                    start + timedelta(days=index)
                ).isoformat()

                daily_weather[index] = unavailable_weather(
                    destination,
                    requested_date,
                    f"Weather service temporarily unavailable: {error}",
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

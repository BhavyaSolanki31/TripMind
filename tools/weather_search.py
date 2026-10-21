
import json
import time
from datetime import date as Date
from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.error import HTTPError, URLError


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

TIMEOUT_SECONDS = 12
MAX_ATTEMPTS = 3
MAX_FORECAST_DAYS = 16


def _get_json(url):
    """Fetch JSON with a timeout and retries for temporary failures."""

    for attempt in range(MAX_ATTEMPTS):
        try:
            with urlopen(url, timeout=TIMEOUT_SECONDS) as response:
                return json.loads(response.read().decode("utf-8"))

        except HTTPError as error:
            # Retry rate limits and temporary server failures.
            if error.code not in (429, 500, 502, 503, 504):
                raise

            if attempt == MAX_ATTEMPTS - 1:
                raise

        except (URLError, TimeoutError, OSError, json.JSONDecodeError):
            if attempt == MAX_ATTEMPTS - 1:
                raise

        time.sleep(0.5 * (attempt + 1))


def get_coordinates(destination):
    """Resolve a destination to geographic coordinates."""

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

    return {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "name": location.get("name", destination),
        "country": location.get("country", ""),
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


def search_weather(destination, date):
    """Fetch a daily forecast for a future date."""

    # Validate the requested date.
    try:
        requested_date = Date.fromisoformat(date)
    except (TypeError, ValueError):
        return unavailable_weather(
            str(destination),
            str(date),
            "Invalid date. Expected YYYY-MM-DD.",
        )

    today = Date.today()

    if requested_date < today:
        return unavailable_weather(
            destination,
            date,
            "Past dates are not supported. Please choose a future travel date.",
        )
    if (requested_date - today).days > MAX_FORECAST_DAYS:
      return unavailable_weather(
        destination,
        date,
        f"Forecasts are available for up to {MAX_FORECAST_DAYS} days ahead. "
        "Choose a date within that range.",
    )
    # Validate the destination.
    if not isinstance(destination, str) or not destination.strip():
        return unavailable_weather(
            str(destination),
            date,
            "Destination must be a non-empty city name.",
        )

    destination = destination.strip()

    try:
        location = get_coordinates(destination)

        params = {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "daily": (
                "temperature_2m_max,"
                "weather_code,"
                "precipitation_probability_max,"
                "wind_speed_10m_max"
            ),
            "timezone": "auto",
            "start_date": requested_date.isoformat(),
            "end_date": requested_date.isoformat(),
        }

        url = f"{FORECAST_URL}?{urlencode(params)}"
        data = _get_json(url)

        daily = data.get("daily")

        if not isinstance(daily, dict):
            return unavailable_weather(
                destination,
                date,
                "The weather service returned no daily forecast data.",
            )

        dates = daily.get("time")

        if not isinstance(dates, list) or date not in dates:
            return unavailable_weather(
                destination,
                date,
                "No forecast is available for the requested date.",
            )

        index = dates.index(date)

        required_fields = {
            "temperature_2m_max": "temperature",
            "weather_code": "condition",
            "precipitation_probability_max": "rain probability",
            "wind_speed_10m_max": "wind speed",
        }

        values = {}

        for field, label in required_fields.items():
            series = daily.get(field)

            if not isinstance(series, list) or index >= len(series):
                return unavailable_weather(
                    destination,
                    date,
                    f"The {label} measurement is missing.",
                )

            value = series[index]

            if value is None:
                return unavailable_weather(
                    destination,
                    date,
                    f"The {label} measurement is unavailable.",
                )

            values[field] = value

        temperature = values["temperature_2m_max"]
        weather_code = values["weather_code"]
        rain_probability = values["precipitation_probability_max"]
        wind_speed = values["wind_speed_10m_max"]

        if not isinstance(weather_code, int):
            return unavailable_weather(
                destination,
                date,
                "The weather service returned an invalid weather code.",
            )

        if not 0 <= rain_probability <= 100:
            return unavailable_weather(
                destination,
                date,
                "The rain probability is outside the valid range.",
            )

        if temperature < -100 or temperature > 70 or wind_speed < 0:
            return unavailable_weather(
                destination,
                date,
                "The weather service returned implausible measurements.",
            )

        return {
            "destination": destination,
            "date": date,
            "temperature": temperature,
            "condition": weather_code_to_condition(weather_code),
            "rain_probability": rain_probability,
            "wind": f"{wind_speed} km/h",
            "source": "Open-Meteo forecast API",
            "status": "forecast",
        }

    except Exception as error:
        # Log diagnostic details locally, but return a friendly message.
        print(
            f"Weather lookup failed for {destination} "
            f"on {date}: {error}"
        )

        return unavailable_weather(
            destination,
            date,
            "Could not retrieve weather data. Please try again later.",
        )


if __name__ == "__main__":
    # Use a future date within the forecast horizon for testing.
    test_date = (Date.today()).isoformat()

    print(
        json.dumps(
            search_weather("Mumbai", test_date),
            indent=2,
        )
    )

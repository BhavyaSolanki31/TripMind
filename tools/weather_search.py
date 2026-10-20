
import json
import time
from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.error import HTTPError, URLError


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

TIMEOUT_SECONDS = 12
MAX_ATTEMPTS = 3


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
    """Fetch a daily forecast, returning a safe fallback on failure."""

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
            "start_date": date,
            "end_date": date,
        }

        url = f"{FORECAST_URL}?{urlencode(params)}"
        data = _get_json(url)

        daily = data.get("daily")

        if not daily or not daily.get("time"):
            return unavailable_weather(
                destination, date, "No forecast is available for this date."
            )

        if date not in daily["time"]:
            return unavailable_weather(
                destination, date, "The requested date was not returned."
            )

        index = daily["time"].index(date)

        temperature = daily["temperature_2m_max"][index]
        weather_code = daily["weather_code"][index]
        rain_probability = daily["precipitation_probability_max"][index]
        wind_speed = daily["wind_speed_10m_max"][index]

        if any(
            value is None
            for value in (
                temperature,
                weather_code,
                rain_probability,
                wind_speed,
            )
        ):
            return unavailable_weather(
                destination, date, "Some forecast measurements are missing."
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
        return unavailable_weather(
            destination,
            date,
            f"Could not retrieve forecast after retries: {error}",
        )


if __name__ == "__main__":
    print(json.dumps(search_weather("Mumbai", "2026-10-20"), indent=2))

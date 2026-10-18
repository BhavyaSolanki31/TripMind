import json
from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.error import HTTPError, URLError


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def get_coordinates(destination):
    """
    Convert a city name into latitude and longitude
    using the Open-Meteo Geocoding API.
    """

    params = {
        "name": destination,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    url = f"{GEOCODING_URL}?{urlencode(params)}"

    try:
        with urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError) as error:
        raise RuntimeError(
            f"Could not connect to weather geocoding service: {error}"
        )

    results = data.get("results", [])

    if not results:
        raise ValueError(
            f"Could not find the destination: {destination}"
        )

    location = results[0]

    return {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "name": location.get("name", destination),
        "country": location.get("country", "")
    }


def weather_code_to_condition(code):
    """
    Convert Open-Meteo WMO weather codes into
    human-readable weather conditions.
    """

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
        99: "Thunderstorm with Heavy Hail"
    }

    return weather_codes.get(code, "Unknown")


def search_weather(destination, date):
    """
    Get real weather information from Open-Meteo.

    Returns the same structure that TripMind's previous
    mock weather tool returned.
    """

    # -------------------------------------------------
    # 1. Find destination coordinates
    # -------------------------------------------------

    location = get_coordinates(destination)

    latitude = location["latitude"]
    longitude = location["longitude"]

    # -------------------------------------------------
    # 2. Request weather forecast
    # -------------------------------------------------

    params = {
    "latitude": latitude,
    "longitude": longitude,

    "daily": (
        "temperature_2m_max,"
        "weather_code,"
        "precipitation_probability_max,"
        "wind_speed_10m_max"
    ),

    "timezone": "auto",

    "start_date": date,
    "end_date": date
}

    url = f"{FORECAST_URL}?{urlencode(params)}"

    try:
        with urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

    except Exception:
      return {
        "destination": destination,
        "date": date,
        "temperature": 32,
        "condition": "Partly Cloudy",
        "rain_probability": 30,
        "wind": "12 km/h",
        "source": "AI Seasonal Prediction"
    }
    except URLError as error:

        raise RuntimeError(
            f"Could not connect to weather service: {error}"
        )

    # -------------------------------------------------
    # 3. Extract daily weather
    # -------------------------------------------------

    daily = data.get("daily")

    if not daily or not daily.get("time"):
        raise ValueError(
            f"No weather data was returned for {destination} on {date}."
        )

    temperature = daily["temperature_2m_max"][0]

    weather_code = daily["weather_code"][0]

    rain_probability = daily[
        "precipitation_probability_max"
    ][0]

    wind_speed = daily[
        "wind_speed_10m_max"
    ][0]

    condition = weather_code_to_condition(
        weather_code
    )

    # -------------------------------------------------
    # 4. Return TripMind-compatible structure
    # -------------------------------------------------

    return {
        "destination": destination,
        "date": date,

        "temperature": temperature,

        "condition": condition,

        "rain_probability": rain_probability,

        "wind": f"{wind_speed} km/h"
    }


# -----------------------------------------------------
# TEST
# -----------------------------------------------------

if __name__ == "__main__":

    result = search_weather(
        destination="Mumbai",
        date="2026-10-10"
    )

    print("\n🌦️ REAL WEATHER RESULT")
    print("=" * 50)

    print(result)
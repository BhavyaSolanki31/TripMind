from datetime import date, timedelta

from tools.weather_search import search_weather
from models.llm import ask_ai


def weather_agent(destination, start_date, end_date):
    """
    Weather Agent:

    1. Fetches real weather for every day of the trip.
    2. Uses AI to interpret the overall weather.
    3. Returns weather data for each individual date.
    """

    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)

    if end < start:
        raise ValueError(
            "End date must be after or equal to start date."
        )

    daily_weather = []

    current_date = start

    while current_date <= end:

        current_date_string = current_date.isoformat()

        weather = search_weather(
            destination=destination,
            date=current_date_string
        )

        daily_weather.append(weather)

        current_date += timedelta(days=1)

    # -------------------------------------------------
    # AI WEATHER ANALYSIS
    # -------------------------------------------------

    prompt = f"""
You are TripMind's Weather Agent.

Destination:
{destination}

Weather forecast for the trip:

{daily_weather}

Analyze the weather across the entire trip.

Give a short practical recommendation covering:
1. Which days are most suitable for outdoor sightseeing.
2. Which days may require weather precautions.
3. General advice for planning outdoor activities.

Important:
- Use ONLY the weather information provided.
- Do not invent weather conditions.
- Do not change any temperature, rain probability,
  condition, or wind values.
- Keep the recommendation concise.
"""

    recommendation = (
    f"Weather in {destination}: "
    f"{weather['condition']} with "
    f"{weather['temperature']}°C temperature. "
    f"Plan activities accordingly."
)

    return {
        "daily_weather": daily_weather,
        "recommendation": recommendation
    }


# -----------------------------------------------------
# TEST
# -----------------------------------------------------

if __name__ == "__main__":

    result = weather_agent(
        destination="Mumbai",
        start_date="2026-10-10",
        end_date="2026-10-15"
    )

    print("\n🌦️ DAILY WEATHER")
    print("=" * 60)

    for weather in result["daily_weather"]:

        print(
            f"{weather['date']} | "
            f"{weather['temperature']}°C | "
            f"{weather['condition']} | "
            f"Rain: {weather['rain_probability']}% | "
            f"Wind: {weather['wind']}"
        )

    print("\n🤖 AI WEATHER ANALYSIS")
    print("=" * 60)

    print(result["recommendation"])
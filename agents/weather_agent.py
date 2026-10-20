
from datetime import date, timedelta

from tools.weather_search import search_weather


def weather_agent(destination, start_date, end_date):
    """
    Fetch daily weather and produce a recommendation based only
    on the returned forecast data.
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
            date=current_date_string,
        )

        daily_weather.append(weather)
        current_date += timedelta(days=1)

    available_days = [
        item for item in daily_weather
        if item.get("status") == "forecast"
    ]

    unavailable_count = len(daily_weather) - len(available_days)

    if not available_days:
        recommendation = (
            f"Weather forecasts for {destination} are currently unavailable. "
            "Check a reliable weather service before planning outdoor activities."
        )

    else:
        temperatures = [
            item["temperature"]
            for item in available_days
            if isinstance(item.get("temperature"), (int, float))
        ]

        rain_values = [
            item["rain_probability"]
            for item in available_days
            if isinstance(item.get("rain_probability"), (int, float))
        ]

        wet_days = [
            item for item in available_days
            if isinstance(item.get("rain_probability"), (int, float))
            and item["rain_probability"] >= 50
        ]

        details = []

        if temperatures:
            details.append(
                f"Forecast maximum temperatures range from "
                f"{min(temperatures):g}°C to {max(temperatures):g}°C"
            )

        if rain_values:
            details.append(
                f"rain probability ranges from "
                f"{min(rain_values):g}% to {max(rain_values):g}%"
            )

        if wet_days:
            dates_text = ", ".join(item["date"] for item in wet_days)
            advice = (
                f"Consider rain precautions on {dates_text}."
            )
        else:
            advice = (
                "No available forecast reports a rain probability of 50% or higher."
                if rain_values
                else "Check precipitation details before outdoor activities."
            )

        recommendation = (
            f"Weather in {destination}: "
            + "; ".join(details)
            + f". {advice}"
        )

        if unavailable_count:
            recommendation += (
                f" Forecast data is unavailable for "
                f"{unavailable_count} day(s); check those dates again."
            )

        recommendation += (
            " Check updated forecasts before travelling, as weather can change."
        )

    return {
        "daily_weather": daily_weather,
        "recommendation": recommendation,
    }


if __name__ == "__main__":
    result = weather_agent(
        destination="Mumbai",
        start_date="2026-10-20",
        end_date="2026-10-25",
    )

    print("\nDAILY WEATHER")
    print("=" * 60)

    for item in result["daily_weather"]:
        print(
            f"{item['date']} | "
            f"{item['temperature']}°C | "
            f"{item['condition']} | "
            f"Rain: {item['rain_probability']}% | "
            f"Wind: {item['wind']} | "
            f"Status: {item['status']}"
        )

    print("\nWEATHER RECOMMENDATION")
    print("=" * 60)
    print(result["recommendation"])

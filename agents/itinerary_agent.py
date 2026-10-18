
import json
from datetime import datetime, timedelta

from models.llm import ask_ai_json

USE_AI = False


def normalize_activity(activity, destination):
    """Convert an activity into TripMind's standard format."""

    if isinstance(activity, str):
        return {
            "time": "Morning",
            "title": activity,
            "description": f"Explore {activity} in {destination}.",
            "location": activity,
            "cost": 0,
        }

    if isinstance(activity, dict):
        title = (
            activity.get("title")
            or activity.get("name")
            or activity.get("activity")
            or "Activity"
        )

        return {
            "time": activity.get("time", "Morning"),
            "title": title,
            "description": activity.get(
                "description",
                activity.get(
                    "details",
                    f"Explore {title} in {destination}.",
                ),
            ),
            "location": activity.get("location", title),
            "cost": activity.get("cost", activity.get("price", 0)),
        }

    return {
        "time": "Morning",
        "title": "Activity",
        "description": "Explore the destination.",
        "location": destination,
        "cost": 0,
    }


def create_fallback_itinerary(
    origin,
    destination,
    check_in,
    check_out,
    selected_flight,
    selected_stay,
    optimized_activities,
    weather,
):
    """Create a deterministic itinerary without calling an LLM."""

    start = datetime.strptime(check_in, "%Y-%m-%d").date()
    end = datetime.strptime(check_out, "%Y-%m-%d").date()

    if end < start:
        raise ValueError("Check-out date cannot be before check-in date.")

    dates = []
    current = start

    while current <= end:
        dates.append(current.isoformat())
        current += timedelta(days=1)

    weather_map = {}

    if isinstance(weather, list):
        for item in weather:
            if isinstance(item, dict) and item.get("date"):
                weather_map[item["date"]] = item

    elif isinstance(weather, dict) and weather.get("date"):
        weather_map[weather["date"]] = weather

    # Normalize activities and avoid duplicate titles.
    normalized_activities = []
    seen_titles = set()

    for item in optimized_activities or []:
        activity = normalize_activity(item, destination)
        title_key = activity["title"].strip().casefold()

        if title_key not in seen_titles:
            seen_titles.add(title_key)
            normalized_activities.append(activity)

    days = []

    # The first day is arrival; the final day is checkout.
    # All activities are distributed across the intervening days.
    sightseeing_dates = dates[1:-1]

    if len(dates) == 1:
        sightseeing_dates = []

    # Spread activities as evenly as possible across sightseeing days.
    activities_by_date = {date: [] for date in sightseeing_dates}

    for index, activity in enumerate(normalized_activities):
        if sightseeing_dates:
            date = sightseeing_dates[index % len(sightseeing_dates)]
            activities_by_date[date].append(activity)

    for index, date in enumerate(dates):
        daily_activities = []

        daily_weather = weather_map.get(
            date,
            {
                "date": date,
                "destination": destination,
                "temperature": None,
                "condition": "Unavailable",
                "rain_probability": None,
                "wind": "Unavailable",
            },
        )

        if index == 0:
            daily_activities.append({
                "time": "Morning",
                "title": f"Flight from {origin} to {destination}",
                "description": (
                    f"Travel via {selected_flight.get('airline', 'your selected airline')}. "
                    "Confirm your actual departure time before travelling."
                ),
                "location": f"{origin} Airport → {destination} Airport",
                "cost": selected_flight.get("price", 0),
            })

            daily_activities.append({
                "time": "Afternoon",
                "title": "Hotel Check-in",
                "description": (
                    f"Check in at {selected_stay.get('name', 'your selected hotel')}."
                ),
                "location": selected_stay.get("location", destination),
                "cost": 0,
            })

        elif index == len(dates) - 1:
            daily_activities.append({
                "time": "Morning",
                "title": "Hotel Check-out",
                "description": (
                    f"Check out from {selected_stay.get('name', 'your selected hotel')}."
                ),
                "location": selected_stay.get("location", destination),
                "cost": 0,
            })

        else:
            daily_activities.extend(activities_by_date.get(date, []))

            if not daily_activities:
                daily_activities.append({
                    "time": "Free Time",
                    "title": "Leisure Time",
                    "description": (
                        "Enjoy flexible time. Choose nearby activities "
                        "after checking opening hours and travel time."
                    ),
                    "location": destination,
                    "cost": 0,
                })

        days.append({
            "day": index + 1,
            "date": date,
            "title": f"Day {index + 1} in {destination}",
            "weather": daily_weather,
            "activities": daily_activities,
        })

    return {
        "trip_title": f"{destination} Trip",
        "summary": (
            f"{len(dates)} days and {max(len(dates) - 1, 0)} nights "
            f"trip from {origin} to {destination}."
        ),
        "days": days,
    }


def itinerary_agent(
    origin,
    destination,
    date,
    check_in,
    check_out,
    travelers,
    selected_flight,
    selected_stay,
    optimized_activities,
    optimized_route,
    budget_breakdown,
    weather,
):
    """Generate the final itinerary, with a reliable offline fallback."""

    prompt = f"""
You are TripMind's final itinerary agent.

Create a realistic itinerary using only the supplied activities.
- Use the exact check-in and check-out dates.
- First day: flight and hotel check-in only.
- Last day: hotel check-out only.
- Distribute all supplied selected activities across sightseeing days.
- Follow the optimized route order as far as practical.
- Do not invent attractions, prices, or weather.
- Preserve the supplied weather for each date.
- Return valid JSON only.

Origin: {origin}
Destination: {destination}
Check-in: {check_in}
Check-out: {check_out}
Travelers: {travelers}
Selected flight: {selected_flight}
Selected stay: {selected_stay}
Selected activities: {optimized_activities}
Optimized route: {optimized_route}
Budget: {budget_breakdown}
Weather: {weather}

Return an object with trip_title, summary, and days.
Each day must include day, date, title, weather, and activities.
Each activity must include time, title, description, location, and cost.
"""

    try:
        if not USE_AI:
            raise RuntimeError("AI disabled; using deterministic fallback.")

        response = ask_ai_json(prompt)

        if not response:
            raise ValueError("Empty AI response.")

        if isinstance(response, dict):
            itinerary = response
        else:
            itinerary = json.loads(response)

        if not isinstance(itinerary, dict) or not isinstance(
            itinerary.get("days"), list
        ):
            raise ValueError("AI response is missing a valid days list.")

        # Normalize activity format and preserve the existing weather.
        weather_map = {}

        if isinstance(weather, list):
            weather_map = {
                item["date"]: item
                for item in weather
                if isinstance(item, dict) and item.get("date")
            }

        for day in itinerary["days"]:
            day_activities = day.get("activities", day.get("schedule", []))
            day["activities"] = [
                normalize_activity(item, destination)
                for item in day_activities
            ]

            if day.get("date") in weather_map:
                day["weather"] = weather_map[day["date"]]

        return {"final_itinerary": itinerary}

    except Exception as error:
        print(f"Using fallback itinerary: {error}")

        return {
            "final_itinerary": create_fallback_itinerary(
                origin,
                destination,
                check_in,
                check_out,
                selected_flight,
                selected_stay,
                optimized_activities,
                weather,
            )
        }

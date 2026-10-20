
import json
from datetime import datetime, timedelta

from models.llm import ask_ai_json

# Keep False for predictable scheduling without requiring an AI API call.
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
            "duration": "2 hours",
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
            "duration": activity.get("duration", "2 hours"),
        }

    return {
        "time": "Morning",
        "title": "Activity",
        "description": "Explore the destination.",
        "location": destination,
        "cost": 0,
        "duration": "2 hours",
    }


def _title_key(value):
    return str(value or "").strip().casefold()


def _is_ferry_activity(activity):
    title = _title_key(activity.get("title"))
    location = _title_key(activity.get("location"))

    return (
        "elephanta caves" in title
        or "elephanta caves" in location
    )


def _duration_hours(activity):
    """Extract a rough duration in hours from common duration formats."""

    duration = activity.get("duration", "2 hours")

    if isinstance(duration, (int, float)):
        return max(float(duration), 0.5)

    text = str(duration).strip().casefold()

    import re

    numbers = re.findall(r"\d+(?:\.\d+)?", text)

    if not numbers:
        return 2.0

    value = float(numbers[0])

    if "minute" in text or "min" in text:
        return max(value / 60, 0.5)

    if "day" in text:
        return max(value * 6, 1.0)

    return max(value, 0.5)


def _suggest_time_slot(activity):
    """
    Choose a practical default time based on the attraction.

    This is a planning suggestion, not a verified opening or booking time.
    """

    title = _title_key(activity.get("title"))
    duration = _duration_hours(activity)

    if _is_ferry_activity(activity):
        return "Morning"

    # Sunset and evening-friendly activities.
    if any(
        word in title
        for word in (
            "marine drive",
            "sunset",
            "night market",
            "evening",
            "street food",
            "food tour",
        )
    ):
        return "Evening"

    # Shopping is usually more comfortable during the day.
    if any(
        word in title
        for word in (
            "causeway",
            "market",
            "shopping",
            "mall",
        )
    ):
        return "Afternoon"

    # Longer excursions are best started early.
    if duration >= 3:
        return "Morning"

    return "Morning"


def _order_by_route(activities, optimized_route):
    """Order activities using the route when matching names are available."""

    if not optimized_route:
        return activities

    route_positions = {
        _title_key(name): index
        for index, name in enumerate(optimized_route)
    }

    indexed_activities = list(enumerate(activities))

    indexed_activities.sort(
        key=lambda pair: (
            route_positions.get(
                _title_key(pair[1].get("title")),
                len(route_positions) + pair[0],
            ),
            pair[0],
        )
    )

    return [activity for _, activity in indexed_activities]


def _distribute_activities(activities, dates):
    """Assign every activity once, balancing activity counts across dates."""

    result = {date: [] for date in dates}

    if not activities or not dates:
        return result

    base_count, extra = divmod(len(activities), len(dates))
    position = 0

    for index, date in enumerate(dates):
        count = base_count + (1 if index < extra else 0)

        result[date] = activities[position:position + count]
        position += count

    return result


def _assign_daily_time_slots(activities):
    """
    Give activities sensible time slots and avoid duplicate slots on a day
    whenever practical.
    """

    if not activities:
        return activities

    # Preferred slots in chronological order.
    slots = ["Morning", "Afternoon", "Evening"]
    used_slots = set()

    # First assign special activities their preferred times.
    for activity in activities:
        preferred = _suggest_time_slot(activity)

        if preferred not in used_slots:
            activity["time"] = preferred
            used_slots.add(preferred)
        else:
            # A second activity with the same preference is deferred
            # to the next available slot.
            activity["time"] = None

    # Fill unassigned activities using remaining time slots.
    for activity in activities:
        if activity.get("time") is not None:
            continue

        available = [
            slot for slot in slots
            if slot not in used_slots
        ]

        if available:
            activity["time"] = available[0]
            used_slots.add(available[0])
        else:
            # More than three activities may share a day.
            # Keep the suggested time rather than dropping an activity.
            activity["time"] = _suggest_time_slot(activity)

    # Return the activities in morning-to-evening order.
    slot_order = {
        "Morning": 0,
        "Afternoon": 1,
        "Evening": 2,
    }

    return sorted(
        activities,
        key=lambda activity: slot_order.get(
            activity.get("time"),
            0,
        ),
    )


def create_fallback_itinerary(
    origin,
    destination,
    check_in,
    check_out,
    selected_flight,
    selected_stay,
    optimized_activities,
    weather,
    optimized_route=None,
):
    """Create a complete deterministic itinerary."""

    start = datetime.strptime(check_in, "%Y-%m-%d").date()
    end = datetime.strptime(check_out, "%Y-%m-%d").date()

    if end < start:
        raise ValueError(
            "Check-out date cannot be before check-in date."
        )

    dates = []
    current = start

    while current <= end:
        dates.append(current.isoformat())
        current += timedelta(days=1)

    # Index available weather records by date.
    weather_map = {}

    if isinstance(weather, list):
        for item in weather:
            if isinstance(item, dict) and item.get("date"):
                weather_map[item["date"]] = item

    elif isinstance(weather, dict) and weather.get("date"):
        if weather.get("date"):
            weather_map[weather["date"]] = weather

    # Normalize activities and remove duplicate titles.
    normalized_activities = []
    seen_titles = set()

    for item in optimized_activities or []:
        activity = normalize_activity(item, destination)
        key = _title_key(activity["title"])

        if not key or key in seen_titles:
            continue

        seen_titles.add(key)
        normalized_activities.append(activity)

    normalized_activities = _order_by_route(
        normalized_activities,
        optimized_route,
    )

        # Keep arrival and checkout days free of sightseeing assignments.
    sightseeing_dates = dates[1:-1] if len(dates) > 2 else []

    activities_by_date = {
        date: [] for date in sightseeing_dates
    }

    # Preserve every unique activity and keep ferry-dependent visits
    # separate from mainland sightseeing.
    ferry_activities = []
    mainland_activities = []

    for activity in normalized_activities:
        if _is_ferry_activity(activity):
            ferry_activities.append(activity)
        else:
            mainland_activities.append(activity)

    if sightseeing_dates:
        # Schedule mainland activities across all sightseeing days first.
        mainland_schedule = _distribute_activities(
            mainland_activities,
            sightseeing_dates,
        )

        for date in sightseeing_dates:
            activities_by_date[date].extend(
                mainland_schedule[date]
            )

        # Put ferry-dependent activities on the last sightseeing day.
        if ferry_activities:
            ferry_date = sightseeing_dates[-1]

            activities_by_date[ferry_date].extend(
                ferry_activities
            )

        # Assign practical time slots independently for each day.
        for date in activities_by_date:
            activities_by_date[date] = _assign_daily_time_slots(
                activities_by_date[date]
            )
    elif normalized_activities:
        # Short trips may have no separate sightseeing day.
        # Preserve activities rather than silently dropping them.
        activities_by_date = {
            dates[0]: _assign_daily_time_slots(
                normalized_activities
            )
        }

    days = []

    for index, date in enumerate(dates):
        daily_activities = []

        daily_weather = weather_map.get(
            date,
            {
                "date": date,
                "destination": destination,
                "temperature": None,
                "condition": "Weather unavailable",
                "rain_probability": None,
                "wind": "Unavailable",
                "source": "unavailable",
                "status": "unavailable",
            },
        )

        if index == 0:
            daily_activities.append(
                {
                    "time": "Morning",
                    "title": f"Flight from {origin} to {destination}",
                    "description": (
                        f"Travel via {selected_flight.get('airline', 'your selected airline')}. "
                        "Confirm your actual departure time before travelling."
                    ),
                    "location": (
                        f"{origin} Airport → {destination} Airport"
                    ),
                    "cost": selected_flight.get("price", 0),
                    "duration": selected_flight.get(
                        "duration", "Unavailable"
                    ),
                }
            )

            daily_activities.append(
                {
                    "time": "Afternoon",
                    "title": "Hotel Check-in",
                    "description": (
                        f"Check in at {selected_stay.get('name', 'your selected hotel')}."
                    ),
                    "location": selected_stay.get(
                        "location", destination
                    ),
                    "cost": 0,
                }
            )

        elif index == len(dates) - 1:
            daily_activities.append(
                {
                    "time": "Morning",
                    "title": "Hotel Check-out",
                    "description": (
                        f"Check out from {selected_stay.get('name', 'your selected hotel')}."
                    ),
                    "location": selected_stay.get(
                        "location", destination
                    ),
                    "cost": 0,
                }
            )

        else:
            daily_activities.extend(
                activities_by_date.get(date, [])
            )

            if not daily_activities:
                daily_activities.append(
                    {
                        "time": "Flexible",
                        "title": "Leisure Time",
                        "description": (
                            "Enjoy flexible time. Check local opening hours "
                            "and travel times before choosing activities."
                        ),
                        "location": destination,
                        "cost": 0,
                    }
                )

        days.append(
            {
                "day": index + 1,
                "date": date,
                "title": f"Day {index + 1} in {destination}",
                "weather": daily_weather,
                "activities": daily_activities,
            }
        )

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
    """Generate an itinerary with a deterministic fallback."""

    prompt = f"""
Create a travel itinerary as valid JSON.

Origin: {origin}
Destination: {destination}
Check-in: {check_in}
Check-out: {check_out}
Travelers: {travelers}
Flight: {selected_flight}
Stay: {selected_stay}
Activities: {optimized_activities}
Optimized route: {optimized_route}
Budget: {budget_breakdown}
Weather: {weather}

Return an object containing trip_title, summary, and days.
Each day must contain day, date, title, weather, and activities.
Each activity must contain time, title, description, location, and cost.
Do not invent bookings, prices, opening hours, or weather.
"""

    try:
        if not USE_AI:
            raise RuntimeError(
                "AI disabled; using deterministic itinerary."
            )

        response = ask_ai_json(prompt)

        if not response:
            raise ValueError("Empty AI response.")

        itinerary = (
            response
            if isinstance(response, dict)
            else json.loads(response)
        )

        if (
            not isinstance(itinerary, dict)
            or not isinstance(itinerary.get("days"), list)
        ):
            raise ValueError(
                "AI response is missing a valid days list."
            )

        # Keep the deterministic version's timing and duplicate protection.
        return {
            "final_itinerary": create_fallback_itinerary(
                origin=origin,
                destination=destination,
                check_in=check_in,
                check_out=check_out,
                selected_flight=selected_flight,
                selected_stay=selected_stay,
                optimized_activities=optimized_activities,
                weather=weather,
                optimized_route=optimized_route,
            )
        }

    except Exception as error:
        print(f"Using fallback itinerary: {error}")

        return {
            "final_itinerary": create_fallback_itinerary(
                origin=origin,
                destination=destination,
                check_in=check_in,
                check_out=check_out,
                selected_flight=selected_flight,
                selected_stay=selected_stay,
                optimized_activities=optimized_activities,
                weather=weather,
                optimized_route=optimized_route,
            )
        }
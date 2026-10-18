
from math import radians, sin, cos, sqrt, atan2, isfinite


# Places that require a ferry or special transport.
# This is metadata for route planning, not a live transport lookup.
SPECIAL_TRANSPORT_PLACES = {
    "elephanta caves": "ferry",
}


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate approximate straight-line distance using Haversine.
    Returns distance in kilometers.
    """

    values = (lat1, lon1, lat2, lon2)

    if not all(isfinite(float(value)) for value in values):
        raise ValueError("Coordinates must be finite numbers.")

    if not (-90 <= float(lat1) <= 90):
        raise ValueError("Latitude must be between -90 and 90.")

    if not (-90 <= float(lat2) <= 90):
        raise ValueError("Latitude must be between -90 and 90.")

    if not (-180 <= float(lon1) <= 180):
        raise ValueError("Longitude must be between -180 and 180.")

    if not (-180 <= float(lon2) <= 180):
        raise ValueError("Longitude must be between -180 and 180.")

    lat1, lon1, lat2, lon2 = map(
        radians,
        map(float, values)
    )

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(delta_lon / 2) ** 2
    )

    # Protect against small floating-point rounding errors.
    a = min(1.0, max(0.0, a))

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return round(6371.0 * c, 2)


def get_transport_type(activity):
    """Identify known special transport requirements."""

    name = activity.get("name", "").strip().lower()

    return SPECIAL_TRANSPORT_PLACES.get(name, "land")


def optimize_route(activities):
    """
    Order activities using a nearest-neighbor heuristic.

    Distances are straight-line estimates between coordinates.
    Ferry travel, road networks, opening hours, and travel times
    are not calculated by this function.

    Existing return keys are preserved for compatibility.
    """

    activities = list(activities or [])

    if not activities:
        return {
            "optimized_activities": [],
            "route": [],
            "total_stops": 0,
            "total_distance_km": 0,
            "distance_type": "straight-line estimate",
            "special_transport": [],
        }

    # Validate coordinates before route optimization.
    for activity in activities:
        if not isinstance(activity, dict):
            raise ValueError("Each activity must be a dictionary.")

        if not activity.get("name"):
            raise ValueError("Every activity must have a name.")

        if "latitude" not in activity or "longitude" not in activity:
            raise ValueError(
                f"Missing coordinates for {activity['name']}."
            )

        # Validate coordinates using the same public distance function.
        calculate_distance(
            activity["latitude"],
            activity["longitude"],
            activity["latitude"],
            activity["longitude"],
        )

    if len(activities) == 1:
        ordered = activities.copy()
        distance = 0.0
    else:
        remaining = activities.copy()
        ordered = [remaining.pop(0)]
        distance = 0.0

        while remaining:
            current = ordered[-1]

            nearest = min(
                remaining,
                key=lambda item: calculate_distance(
                    current["latitude"],
                    current["longitude"],
                    item["latitude"],
                    item["longitude"],
                ),
            )

            distance += calculate_distance(
                current["latitude"],
                current["longitude"],
                nearest["latitude"],
                nearest["longitude"],
            )

            ordered.append(nearest)
            remaining.remove(nearest)

    route = [activity["name"] for activity in ordered]

    special_transport = [
        {
            "activity": activity["name"],
            "transport": get_transport_type(activity),
        }
        for activity in ordered
        if get_transport_type(activity) != "land"
    ]

    return {
        "optimized_activities": ordered,
        "route": route,
        "total_stops": len(ordered),
        "total_distance_km": round(distance, 2),
        "distance_type": "straight-line estimate",
        "special_transport": special_transport,
    }


if __name__ == "__main__":
    sample_activities = [
        {
            "name": "Gateway of India",
            "latitude": 18.9220,
            "longitude": 72.8347,
        },
        {
            "name": "Marine Drive",
            "latitude": 18.9431,
            "longitude": 72.8238,
        },
        {
            "name": "Elephanta Caves",
            "latitude": 18.9633,
            "longitude": 72.9315,
        },
        {
            "name": "Colaba Causeway",
            "latitude": 18.9150,
            "longitude": 72.8317,
        },
    ]

    result = optimize_route(sample_activities)

    print("\nOPTIMIZED ROUTE")
    for index, place in enumerate(result["route"], start=1):
        print(f"{index}. {place}")

    print("\nTOTAL STOPS:", result["total_stops"])
    print("STRAIGHT-LINE DISTANCE:", result["total_distance_km"], "km")
    print("DISTANCE TYPE:", result["distance_type"])
    print("SPECIAL TRANSPORT:", result["special_transport"])


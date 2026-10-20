
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
    Optimize mainland activities using nearest-neighbor ordering.
    Special-transport activities are listed separately at the end.

    All calculated distances remain straight-line estimates.
    This function does not calculate ferry or road distances.
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

    # Validate every activity and its coordinates.
    for activity in activities:
        if not isinstance(activity, dict):
            raise ValueError("Each activity must be a dictionary.")

        if not activity.get("name"):
            raise ValueError("Every activity must have a name.")

        if "latitude" not in activity or "longitude" not in activity:
            raise ValueError(
                f"Missing coordinates for {activity['name']}."
            )

        calculate_distance(
            activity["latitude"],
            activity["longitude"],
            activity["latitude"],
            activity["longitude"],
        )

    # Separate mainland activities from special-transport activities.
    mainland = [
        activity for activity in activities
        if get_transport_type(activity) == "land"
    ]

    special = [
        activity for activity in activities
        if get_transport_type(activity) != "land"
    ]

    # Optimize mainland stops only.
    ordered_mainland = []

    if mainland:
        remaining = mainland.copy()
        ordered_mainland.append(remaining.pop(0))

        while remaining:
            current = ordered_mainland[-1]

            nearest = min(
                remaining,
                key=lambda item: calculate_distance(
                    current["latitude"],
                    current["longitude"],
                    item["latitude"],
                    item["longitude"],
                ),
            )

            ordered_mainland.append(nearest)
            remaining.remove(nearest)

    # Keep special-transport stops separate from mainland calculations.
    ordered_special = special
    ordered = ordered_mainland + ordered_special

    distance = 0.0

    for previous, current in zip(
        ordered_mainland, ordered_mainland[1:]
    ):
        distance += calculate_distance(
            previous["latitude"],
            previous["longitude"],
            current["latitude"],
            current["longitude"],
        )

    route = [activity["name"] for activity in ordered]

    special_transport = [
        {
            "activity": activity["name"],
            "transport": get_transport_type(activity),
        }
        for activity in ordered_special
    ]

    return {
        "optimized_activities": ordered,
        "route": route,
        "total_stops": len(ordered),
        "total_distance_km": round(distance, 2),
        "distance_type": "mainland straight-line estimate; special transport excluded",
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


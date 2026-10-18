from math import radians, sin, cos, sqrt, atan2


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the approximate distance between two
    geographic coordinates using the Haversine formula.

    Returns distance in kilometers.
    """

    earth_radius = 6371.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)

    lat2 = radians(lat2)
    lon2 = radians(lon2)

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(delta_lon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = earth_radius * c

    return round(distance, 2)


def optimize_route(activities):
    """
    Optimize the order of activities using a simple
    nearest-neighbor algorithm.

    The algorithm:
    1. Starts from the first activity.
    2. Finds the nearest unvisited activity.
    3. Moves to that activity.
    4. Repeats until all activities are visited.

    Returns the optimized activity order and
    total route distance.
    """

    if not activities:
        return {
            "optimized_activities": [],
            "route": [],
            "total_stops": 0,
            "total_distance_km": 0
        }

    if len(activities) == 1:
        return {
            "optimized_activities": activities,
            "route": [activities[0]["name"]],
            "total_stops": 1,
            "total_distance_km": 0
        }

    remaining = activities.copy()

    optimized_activities = []

    # Start from the first activity
    current = remaining.pop(0)

    optimized_activities.append(current)

    total_distance = 0

    while remaining:

        nearest_activity = min(
            remaining,
            key=lambda activity: calculate_distance(
                current["latitude"],
                current["longitude"],
                activity["latitude"],
                activity["longitude"]
            )
        )

        distance = calculate_distance(
            current["latitude"],
            current["longitude"],
            nearest_activity["latitude"],
            nearest_activity["longitude"]
        )

        total_distance += distance

        optimized_activities.append(nearest_activity)

        remaining.remove(nearest_activity)

        current = nearest_activity

    route = [
        activity["name"]
        for activity in optimized_activities
    ]

    return {
        "optimized_activities": optimized_activities,
        "route": route,
        "total_stops": len(optimized_activities),
        "total_distance_km": round(total_distance, 2)
    }


if __name__ == "__main__":

    sample_activities = [
        {
            "name": "Gateway of India",
            "category": "Sightseeing",
            "price": 0,
            "duration": "2 hours",
            "latitude": 18.9220,
            "longitude": 72.8347
        },
        {
            "name": "Marine Drive",
            "category": "Sightseeing",
            "price": 0,
            "duration": "2 hours",
            "latitude": 18.9431,
            "longitude": 72.8238
        },
        {
            "name": "Elephanta Caves",
            "category": "History",
            "price": 600,
            "duration": "4 hours",
            "latitude": 18.9633,
            "longitude": 72.9315
        },
        {
            "name": "Colaba Market",
            "category": "Shopping",
            "price": 0,
            "duration": "2 hours",
            "latitude": 18.9150,
            "longitude": 72.8258
        }
    ]

    result = optimize_route(sample_activities)

    print("\n🗺️ OPTIMIZED ROUTE")
    print("=" * 50)

    for index, place in enumerate(
        result["route"],
        start=1
    ):
        print(f"{index}. {place}")

    print("\nTOTAL STOPS:")
    print(result["total_stops"])

    print("\nTOTAL ROUTE DISTANCE:")
    print(f"{result['total_distance_km']} km")
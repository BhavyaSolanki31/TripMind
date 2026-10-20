
from tools.route_optimizer import optimize_route


def route_agent(activities):
    """
    Route Agent:
    Optimizes activity order and explains route limitations.

    Distances are straight-line estimates, not road or ferry distances.
    """

    result = optimize_route(activities)

    optimized_activities = result["optimized_activities"]
    optimized_route = result["route"]
    total_distance = result["total_distance_km"]

    distance_type = result.get(
        "distance_type",
        "straight-line estimate",
    )

    special_transport = result.get("special_transport", [])

    if not optimized_route:
        recommendation = "No activities were provided for route optimization."
    else:
        recommendation = (
    f"The optimized route covers {len(optimized_activities)} locations. "
    f"The estimated mainland straight-line distance is "
    f"{total_distance} km; special transport distances are excluded. "
    f"Actual road distances, ferry journeys, and schedules may differ."
)

        if special_transport:
            transport_details = ", ".join(
                f"{item['activity']} ({item['transport']} required)"
                for item in special_transport
            )

            recommendation += (
                f" Special transport considerations: {transport_details}. "
                "The distance estimate does not include verified road, "
                "ferry, or timetable routing."
            )

    return {
        "optimized_activities": optimized_activities,
        "route": optimized_route,
        "total_distance_km": total_distance,
        "recommendation": recommendation,
        "distance_type": distance_type,
        "special_transport": special_transport,
    }


if __name__ == "__main__":
    sample_activities = [
        {
            "name": "Gateway of India",
            "category": "Historical",
            "price": 0,
            "duration": "2 hours",
            "latitude": 18.9220,
            "longitude": 72.8347,
        },
        {
            "name": "Elephanta Caves",
            "category": "History",
            "price": 600,
            "duration": "4 hours",
            "latitude": 18.9633,
            "longitude": 72.9315,
        },
    ]

    result = route_agent(sample_activities)

    print("Route:", result["route"])
    print("Distance:", result["total_distance_km"], "km")
    print("Distance type:", result["distance_type"])
    print("Special transport:", result["special_transport"])
    print("Recommendation:", result["recommendation"])


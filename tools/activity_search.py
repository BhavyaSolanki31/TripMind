def search_activities(destination, interests):
    """
    Mock activity search tool for TripMind.

    Each activity now includes latitude and longitude
    so the Route Optimizer can calculate distances.
    """

    activities = [
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

    return activities


if __name__ == "__main__":

    result = search_activities(
        destination="Mumbai",
        interests=["sightseeing", "history"]
    )

    print("\n🎯 ACTIVITIES")

    for activity in result:
        print(activity)
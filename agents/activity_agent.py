
"""
TripMind Activity Agent

Responsibilities:
- Find activities for a destination.
- Match activities to user interests.
- Filter activities using the activity budget.
- Return structured data compatible with trip_graph.py.
"""

ACTIVITY_DATABASE = {
    "mumbai": [
        {
            "name": "Gateway of India",
            "category": "Historical",
            "price": 0,
            "duration": "2 hours",
            "latitude": 18.9220,
            "longitude": 72.8347,
        },
        {
            "name": "Marine Drive",
            "category": "Nature",
            "price": 0,
            "duration": "2 hours",
            "latitude": 18.9431,
            "longitude": 72.8238,
        },
        {
            "name": "Elephanta Caves",
            "category": "History",
            "price": 600,
            "duration": "4 hours",
            "latitude": 18.9633,
            "longitude": 72.9315,
        },
        {
            "name": "Colaba Causeway",
            "category": "Shopping",
            "price": 1000,
            "duration": "2 hours",
            "latitude": 18.9150,
            "longitude": 72.8317,
        },
        {
            "name": "Mumbai Street Food Tour",
            "category": "Food",
            "price": 800,
            "duration": "3 hours",
            "latitude": 18.9435,
            "longitude": 72.8248,
        },
        {
            "name": "Chhatrapati Shivaji Maharaj Terminus",
            "category": "Historical",
            "price": 0,
            "duration": "1 hour",
            "latitude": 18.9402,
            "longitude": 72.8355,
        },
        {
            "name": "Juhu Beach",
            "category": "Nature",
            "price": 0,
            "duration": "2 hours",
            "latitude": 19.0988,
            "longitude": 72.8267,
        },
        {
            "name": "Sanjay Gandhi National Park",
            "category": "Adventure",
            "price": 100,
            "duration": "4 hours",
            "latitude": 19.2147,
            "longitude": 72.9106,
        },
    ]
}

INTEREST_CATEGORY_MAP = {
    "history": {"historical", "history"},
    "historical": {"historical", "history"},
    "historical places": {"historical", "history"},
    "culture": {"historical", "history"},
    "beach": {"nature"},
    "beaches": {"nature"},
    "nature": {"nature"},
    "outdoors": {"nature", "adventure"},
    "adventure": {"adventure"},
    "shopping": {"shopping"},
    "food": {"food"},
    "street food": {"food"},
    "food tours": {"food"},
}


def activity_agent(destination, interests=None, budget=None):
    """Return affordable, interest-matched destination activities."""

    destination_key = (destination or "").strip().lower()

    if isinstance(interests, str):
        interests = [interests]

    interests = [
        str(item).strip().lower()
        for item in (interests or [])
        if str(item).strip()
    ]

    available_activities = ACTIVITY_DATABASE.get(
        destination_key, []
    )

    if not available_activities:
        return {
            "available_activities": [],
            "selected_activities": [],
            "recommendation": (
                f"No activities are currently available in the "
                f"local database for {destination or 'this destination'}."
            ),
        }

    # Apply the activity budget.
    if budget is not None:
        try:
            activity_budget = float(budget)
        except (TypeError, ValueError):
            raise ValueError(
                "Activity budget must be a valid number."
            )

        if activity_budget < 0:
            raise ValueError("Activity budget cannot be negative.")

        affordable_activities = [
            activity
            for activity in available_activities
            if activity["price"] <= activity_budget
        ]
    else:
        affordable_activities = list(available_activities)

    # Resolve user interests into activity categories.
    desired_categories = set()

    for interest in interests:
        mapped_categories = INTEREST_CATEGORY_MAP.get(interest)

        if mapped_categories:
            desired_categories.update(mapped_categories)
        else:
            desired_categories.add(interest)

    # Strict interest matching: do not add unrelated activities.
    if desired_categories:
        selected_activities = [
            activity
            for activity in affordable_activities
            if activity["category"].strip().lower()
            in desired_categories
        ]
    else:
        # No interests supplied: use all affordable activities.
        selected_activities = list(affordable_activities)

    # Limit recommendations to five activities.
    selected_activities = selected_activities[:5]

    # Generate an accurate recommendation.
    if not affordable_activities:
        recommendation = (
            "No activities fit within the specified activity budget. "
            "Increase the activity budget or choose another destination."
        )

    elif desired_categories and not selected_activities:
        recommendation = (
            f"No affordable activities matching your selected interests "
            f"were found in {destination.title()}. "
            "Try broadening your interests or increasing your activity budget."
        )

    elif desired_categories:
        recommendation = (
            f"Selected {len(selected_activities)} activities in "
            f"{destination.title()}, matching your interests: "
            f"{', '.join(interests)}. "
            "Unrelated activities have been excluded."
        )

    else:
        recommendation = (
            f"Selected {len(selected_activities)} affordable activities "
            f"in {destination.title()} because no specific interests "
            "were provided."
        )

    return {
        "available_activities": available_activities,
        "selected_activities": selected_activities,
        "recommendation": recommendation,
    }


if __name__ == "__main__":
    result = activity_agent(
        destination="Mumbai",
        interests=["Food", "Shopping", "Nature"],
        budget=10000,
    )

    print("\nRecommendation:")
    print(result["recommendation"])

    print("\nSelected activities:")
    for activity in result["selected_activities"]:
        print(
            f"- {activity['name']} "
            f"({activity['category']}, ₹{activity['price']})"
        )

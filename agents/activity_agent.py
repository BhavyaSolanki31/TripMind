
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


# Interest keywords mapped to activity categories.
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
    """
    Return destination activities, selected activities, and a recommendation.

    The return format is compatible with activity_node() in trip_graph.py.
    """

    destination_key = (destination or "").strip().lower()

    # Always return a list of normalized interests.
    if isinstance(interests, str):
        interests = [interests]

    interests = [
        str(item).strip().lower()
        for item in (interests or [])
        if str(item).strip()
    ]

    # Retrieve all activities for the requested destination.
    available_activities = ACTIVITY_DATABASE.get(
        destination_key, []
    )

    # Return a consistent structure for unsupported destinations.
    if not available_activities:
        return {
            "available_activities": [],
            "selected_activities": [],
            "recommendation": (
                f"No activities are currently available in the "
                f"local database for {destination or 'this destination'}. "
                "More destinations can be added to the activity database."
            ),
        }

    # Resolve interests to activity categories.
    desired_categories = set()

    for interest in interests:
        mapped_categories = INTEREST_CATEGORY_MAP.get(interest)

        if mapped_categories:
            desired_categories.update(mapped_categories)
        else:
            # Allow direct category matching for other inputs.
            desired_categories.add(interest)

    # Filter by the activity budget.
    # A budget of 0 is valid and should not be ignored.
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

    # Prioritize interest-matching activities.
    if desired_categories:
        matching_activities = [
            activity
            for activity in affordable_activities
            if activity["category"].lower() in desired_categories
        ]
    else:
        matching_activities = []

    # Fill the list with other affordable activities when needed.
    # This keeps recommendations useful even if interests match
    # only a few activities.
    selected_activities = list(matching_activities)

    for activity in affordable_activities:
        if activity not in selected_activities:
            selected_activities.append(activity)

        if len(selected_activities) >= 5:
            break

    # Return at most six activities.
    selected_activities = selected_activities[:6]

    # Explain the result.
    if not affordable_activities:
        recommendation = (
            "No activities fit within the specified activity budget. "
            "Increase the activity budget or choose another destination."
        )
    elif matching_activities:
        recommendation = (
            f"Selected {len(selected_activities)} activities in "
            f"{destination.title()}, prioritizing your interests"
            + (
                f": {', '.join(interests)}."
                if interests
                else "."
            )
            + " Remaining selections are affordable alternatives."
        )
    else:
        recommendation = (
            f"Selected {len(selected_activities)} affordable activities "
            f"in {destination.title()}. No exact interest-category "
            "matches were found, so affordable alternatives were used."
        )

    # IMPORTANT: Preserve the dictionary interface expected by
    # activity_node() in orchestrator/trip_graph.py.
    return {
        "available_activities": available_activities,
        "selected_activities": selected_activities,
        "recommendation": recommendation,
    }


if __name__ == "__main__":
    result = activity_agent(
        destination="Mumbai",
        interests=[
            "historical places",
            "beaches",
            "food",
            "shopping",
        ],
        budget=50000,
    )

    print("\nRecommendation:")
    print(result["recommendation"])

    print("\nAvailable activities:")
    for activity in result["available_activities"]:
        print(f"- {activity['name']} (₹{activity['price']})")

    print("\nSelected activities:")
    for activity in result["selected_activities"]:
        print(f"- {activity['name']} (₹{activity['price']})")

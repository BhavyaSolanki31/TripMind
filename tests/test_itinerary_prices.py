
from agents.itinerary_agent import normalize_activity, create_fallback_itinerary


def test_unknown_activity_price_remains_none():
    result = normalize_activity(
        {"name": "City Museum", "price": None, "price_status": "unknown"},
        "Mumbai",
    )

    assert result["cost"] is None
    assert result["price_status"] == "unknown"


def test_explicitly_free_activity_remains_zero():
    result = normalize_activity(
        {"name": "India Gate", "price": 0, "price_status": "free"},
        "Delhi",
    )

    assert result["cost"] == 0
    assert result["price_status"] == "free"


def test_unverified_price_is_preserved():
    result = normalize_activity(
        {"name": "Museum", "price": 500, "price_status": "unverified"},
        "Mumbai",
    )

    assert result["cost"] == 500
    assert result["price_status"] == "unverified"


def test_missing_activity_price_is_not_defaulted_to_zero():
    result = normalize_activity(
        {"name": "Historical Monument"},
        "Mumbai",
    )

    assert result["cost"] is None
    assert result["price_status"] == "unknown"


def test_fallback_itinerary_preserves_unknown_price():
    itinerary = create_fallback_itinerary(
        origin="Delhi",
        destination="Mumbai",
        check_in="2026-12-01",
        check_out="2026-12-02",
        selected_flight={},
        selected_stay={},
        optimized_activities=[
            {
                "name": "City Museum",
                "price": None,
                "price_status": "unknown",
                "latitude": 19.0,
                "longitude": 72.0,
            }
        ],
        weather=[],
    )

    activities = [
        activity
        for day in itinerary["days"]
        for activity in day["activities"]
    ]

    museum = next(
        activity
        for activity in activities
        if activity["title"] == "City Museum"
    )

    assert museum["cost"] is None
    assert museum["price_status"] == "unknown"


def test_unavailable_activity_data_shows_warning_placeholder():
    itinerary = create_fallback_itinerary(
        origin="Delhi",
        destination="Mumbai",
        check_in="2026-12-01",
        check_out="2026-12-04",
        selected_flight={},
        selected_stay={},
        optimized_activities=[],
        weather=[],
        activity_data_status="unavailable",
    )

    middle_day = itinerary["days"][1]
    placeholder = middle_day["activities"][0]

    assert placeholder["title"] == "Activity Information Unavailable"
    assert placeholder["cost"] is None
    assert placeholder["price_status"] == "unknown"


def test_available_activity_data_with_no_matches_shows_message():
    itinerary = create_fallback_itinerary(
        origin="Delhi",
        destination="Mumbai",
        check_in="2026-12-01",
        check_out="2026-12-04",
        selected_flight={},
        selected_stay={},
        optimized_activities=[],
        weather=[],
        activity_data_status="available",
    )

    middle_day = itinerary["days"][1]
    placeholder = middle_day["activities"][0]

    assert placeholder["title"] == "No Matching Activities"
    assert placeholder["cost"] is None
    assert placeholder["price_status"] == "unknown"



def test_existing_activities_are_not_replaced_by_placeholder():
    itinerary = create_fallback_itinerary(
        origin="Delhi",
        destination="Mumbai",
        check_in="2026-12-01",
        check_out="2026-12-04",
        selected_flight={},
        selected_stay={},
        optimized_activities=[
            {
                "name": "City Museum",
                "price": None,
                "price_status": "unknown",
                "latitude": 19.0,
                "longitude": 72.0,
            }
        ],
        weather=[],
        activity_data_status="unavailable",
    )

    museum_day = next(
        day
        for day in itinerary["days"]
        if any(
            activity["title"] == "City Museum"
            for activity in day["activities"]
        )
    )

    titles = [
        activity["title"]
        for activity in museum_day["activities"]
    ]

    assert "City Museum" in titles
    assert "Activity Information Unavailable" not in titles

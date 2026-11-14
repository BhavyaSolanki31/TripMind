
from agents.itinerary_agent import create_fallback_itinerary


def test_one_day_trip_preserves_activities():
    itinerary = create_fallback_itinerary(
        origin="Delhi",
        destination="Mumbai",
        check_in="2026-12-10",
        check_out="2026-12-10",
        selected_flight={},
        selected_stay={},
        optimized_activities=[
            {"name": "Gateway of India", "price": None},
        ],
        weather=[],
    )

    all_activities = [
        activity
        for day in itinerary["days"]
        for activity in day["activities"]
    ]

    titles = [activity["title"] for activity in all_activities]

    assert "Gateway of India" in titles


def test_two_day_trip_preserves_activities():
    itinerary = create_fallback_itinerary(
        origin="Delhi",
        destination="Mumbai",
        check_in="2026-12-10",
        check_out="2026-12-11",
        selected_flight={},
        selected_stay={},
        optimized_activities=[
            {"name": "Gateway of India", "price": 0},
            {"name": "Marine Drive", "price": None},
        ],
        weather=[],
    )

    all_activities = [
        activity
        for day in itinerary["days"]
        for activity in day["activities"]
    ]

    titles = [activity["title"] for activity in all_activities]

    assert "Gateway of India" in titles
    assert "Marine Drive" in titles

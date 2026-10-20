
from fastapi.testclient import TestClient

from api.main import app

from unittest.mock import patch

client = TestClient(app)


def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert "message" in response.json()


def test_plan_trip_rejects_same_start_and_end_date():
    payload = {
        "origin": "Delhi",
        "destination": "Mumbai",
        "start_date": "2026-10-20",
        "end_date": "2026-10-20",
        "travelers": 2,
        "total_budget": 50000,
        "interests": ["food", "historical places"],
    }

    response = client.post("/plan-trip", json=payload)

    assert response.status_code == 422

def test_plan_trip_rejects_end_date_before_start_date():
    payload = {
        "origin": "Delhi",
        "destination": "Mumbai",
        "start_date": "2026-10-25",
        "end_date": "2026-10-20",
        "travelers": 2,
        "total_budget": 50000,
        "interests": ["food"],
    }

    response = client.post("/plan-trip", json=payload)

    assert response.status_code == 422
    assert any(
        "End date must be after start date." in error["msg"]
         for error in response.json()["detail"]
    )

def test_plan_trip_returns_expected_response():
    fake_result = {
        "selected_flight": {"airline": "Test Air"},
        "selected_stay": {"name": "Test Hotel"},
        "selected_activities": [{"name": "Test Activity"}],
        "optimized_route": [],
        "total_route_distance_km": 0,
        "route_recommendation": "Test route",
        "route_distance_type": "straight-line estimate",
        "special_transport": [],
        "budget_breakdown": {"total_cost": 10000},
        "budget_recommendation": "Within budget",
        "weather": [],
        "weather_recommendation": "Weather available",
        "final_itinerary": "Test itinerary",
    }

    payload = {
        "origin": "Delhi",
        "destination": "Mumbai",
        "start_date": "2026-10-20",
        "end_date": "2026-10-25",
        "travelers": 2,
        "total_budget": 50000,
        "interests": ["food"],
    }

    with patch("api.main.trip_graph.invoke", return_value=fake_result) as mock_invoke:
        response = client.post("/plan-trip", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert data["selected_flight"]["airline"] == "Test Air"
    assert data["selected_stay"]["name"] == "Test Hotel"
    assert data["budget"]["total_cost"] == 10000
    assert data["itinerary"] == "Test itinerary"

    mock_invoke.assert_called_once()


def test_plan_trip_rejects_missing_required_field():
    payload = {
        "origin": "Delhi",
        # destination is intentionally missing
        "start_date": "2026-10-20",
        "end_date": "2026-10-25",
        "travelers": 2,
        "total_budget": 50000,
        "interests": ["food"],
    }

    response = client.post("/plan-trip", json=payload)

    assert response.status_code == 422


def test_plan_trip_rejects_invalid_travelers_type():
    payload = {
        "origin": "Delhi",
        "destination": "Mumbai",
        "start_date": "2026-10-20",
        "end_date": "2026-10-25",
        "travelers": "two",
        "total_budget": 50000,
        "interests": ["food"],
    }

    response = client.post("/plan-trip", json=payload)

    assert response.status_code == 422

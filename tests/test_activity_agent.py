
import pytest

import agents.activity_agent as activity_module


def test_extract_price_unknown_is_not_free():
    price, status = activity_module._extract_price({})

    assert price is None
    assert status == "unknown"


def test_extract_price_explicitly_free():
    price, status = activity_module._extract_price({"fee": "no"})

    assert price == 0
    assert status == "free"


def test_extract_price_charge_is_unverified():
    price, status = activity_module._extract_price(
        {"charge": "INR 250"}
    )

    assert price == 250.0
    assert status == "unverified"


def test_normalize_activities_removes_duplicates_and_invalid_places():
    elements = [
        {
            "type": "node",
            "id": 1,
            "lat": 28.6,
            "lon": 77.2,
            "tags": {"name": "India Gate", "tourism": "attraction"},
        },
        {
            "type": "node",
            "id": 2,
            "lat": 28.7,
            "lon": 77.3,
            "tags": {"name": "India Gate", "tourism": "attraction"},
        },
        {
            "type": "node",
            "id": 3,
            "lat": 28.6,
            "lon": 77.2,
            "tags": {"tourism": "attraction"},
        },
        {
            "type": "way",
            "id": 4,
            "tags": {"name": "Unnamed Coordinates Missing"},
        },
    ]

    activities = activity_module._normalize_activities(elements)

    assert len(activities) == 1
    assert activities[0]["name"] == "India Gate"
    assert activities[0]["price"] is None
    assert activities[0]["price_status"] == "unknown"


def test_normalize_activities_supports_way_center_coordinates():
    elements = [
        {
            "type": "way",
            "id": 10,
            "center": {"lat": 28.6, "lon": 77.2},
            "tags": {"name": "City Park", "leisure": "park"},
        }
    ]

    activities = activity_module._normalize_activities(elements)

    assert len(activities) == 1
    assert activities[0]["latitude"] == 28.6
    assert activities[0]["longitude"] == 77.2
    assert activities[0]["category"] == "Nature"


def test_activity_agent_retains_unknown_prices_with_budget(monkeypatch):
    monkeypatch.setattr(
        activity_module,
        "_geocode_destination",
        lambda destination: {
            "latitude": 28.6,
            "longitude": 77.2,
            "display_name": destination,
        },
    )

    monkeypatch.setattr(
        activity_module,
        "_fetch_activities",
        lambda latitude, longitude: [
            {
                "type": "node",
                "id": 1,
                "lat": 28.6,
                "lon": 77.2,
                "tags": {
                    "name": "India Gate",
                    "tourism": "attraction",
                },
            },
            {
                "type": "node",
                "id": 2,
                "lat": 28.61,
                "lon": 77.21,
                "tags": {
                    "name": "Paid Museum",
                    "tourism": "museum",
                    "charge": "500",
                },
            },
        ],
    )

    result = activity_module.activity_agent(
        destination="Delhi",
        interests=["sightseeing"],
        budget=100,
    )

    assert len(result["selected_activities"]) == 1
    assert result["selected_activities"][0]["name"] == "India Gate"
    assert result["selected_activities"][0]["price"] is None
    assert result["selected_activities"][0]["price_status"] == "unknown"
    assert result["unknown_price_count"] == 1


def test_activity_agent_returns_unavailable_on_geocoding_failure(monkeypatch):
    def fail_geocoding(destination):
        raise ValueError("Destination not found")

    monkeypatch.setattr(
        activity_module,
        "_geocode_destination",
        fail_geocoding,
    )

    result = activity_module.activity_agent(destination="Unknown Place")

    assert result["activity_data_status"] == "unavailable"
    assert result["available_activities"] == []
    assert result["selected_activities"] == []


def test_activity_agent_rejects_negative_budget():
    with pytest.raises(ValueError):
        activity_module.activity_agent(
            destination="Delhi",
            budget=-100,
        )


def test_activity_agent_rejects_boolean_budget():
    with pytest.raises(ValueError):
        activity_module.activity_agent(
            destination="Delhi",
            budget=True,
        )

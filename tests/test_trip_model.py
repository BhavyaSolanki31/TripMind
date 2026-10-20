
import pytest
from pydantic import ValidationError

from models.trip import TripRequest


def valid_payload():
    return {
        "origin": "Delhi",
        "destination": "Mumbai",
        "start_date": "2026-10-20",
        "end_date": "2026-10-25",
        "travelers": 2,
        "total_budget": 50000,
        "interests": ["food", "history"],
    }


def test_accepts_valid_trip_request():
    request = TripRequest(**valid_payload())

    assert request.origin == "Delhi"
    assert request.destination == "Mumbai"
    assert request.travelers == 2


@pytest.mark.parametrize("field", ["origin", "destination"])
def test_rejects_blank_locations(field):
    payload = valid_payload()
    payload[field] = "   "

    with pytest.raises(ValidationError):
        TripRequest(**payload)


def test_rejects_zero_travelers():
    payload = valid_payload()
    payload["travelers"] = 0

    with pytest.raises(ValidationError):
        TripRequest(**payload)


def test_rejects_negative_budget():
    payload = valid_payload()
    payload["total_budget"] = -100

    with pytest.raises(ValidationError):
        TripRequest(**payload)


def test_rejects_invalid_date():
    payload = valid_payload()
    payload["start_date"] = "not-a-date"

    with pytest.raises(ValidationError):
        TripRequest(**payload)


def test_rejects_empty_interests():
    payload = valid_payload()
    payload["interests"] = []

    with pytest.raises(ValidationError):
        TripRequest(**payload)


def test_rejects_end_date_before_start_date():
    payload = valid_payload()
    payload["end_date"] = "2026-10-19"

    with pytest.raises(ValidationError):
        TripRequest(**payload)


def test_rejects_unexpected_fields():
    payload = valid_payload()
    payload["unexpected_field"] = "not allowed"

    with pytest.raises(ValidationError):
        TripRequest(**payload)

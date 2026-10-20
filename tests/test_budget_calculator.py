
import pytest

from tools.budget_calculator import calculate_trip_budget


def test_calculates_total_trip_cost():
    result = calculate_trip_budget(
        flight_cost=18500,
        hotel_price_per_night=2800,
        nights=5,
        activity_cost=1500,
    )

    assert result["flight_cost"] == 18500
    assert result["hotel_cost"] == 14000
    assert result["activity_cost"] == 1500
    assert result["total_cost"] == 34000


def test_handles_zero_nights():
    result = calculate_trip_budget(
        flight_cost=10000,
        hotel_price_per_night=2000,
        nights=0,
        activity_cost=500,
    )

    assert result["hotel_cost"] == 0
    assert result["total_cost"] == 10500


def test_handles_zero_costs():
    result = calculate_trip_budget(
        flight_cost=0,
        hotel_price_per_night=0,
        nights=0,
        activity_cost=0,
    )

    assert result["total_cost"] == 0


@pytest.mark.parametrize(
    "flight_cost, hotel_price_per_night, nights, activity_cost",
    [
        (-1000, 2000, 3, 500),
        (10000, -2000, 3, 500),
        (10000, 2000, -3, 500),
        (10000, 2000, 3, -500),
    ],
)
def test_rejects_negative_budget_inputs(
    flight_cost,
    hotel_price_per_night,
    nights,
    activity_cost,
):
    with pytest.raises(ValueError):
        calculate_trip_budget(
            flight_cost=flight_cost,
            hotel_price_per_night=hotel_price_per_night,
            nights=nights,
            activity_cost=activity_cost,
        )


@pytest.mark.parametrize(
    "flight_cost, hotel_price_per_night, nights, activity_cost",
    [
        ("1000", 2000, 3, 500),
        (1000, None, 3, 500),
        (1000, 2000, True, 500),
    ],
)
def test_rejects_invalid_budget_input_types(
    flight_cost,
    hotel_price_per_night,
    nights,
    activity_cost,
):
    with pytest.raises(ValueError):
        calculate_trip_budget(
            flight_cost=flight_cost,
            hotel_price_per_night=hotel_price_per_night,
            nights=nights,
            activity_cost=activity_cost,
        )

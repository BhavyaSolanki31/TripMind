
import pytest

from agents.budget_agent import budget_agent


def test_reallocates_unused_budget_to_overspending_category():
    result = budget_agent(
        flight_cost=37000,
        hotel_price_per_night=3500,
        nights=3,
        activity_cost=1600,
        total_budget=50000,
    )

    analysis = result["reallocation_analysis"]

    assert result["budget_status"] == "Within budget"
    assert result["remaining_balance"] == 900
    assert analysis["total_unused_allocation"] == 15400
    assert analysis["total_category_overspending"] == 14500
    assert analysis["total_reallocated"] == 14500
    assert analysis["uncovered_overspending"] == 0


def test_detects_insufficient_category_surplus():
    result = budget_agent(
        flight_cost=30000,
        hotel_price_per_night=5000,
        nights=2,
        activity_cost=5000,
        total_budget=50000,
        flight_budget=15000,
        accommodation_budget=15000,
        activity_budget=10000,
    )

    analysis = result["reallocation_analysis"]

    assert result["budget_status"] == "Within budget"
    assert result["remaining_balance"] == 5000
    assert analysis["total_category_overspending"] == 15000
    assert analysis["total_reallocated"] == 10000
    assert analysis["uncovered_overspending"] == 5000


def test_detects_overall_budget_exceeded():
    result = budget_agent(
        flight_cost=40000,
        hotel_price_per_night=5000,
        nights=3,
        activity_cost=5000,
        total_budget=50000,
    )

    assert result["budget_status"] == "Over budget"
    assert result["remaining_balance"] == -10000


def test_no_reallocation_when_all_categories_are_within_allocation():
    result = budget_agent(
        flight_cost=15000,
        hotel_price_per_night=3000,
        nights=3,
        activity_cost=2000,
        total_budget=50000,
    )

    analysis = result["reallocation_analysis"]

    assert analysis["total_reallocated"] == 0
    assert analysis["uncovered_overspending"] == 0
    assert analysis["transfers"] == []


@pytest.mark.parametrize(
    "allocation",
    [-1000, float("inf"), float("nan"), True],
)
def test_rejects_invalid_category_allocations(allocation):
    with pytest.raises(ValueError):
        budget_agent(
            flight_cost=10000,
            hotel_price_per_night=2000,
            nights=2,
            activity_cost=1000,
            total_budget=50000,
            flight_budget=allocation,
        )

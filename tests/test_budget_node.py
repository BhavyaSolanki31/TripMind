
from orchestrator.trip_graph import budget_node


def make_budget_state(activities):
    """Create a minimal state for testing the Budget Node."""

    return {
        "selected_flight": {
            "price": 1000,
        },
        "selected_stay": {
            "price_per_night": 1000,
        },
        "travelers": 1,
        "optimized_activities": activities,
        "total_budget": 10000,
        "nights": 1,
    }


def test_unknown_activity_price_is_not_treated_as_free():
    state = make_budget_state([
        {
            "name": "Museum",
            "price": None,
            "price_status": "unknown",
        }
    ])

    result = budget_node(state)

    assert result["budget_breakdown"]["activity_cost"] == 0
    assert result["budget_status"] == "Incomplete estimate"
    assert result["budget_estimate_status"] == "Incomplete estimate"


def test_explicitly_free_activity_is_counted_as_zero():
    state = make_budget_state([
        {
            "name": "India Gate",
            "price": 0,
            "price_status": "free",
        }
    ])

    result = budget_node(state)

    assert result["budget_breakdown"]["activity_cost"] == 0
    assert result["budget_status"] == "Within budget"
    assert result["budget_estimate_status"] == "Complete estimate"


def test_unverified_activity_price_is_included_and_flagged():
    state = make_budget_state([
        {
            "name": "Museum",
            "price": 500,
            "price_status": "unverified",
        }
    ])

    result = budget_node(state)

    assert result["budget_breakdown"]["activity_cost"] == 500
    assert result["budget_estimate_status"] == "Contains unverified prices"
    assert "unverified" in result["budget_recommendation"].lower()


def test_missing_activity_price_is_not_treated_as_free():
    state = make_budget_state([
        {
            "name": "Historical Monument",
        }
    ])

    result = budget_node(state)

    assert result["budget_breakdown"]["activity_cost"] == 0
    assert result["budget_status"] == "Incomplete estimate"
    assert result["budget_estimate_status"] == "Incomplete estimate"

def test_budget_node_marks_unavailable_activities_as_incomplete():
    from orchestrator.trip_graph import budget_node

    state = {
        "total_budget": 40000,
        "flight_data": {"price": 18500},
        "stay_data": {"price_per_night": 3500},
        "optimized_activities": [],
        "unknown_activity_count": 0,
        "activity_data_status": "unavailable",
        "nights": 2,
    }

    result = budget_node(state)

    assert result["budget_estimate_status"] == "Incomplete estimate"
    assert "Activity discovery was unavailable" in result["budget_recommendation"]


def test_unavailable_activities_update_budget_analysis_status():
    state = make_budget_state([])
    state["activity_data_status"] = "unavailable"

    result = budget_node(state)

    assert result["budget_estimate_status"] == "Incomplete estimate"
    assert "**Budget Estimate Status:** Incomplete estimate" in (
        result["budget_recommendation"]
    )
    assert "Activity discovery was unavailable" in (
        result["budget_recommendation"]
    )


def test_available_activities_do_not_add_unavailable_warning():
    state = make_budget_state([])
    state["activity_data_status"] = "available"

    result = budget_node(state)

    assert result["budget_estimate_status"] == "Complete estimate"
    assert "Activity discovery was unavailable" not in (
        result["budget_recommendation"]
    )


def test_unverified_prices_are_consistent_in_budget_analysis():
    state = make_budget_state([
        {
            "name": "Museum",
            "price": 500,
            "price_status": "unverified",
        }
    ])

    result = budget_node(state)

    assert result["budget_estimate_status"] == (
        "Contains unverified prices"
    )
    assert "**Budget Estimate Status:** Contains unverified prices" in (
        result["budget_recommendation"]
    )

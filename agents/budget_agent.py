
from tools.budget_calculator import calculate_trip_budget


def budget_agent(
    flight_cost,
    hotel_price_per_night,
    nights,
    activity_cost,
    total_budget,
    flight_budget=None,
    accommodation_budget=None,
    activity_budget=None,
):
    """
    Budget Agent:
    1. Calculates exact trip costs using Python.
    2. Checks the overall trip budget.
    3. Checks individual category allocations.
    4. Generates a clear budget recommendation.
    """

    if not isinstance(total_budget, (int, float)) or isinstance(total_budget, bool):
        raise ValueError("Total budget must be a valid number.")

    if total_budget < 0:
        raise ValueError("Total budget cannot be negative.")

    # Default allocation policy: 45%, 35%, 20%.
    flight_budget = (
        total_budget * 0.45
        if flight_budget is None
        else flight_budget
    )

    accommodation_budget = (
        total_budget * 0.35
        if accommodation_budget is None
        else accommodation_budget
    )

    activity_budget = (
        total_budget * 0.20
        if activity_budget is None
        else activity_budget
    )

    allocations = {
        "Flights": (flight_budget, flight_cost),
        "Accommodation": (
            accommodation_budget,
            hotel_price_per_night * nights,
        ),
        "Activities": (activity_budget, activity_cost),
    }

    # Calculate exact actual trip expenses.
    budget = calculate_trip_budget(
        flight_cost=flight_cost,
        hotel_price_per_night=hotel_price_per_night,
        nights=nights,
        activity_cost=activity_cost,
    )

    total_cost = budget["total_cost"]
    remaining = total_budget - total_cost

    # Overall budget status.
    if remaining >= 0:
        budget_status = "Within budget"
        balance_message = f"₹{remaining:,.0f} remains."
    else:
        budget_status = "Over budget"
        balance_message = f"₹{abs(remaining):,.0f} over budget."

    # Category-level analysis.
    category_lines = []
    category_overspending = []

    for category, (allocated, actual) in allocations.items():
        difference = actual - allocated

        if difference > 0:
            status = f"Over allocation by ₹{difference:,.0f}"
            category_overspending.append(
                f"{category}: ₹{difference:,.0f} over"
            )
        else:
            status = f"Within allocation (₹{abs(difference):,.0f} remaining)"

        category_lines.append(
            f"**{category}:** "
            f"Allocated ₹{allocated:,.0f} | "
            f"Spent ₹{actual:,.0f} | "
            f"{status}"
        )

    if category_overspending and remaining >= 0:
        recommendation = (
            "The overall trip is within budget, but some category "
            "allocations have been exceeded. Consider reallocating "
            "unused accommodation or activity funds toward flights."
        )
    elif category_overspending and remaining < 0:
        recommendation = (
            "The trip exceeds the overall budget and some category "
            "allocations. Consider choosing lower-cost options."
        )
    elif remaining < 0:
        recommendation = (
            "The trip exceeds the overall budget. Consider reducing "
            "travel or accommodation expenses."
        )
    else:
        recommendation = (
            "The trip is within the overall budget and all category "
            "allocations."
        )

    budget_analysis = (
        f"**TripMind Budget Analysis:**\n\n"
        f"**Overall Budget Status:** {budget_status}\n\n"
        f"**Total Budget:** ₹{total_budget:,.0f}\n\n"
        f"**Total Estimated Cost:** ₹{total_cost:,.0f}\n\n"
        f"**Remaining Balance:** {balance_message}\n\n"
        f"**Category Breakdown:**\n\n"
        + "\n\n".join(category_lines)
        + f"\n\n**Suggestion:** {recommendation}"
    )

    return {
        "budget_breakdown": budget,
        "budget_status": budget_status,
        "remaining_balance": remaining,
        "budget_recommendation": budget_analysis,
        "category_analysis": {
            category: {
                "allocated": allocated,
                "actual": actual,
                "remaining": allocated - actual,
                "status": (
                    "Over allocation"
                    if actual > allocated
                    else "Within allocation"
                ),
            }
            for category, (allocated, actual) in allocations.items()
        },
    }


if __name__ == "__main__":
    result = budget_agent(
        flight_cost=37000,
        hotel_price_per_night=3500,
        nights=3,
        activity_cost=1800,
        total_budget=50000,
    )

    print(result["budget_recommendation"])

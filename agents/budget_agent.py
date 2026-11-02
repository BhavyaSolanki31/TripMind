
import math

from tools.budget_calculator import calculate_trip_budget


def _validate_money(name, value):
    """Validate budget and allocation values."""
    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not math.isfinite(value)
    ):
        raise ValueError(f"{name} must be a valid finite number.")

    if value < 0:
        raise ValueError(f"{name} cannot be negative.")


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
    1. Calculates trip expenses.
    2. Checks the overall budget.
    3. Analyzes category allocations.
    4. Calculates possible allocation transfers.
    5. Generates actionable budget recommendations.
    """

    _validate_money("Total budget", total_budget)

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

    # Validate category allocations.
    for category, (allocated, actual) in allocations.items():
        _validate_money(f"{category} allocation", allocated)

    # Calculate actual trip expenses.
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
    category_analysis = {}
    category_lines = []
    surplus_pool = 0
    total_category_overspending = 0

    for category, (allocated, actual) in allocations.items():
        difference = actual - allocated
        unused = max(allocated - actual, 0)
        excess = max(actual - allocated, 0)

        surplus_pool += unused
        total_category_overspending += excess

        if excess > 0:
            status = "Over allocation"
            status_message = f"Over by ₹{excess:,.0f}"
        else:
            status = "Within allocation"
            status_message = f"₹{unused:,.0f} unused"

        category_analysis[category] = {
            "allocated": allocated,
            "actual": actual,
            "remaining": allocated - actual,
            "status": status,
            "surplus": unused,
            "overspending": excess,
        }

        category_lines.append(
            f"**{category}:** "
            f"Allocated ₹{allocated:,.0f} | "
            f"Spent ₹{actual:,.0f} | "
            f"{status_message}"
        )

    
    # Calculate possible reallocation transfers.
    # Keep original category analysis values unchanged.
    available_surplus = {
        category: data["surplus"]
        for category, data in category_analysis.items()
    }

    remaining_surplus = surplus_pool
    reallocation_transfers = []
    uncovered_overspending = 0

    for recipient, recipient_data in category_analysis.items():
        deficit = recipient_data["overspending"]

        if deficit <= 0:
            continue

        for donor in category_analysis:
            if donor == recipient or remaining_surplus <= 0:
                continue

            available = available_surplus[donor]

            if available <= 0:
                continue

            transfer = min(deficit, available)

            if transfer > 0:
                reallocation_transfers.append({
                    "from": donor,
                    "to": recipient,
                    "amount": transfer,
                })

                available_surplus[donor] -= transfer
                deficit -= transfer
                remaining_surplus -= transfer

            if deficit <= 0:
                break

        uncovered_overspending += max(deficit, 0)

    total_reallocated = sum(
        transfer["amount"] for transfer in reallocation_transfers
    )

    # Actionable savings suggestions.
    savings_suggestions = []

    if category_analysis["Flights"]["overspending"] > 0:
        savings_suggestions.append(
            "Compare alternative flight dates, airlines, and departure "
            "times to reduce airfare."
        )

    if category_analysis["Accommodation"]["overspending"] > 0:
        savings_suggestions.append(
            "Consider budget hotels, alternative neighbourhoods, "
            "or shorter stays."
        )

    if category_analysis["Activities"]["overspending"] > 0:
        savings_suggestions.append(
            "Prioritize free attractions and reduce paid activities."
        )

    # Overall recommendation.
    if remaining < 0:
        recommendation = (
            f"The trip exceeds the total budget by ₹{abs(remaining):,.0f}. "
            "Reduce expenses or increase the available budget."
        )
    elif uncovered_overspending > 0:
        recommendation = (
            f"The trip is within the total budget, but ₹"
            f"{uncovered_overspending:,.0f} of category overspending "
            "cannot be covered by unused category allocations."
        )
    elif total_reallocated > 0:
        recommendation = (
            f"The trip is within budget. ₹{total_reallocated:,.0f} "
            "can be reallocated from underused categories to cover "
            "category overspending."
        )
    else:
        recommendation = (
            "The trip is within the overall budget and all category "
            "allocations."
        )

    transfer_lines = [
        f"{item['from']} → {item['to']}: ₹{item['amount']:,.0f}"
        for item in reallocation_transfers
    ]

    budget_analysis = (
        f"**TripMind Budget Analysis:**\n\n"
        f"**Overall Budget Status:** {budget_status}\n\n"
        f"**Total Budget:** ₹{total_budget:,.0f}\n\n"
        f"**Total Estimated Cost:** ₹{total_cost:,.0f}\n\n"
        f"**Remaining Balance:** {balance_message}\n\n"
        f"**Category Breakdown:**\n\n"
        + "\n\n".join(category_lines)
        + "\n\n**Suggested Reallocations:**\n\n"
        + (
            "\n".join(transfer_lines)
            if transfer_lines
            else "No reallocation required."
        )
        + f"\n\n**Suggestion:** {recommendation}"
    )

    if savings_suggestions:
        budget_analysis += (
            "\n\n**Cost-Saving Tips:**\n\n"
            + "\n".join(f"- {tip}" for tip in savings_suggestions)
        )

    return {
        "budget_breakdown": budget,
        "budget_status": budget_status,
        "remaining_balance": remaining,
        "budget_recommendation": budget_analysis,
        "category_analysis": category_analysis,
        "reallocation_analysis": {
            "total_unused_allocation": surplus_pool,
            "total_category_overspending": total_category_overspending,
            "total_reallocated": total_reallocated,
            "uncovered_overspending": uncovered_overspending,
            "transfers": reallocation_transfers,
        },
        "savings_suggestions": savings_suggestions,
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

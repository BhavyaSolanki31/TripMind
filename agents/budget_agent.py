from tools.budget_calculator import calculate_trip_budget
from models.llm import ask_ai


def budget_agent(
    flight_cost,
    hotel_price_per_night,
    nights,
    activity_cost,
    total_budget
):
    """
    Budget Agent:
    1. Calculates the exact trip cost using Python.
    2. Determines whether the trip is within budget.
    3. Uses AI only for a practical recommendation.
    """

    budget = calculate_trip_budget(
        flight_cost=flight_cost,
        hotel_price_per_night=hotel_price_per_night,
        nights=nights,
        activity_cost=activity_cost
    )

    total_cost = budget["total_cost"]
    remaining = total_budget - total_cost

    if remaining >= 0:
        budget_status = "Within budget"
        balance_message = f"₹{remaining:,} remains."
    else:
        budget_status = "Over budget"
        balance_message = f"₹{abs(remaining):,} over budget."

    prompt = f"""
You are TripMind's Budget Agent.

Python has already calculated the exact financial values.
DO NOT recalculate or modify any numbers.

Trip budget: ₹{total_budget:,}
Flight cost: ₹{budget["flight_cost"]:,}
Hotel cost: ₹{budget["hotel_cost"]:,}
Activity cost: ₹{budget["activity_cost"]:,}
Total trip cost: ₹{total_cost:,}
Remaining balance: ₹{remaining:,}

Budget status: {budget_status}

Write ONE short practical suggestion for the traveler.

Important:
- Do not change any numbers.
- Do not perform additional calculations.
- Do not invent fees or adjustments.
- Do not mention a different remaining balance.
- Keep the suggestion concise.
"""

    if total_cost <= total_budget:

      recommendation = (
        f"Trip is within budget. "
        f"Remaining balance is ₹{total_budget-total_cost}."
    )

    else:

      recommendation = (
        f"Trip exceeds budget by "
        f"₹{total_cost-total_budget}."
    )

    budget_analysis = (
        f"**TripMind Budget Analysis:**\n\n"
        f"**Budget Status:** {budget_status}.\n\n"
        f"**Remaining Balance:** {balance_message}\n\n"
        f"**Suggestion:** {recommendation}"
    )

    return {
        "budget_breakdown": budget,
        "budget_status": budget_status,
        "remaining_balance": remaining,
        "budget_recommendation": budget_analysis
    }


if __name__ == "__main__":

    result = budget_agent(
        flight_cost=18500,
        hotel_price_per_night=2800,
        nights=5,
        activity_cost=600,
        total_budget=40000
    )

    print("\nBUDGET BREAKDOWN:")
    print(result["budget_breakdown"])

    print("\nBUDGET STATUS:")
    print(result["budget_status"])

    print("\nREMAINING BALANCE:")
    print(result["remaining_balance"])

    print("\nAI BUDGET ANALYSIS:")
    print(result["budget_recommendation"])
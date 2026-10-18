from tools.stay_search import search_stays
from models.llm import ask_ai


def stay_agent(destination, check_in, check_out, travelers, budget):
    """
    Stay Agent:
    1. Searches available stays.
    2. Selects the best stay within budget.
    3. Returns structured stay information.
    """

    stays = search_stays(
        destination,
        check_in,
        check_out,
        travelers
    )

    affordable_stays = [
        stay for stay in stays
        if stay["price_per_night"] <= budget
    ]

    if affordable_stays:
        selected_stay = max(
            affordable_stays,
            key=lambda stay: (
                stay["rating"],
                -stay["price_per_night"]
            )
        )
    else:
        selected_stay = min(
            stays,
            key=lambda stay: stay["price_per_night"]
        )

    prompt = f"""
You are TripMind's Stay Agent.

The user wants to stay in {destination}
from {check_in} to {check_out}.

Travelers: {travelers}
Maximum nightly budget: ₹{budget}

Selected stay:

{selected_stay}

Briefly explain why this stay is a good choice.
Consider price, rating, and location.
"""

    recommendation = (
    f"{selected_stay['name']} is recommended because "
    f"it has a rating of {selected_stay['rating']}/5 "
    f"and costs ₹{selected_stay['price_per_night']} per night "
    f"within your budget."
)

    return {
        "available_stays": stays,
        "selected_stay": selected_stay,
        "recommendation": recommendation
    }


if __name__ == "__main__":

    result = stay_agent(
        destination="Mumbai",
        check_in="2026-12-10",
        check_out="2026-12-13",
        travelers=2,
        budget=3000
    )

    print("\nAVAILABLE STAYS:")

    for stay in result["available_stays"]:
        print(stay)

    print("\nSELECTED STAY:")
    print(result["selected_stay"])

    print("\nAI RECOMMENDATION:")
    print(result["recommendation"])
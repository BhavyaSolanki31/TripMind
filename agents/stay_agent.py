from datetime import date

from tools.stay_search import search_stays


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

    if not stays:
        return {
            "available_stays": [],
            "selected_stay": {},
            "recommendation": f"No stay options were found in {destination}.",
        }

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

    is_affordable = selected_stay["price_per_night"] <= budget
    nights = max(0, (
        date.fromisoformat(check_out)
        - date.fromisoformat(check_in)
    ).days)
    total_stay_cost = selected_stay["price_per_night"] * nights
    if is_affordable:
        recommendation = (
            f"{selected_stay['name']} is recommended with a rating of "
            f"{selected_stay['rating']}/5 at ₹{selected_stay['price_per_night']:,} per night, "
            f"within the nightly target of ₹{budget:,}. The estimated stay total for "
            f"{nights} night(s) is ₹{total_stay_cost:,}. Prices are mock estimates."
        )
    else:
        recommendation = (
            f"No listed stay fits the nightly target of ₹{budget:,}. The lowest-priced "
            f"selected option is {selected_stay['name']} at ₹{selected_stay['price_per_night']:,} per night "
            f"(₹{total_stay_cost:,} for {nights} night(s)), which is "
            f"₹{selected_stay['price_per_night'] - budget:,} per night over target. "
            "Prices are mock estimates, not live availability or quotes."
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
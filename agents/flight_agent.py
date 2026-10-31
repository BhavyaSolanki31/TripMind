
from tools.flight_search import search_flights


def flight_agent(origin, destination, date, budget, travelers=1):
    """
    Flight Agent:
    - Searches mock flight options.
    - Treats each listed fare as a per-person estimate.
    - Calculates the total flight cost for all travelers.
    """

    if not isinstance(travelers, int) or isinstance(travelers, bool) or travelers < 1:
        raise ValueError("travelers must be a positive whole number.")

    flights = search_flights(origin, destination, date)

    if not flights:
        return {
            "available_flights": [],
            "selected_flight": {},
            "recommendation": (
                f"No flight options were found for {origin} to {destination}."
            ),
        }

    # Preserve the listed per-person fare and calculate a group estimate.
    normalized_flights = []
    for flight in flights:
        fare_per_person = flight["price"]
        normalized_flights.append({
            **flight,
            "price_per_person": fare_per_person,
            "price": fare_per_person * travelers,
            "travelers": travelers,
            "price_scope": "total_for_all_travelers",
        })

    affordable_flights = [
        flight for flight in normalized_flights
        if flight["price"] <= budget
    ]

    if affordable_flights:
        selected_flight = min(
            affordable_flights,
            key=lambda flight: (flight["stops"], flight["price"])
        )
    else:
        selected_flight = min(
            normalized_flights,
            key=lambda flight: flight["price"]
        )

    if selected_flight["price"] <= budget:
        recommendation = (
            f"{selected_flight['airline']} is estimated at "
            f"₹{selected_flight['price_per_person']:,} per person, "
            f"or ₹{selected_flight['price']:,} for {travelers} traveler(s). "
            "These are mock estimates, not live quotes."
        )
    else:
        recommendation = (
            f"No listed flight fits the flight budget of ₹{budget:,}. "
            f"The cheapest listed option is estimated at "
            f"₹{selected_flight['price']:,} for {travelers} traveler(s). "
            "These are mock estimates, not live quotes."
        )

    return {
        "available_flights": normalized_flights,
        "selected_flight": selected_flight,
        "recommendation": recommendation,
    }

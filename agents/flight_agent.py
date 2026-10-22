from tools.flight_search import search_flights


def flight_agent(origin, destination, date, budget):
    """
    Flight Agent:
    1. Searches available flights.
    2. Selects the best flight based on budget and travel time.
    3. Returns structured flight information.
    """

    flights = search_flights(origin, destination, date)

    if not flights:
        return {
            "available_flights": [],
            "selected_flight": {},
            "recommendation": f"No flight options were found for {origin} to {destination}.",
        }

    # Prefer an affordable option; otherwise clearly report the cheapest over-budget option.
    affordable_flights = [
        flight for flight in flights
        if flight["price"] <= budget
    ]

    if affordable_flights:
        selected_flight = min(
            affordable_flights,
            key=lambda flight: (flight["stops"], flight["price"])
        )
    else:
        selected_flight = min(
            flights,
            key=lambda flight: flight["price"]
        )

    is_affordable = selected_flight["price"] <= budget
    if is_affordable:
        recommendation = (
            f"{selected_flight['airline']} is selected at ₹{selected_flight['price']:,}, "
            f"within your flight budget of ₹{budget:,}. It has "
            f"{selected_flight.get('stops', 'an unspecified number of')} stop(s)."
        )
    else:
        recommendation = (
            f"No listed flight fits the flight budget of ₹{budget:,}. "
            f"The cheapest listed option is {selected_flight['airline']} at "
            f"₹{selected_flight['price']:,}, which is ₹{selected_flight['price'] - budget:,} over the flight budget. "
            "Prices are mock estimates, not live quotes."
        )

    return {
        "available_flights": flights,
        "selected_flight": selected_flight,
        "recommendation": recommendation
    }


if __name__ == "__main__":

    result = flight_agent(
        origin="Delhi",
        destination="Mumbai",
        date="2026-12-10",
        budget=20000
    )

    print("\nAVAILABLE FLIGHTS:")

    for flight in result["available_flights"]:
        print(flight)

    print("\nSELECTED FLIGHT:")
    print(result["selected_flight"])

    print("\nAI RECOMMENDATION:")
    print(result["recommendation"])
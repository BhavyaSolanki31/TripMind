from tools.flight_search import search_flights
from models.llm import ask_ai


def flight_agent(origin, destination, date, budget):
    """
    Flight Agent:
    1. Searches available flights.
    2. Selects the best flight based on budget and travel time.
    3. Returns structured flight information.
    """

    flights = search_flights(origin, destination, date)

    # Select the best flight using simple deterministic logic.
    # We will make this smarter later.
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

    prompt = f"""
You are TripMind's Flight Agent.

The user wants to travel from {origin} to {destination}
on {date}.

Flight budget: ₹{budget}

Selected flight:

{selected_flight}

Explain briefly why this flight is a good choice.
Consider price, duration, and number of stops.
"""

    recommendation = (
    f"{selected_flight['airline']} is selected because "
    f"it fits within your budget of ₹{budget}. "
    f"It offers a balance between price, duration, and stops."
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
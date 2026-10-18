def search_flights(origin, destination, date):
    """
    Search for available flights.

    Currently using mock data.
    Later, this function will connect to a real flight API.
    """

    flights = [
        {
            "airline": "Air India",
            "price": 18500,
            "duration": "2h 10m",
            "stops":1
        },
        {
            "airline": "IndiGo",
            "price": 21000,
            "duration": "7h 10m",
            "stops": 0
        },
        {
            "airline": "Vistara",
            "price": 19500,
            "duration": "7h 45m",
            "stops": 1
        }
    ]

    return flights


if __name__ == "__main__":
    results = search_flights(
        "Delhi",
        "Mumbai",
        "2026-12-10"
    )

    for flight in results:
        print(flight)
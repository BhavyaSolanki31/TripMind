def search_stays(destination, check_in, check_out, travelers):
    """
    Search for available stays.

    Currently using mock data.
    Later, this will connect to a real hotel/stay API.
    """

    stays = [
        {
            "name": "The Grand Residency",
            "price_per_night": 3500,
            "rating": 4.5,
            "location": "City Center"
        },
        {
            "name": "Urban Nest Hotel",
            "price_per_night": 2800,
            "rating": 4.2,
            "location": "Near Metro"
        },
        {
            "name": "Budget Comfort Inn",
            "price_per_night": 1800,
            "rating": 3.9,
            "location": "Downtown"
        }
    ]

    return stays


if __name__ == "__main__":

    results = search_stays(
        destination="Mumbai",
        check_in="2026-12-10",
        check_out="2026-12-13",
        travelers=2
    )

    for stay in results:
        print(stay)
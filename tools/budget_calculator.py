def calculate_trip_budget(
    flight_cost,
    hotel_price_per_night,
    nights,
    activity_cost
):
    """
    Calculate the estimated total trip cost.
    """

    hotel_cost = hotel_price_per_night * nights

    total_cost = (
        flight_cost
        + hotel_cost
        + activity_cost
    )

    return {
        "flight_cost": flight_cost,
        "hotel_cost": hotel_cost,
        "activity_cost": activity_cost,
        "total_cost": total_cost
    }


if __name__ == "__main__":

    result = calculate_trip_budget(
        flight_cost=19500,
        hotel_price_per_night=2800,
        nights=3,
        activity_cost=600
    )

    print(result)
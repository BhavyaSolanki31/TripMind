
def calculate_trip_budget(
    flight_cost,
    hotel_price_per_night,
    nights,
    activity_cost,
):
    """Calculate estimated trip cost with input validation."""

    inputs = {
        "flight_cost": flight_cost,
        "hotel_price_per_night": hotel_price_per_night,
        "nights": nights,
        "activity_cost": activity_cost,
    }

    for name, value in inputs.items():
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError(f"{name} must be a number.")

        if value < 0:
            raise ValueError(f"{name} cannot be negative.")

    hotel_cost = hotel_price_per_night * nights
    total_cost = flight_cost + hotel_cost + activity_cost

    return {
        "flight_cost": flight_cost,
        "hotel_cost": hotel_cost,
        "activity_cost": activity_cost,
        "total_cost": total_cost,
    }


if __name__ == "__main__":
    result = calculate_trip_budget(
        flight_cost=19500,
        hotel_price_per_night=2800,
        nights=3,
        activity_cost=600,
    )
    print(result)

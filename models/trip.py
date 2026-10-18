from typing import TypedDict


class TripRequest(TypedDict):
    origin: str
    destination: str
    start_date: str
    end_date: str
    travelers: int
    total_budget: int
    interests: list
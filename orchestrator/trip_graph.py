
import json
import math
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

from agents.flight_agent import flight_agent
from agents.stay_agent import stay_agent
from agents.activity_agent import activity_agent
from agents.route_agent import route_agent
from agents.budget_agent import budget_agent
from agents.weather_agent import weather_agent
from agents.itinerary_agent import itinerary_agent


class TripState(TypedDict):
    origin: str
    destination: str
    date: str

    flight_budget: int
    flights: list
    selected_flight: dict
    flight_recommendation: str

    check_in: str
    check_out: str
    travelers: int

    stay_budget: int
    stays: list
    selected_stay: dict
    stay_recommendation: str

    interests: list
    activity_budget: int
    activities: list
    selected_activities: list
    activity_recommendation: str

    activity_data_status: str
    activity_source: str
    unknown_activity_count: int
    unverified_activity_count: int
    destination_coordinates: dict

    optimized_activities: list
    optimized_route: list
    total_route_distance_km: float
    route_recommendation: str
    route_distance_type: str
    special_transport: list

    total_budget: int
    nights: int
    budget_breakdown: dict
    budget_status: str
    budget_estimate_status: str
    remaining_balance: float
    budget_recommendation: str
    category_analysis: dict
    reallocation_analysis: dict
    savings_suggestions: list

    weather: list
    weather_recommendation: str
    final_itinerary: dict

    unverified_activity_count: int


def flight_node(state):
    travelers = state["travelers"]

    result = flight_agent(
        origin=state["origin"],
        destination=state["destination"],
        date=state["date"],
        budget=state["flight_budget"],
        travelers=travelers,
    )

    return {
        "flights": result["available_flights"],
        "selected_flight": result["selected_flight"],
        "flight_recommendation": result["recommendation"],
    }


def stay_node(state):
    result = stay_agent(
        destination=state["destination"],
        check_in=state["check_in"],
        check_out=state["check_out"],
        travelers=state["travelers"],
        budget=state["stay_budget"],
    )

    return {
        "stays": result["available_stays"],
        "selected_stay": result["selected_stay"],
        "stay_recommendation": result["recommendation"],
    }


def activity_node(state):
    result = activity_agent(
        destination=state["destination"],
        interests=state["interests"],
        budget=state["activity_budget"],
    )

    return {
        "activities": result["available_activities"],
        "selected_activities": result["selected_activities"],
        "activity_recommendation": result["recommendation"],
        "activity_data_status": result.get(
            "activity_data_status", "unknown"
        ),
        "activity_source": result.get("activity_source", "unknown"),
        "unknown_activity_count": result.get(
            "unknown_price_count", 0
        ),
        "destination_coordinates": result.get(
            "destination_coordinates"
        ),
    }


def route_node(state):
    result = route_agent(
        activities=state["selected_activities"]
    )

    return {
        "optimized_activities": result["optimized_activities"],
        "optimized_route": result["route"],
        "total_route_distance_km": result["total_distance_km"],
        "route_recommendation": result["recommendation"],
        "route_distance_type": result["distance_type"],
        "special_transport": result["special_transport"],
    }


def _get_activity_price(activity):
    """
    Return (known_price, price_status).

    Unknown prices are never converted to zero.
    Explicitly free activities remain zero.
    """

    if not isinstance(activity, dict):
        return None, "unknown"

    price = activity.get("price")

    if price is None:
        price = activity.get("cost")

    if price is None:
        return None, "unknown"

    if (
        not isinstance(price, (int, float))
        or isinstance(price, bool)
        or not math.isfinite(price)
        or price < 0
    ):
        return None, "unknown"

    status = str(
        activity.get("price_status", "")
    ).strip().lower()

    if status in {"unknown", "unavailable"}:
        return None, "unknown"

    if status in {"unverified", "estimated"}:
        return float(price), "unverified"

    return float(price), "known"


def budget_node(state):
    selected_flight = state.get("selected_flight") or {}
    selected_stay = state.get("selected_stay") or {}

    # Flight price is already the total for all travelers
    # when price_per_person is provided.
    if "price_per_person" in selected_flight:
        flight_cost = selected_flight.get("price", 0)
    else:
        flight_cost = (
            selected_flight.get("price", 0)
            * state.get("travelers", 1)
        )

    hotel_price = selected_stay.get("price_per_night", 0)

    activities = state.get("optimized_activities") or []

    activity_cost = 0.0
    unknown_activity_count = 0
    unverified_activity_count = 0

    for activity in activities:
        price, status = _get_activity_price(activity)

        if status == "unknown":
            unknown_activity_count += 1
        elif status == "unverified":
            activity_cost += price
            unverified_activity_count += 1
        else:
            activity_cost += price

    # Use the Activity Agent's unknown count as an additional
    # signal, without double-counting unknown optimized activities.
    reported_unknown_count = state.get(
        "unknown_activity_count", 0
    )

    if (
        isinstance(reported_unknown_count, int)
        and not isinstance(reported_unknown_count, bool)
        and reported_unknown_count > unknown_activity_count
    ):
        unknown_activity_count = reported_unknown_count

    total_budget = state["total_budget"]
    nights = state["nights"]

    result = budget_agent(
        flight_cost=flight_cost,
        hotel_price_per_night=hotel_price,
        nights=nights,
        activity_cost=activity_cost,
        total_budget=total_budget,
        flight_budget=total_budget * 0.45,
        accommodation_budget=total_budget * 0.35,
        activity_budget=total_budget * 0.20,
        unknown_activity_count=unknown_activity_count,
        unverified_activity_count=unverified_activity_count,
    )

    activity_unavailable = (
         state.get("activity_data_status") == "unavailable"
    )

    if activity_unavailable:
        result["budget_estimate_status"] = "Incomplete estimate"

    result["budget_recommendation"] += (
        "\n\nActivity discovery was unavailable. "
        "Activity expenses are excluded from this estimate. "
        "The final trip cost may be higher."
    )

    return {
        "budget_breakdown": result["budget_breakdown"],
        "budget_status": result["budget_status"],
        "budget_estimate_status": result["budget_estimate_status"],
        "remaining_balance": result["remaining_balance"],
        "budget_recommendation": result["budget_recommendation"],
        "category_analysis": result["category_analysis"],
        "reallocation_analysis": result["reallocation_analysis"],
        "savings_suggestions": result["savings_suggestions"],
        "unknown_activity_count": result["unknown_activity_count"],
        "unverified_activity_count": result["unverified_activity_count"],
    }


def weather_node(state):
    result = weather_agent(
        destination=state["destination"],
        start_date=state["check_in"],
        end_date=state["check_out"],
    )

    return {
        "weather": result["daily_weather"],
        "weather_recommendation": result["recommendation"],
    }


def itinerary_node(state):
    result = itinerary_agent(
        origin=state["origin"],
        destination=state["destination"],
        date=state["date"],
        check_in=state["check_in"],
        check_out=state["check_out"],
        travelers=state["travelers"],
        selected_flight=state["selected_flight"],
        selected_stay=state["selected_stay"],
        optimized_activities=state["optimized_activities"],
        optimized_route=state["optimized_route"],
        budget_breakdown=state["budget_breakdown"],
        weather=state["weather"],
        activity_data_status=state.get(
            "activity_data_status", "unknown"
        ),
    )

    return {
        "final_itinerary": result["final_itinerary"]
    }


builder = StateGraph(TripState)

builder.add_node("flight_agent", flight_node)
builder.add_node("stay_agent", stay_node)
builder.add_node("activity_agent", activity_node)
builder.add_node("route_agent", route_node)
builder.add_node("budget_agent", budget_node)
builder.add_node("weather_agent", weather_node)
builder.add_node("itinerary_agent", itinerary_node)

builder.add_edge(START, "flight_agent")
builder.add_edge("flight_agent", "stay_agent")
builder.add_edge("stay_agent", "activity_agent")
builder.add_edge("activity_agent", "route_agent")
builder.add_edge("route_agent", "budget_agent")
builder.add_edge("budget_agent", "weather_agent")
builder.add_edge("weather_agent", "itinerary_agent")
builder.add_edge("itinerary_agent", END)

trip_graph = builder.compile()


def create_trip_request():
    return {
        "origin": "Delhi",
        "destination": "Mumbai",
        "start_date": "2026-10-10",
        "end_date": "2026-10-15",
        "travelers": 2,
        "total_budget": 40000,
        "interests": ["sightseeing", "history"],
    }


if __name__ == "__main__":
    print(
        "TripMind graph is ready. "
        "Run it through the /plan-trip API endpoint."
    )

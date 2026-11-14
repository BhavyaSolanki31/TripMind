
import os
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models.trip import TripRequest
from orchestrator.trip_graph import trip_graph


logger = logging.getLogger("uvicorn.error")


app = FastAPI(
    title="TripMind API",
    description="Multi-Agent AI Travel Planner",
    version="1.2.0",
)


# CORS configuration.
_default_origins = "http://localhost:3000,http://127.0.0.1:3000"

_allowed_origins = [
    origin.strip().rstrip("/")
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        _default_origins,
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Welcome to TripMind API 🚀",
        "status": "running",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/plan-trip")
def plan_trip(request: TripRequest):
    """
    Create a trip plan using multiple specialized agents.

    Budget allocation:
    - 45% flights
    - 35% accommodation
    - 20% activities

    Flight and accommodation prices use mock estimates.
    Activity prices may be known, unknown, or unverified.
    """

    nights = (request.end_date - request.start_date).days

    if nights <= 0:
        raise HTTPException(
            status_code=400,
            detail="End date must be after start date.",
        )

    if nights > 30:
        raise HTTPException(
            status_code=400,
            detail=(
                "Trips can be up to 30 nights long. "
                "Please choose an earlier return date."
            ),
        )

    # Calculate budget allocations.
    total_budget = request.total_budget

    flight_budget = int(total_budget * 0.45)

    stay_total_budget = total_budget * 0.35

    stay_budget_per_night = max(
        1,
        int(stay_total_budget / nights),
    )

    activity_budget = int(total_budget * 0.20)

    # Initialize LangGraph state.
    initial_state = {
        "origin": request.origin,
        "destination": request.destination,
        "date": request.start_date.isoformat(),

        "flight_budget": flight_budget,
        "flights": [],
        "selected_flight": {},
        "flight_recommendation": "",

        "check_in": request.start_date.isoformat(),
        "check_out": request.end_date.isoformat(),
        "travelers": request.travelers,

        "stay_budget": stay_budget_per_night,
        "stays": [],
        "selected_stay": {},
        "stay_recommendation": "",

        "interests": request.interests,
        "activity_budget": activity_budget,
        "activities": [],
        "selected_activities": [],
        "activity_recommendation": "",

        "activity_data_status": "unknown",
        "activity_source": "unknown",
        "unknown_activity_count": 0,
        "unverified_activity_count": 0,

        "total_budget": total_budget,
        "nights": nights,

        "budget_breakdown": {},
        "budget_status": "",
        "budget_estimate_status": "",
        "remaining_balance": 0,
        "budget_recommendation": "",
        "category_analysis": {},
        "reallocation_analysis": {},
        "savings_suggestions": [],

        "optimized_activities": [],
        "optimized_route": [],
        "total_route_distance_km": 0.0,
        "route_recommendation": "",
        "route_distance_type": "straight-line estimate",
        "special_transport": [],

        "weather": [],
        "weather_recommendation": "",

        "final_itinerary": {},
    }

    # Execute the multi-agent workflow.
    try:
        result = trip_graph.invoke(initial_state)

    except Exception as exc:
        logger.exception(
            "Trip planning failed: %s",
            exc,
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Trip planning failed. "
                "Check the backend logs for details."
            ),
        ) from exc

    # Activity price metadata.
    unknown_activity_count = result.get(
        "unknown_activity_count", 0
    )

    unverified_activity_count = result.get(
        "unverified_activity_count", 0
    )

    activity_data_status = result.get(
        "activity_data_status", "unknown"
    )

    activity_source = result.get(
        "activity_source", "unknown"
    )

    # Return the completed trip plan.
    return {
        "selected_flight": result["selected_flight"],

        "selected_stay": result["selected_stay"],

        "selected_activities": result["selected_activities"],

        "activity_data_status": activity_data_status,

        "activity_source": activity_source,

        "unknown_activity_count": unknown_activity_count,

        "unverified_activity_count": unverified_activity_count,

        "optimized_route": result["optimized_route"],

        "total_route_distance_km": (
            result["total_route_distance_km"]
        ),

        "route_recommendation": (
            result["route_recommendation"]
        ),

        "route_distance_type": result.get(
            "route_distance_type",
            "straight-line estimate",
        ),

        "special_transport": result.get(
            "special_transport",
            [],
        ),

        # Budget information.
        "budget": result["budget_breakdown"],

        "budget_status": result.get(
            "budget_status",
            "Unavailable",
        ),

        "budget_estimate_status": result.get(
            "budget_estimate_status",
            "Unavailable",
        ),

        "remaining_balance": result.get(
            "remaining_balance",
        ),

        "budget_analysis": result["budget_recommendation"],

        "category_analysis": result.get(
            "category_analysis", {}
        ),

        "reallocation_analysis": result.get(
            "reallocation_analysis", {}
        ),

        "savings_suggestions": result.get(
            "savings_suggestions", []
        ),

        "budget_allocation": {
            "flight_budget": flight_budget,
            "stay_budget_per_night": stay_budget_per_night,
            "activity_budget": activity_budget,
            "policy": (
                "45% flights, 35% accommodation, "
                "20% activities"
            ),
        },

        "data_notice": (
            "Flight and accommodation listings currently use "
            "mock data; prices are illustrative estimates, "
            "not live availability or quotes. Activity prices "
            "may be unknown or unverified."
        ),

        "weather": result["weather"],

        "weather_recommendation": (
            result["weather_recommendation"]
        ),

        "itinerary": result["final_itinerary"],
    }

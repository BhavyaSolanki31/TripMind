import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models.trip import TripRequest
from orchestrator.trip_graph import trip_graph

app = FastAPI(
    title="TripMind API",
    description="Multi-Agent AI Travel Planner",
    version="1.1.0",
)

# Set ALLOWED_ORIGINS in the deployment environment to a comma-separated list
# of trusted frontend origins, for example:
# ALLOWED_ORIGINS=https://tripmind.example.com,https://www.tripmind.example.com
_default_origins = "http://localhost:3000,http://127.0.0.1:3000"
_allowed_origins = [
    origin.strip().rstrip("/")
    for origin in os.getenv("ALLOWED_ORIGINS", _default_origins).split(",")
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
    return {"message": "Welcome to TripMind API 🚀", "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/plan-trip")
def plan_trip(request: TripRequest):
    """Create a trip plan using budget allocations derived from the user's budget.

    Allocation policy: 45% flight, 35% accommodation, 20% activities.
    Flight and stay prices are currently mock estimates, not live quotes.
    """
    nights = (request.end_date - request.start_date).days
    if nights <= 0:
        raise HTTPException(
            status_code=400,
            detail="End date must be after start date.",
        )

    total_budget = request.total_budget
    flight_budget = int(total_budget * 0.45)
    stay_total_budget = total_budget * 0.35
    stay_budget_per_night = max(1, int(stay_total_budget / nights))
    activity_budget = int(total_budget * 0.20)

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
        "total_budget": total_budget,
        "nights": nights,
        "budget_breakdown": {},
        "budget_recommendation": "",
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

    try:
        result = trip_graph.invoke(initial_state)
    except Exception as exc:
        # Keep internal stack traces out of the public API response.
        raise HTTPException(
            status_code=500,
            detail="Trip planning failed. Check that the backend services and API configuration are available, then try again.",
        ) from exc

    return {
        "selected_flight": result["selected_flight"],
        "selected_stay": result["selected_stay"],
        "selected_activities": result["selected_activities"],
        "optimized_route": result["optimized_route"],
        "total_route_distance_km": result["total_route_distance_km"],
        "route_recommendation": result["route_recommendation"],
        "route_distance_type": result.get("route_distance_type", "straight-line estimate"),
        "special_transport": result.get("special_transport", []),
        "budget": result["budget_breakdown"],
        "budget_analysis": result["budget_recommendation"],
        "budget_allocation": {
            "flight_budget": flight_budget,
            "stay_budget_per_night": stay_budget_per_night,
            "activity_budget": activity_budget,
            "policy": "45% flights, 35% accommodation, 20% activities",
        },
        "data_notice": "Flight and accommodation listings currently use mock data; prices are illustrative estimates, not live availability or quotes.",
        "weather": result["weather"],
        "weather_recommendation": result["weather_recommendation"],
        "itinerary": result["final_itinerary"],
    }

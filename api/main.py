from fastapi import FastAPI, HTTPException
from models.trip import TripRequest
from orchestrator.trip_graph import trip_graph
from datetime import date
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI(
    title="TripMind API",
    description="Multi-Agent AI Travel Planner",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "message": "Welcome to TripMind API 🚀"
    }


@app.post("/plan-trip")
def plan_trip(request: TripRequest):

    start_date = request.start_date
    end_date = request.end_date

    nights = (end_date - start_date).days

    if nights <= 0:
        raise HTTPException(
            status_code=400,
            detail="End date must be after start date."
        )

    result = trip_graph.invoke({
        "origin": request.origin,
        "destination": request.destination,
        "date": request.start_date.isoformat(),

        "flight_budget": 20000,
        "flights": [],
        "selected_flight": {},
        "flight_recommendation": "",

        "check_in": request.start_date.isoformat(),
        "check_out": request.end_date.isoformat(),
        "travelers": request.travelers,
        "stay_budget": 3000,
        "stays": [],
        "selected_stay": {},
        "stay_recommendation": "",

        "interests": request.interests,
        "activity_budget": 1500,
        "activities": [],
        "selected_activities": [],
        "activity_recommendation": "",

        "total_budget": request.total_budget,
        "nights": nights,
        "budget_breakdown": {},
        "budget_recommendation": "",

        "final_itinerary": ""
    })

    
    return {
        "selected_flight": result["selected_flight"],
        "selected_stay": result["selected_stay"],
        "selected_activities": result["selected_activities"],

        "optimized_route": result["optimized_route"],
        "total_route_distance_km": result["total_route_distance_km"],
        "route_recommendation": result["route_recommendation"],
        "route_distance_type": result.get(
            "route_distance_type",
            "straight-line estimate"
        ),
        "special_transport": result.get("special_transport", []),

        "budget": result["budget_breakdown"],
        "budget_analysis": result["budget_recommendation"],

        "weather": result["weather"],
        "weather_recommendation": result["weather_recommendation"],

        "itinerary": result["final_itinerary"]
    }

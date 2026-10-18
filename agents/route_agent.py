from tools.route_optimizer import optimize_route
from models.llm import ask_ai


def route_agent(activities):

    """
    Route Agent:
    Optimizes activity order and generates route explanation.
    """


    result = optimize_route(
        activities
    )


    optimized_activities = result["optimized_activities"]

    optimized_route = result["route"]

    total_distance = result["total_distance_km"]



    prompt = f"""

You are TripMind's Route Optimization Agent.

Optimized Route:

{optimized_route}


Total Distance:

{total_distance} km


Explain why this route is practical and efficient.

"""


    try:

        recommendation = (
    f"The optimized route covers "
    f"{len(optimized_route)} locations "
    f"with a total distance of "
    f"{total_distance} km."
)


    except Exception as e:

        print(
            f"⚠️ AI route recommendation failed: {e}"
        )

        recommendation = (
            f"This optimized route covers "
            f"{len(optimized_route)} locations "
            f"with a total travel distance of "
            f"{total_distance} km."
        )



    return {

        "optimized_activities":
            optimized_activities,


        "route":
            optimized_route,


        "total_distance_km":
            total_distance,


        "recommendation":
            recommendation

    }
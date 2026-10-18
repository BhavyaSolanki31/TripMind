import json
from datetime import datetime, timedelta

from models.llm import ask_ai_json
USE_AI = False



def normalize_activity(activity, destination):

    """
    Converts any Gemini activity format into standard format.
    """

    # Gemini returned string
    if isinstance(activity, str):

        return {
            "time": "Morning",
            "title": activity,
            "description": f"Explore {activity} in {destination}.",
            "location": activity,
            "cost": 0
        }


    # Gemini returned dictionary

    if isinstance(activity, dict):

        title = (
            activity.get("title")
            or activity.get("name")
            or activity.get("activity")
            or "Activity"
        )


        return {

            "time":
                activity.get(
                    "time",
                    "Morning"
                ),


            "title":
                title,


            "description":
                activity.get(
                    "description",
                    activity.get(
                        "details",
                        f"Explore {title} in {destination}."
                    )
                ),


            "location":
                activity.get(
                    "location",
                    title
                ),


            "cost":
                activity.get(
                    "cost",
                    activity.get(
                        "price",
                        0
                    )
                )
        }


    return {
        "time":"Morning",
        "title":"Activity",
        "description":"Explore destination.",
        "location":destination,
        "cost":0
    }




def create_fallback_itinerary(
        origin,
        destination,
        check_in,
        check_out,
        selected_flight,
        selected_stay,
        optimized_activities,
        weather
):


    days=[]


    start=datetime.strptime(
        check_in,
        "%Y-%m-%d"
    )


    end=datetime.strptime(
        check_out,
        "%Y-%m-%d"
    )


    dates=[]

    current=start

    while current<=end:

        dates.append(
            current.strftime("%Y-%m-%d")
        )

        current+=timedelta(days=1)



    # weather map

    weather_map={}


    if isinstance(weather,list):

        for w in weather:

            weather_map[w["date"]]=w


    elif isinstance(weather,dict):

        weather_map[
            weather["date"]
        ]=weather



    activity_index=0



    for index,date in enumerate(dates):


        activities=[]


        daily_weather=weather_map.get(
            date,
            {
                "temperature":0,
                "condition":"Unknown",
                "rain_probability":0,
                "wind":"Unknown"
            }
        )



        # arrival day

        if index==0:


            activities.append(
                {
                    "time":"Morning",
                    "title":
                    f"Flight from {origin} to {destination}",

                    "description":
                    f"Travel via {selected_flight.get('airline','Flight')}.",

                    "location":
                    f"{origin} Airport → {destination} Airport",

                    "cost":
                    selected_flight.get(
                        "price",
                        0
                    )
                }
            )


            activities.append(
                {
                    "time":"Afternoon",
                    "title":"Hotel Check-in",

                    "description":
                    f"Check-in at {selected_stay.get('name','Hotel')}.",

                    "location":
                    selected_stay.get(
                        "location",
                        destination
                    ),

                    "cost":0
                }
            )



        # checkout day

        elif index==len(dates)-1:


            activities.append(
                {
                    "time":"Morning",

                    "title":"Hotel Check-out",

                    "description":
                    f"Check out from {selected_stay.get('name','Hotel')}.",

                    "location":
                    selected_stay.get(
                        "location",
                        destination
                    ),

                    "cost":0
                }
            )



        # sightseeing days

        elif activity_index < len(optimized_activities):


            activities.append(
                normalize_activity(
                    optimized_activities[activity_index],
                    destination
                )
            )


            activity_index+=1



        else:


            activities.append(
                {
                    "time":"Free Time",

                    "title":"Leisure Time",

                    "description":
                    "Relax and explore nearby areas.",

                    "location":
                    destination,

                    "cost":0
                }
            )



        days.append(
            {
                "day":index+1,

                "date":date,

                "title":
                f"Day {index+1} in {destination}",

                "weather":
                daily_weather,

                "activities":
                activities
            }
        )



    return {

        "trip_title":
        f"{destination} Trip",


        "summary":
        f"{len(dates)} days and {len(dates)-1} nights trip from {origin} to {destination}.",


        "days":
        days

    }





def itinerary_agent(
    origin,
    destination,
    date,
    check_in,
    check_out,
    travelers,
    selected_flight,
    selected_stay,
    optimized_activities,
    optimized_route,
    budget_breakdown,
    weather
):


    prompt=f"""

You are TripMind Final Itinerary Agent.

Create a realistic travel itinerary.

Rules:

- Exactly 6 days
- First day only flight + hotel check-in
- Last day only hotel checkout
- Use provided activities only
- Follow route order
- Never create new places
- Every day requires weather
- Return ONLY JSON


Destination:
{destination}


Activities:
{optimized_activities}


Route:
{optimized_route}


Weather:
{weather}


Return:

{{
"trip_title":"",
"summary":"",
"days":[]
}}

"""


    try:

        if not USE_AI:

           raise Exception(
        "AI disabled for testing"
    )
        response=ask_ai_json(prompt)


        if not response:

            raise Exception(
                "Empty Gemini response"
            )


        itinerary=json.loads(response)



        if "days" not in itinerary:

            raise Exception(
                "Missing days"
            )



        # normalize days


        for day in itinerary["days"]:


            if "activities" not in day:

                day["activities"]=day.get(
                    "schedule",
                    []
                )


            day["activities"]=[

                normalize_activity(
                    a,
                    destination
                )

                for a in day["activities"]

            ]



        return {

            "final_itinerary":
            itinerary

        }



    except Exception as e:


        print(
            "⚠️ Using fallback itinerary"
        )

        print(e)



        return {

            "final_itinerary":
            create_fallback_itinerary(
                origin,
                destination,
                check_in,
                check_out,
                selected_flight,
                selected_stay,
                optimized_activities,
                weather
            )

        }
# agents/activity_agent.py

"""
TripMind Activity Agent

Responsible for:
- Finding destination activities
- Filtering according to user interests
- Returning structured activity data
"""


def activity_agent(
    destination,
    interests=None,
    budget=None
):
    """
    Activity Agent:
    Generates travel activities based on destination and interests.
    """


    # -----------------------------
    # Default interests handling
    # -----------------------------

    if interests is None:
        interests = []


    interests = [
        item.lower()
        for item in interests
    ]



    # -----------------------------
    # Destination database
    # -----------------------------

    activity_database = {


        "mumbai": [

            {
                "name": "Gateway of India",
                "category": "Historical",
                "price": 0,
                "duration": "2 hours",
                "latitude": 18.9220,
                "longitude": 72.8347
            },


            {
                "name": "Marine Drive",
                "category": "Nature",
                "price": 0,
                "duration": "2 hours",
                "latitude": 18.9431,
                "longitude": 72.8238
            },


            {
                "name": "Elephanta Caves",
                "category": "History",
                "price": 600,
                "duration": "4 hours",
                "latitude": 18.9633,
                "longitude": 72.9315
            },


            {
                "name": "Colaba Causeway",
                "category": "Shopping",
                "price": 1000,
                "duration": "2 hours",
                "latitude": 18.9150,
                "longitude": 72.8317
            },


            {
                "name": "Mumbai Street Food Tour",
                "category": "Food",
                "price": 800,
                "duration": "3 hours",
                "latitude": 18.9435,
                "longitude": 72.8248
            },


            {
                "name": "Chhatrapati Shivaji Maharaj Terminus",
                "category": "Historical",
                "price": 0,
                "duration": "1 hour",
                "latitude": 18.9402,
                "longitude": 72.8355
            },


            {
                "name": "Juhu Beach",
                "category": "Nature",
                "price": 0,
                "duration": "2 hours",
                "latitude": 19.0988,
                "longitude": 72.8267
            },


            {
                "name": "Sanjay Gandhi National Park",
                "category": "Adventure",
                "price": 100,
                "duration": "4 hours",
                "latitude": 19.2147,
                "longitude": 72.9106
            }

        ]

    }



    # -----------------------------
    # Get destination activities
    # -----------------------------


    activities = activity_database.get(
        destination.lower(),
        []
    )



    # -----------------------------
    # Interest based filtering
    # -----------------------------


    selected = []


    for activity in activities:


        category = activity["category"].lower()


        matched = False


        for interest in interests:


            if (
                interest in category
                or category in interest
            ):
                matched = True



        if matched:

            selected.append(activity)



    # -----------------------------
    # If no interest match
    # return popular places
    # -----------------------------


    if len(selected) < 5:

        for activity in activities:

            if activity not in selected:

                selected.append(activity)



    # -----------------------------
    # Budget filtering
    # -----------------------------


    if budget:


        affordable = []


        for activity in selected:

            if activity["price"] <= budget:

                affordable.append(activity)



        if affordable:

            selected = affordable



    # -----------------------------
    # Return top activities
    # -----------------------------

    return selected[:6]



# -----------------------------
# Testing
# -----------------------------

if __name__ == "__main__":


    result = activity_agent(

        destination="Mumbai",

        interests=[
            "historical places",
            "beaches",
            "food",
            "shopping"
        ],

        budget=50000

    )


    for item in result:

        print(item)
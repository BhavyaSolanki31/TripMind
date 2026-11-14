
"""
TripMind Dynamic Activity Agent

Discovers destination activities using OpenStreetMap.
No manually maintained destination database or paid API key.

Public data providers:
- Nominatim: destination geocoding
- Overpass API: nearby points of interest

Unknown admission prices are never represented as free.
"""

import re
import time
import requests

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

USER_AGENT = "TripMind/1.0 (travel discovery application)"

GEOCODING_TIMEOUT = 20
OVERPASS_TIMEOUT = 35
OVERPASS_QUERY_TIMEOUT = 25
SEARCH_RADIUS_METERS = 5000
MAX_RESULTS = 30
MAX_SELECTED = 10

# Respect public geocoding service usage limits.
_last_geocoding_request = 0.0

INTEREST_CATEGORY_MAP = {
    "sightseeing": {
        "sightseeing", "historical", "history",
        "culture", "nature", "adventure"
    },
    "history": {"historical", "history", "culture"},
    "historical": {"historical", "history", "culture"},
    "historical places": {"historical", "history", "culture"},
    "culture": {"historical", "history", "culture"},
    "food": {"food"},
    "street food": {"food"},
    "food tours": {"food"},
    "shopping": {"shopping"},
    "nature": {"nature"},
    "beach": {"nature"},
    "beaches": {"nature"},
    "outdoors": {"nature", "adventure"},
    "adventure": {"adventure"},
}


def _geocode_destination(destination):
    """Resolve a destination to geographic coordinates."""

    global _last_geocoding_request

    wait = 1.0 - (time.monotonic() - _last_geocoding_request)

    if wait > 0:
        time.sleep(wait)

    response = requests.get(
        NOMINATIM_URL,
        params={
            "q": destination,
            "format": "jsonv2",
            "limit": 1,
        },
        headers={"User-Agent": USER_AGENT},
        timeout=GEOCODING_TIMEOUT,
    )

    _last_geocoding_request = time.monotonic()
    response.raise_for_status()

    results = response.json()

    if not results:
        raise ValueError(
            f"Could not identify destination: {destination}"
        )

    place = results[0]

    return {
        "latitude": float(place["lat"]),
        "longitude": float(place["lon"]),
        "display_name": place.get("display_name", destination),
    }


def _build_overpass_query(latitude, longitude):
    """Build a smaller, named-POI query to reduce Overpass server load."""

    radius = SEARCH_RADIUS_METERS

    return f"""
    [out:json][timeout:{OVERPASS_QUERY_TIMEOUT}];
    (
      node["name"]["tourism"~"attraction|museum|gallery|viewpoint"](around:{radius},{latitude},{longitude});
      way["name"]["tourism"~"attraction|museum|gallery|viewpoint"](around:{radius},{latitude},{longitude});

      node["name"]["historic"](around:{radius},{latitude},{longitude});
      way["name"]["historic"](around:{radius},{latitude},{longitude});

      node["name"]["leisure"~"park|garden|nature_reserve"](around:{radius},{latitude},{longitude});
      way["name"]["leisure"~"park|garden|nature_reserve"](around:{radius},{latitude},{longitude});

      node["name"]["amenity"~"restaurant|cafe|marketplace"](around:{radius},{latitude},{longitude});
      way["name"]["amenity"~"restaurant|cafe|marketplace"](around:{radius},{latitude},{longitude});

      node["name"]["shop"](around:{radius},{latitude},{longitude});
    );
    out center tags;
    """


def _classify_activity(tags):
    """Map OpenStreetMap tags to TripMind categories."""

    tourism = tags.get("tourism", "").lower()
    historic = tags.get("historic", "").lower()
    leisure = tags.get("leisure", "").lower()
    amenity = tags.get("amenity", "").lower()
    shop = tags.get("shop", "").lower()

    if historic:
        return "Historical"

    if tourism == "museum":
        return "History"

    if tourism in {"attraction", "gallery"}:
        return "Sightseeing"

    if tourism == "viewpoint":
        return "Nature"

    if leisure in {"park", "garden", "nature_reserve"}:
        return "Nature"

    if amenity in {"restaurant", "cafe"}:
        return "Food"

    if amenity == "marketplace":
        return "Shopping"

    if shop:
        return "Shopping"

    return "Sightseeing"


def _extract_price(tags):
    """
    Return price and price status.

    Only explicit free/no-fee tags establish a free activity.
    """

    fee = str(tags.get("fee", "")).strip().lower()

    if fee == "no":
        return 0, "free"

    raw_price = tags.get("charge")

    if raw_price:
        match = re.search(r"\d+(?:\.\d+)?", str(raw_price))

        if match:
            try:
                return float(match.group()), "unverified"
            except ValueError:
                pass

    return None, "unknown"


def _extract_coordinates(element):
    """Extract coordinates from OSM nodes or centered ways."""

    if "lat" in element and "lon" in element:
        return float(element["lat"]), float(element["lon"])

    center = element.get("center", {})

    if "lat" in center and "lon" in center:
        return float(center["lat"]), float(center["lon"])

    return None, None


def _fetch_activities(latitude, longitude):
    """Fetch named POIs, trying each public Overpass endpoint in turn."""

    query = _build_overpass_query(latitude, longitude)
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }

    errors = []

    for endpoint in OVERPASS_URLS:
        try:
            response = requests.post(
                endpoint,
                data={"data": query},
                headers=headers,
                timeout=OVERPASS_TIMEOUT,
            )
            response.raise_for_status()

            data = response.json()
            if not isinstance(data, dict):
                raise ValueError("Overpass returned an unexpected response.")

            elements = data.get("elements", [])
            if not isinstance(elements, list):
                raise ValueError("Overpass response did not contain an elements list.")

            return elements

        except (requests.RequestException, ValueError) as exc:
            errors.append(f"{endpoint}: {exc}")

    details = " | ".join(errors) if errors else "No endpoints configured"
    raise RuntimeError(
        "All Overpass endpoints failed. This is usually a temporary "
        f"upstream availability issue. Details: {details}"
    )


def _normalize_activities(elements):
    """Convert OpenStreetMap results to TripMind's activity format."""

    activities = []
    seen = set()

    for element in elements:
        tags = element.get("tags", {})
        name = tags.get("name")

        if not name:
            continue

        latitude, longitude = _extract_coordinates(element)

        if latitude is None or longitude is None:
            continue

        identity = name.strip().lower()

        if identity in seen:
            continue

        seen.add(identity)

        price, price_status = _extract_price(tags)

        category = _classify_activity(tags)

        activities.append({
            "name": name,
            "category": category,
            "price": price,
            "price_status": price_status,
            "cost": price,
            "duration": "Duration varies",
            "latitude": latitude,
            "longitude": longitude,
            "source": "OpenStreetMap",
            "source_url": (
                f"https://www.openstreetmap.org/"
                f"{element.get('type')}/{element.get('id')}"
            ),
        })

    return activities


def _matches_interests(activity, interests):
    """Match normalized activity categories to user interests."""

    if not interests:
        return True

    desired_categories = set()

    for interest in interests:
        normalized = str(interest).strip().lower()

        desired_categories.update(
            INTEREST_CATEGORY_MAP.get(
                normalized,
                {normalized},
            )
        )

    category = activity["category"].lower()

    return category in desired_categories


def activity_agent(destination, interests=None, budget=None):
    """
    Dynamically discover affordable, interest-matched activities.

    Unknown admission prices are retained but never treated as free.
    """

    if not destination or not str(destination).strip():
        raise ValueError("A destination is required.")

    if isinstance(interests, str):
        interests = [interests]

    interests = [
        str(item).strip()
        for item in (interests or [])
        if str(item).strip()
    ]

    activity_budget = None

    if budget is not None:
        if isinstance(budget, bool):
            raise ValueError("Activity budget must be a valid number.")

        try:
            activity_budget = float(budget)
        except (TypeError, ValueError):
            raise ValueError("Activity budget must be a valid number.")

        if activity_budget < 0:
            raise ValueError("Activity budget cannot be negative.")

    try:
        location = _geocode_destination(str(destination).strip())

        elements = _fetch_activities(
            location["latitude"],
            location["longitude"],
        )

        available_activities = _normalize_activities(elements)

    except (requests.RequestException, RuntimeError, ValueError) as exc:
        return {
            "available_activities": [],
            "selected_activities": [],
            "recommendation": (
                f"Live activity discovery is temporarily unavailable "
                f"for {destination}: {exc}"
            ),
            "activity_data_status": "unavailable",
            "activity_source": "OpenStreetMap",
            "unknown_price_count": 0,
            "unverified_price_count": 0,
        }

    matching_activities = [
        activity
        for activity in available_activities
        if _matches_interests(activity, interests)
    ]

    # Only known numeric prices are compared with the budget.
    # Unknown prices are retained but clearly identified.
    if activity_budget is not None:
        matching_activities = [
            activity
            for activity in matching_activities
            if activity["price"] is None
            or activity["price"] <= activity_budget
        ]

    selected_activities = matching_activities[:MAX_SELECTED]

    unknown_price_count = sum(
        activity["price_status"] == "unknown"
        for activity in selected_activities
    )
    unverified_price_count = sum(
        activity["price_status"] == "unverified"
        for activity in selected_activities
    )

    if not available_activities:
        recommendation = (
            f"No named attractions were found near {destination}. "
            "This may reflect incomplete OpenStreetMap coverage."
        )

    elif not selected_activities:
        recommendation = (
            f"No activities matched the selected interests "
            f"and budget for {destination}."
        )

    else:
        recommendation = (
            f"Discovered {len(selected_activities)} activities near "
            f"{destination} using OpenStreetMap."
        )

        if unknown_price_count:
            recommendation += (
                f" Admission prices are unknown for "
                f"{unknown_price_count} selected activities."
            )

    return {
        "available_activities": available_activities[:MAX_RESULTS],
        "selected_activities": selected_activities,
        "recommendation": recommendation,
        "activity_data_status": "available",
        "activity_source": "OpenStreetMap",
        "unknown_price_count": unknown_price_count,
        "unverified_price_count": unverified_price_count,
        "destination_coordinates": {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
        },
    }


if __name__ == "__main__":
    result = activity_agent(
        destination="Jaipur",
        interests=["History", "Sightseeing", "Food"],
        budget=10000,
    )

    print("\nRecommendation:")
    print(result["recommendation"])

    print("\nSelected activities:")

    for activity in result["selected_activities"]:
        print(
            activity["name"],
            "|",
            activity["category"],
            "|",
            activity["price_status"],
            "|",
            activity["price"],
        )

import pytest
from datetime import date, timedelta

from tools.weather_search import search_weather


def test_past_date_returns_unavailable_weather():
    past_date = (date.today() - timedelta(days=1)).isoformat()

    result = search_weather("Mumbai", past_date)

    assert result["status"] == "unavailable"
    assert result["temperature"] is None


def test_date_beyond_forecast_window_returns_unavailable_weather():
    future_date = (date.today() + timedelta(days=30)).isoformat()

    result = search_weather("Mumbai", future_date)

    assert result["status"] == "unavailable"
    assert result["temperature"] is None


def test_invalid_date_returns_unavailable_weather():
    result = search_weather("Mumbai", "not-a-date")

    assert result["status"] == "unavailable"
    assert result["temperature"] is None

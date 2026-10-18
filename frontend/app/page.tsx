"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";

export default function Home() {
  const [origin, setOrigin] = useState("");
  const [destination, setDestination] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [travelers, setTravelers] = useState(2);
  const [budget, setBudget] = useState("");
  const [interests, setInterests] = useState<string[]>([]);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const availableInterests = [
    "Sightseeing",
    "History",
    "Food",
    "Shopping",
    "Nature",
    "Adventure",
  ];

  const toggleInterest = (interest: string) => {
    setInterests((current) =>
      current.includes(interest)
        ? current.filter((item) => item !== interest)
        : [...current, interest]
    );
  };

  const planTrip = async () => {
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/plan-trip", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          origin,
          destination,
          start_date: startDate,
          end_date: endDate,
          travelers,
          total_budget: Number(budget),
          interests: interests.map((item) => item.toLowerCase()),
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to generate trip plan");
      }

      const data = await response.json();

      setResult(data);
    } catch (error) {
      console.error(error);
      alert("Something went wrong while planning the trip.");
    } finally {
      setLoading(false);
    }
  };

  const getWeatherIcon = (condition: string, rainProbability: number) => {
    const weather = condition?.toLowerCase() || "";

    if (rainProbability >= 50) {
      return "🌧️";
    }

    if (weather.includes("cloud")) {
      return "⛅";
    }

    if (weather.includes("rain")) {
      return "🌧️";
    }

    if (weather.includes("clear")) {
      return "🌤️";
    }

    if (weather.includes("sun")) {
      return "☀️";
    }

    return "🌤️";
  };

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      {/* Navbar */}
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-6">
        <div className="text-2xl font-bold">✈️ TripMind</div>

        <div className="flex gap-6 text-sm text-slate-300">
          <span className="cursor-pointer hover:text-white">About</span>

          <span className="cursor-pointer hover:text-white">GitHub</span>
        </div>
      </nav>

      {/* Hero */}
      <section className="mx-auto max-w-4xl px-6 pb-12 pt-16 text-center">
        <p className="mb-4 text-sm font-medium uppercase tracking-[0.3em] text-blue-400">
          Multi-Agent AI Travel Planner
        </p>

        <h1 className="text-5xl font-bold leading-tight md:text-6xl">
          Plan your perfect trip
          <span className="block text-blue-400">with AI.</span>
        </h1>

        <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-400">
          TripMind combines intelligent travel agents to plan flights, stays,
          activities, budgets, weather, and your complete itinerary.
        </p>
      </section>

      {/* Trip Form */}
      <section className="mx-auto max-w-4xl px-6 pb-20">
        <div className="rounded-3xl border border-slate-800 bg-slate-900 p-8 shadow-2xl">
          <div className="grid gap-6 md:grid-cols-2">
            {/* Origin */}
            <div>
              <label className="mb-2 block text-sm text-slate-400">
                From
              </label>

              <input
                value={origin}
                onChange={(e) => setOrigin(e.target.value)}
                placeholder="Delhi"
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 outline-none transition focus:border-blue-500"
              />
            </div>

            {/* Destination */}
            <div>
              <label className="mb-2 block text-sm text-slate-400">
                To
              </label>

              <input
                value={destination}
                onChange={(e) => setDestination(e.target.value)}
                placeholder="Mumbai"
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 outline-none transition focus:border-blue-500"
              />
            </div>

            {/* Start Date */}
            <div>
              <label className="mb-2 block text-sm text-slate-400">
                Start Date
              </label>

              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 outline-none focus:border-blue-500"
              />
            </div>

            {/* End Date */}
            <div>
              <label className="mb-2 block text-sm text-slate-400">
                End Date
              </label>

              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 outline-none focus:border-blue-500"
              />
            </div>

            {/* Travelers */}
            <div>
              <label className="mb-2 block text-sm text-slate-400">
                Travelers
              </label>

              <input
                type="number"
                min="1"
                value={travelers}
                onChange={(e) => setTravelers(Number(e.target.value))}
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 outline-none focus:border-blue-500"
              />
            </div>

            {/* Budget */}
            <div>
              <label className="mb-2 block text-sm text-slate-400">
                Total Budget (₹)
              </label>

              <input
                type="number"
                value={budget}
                onChange={(e) => setBudget(e.target.value)}
                placeholder="40000"
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 outline-none focus:border-blue-500"
              />
            </div>
          </div>

          {/* Interests */}
          <div className="mt-8">
            <label className="mb-3 block text-sm text-slate-400">
              What are you interested in?
            </label>

            <div className="flex flex-wrap gap-3">
              {availableInterests.map((interest) => (
                <button
                  key={interest}
                  onClick={() => toggleInterest(interest)}
                  className={`rounded-full border px-4 py-2 text-sm transition ${
                    interests.includes(interest)
                      ? "border-blue-500 bg-blue-500 text-white"
                      : "border-slate-700 bg-slate-950 text-slate-300 hover:border-slate-500"
                  }`}
                >
                  {interest}
                </button>
              ))}
            </div>
          </div>

          {/* Button */}
          <button
            onClick={planTrip}
            disabled={loading}
            className="mt-8 w-full rounded-xl bg-blue-500 px-6 py-4 text-lg font-semibold transition hover:bg-blue-400 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? "🧠 Planning your trip..." : "✨ Plan My Trip"}
          </button>
        </div>
      </section>

      {/* Results */}
      {result && (
        <section className="mx-auto max-w-6xl px-6 pb-24">
          {/* Trip Header */}
          <div className="mb-8 overflow-hidden rounded-3xl border border-slate-800 bg-gradient-to-br from-slate-900 via-slate-900 to-blue-950 p-8">
            <div className="flex flex-col justify-between gap-6 md:flex-row md:items-end">
              <div>
                <p className="text-sm font-medium uppercase tracking-[0.3em] text-blue-400">
                  AI Trip Planner
                </p>

                <h2 className="mt-3 text-4xl font-bold tracking-tight md:text-5xl">
                  {origin} → {destination}
                </h2>

                <p className="mt-3 text-slate-400">
                  {startDate} → {endDate} · {travelers}{" "}
                  {travelers === 1 ? "Traveler" : "Travelers"}
                </p>
              </div>

              <div className="rounded-2xl border border-slate-700 bg-slate-950/60 px-6 py-4">
                <p className="text-xs uppercase tracking-wider text-slate-500">
                  Estimated Trip Cost
                </p>

                <p className="mt-1 text-3xl font-bold text-blue-400">
                  ₹{result.budget.total_cost.toLocaleString()}
                </p>
              </div>
            </div>
          </div>

          {/* Summary Cards */}
          <div className="grid gap-5 md:grid-cols-3">
            {/* Flight */}
            <div className="group rounded-2xl border border-slate-800 bg-slate-900 p-6 transition hover:-translate-y-1 hover:border-blue-500/50">
              <div className="flex items-center justify-between">
                <span className="text-2xl">✈️</span>

                <span className="text-xs uppercase tracking-wider text-slate-500">
                  Flight
                </span>
              </div>

              <h3 className="mt-5 text-xl font-semibold">
                {result.selected_flight.airline}
              </h3>

              <div className="mt-4 space-y-2 text-sm text-slate-400">
                <p>₹{result.selected_flight.price.toLocaleString()}</p>

                <p>{result.selected_flight.duration}</p>

                <p>
                  {result.selected_flight.stops === 0
                    ? "Non-stop"
                    : `${result.selected_flight.stops} stop`}
                </p>
              </div>
            </div>

            {/* Hotel */}
            <div className="group rounded-2xl border border-slate-800 bg-slate-900 p-6 transition hover:-translate-y-1 hover:border-blue-500/50">
              <div className="flex items-center justify-between">
                <span className="text-2xl">🏨</span>

                <span className="text-xs uppercase tracking-wider text-slate-500">
                  Stay
                </span>
              </div>

              <h3 className="mt-5 text-xl font-semibold">
                {result.selected_stay.name}
              </h3>

              <div className="mt-4 space-y-2 text-sm text-slate-400">
                <p>⭐ {result.selected_stay.rating}/5</p>

                <p>
                  ₹
                  {result.selected_stay.price_per_night.toLocaleString()} /
                  night
                </p>

                <p>📍 {result.selected_stay.location}</p>
              </div>
            </div>

            {/* Budget */}
            <div className="group rounded-2xl border border-slate-800 bg-slate-900 p-6 transition hover:-translate-y-1 hover:border-blue-500/50">
              <div className="flex items-center justify-between">
                <span className="text-2xl">💰</span>

                <span className="text-xs uppercase tracking-wider text-slate-500">
                  Budget
                </span>
              </div>

              <h3 className="mt-5 text-xl font-semibold">
                ₹{result.budget.total_cost.toLocaleString()}
              </h3>

              <div className="mt-4">
                <div className="mb-2 flex justify-between text-xs text-slate-500">
                  <span>Used</span>

                  <span>₹{Number(budget).toLocaleString()}</span>
                </div>

                <div className="h-2 overflow-hidden rounded-full bg-slate-800">
                  <div
                    className="h-full rounded-full bg-blue-500"
                    style={{
                      width: `${Math.min(
                        (result.budget.total_cost / Number(budget)) * 100,
                        100
                      )}%`,
                    }}
                  />
                </div>

                <p className="mt-3 text-sm text-green-400">
                  ₹
                  {(
                    Number(budget) - result.budget.total_cost
                  ).toLocaleString()}{" "}
                  remaining
                </p>
              </div>
            </div>
          </div>

          {/* Activities */}
          <div className="mt-8 rounded-3xl border border-slate-800 bg-slate-900 p-7">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm uppercase tracking-[0.2em] text-blue-400">
                  Explore
                </p>

                <h3 className="mt-2 text-2xl font-bold">
                  Recommended Activities
                </h3>
              </div>

              <span className="rounded-full bg-slate-800 px-4 py-2 text-sm text-slate-400">
                {result.selected_activities.length} places
              </span>
            </div>

            <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {result.selected_activities.map(
                (activity: any, index: number) => (
                  <div
                    key={index}
                    className="rounded-2xl border border-slate-800 bg-slate-950 p-5 transition hover:border-blue-500/50"
                  >
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-500/10 text-lg">
                      {activity.category.toLowerCase().includes("history")
                        ? "🏛️"
                        : activity.category
                              .toLowerCase()
                              .includes("shopping")
                        ? "🛍️"
                        : "📍"}
                    </div>

                    <h4 className="mt-4 font-semibold">
                      {activity.name}
                    </h4>

                    <p className="mt-1 text-xs text-slate-500">
                      {activity.category}
                    </p>

                    <div className="mt-4 flex items-center justify-between text-sm">
                      <span className="text-slate-400">
                        ⏱️ {activity.duration}
                      </span>

                      <span className="font-medium text-blue-400">
                        {activity.price === 0
                          ? "Free"
                          : `₹${activity.price.toLocaleString()}`}
                      </span>
                    </div>
                  </div>
                )
              )}
            </div>
          </div>
{/* Route Optimization */}
<div className="mt-8 rounded-3xl border border-slate-800 bg-slate-900 p-7">
  <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
    <div>
      <p className="text-sm uppercase tracking-[0.2em] text-blue-400">
        Smart Routing
      </p>

      <h3 className="mt-2 text-2xl font-bold">
        Optimized Travel Route
      </h3>

      <p className="mt-2 text-sm text-slate-400">
        TripMind arranged your activities using geographic distance
        optimization.
      </p>
    </div>

    <div className="w-fit rounded-2xl border border-blue-500/20 bg-blue-500/5 px-5 py-4">
      <p className="text-xs uppercase tracking-wider text-slate-500">
        Route Distance
      </p>

      <p className="mt-1 text-2xl font-bold text-blue-400">
        {result.total_route_distance_km} km
      </p>
    </div>
  </div>

  {/* Route Timeline */}
  <div className="mt-7">
    <div className="space-y-3">
      {result.optimized_route.map(
        (place: string, index: number) => (
          <div key={index}>
            <div className="flex items-center gap-4 rounded-2xl border border-slate-800 bg-slate-950 p-4">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-blue-500/10 font-semibold text-blue-400">
                {index + 1}
              </div>

              <div className="flex-1">
                <p className="font-semibold text-white">
                  {place}
                </p>

                <p className="mt-1 text-xs text-slate-500">
                  Stop {index + 1}
                </p>
              </div>

              {index < result.optimized_route.length - 1 && (
                <span className="text-slate-600">↓</span>
              )}
            </div>
          </div>
        )
      )}
    </div>
  </div>

  {/* AI Route Explanation */}
  {result.route_recommendation && (
    <div className="mt-6 rounded-2xl bg-slate-950 p-5">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-500/10 text-lg">
          🤖
        </div>

        <div>
          <p className="text-xs uppercase tracking-wider text-purple-400">
            AI Route Analysis
          </p>

          <p className="font-semibold text-white">
            Why this route?
          </p>
        </div>
      </div>

      <div className="mt-4 text-sm leading-6 text-slate-400">
        {result.route_recommendation}
      </div>
    </div>
  )}
</div>
          {/* Budget Analysis */}
          <div className="mt-8 rounded-3xl border border-slate-800 bg-slate-900 p-7">
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-green-500/10 text-xl">
                💡
              </div>

              <div>
                <p className="text-sm uppercase tracking-[0.2em] text-green-400">
                  AI Analysis
                </p>

                <h3 className="mt-1 text-xl font-bold">
                  Budget Recommendation
                </h3>
              </div>
            </div>

            <div className="mt-5 rounded-2xl bg-slate-950 p-5">
              <div className="text-sm leading-7 text-slate-300">
                <ReactMarkdown
                  components={{
                    strong: ({ children }) => (
                      <strong className="font-semibold text-white">
                        {children}
                      </strong>
                    ),
                    p: ({ children }) => (
                      <p className="mb-3 last:mb-0">{children}</p>
                    ),
                  }}
                >
                  {result.budget_analysis}
                </ReactMarkdown>
              </div>
            </div>
          </div>

          {/* Itinerary */}
          <div className="mt-8 rounded-3xl border border-slate-800 bg-slate-900 p-7">
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-500/10 text-xl">
                🗓️
              </div>

              <div>
                <p className="text-sm uppercase tracking-[0.2em] text-blue-400">
                  AI Generated
                </p>

                <h3 className="mt-1 text-2xl font-bold">
                  {result.itinerary.trip_title}
                </h3>

                <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
                  {result.itinerary.summary}
                </p>
              </div>
            </div>

            <div className="mt-8 space-y-6">
              {result.itinerary.days.map((day: any) => (
                <div
                  key={day.day}
                  className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-950"
                >
                  {/* Day Header */}
                  <div className="border-b border-slate-800 bg-slate-900/70 p-5">
                    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                      <div>
                        <span className="text-xs font-semibold uppercase tracking-[0.2em] text-blue-400">
                          Day {day.day}
                        </span>

                        <h4 className="mt-1 text-xl font-bold text-white">
                          {day.title}
                        </h4>
                      </div>

                      <span className="w-fit rounded-full bg-slate-800 px-4 py-2 text-sm text-slate-400">
                        {day.date}
                      </span>
                    </div>

                    {/* WEATHER CARD */}
                    {day.weather && (
                      <div className="mt-5 rounded-2xl border border-blue-500/20 bg-blue-500/5 p-5">
                        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                          <div className="flex items-center gap-4">
                            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-500/10 text-3xl">
                              {getWeatherIcon(
                                day.weather.condition,
                                day.weather.rain_probability
                              )}
                            </div>

                            <div>
                              <p className="text-xs font-medium uppercase tracking-[0.2em] text-blue-400">
                                Weather
                              </p>

                              <p className="mt-1 text-lg font-semibold text-white">
                                {day.weather.condition}
                              </p>
                            </div>
                          </div>

                          <div className="grid grid-cols-3 gap-5 sm:min-w-[360px]">
                            <div>
                              <p className="text-xs text-slate-500">
                                Temperature
                              </p>

                              <p className="mt-1 font-semibold text-white">
                                {day.weather.temperature}°C
                              </p>
                            </div>

                            <div>
                              <p className="text-xs text-slate-500">
                                Rain
                              </p>

                              <p className="mt-1 font-semibold text-white">
                                {day.weather.rain_probability}%
                              </p>
                            </div>

                            <div>
                              <p className="text-xs text-slate-500">
                                Wind
                              </p>

                              <p className="mt-1 font-semibold text-white">
                                {day.weather.wind}
                              </p>
                            </div>
                          </div>
                        </div>

                        {/* Weather suitability */}
                        <div className="mt-4 border-t border-slate-800 pt-4">
                          <p className="text-sm text-slate-400">
                            {day.weather.rain_probability >= 50
                              ? "🌧️ Outdoor activities may be affected. Keep indoor or flexible plans in mind."
                              : day.weather.rain_probability >= 30
                              ? "⛅ Outdoor activities are possible, but carrying a light rain layer is recommended."
                              : "☀️ Conditions look favorable for outdoor sightseeing."}
                          </p>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Activities */}
                  <div className="p-5">
                    <div className="space-y-5">
                      {day.activities.map(
                        (activity: any, index: number) => (
                          <div
                            key={index}
                            className="relative flex gap-4"
                          >
                            {/* Timeline */}
                            <div className="flex flex-col items-center">
                              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-blue-500/10 text-lg">
                                {activity.time
                                  .toLowerCase()
                                  .includes("morning")
                                  ? "🌅"
                                  : activity.time
                                      .toLowerCase()
                                      .includes("afternoon")
                                  ? "☀️"
                                  : "🌙"}
                              </div>

                              {index < day.activities.length - 1 && (
                                <div className="mt-2 h-full w-px bg-slate-800" />
                              )}
                            </div>

                            {/* Activity Content */}
                            <div className="min-w-0 flex-1 pb-2">
                              <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                                <div>
                                  <p className="text-xs font-medium uppercase tracking-wider text-blue-400">
                                    {activity.time}
                                  </p>

                                  <h5 className="mt-1 text-lg font-semibold text-white">
                                    {activity.title}
                                  </h5>
                                </div>

                                <span className="w-fit rounded-full bg-slate-900 px-3 py-1 text-xs text-slate-400">
                                  {activity.cost === 0
                                    ? "Free"
                                    : `₹${activity.cost.toLocaleString()}`}
                                </span>
                              </div>

                              <p className="mt-2 text-sm leading-6 text-slate-400">
                                {activity.description}
                              </p>

                              <p className="mt-3 text-xs text-slate-500">
                                📍 {activity.location}
                              </p>
                            </div>
                          </div>
                        )
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Footer Action */}
          <div className="mt-8 flex justify-center">
            <button
              onClick={() =>
                window.scrollTo({
                  top: 0,
                  behavior: "smooth",
                })
              }
              className="rounded-xl border border-slate-700 px-6 py-3 text-sm font-medium text-slate-300 transition hover:border-blue-500 hover:text-white"
            >
              ↑ Plan Another Trip
            </button>
          </div>
        </section>
      )}
    </main>
  );
}
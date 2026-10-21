
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
  const [errorMessage, setErrorMessage] = useState("");

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
    setErrorMessage("");

    // Validate inputs before sending the request.
    if (!origin.trim() || !destination.trim()) {
      setErrorMessage(
        "Please enter both your starting city and destination."
      );
      setLoading(false);
      return;
    }

    if (!startDate || !endDate) {
      setErrorMessage(
        "Please select both your start date and end date."
      );
      setLoading(false);
      return;
    }

    if (endDate <= startDate) {
      setErrorMessage(
        "End date must be after the start date."
      );
      setLoading(false);
      return;
    }

    if (
      !Number.isInteger(travelers) ||
      travelers < 1 ||
      travelers > 50
    ) {
      setErrorMessage(
        "Travelers must be a whole number between 1 and 50."
      );
      setLoading(false);
      return;
    }

    const budgetValue = Number(budget);

    if (
      !budget.trim() ||
      !Number.isFinite(budgetValue) ||
      budgetValue <= 0 ||
      !Number.isInteger(budgetValue)
    ) {
      setErrorMessage(
        "Please enter a valid whole-number budget greater than ₹0."
      );
      setLoading(false);
      return;
    }

    if (interests.length === 0) {
      setErrorMessage(
        "Please select at least one interest."
      );
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/plan-trip",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            origin: origin.trim(),
            destination: destination.trim(),
            start_date: startDate,
            end_date: endDate,
            travelers,
            total_budget: budgetValue,
            interests: interests.map((item) =>
              item.toLowerCase()
            ),
          }),
        }
      );

      if (!response.ok) {
        let message =
          "Unable to generate your trip plan. Please try again.";

        try {
          const errorData = await response.json();

          if (Array.isArray(errorData.detail)) {
            message = errorData.detail
              .map((item: any) => {
                const field = Array.isArray(item.loc)
                  ? item.loc[item.loc.length - 1]
                  : "";

                const description =
                  typeof item.msg === "string"
                    ? item.msg.replace(/^Value error,\s*/i, "")
                    : "Invalid input.";

                return field
                  ? `${String(field)}: ${description}`
                  : description;
              })
              .join(" ");
          } else if (
            typeof errorData.detail === "string"
          ) {
            message = errorData.detail;
          }
        } catch {
          // Use the fallback message if the response isn't JSON.
        }

        throw new Error(message);
      }

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error("Trip planning error:", error);

      setErrorMessage(
        error instanceof Error
          ? error.message
          : "Something went wrong while planning your trip. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  const getWeatherIcon = (
    condition: string,
    rainProbability: number
  ) => {
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
        <div className="text-2xl font-bold">
          ✈️ TripMind
        </div>

        <div className="flex gap-6 text-sm text-slate-300">
          <a
            href="#about"
            className="cursor-pointer hover:text-white"
          >
            About
          </a>

          <a
            href="https://github.com/BhavyaSolanki31/TripMind"
            target="_blank"
            rel="noreferrer"
            className="cursor-pointer hover:text-white"
          >
            GitHub
          </a>
        </div>
      </nav>

      {/* Hero */}
      <section
        id="about"
        className="mx-auto max-w-4xl px-6 pb-12 pt-16 text-center"
      >
        <p className="mb-4 text-sm font-medium uppercase tracking-[0.3em] text-blue-400">
          Multi-Agent AI Travel Planner
        </p>

        <h1 className="text-5xl font-bold leading-tight md:text-6xl">
          Plan your perfect trip
          <span className="block text-blue-400">
            with AI.
          </span>
        </h1>

        <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-400">
          TripMind combines intelligent travel agents to plan
          flights, stays, activities, budgets, weather, and your
          complete itinerary.
        </p>
      </section>

      {/* Trip Form */}
      <section className="mx-auto max-w-4xl px-6 pb-12">
        <div className="rounded-3xl border border-slate-800 bg-slate-900 p-8 shadow-2xl">
          <div className="grid gap-6 md:grid-cols-2">
            {/* Origin */}
            <div>
              <label
                htmlFor="origin"
                className="mb-2 block text-sm text-slate-400"
              >
                From
              </label>

              <input
                id="origin"
                value={origin}
                onChange={(e) => setOrigin(e.target.value)}
                placeholder="Delhi"
                maxLength={100}
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 outline-none transition focus:border-blue-500"
              />
            </div>

            {/* Destination */}
            <div>
              <label
                htmlFor="destination"
                className="mb-2 block text-sm text-slate-400"
              >
                To
              </label>

              <input
                id="destination"
                value={destination}
                onChange={(e) =>
                  setDestination(e.target.value)
                }
                placeholder="Mumbai"
                maxLength={100}
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 outline-none transition focus:border-blue-500"
              />
            </div>

            {/* Start Date */}
            <div>
              <label
                htmlFor="startDate"
                className="mb-2 block text-sm text-slate-400"
              >
                Start Date
              </label>

              <input
                id="startDate"
                type="date"
                value={startDate}
                onChange={(e) =>
                  setStartDate(e.target.value)
                }
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 outline-none focus:border-blue-500"
              />
            </div>

            {/* End Date */}
            <div>
              <label
                htmlFor="endDate"
                className="mb-2 block text-sm text-slate-400"
              >
                End Date
              </label>

              <input
                id="endDate"
                type="date"
                min={startDate || undefined}
                value={endDate}
                onChange={(e) =>
                  setEndDate(e.target.value)
                }
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 outline-none focus:border-blue-500"
              />
            </div>

            {/* Travelers */}
            <div>
              <label
                htmlFor="travelers"
                className="mb-2 block text-sm text-slate-400"
              >
                Travelers
              </label>

              <input
                id="travelers"
                type="number"
                min="1"
                max="50"
                step="1"
                value={travelers}
                onChange={(e) =>
                  setTravelers(Number(e.target.value))
                }
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 outline-none focus:border-blue-500"
              />
            </div>

            {/* Budget */}
            <div>
              <label
                htmlFor="budget"
                className="mb-2 block text-sm text-slate-400"
              >
                Total Budget (₹)
              </label>

              <input
                id="budget"
                type="number"
                min="1"
                step="1"
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
                  type="button"
                  aria-pressed={interests.includes(interest)}
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

          {/* Error Message */}
          {errorMessage && (
            <div
              role="alert"
              className="mt-6 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-300"
            >
              <p className="font-semibold">
                Unable to plan your trip
              </p>
              <p className="mt-1">{errorMessage}</p>
            </div>
          )}

          {/* Button */}
          <button
            type="button"
            onClick={planTrip}
            disabled={loading}
            className="mt-8 w-full rounded-xl bg-blue-500 px-6 py-4 text-lg font-semibold transition hover:bg-blue-400 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading
              ? "🧠 Planning your trip..."
              : "✨ Plan My Trip"}
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
                  {travelers === 1
                    ? "Traveler"
                    : "Travelers"}
                </p>
              </div>

              <div className="rounded-2xl border border-slate-700 bg-slate-950/60 px-6 py-4">
                <p className="text-xs uppercase tracking-wider text-slate-500">
                  Estimated Trip Cost
                </p>

                <p className="mt-1 text-3xl font-bold text-blue-400">
                  ₹
                  {result.budget.total_cost.toLocaleString(
                    "en-IN"
                  )}
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
                <p>
                  ₹
                  {result.selected_flight.price.toLocaleString(
                    "en-IN"
                  )}
                </p>

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
                  {result.selected_stay.price_per_night.toLocaleString(
                    "en-IN"
                  )}{" "}
                  / night
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
                ₹
                {result.budget.total_cost.toLocaleString(
                  "en-IN"
                )}
              </h3>

              <div className="mt-4">
                <div className="mb-2 flex justify-between text-xs text-slate-500">
                  <span>Total Budget</span>
                  <span>
                    ₹{Number(budget).toLocaleString("en-IN")}
                  </span>
                </div>

                <div className="h-2 overflow-hidden rounded-full bg-slate-800">
                  <div
                    className="h-full rounded-full bg-blue-500"
                    style={{
                      width: `${Math.min(
                        (result.budget.total_cost /
                          Number(budget)) *
                          100,
                        100
                      )}%`,
                    }}
                  />
                </div>

                <p className="mt-3 text-sm text-green-400">
                  ₹
                  {(
                    Number(budget) -
                    result.budget.total_cost
                  ).toLocaleString("en-IN")}{" "}
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
                      {activity.category
                        .toLowerCase()
                        .includes("history")
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
                          : `₹${activity.price.toLocaleString(
                              "en-IN"
                            )}`}
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
                  TripMind arranged your activities using
                  geographic distance optimization.
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

            {/* Route Distance Disclaimer */}
            <div className="mt-5 rounded-2xl border border-amber-500/20 bg-amber-500/5 p-5">
              <div className="flex items-start gap-3">
                <span className="text-xl">⚠️</span>

                <div>
                  <h4 className="font-semibold text-amber-300">
                    Estimated Distance Only
                  </h4>

                  <p className="mt-2 text-sm leading-6 text-slate-400">
                    Distance type:{" "}
                    {result.route_distance_type ||
                      "straight-line estimate"}
                    . This is a geographic estimate, not
                    verified road distance. Actual travel
                    distance, ferry routes, schedules, and
                    travel times may differ.
                  </p>
                </div>
              </div>
            </div>

            {/* Special Transport Notice */}
            {Array.isArray(result.special_transport) &&
              result.special_transport.length > 0 && (
                <div className="mt-4 rounded-2xl border border-blue-500/20 bg-blue-500/5 p-5">
                  <h4 className="font-semibold text-blue-300">
                    🚢 Special Transport Required
                  </h4>

                  {result.special_transport.map(
                    (item: any, index: number) => (
                      <p
                        key={index}
                        className="mt-2 text-sm leading-6 text-slate-300"
                      >
                        <strong>{item.activity}</strong>{" "}
                        requires {item.transport}. Confirm
                        transport availability and operating
                        times before your visit.
                      </p>
                    )
                  )}
                </div>
              )}

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

                        {index <
                          result.optimized_route.length - 1 && (
                          <span className="text-slate-600">
                            ↓
                          </span>
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
                      <p className="mb-3 last:mb-0">
                        {children}
                      </p>
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

                    {/* Weather Card */}
                    {day.weather && (
                      <div className="mt-5 rounded-2xl border border-blue-500/20 bg-blue-500/5 p-5">
                        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                          <div className="flex items-center gap-4">
                            <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-blue-500/10 text-3xl">
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

                              <p className="mt-2 text-xs text-slate-500">
                                Source:{" "}
                                {day.weather.source ||
                                  "Source not specified"}

                                {day.weather.status ===
                                  "unavailable" && (
                                  <span className="mt-1 block text-amber-300">
                                    Forecast unavailable for
                                    this date.
                                  </span>
                                )}
                              </p>
                            </div>
                          </div>

                          <div className="grid grid-cols-3 gap-5 sm:min-w-[360px]">
                            <div>
                              <p className="text-xs text-slate-500">
                                Temperature
                              </p>

                              <p className="mt-1 font-semibold text-white">
                                {day.weather.temperature !=
                                null
                                  ? `${day.weather.temperature}°C`
                                  : "Unavailable"}
                              </p>
                            </div>

                            <div>
                              <p className="text-xs text-slate-500">
                                Rain
                              </p>

                              <p className="mt-1 font-semibold text-white">
                                {day.weather.rain_probability !=
                                null
                                  ? `${day.weather.rain_probability}%`
                                  : "Unavailable"}
                              </p>
                            </div>

                            <div>
                              <p className="text-xs text-slate-500">
                                Wind
                              </p>

                              <p className="mt-1 font-semibold text-white">
                                {day.weather.wind ?? "Unavailable"}
                              </p>
                            </div>
                          </div>
                        </div>

                        {/* Weather Suitability */}
                        <div className="mt-4 border-t border-slate-800 pt-4">
                          <p className="text-sm text-slate-400">
                            {day.weather.status === "unavailable" ||
                            day.weather.rain_probability == null
                              ? "Weather data is unavailable. Check a reliable forecast before planning outdoor activities."
                              : day.weather.rain_probability >=
                                  50
                                ? "🌧️ Higher rain probability. Consider flexible or indoor activities and check the latest forecast."
                                : day.weather.rain_probability >=
                                    30
                                  ? "⛅ Some chance of rain. Keep a flexible plan and check the latest forecast before outdoor activities."
                                  : "☀️ Lower rain probability in this forecast. Conditions can change, so check the latest forecast before travelling."}
                          </p>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Day Activities */}
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

                              {index <
                                day.activities.length - 1 && (
                                <div className="mt-2 h-full w-px bg-slate-800" />
                              )}
                            </div>

                            {/* Activity Details */}
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
                                    : `₹${activity.cost.toLocaleString(
                                        "en-IN"
                                      )}`}
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
              type="button"
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

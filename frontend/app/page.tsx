
"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";

const API_URL = "http://127.0.0.1:8000/plan-trip";

const INTERESTS = [
  { name: "Sightseeing", icon: "🏛️" },
  { name: "History", icon: "🏺" },
  { name: "Food", icon: "🍜" },
  { name: "Shopping", icon: "🛍️" },
  { name: "Nature", icon: "🌿" },
  { name: "Adventure", icon: "🏔️" },
];

const money = (value: number | string | null | undefined) =>
  value == null || !Number.isFinite(Number(value))
    ? "—"
    : `₹${Number(value).toLocaleString("en-IN")}`;

function SectionHeading({
  eyebrow,
  title,
  description,
}: {
  eyebrow: string;
  title: string;
  description?: string;
}) {
  return (
    <div className="mb-6">
      <p className="text-xs font-bold uppercase tracking-[0.22em] text-blue-400">
        {eyebrow}
      </p>
      <h3 className="mt-2 text-2xl font-bold tracking-tight text-white sm:text-3xl">
        {title}
      </h3>
      {description && (
        <p className="mt-2 text-sm leading-6 text-slate-400">
          {description}
        </p>
      )}
    </div>
  );
}

function Panel({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <section
      className={`rounded-3xl border border-white/[0.09] bg-slate-900/75 p-5 shadow-xl shadow-black/10 backdrop-blur-sm sm:p-7 ${className}`}
    >
      {children}
    </section>
  );
}

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

  const today = new Date().toLocaleDateString("en-CA");

  const toggleInterest = (interest: string) => {
    setInterests((current) =>
      current.includes(interest)
        ? current.filter((item) => item !== interest)
        : [...current, interest]
    );
  };

  const planTrip = async () => {
    setErrorMessage("");

    if (!origin.trim() || !destination.trim()) {
      setErrorMessage("Please enter both your starting city and destination.");
      return;
    }

    if (!startDate || !endDate) {
      setErrorMessage("Please select both your start and end dates.");
      return;
    }

    if (endDate <= startDate) {
      setErrorMessage("Your end date must be after your start date.");
      return;
    }

    if (startDate < today) {
      setErrorMessage("Please select a start date that is today or later.");
      return;
    }

    if (
      !Number.isInteger(travelers) ||
      travelers < 1 ||
      travelers > 50
    ) {
      setErrorMessage("Travelers must be a whole number between 1 and 50.");
      return;
    }

    const budgetValue = Number(budget);

    if (
      !budget.trim() ||
      !Number.isFinite(budgetValue) ||
      budgetValue <= 0 ||
      !Number.isInteger(budgetValue)
    ) {
      setErrorMessage("Enter a valid whole-number budget greater than ₹0.");
      return;
    }

    if (interests.length === 0) {
      setErrorMessage("Choose at least one interest for your trip.");
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          origin: origin.trim(),
          destination: destination.trim(),
          start_date: startDate,
          end_date: endDate,
          travelers,
          total_budget: budgetValue,
          interests: interests.map((item) => item.toLowerCase()),
        }),
      });

      if (!response.ok) {
        let message = "Unable to generate your trip plan. Please try again.";

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
          } else if (typeof errorData.detail === "string") {
            message = errorData.detail;
          }
        } catch {
          // Keep the fallback error message.
        }

        throw new Error(message);
      }

      const data = await response.json();
      setResult(data);

      window.setTimeout(() => {
        document.getElementById("trip-results")?.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }, 100);
    } catch (error) {
      console.error("Trip planning error:", error);

      setErrorMessage(
        error instanceof Error
          ? error.message
          : "Something went wrong. Please check that the backend is running."
      );
    } finally {
      setLoading(false);
    }
  };

  const getWeatherIcon = (
    condition: string,
    rainProbability: number | null
  ) => {
    const weather = condition?.toLowerCase() || "";

    if (rainProbability != null && rainProbability >= 50) return "🌧️";
    if (weather.includes("cloud")) return "⛅";
    if (weather.includes("rain")) return "🌧️";
    if (weather.includes("clear")) return "🌤️";
    if (weather.includes("sun")) return "☀️";

    return "🌤️";
  };

  const resetTrip = () => {
    setResult(null);
    setErrorMessage("");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const totalCost = Number(result?.budget?.total_cost ?? 0);
  const budgetValue = Number(budget || 0);
  const remaining = budgetValue - totalCost;
  const budgetPercent =
    budgetValue > 0
      ? Math.min((totalCost / budgetValue) * 100, 100)
      : 0;

  return (
    <main className="relative min-h-screen overflow-hidden bg-[#070b16] text-white">
      {/* Ambient background */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-x-0 top-0 h-[620px] bg-[radial-gradient(ellipse_at_50%_0%,rgba(37,99,235,0.20),transparent_65%)]"
      />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -left-40 top-[500px] h-80 w-80 rounded-full bg-blue-600/[0.07] blur-[100px]"
      />

      {/* Navigation */}
      <header className="relative z-10 border-b border-white/[0.07]">
        <nav className="mx-auto flex max-w-7xl items-center justify-between px-5 py-5 sm:px-8">
          <a href="#" className="flex items-center gap-3" aria-label="TripMind home">
            <span className="flex h-11 w-11 items-center justify-center rounded-2xl border border-blue-400/20 bg-blue-500/15 text-xl shadow-lg shadow-blue-950/30">
              ✈
            </span>
            <span>
              <span className="block text-xl font-extrabold tracking-tight">
                Trip<span className="text-blue-400">Mind</span>
              </span>
              <span className="hidden text-[10px] font-medium uppercase tracking-[0.2em] text-slate-500 sm:block">
                Travel smarter
              </span>
            </span>
          </a>

          <div className="flex items-center gap-4 sm:gap-7">
            <a
              href="#about"
              className="text-sm text-slate-400 transition hover:text-white"
            >
              About
            </a>
            <a
              href="https://github.com/BhavyaSolanki31/TripMind"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.04] px-3 py-2 text-sm font-medium text-slate-200 transition hover:border-blue-400/40 hover:bg-blue-500/10 sm:px-4"
            >
              <svg
                viewBox="0 0 24 24"
                className="h-4 w-4"
                fill="currentColor"
                aria-hidden="true"
              >
                <path d="M12 .9a11.1 11.1 0 0 0-3.51 21.63c.55.1.76-.24.76-.53v-2.08c-3.1.68-3.76-1.32-3.76-1.32-.5-1.3-1.24-1.65-1.24-1.65-1.01-.69.08-.68.08-.68 1.12.08 1.71 1.15 1.71 1.15 1 .1.76 1.78 3.43 1.26.1-.72.4-1.21.72-1.49-2.47-.28-5.07-1.24-5.07-5.5 0-1.22.44-2.22 1.15-3-.12-.28-.5-1.42.11-2.96 0 0 .94-.3 3.05 1.15a10.6 10.6 0 0 1 5.55 0c2.11-1.44 3.05-1.15 3.05-1.15.61 1.54.23 2.68.11 2.96.72.78 1.15 1.78 1.15 3 0 4.27-2.6 5.22-5.08 5.5.4.35.76 1.02.76 2.06V22c0 .29.2.63.77.53A11.1 11.1 0 0 0 12 .9Z" />
              </svg>
              <span className="hidden sm:inline">GitHub</span>
            </a>
          </div>
        </nav>
      </header>

      {/* Hero */}
      <section
        id="about"
        className="relative z-10 mx-auto max-w-7xl px-5 pb-12 pt-16 sm:px-8 sm:pt-24 lg:pb-16 lg:pt-28"
      >
        <div className="mx-auto max-w-4xl text-center">
          <div className="mx-auto inline-flex items-center gap-2 rounded-full border border-blue-400/20 bg-blue-500/[0.08] px-4 py-2 text-xs font-semibold tracking-wide text-blue-300 sm:text-sm">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-blue-400 opacity-50" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-blue-400" />
            </span>
            MULTI-AGENT AI TRAVEL PLANNER
          </div>

          <h1 className="mt-7 text-5xl font-black leading-[1.08] tracking-[-0.055em] sm:text-6xl lg:text-7xl">
            Your next adventure,
            <span className="mt-2 block bg-gradient-to-r from-blue-300 via-sky-400 to-indigo-400 bg-clip-text text-transparent">
              thoughtfully planned.
            </span>
          </h1>

          <p className="mx-auto mt-6 max-w-2xl text-base leading-7 text-slate-400 sm:text-lg sm:leading-8">
            From destinations and stays to daily itineraries and budget
            insights, let a team of AI agents help you plan a smarter journey.
          </p>

          <div className="mt-8 flex flex-wrap items-center justify-center gap-x-6 gap-y-3 text-xs font-medium text-slate-400 sm:text-sm">
            <span className="inline-flex items-center gap-2">
              <span className="text-emerald-400">✓</span> Personalized plans
            </span>
            <span className="inline-flex items-center gap-2">
              <span className="text-emerald-400">✓</span> Budget insights
            </span>
            <span className="inline-flex items-center gap-2">
              <span className="text-emerald-400">✓</span> Weather-aware ideas
            </span>
          </div>
        </div>

        {/* Decorative trip preview */}
        <div className="mx-auto mt-12 max-w-4xl rounded-3xl border border-white/10 bg-gradient-to-br from-slate-900/95 via-slate-900/85 to-blue-950/60 p-4 shadow-2xl shadow-blue-950/20 sm:p-6">
          <div className="grid gap-4 sm:grid-cols-[1fr_auto_1fr] sm:items-center">
            <div className="rounded-2xl border border-white/[0.07] bg-black/20 p-4 sm:p-5">
              <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-500">
                Your journey starts
              </p>
              <div className="mt-3 flex items-center gap-3">
                <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-white/[0.06] text-xl">
                  📍
                </span>
                <div className="min-w-0">
                  <p className="text-lg font-bold">Your city</p>
                  <p className="text-xs text-slate-500">Choose your starting point</p>
                </div>
              </div>
            </div>

            <div className="hidden items-center justify-center sm:flex">
              <div className="flex h-11 w-11 items-center justify-center rounded-full border border-blue-400/20 bg-blue-500/10 text-lg text-blue-300">
                →
              </div>
            </div>

            <div className="rounded-2xl border border-blue-400/15 bg-blue-500/[0.06] p-4 sm:p-5">
              <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-blue-300/70">
                Your next destination
              </p>
              <div className="mt-3 flex items-center gap-3">
                <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-500/10 text-xl">
                  🌍
                </span>
                <div className="min-w-0">
                  <p className="text-lg font-bold">Somewhere amazing</p>
                  <p className="text-xs text-slate-400">Your journey, your way</p>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-white/[0.07] pt-4 text-xs text-slate-500 sm:text-sm">
            <span>✦ Flight options · Stays · Experiences</span>
            <a href="#planner" className="font-semibold text-blue-300 hover:text-blue-200">
              Start planning ↓
            </a>
          </div>
        </div>
      </section>

      {/* Trip form */}
      <section
        id="planner"
        className="relative z-10 mx-auto max-w-5xl scroll-mt-8 px-5 pb-16 sm:px-8"
      >
        <div className="overflow-hidden rounded-3xl border border-white/10 bg-slate-900/90 shadow-2xl shadow-black/20">
          <div className="border-b border-white/[0.07] bg-gradient-to-r from-blue-500/[0.09] via-transparent to-indigo-500/[0.06] px-5 py-6 sm:px-8 sm:py-7">
            <div className="flex items-start gap-4">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl border border-blue-400/20 bg-blue-500/10 text-xl">
                🧭
              </div>
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.2em] text-blue-400">
                  Your trip, your rules
                </p>
                <h2 className="mt-2 text-2xl font-bold tracking-tight sm:text-3xl">
                  Build your travel plan
                </h2>
                <p className="mt-2 text-sm leading-6 text-slate-400">
                  Share a few details and let TripMind put your itinerary together.
                </p>
              </div>
            </div>
          </div>

          <div className="p-5 sm:p-8">
            <div className="grid gap-x-6 gap-y-5 md:grid-cols-2">
              <div>
                <label htmlFor="origin" className="mb-2 block text-sm font-medium text-slate-300">
                  From
                </label>
                <div className="relative">
                  <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-slate-500">
                    ↗
                  </span>
                  <input
                    id="origin"
                    value={origin}
                    onChange={(e) => setOrigin(e.target.value)}
                    placeholder="e.g. Delhi"
                    maxLength={100}
                    autoComplete="address-level2"
                    className="w-full rounded-xl border border-white/10 bg-[#090f1d] py-3.5 pl-10 pr-4 text-sm text-white transition placeholder:text-slate-600 hover:border-white/20 focus:border-blue-400"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="destination" className="mb-2 block text-sm font-medium text-slate-300">
                  To
                </label>
                <div className="relative">
                  <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-slate-500">
                    ⌖
                  </span>
                  <input
                    id="destination"
                    value={destination}
                    onChange={(e) => setDestination(e.target.value)}
                    placeholder="e.g. Mumbai"
                    maxLength={100}
                    className="w-full rounded-xl border border-white/10 bg-[#090f1d] py-3.5 pl-10 pr-4 text-sm text-white transition placeholder:text-slate-600 hover:border-white/20 focus:border-blue-400"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="startDate" className="mb-2 block text-sm font-medium text-slate-300">
                  Departure date
                </label>
                <input
                  id="startDate"
                  type="date"
                  min={today}
                  value={startDate}
                  onChange={(e) => {
                    setStartDate(e.target.value);
                    if (endDate && e.target.value >= endDate) setEndDate("");
                  }}
                  className="w-full rounded-xl border border-white/10 bg-[#090f1d] px-4 py-3.5 text-sm text-white transition hover:border-white/20 focus:border-blue-400"
                />
              </div>

              <div>
                <label htmlFor="endDate" className="mb-2 block text-sm font-medium text-slate-300">
                  Return date
                </label>
                <input
                  id="endDate"
                  type="date"
                  min={startDate || today}
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="w-full rounded-xl border border-white/10 bg-[#090f1d] px-4 py-3.5 text-sm text-white transition hover:border-white/20 focus:border-blue-400"
                />
              </div>

              <div>
                <label htmlFor="travelers" className="mb-2 block text-sm font-medium text-slate-300">
                  Number of travelers
                </label>
                <input
                  id="travelers"
                  type="number"
                  min={1}
                  max={50}
                  step={1}
                  value={travelers}
                  onChange={(e) => setTravelers(Number(e.target.value))}
                  className="w-full rounded-xl border border-white/10 bg-[#090f1d] px-4 py-3.5 text-sm text-white transition hover:border-white/20 focus:border-blue-400"
                />
                <p className="mt-1.5 text-xs text-slate-600">Between 1 and 50 people</p>
              </div>

              <div>
                <label htmlFor="budget" className="mb-2 block text-sm font-medium text-slate-300">
                  Total trip budget
                </label>
                <div className="relative">
                  <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-sm font-semibold text-emerald-400">
                    ₹
                  </span>
                  <input
                    id="budget"
                    type="number"
                    min={1}
                    step={1}
                    value={budget}
                    onChange={(e) => setBudget(e.target.value)}
                    placeholder="40000"
                    className="w-full rounded-xl border border-white/10 bg-[#090f1d] py-3.5 pl-10 pr-4 text-sm text-white transition placeholder:text-slate-600 hover:border-white/20 focus:border-blue-400"
                  />
                </div>
                <p className="mt-1.5 text-xs text-slate-600">Enter your total budget in INR</p>
              </div>
            </div>

            <div className="mt-8 border-t border-white/[0.07] pt-7">
              <div className="flex flex-wrap items-end justify-between gap-3">
                <div>
                  <h3 className="text-base font-semibold text-white">
                    What do you love doing?
                  </h3>
                  <p className="mt-1 text-sm text-slate-500">
                    Select at least one interest.
                  </p>
                </div>
                <span className="rounded-full border border-white/10 bg-white/[0.03] px-3 py-1 text-xs text-slate-400">
                  {interests.length} selected
                </span>
              </div>

              <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3">
                {INTERESTS.map((interest) => {
                  const selected = interests.includes(interest.name);

                  return (
                    <button
                      key={interest.name}
                      type="button"
                      aria-pressed={selected}
                      onClick={() => toggleInterest(interest.name)}
                      className={`flex items-center gap-3 rounded-xl border px-3 py-3.5 text-left text-sm font-medium transition sm:px-4 ${
                        selected
                          ? "border-blue-400/50 bg-blue-500/10 text-blue-200 shadow-lg shadow-blue-950/10"
                          : "border-white/[0.09] bg-[#090f1d] text-slate-300 hover:border-white/20 hover:bg-white/[0.03]"
                      }`}
                    >
                      <span className="text-xl">{interest.icon}</span>
                      <span className="flex-1">{interest.name}</span>
                      <span className={`text-xs ${selected ? "text-blue-300" : "text-slate-700"}`}>
                        {selected ? "✓" : "+"}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>

            {errorMessage && (
              <div
                role="alert"
                className="mt-6 rounded-2xl border border-red-400/20 bg-red-500/[0.08] p-4 text-sm text-red-200"
              >
                <div className="flex items-start gap-3">
                  <span className="text-lg">!</span>
                  <div>
                    <p className="font-semibold">Let's check your trip details</p>
                    <p className="mt-1 leading-6 text-red-200/80">{errorMessage}</p>
                  </div>
                </div>
              </div>
            )}

            <button
              type="button"
              onClick={planTrip}
              disabled={loading}
              className="mt-8 flex w-full items-center justify-center gap-3 rounded-xl bg-gradient-to-r from-blue-600 to-blue-500 px-6 py-4 text-base font-bold text-white shadow-lg shadow-blue-950/40 transition hover:from-blue-500 hover:to-sky-500 disabled:cursor-not-allowed disabled:opacity-60 sm:text-lg"
            >
              {loading ? (
                <>
                  <span className="h-5 w-5 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                  Coordinating your trip...
                </>
              ) : (
                <>
                  <span>✦</span>
                  Plan my trip
                  <span aria-hidden="true">→</span>
                </>
              )}
            </button>

            <p className="mt-4 text-center text-xs leading-5 text-slate-600">
              AI-assisted planning · Estimated costs · Flexible travel ideas
            </p>
          </div>
        </div>
      </section>

      {/* Loading feedback */}
      {loading && (
        <div className="mx-auto max-w-5xl px-5 pb-12 sm:px-8" role="status" aria-live="polite">
          <div className="rounded-2xl border border-blue-400/15 bg-blue-500/[0.05] p-6 text-center">
            <p className="font-semibold text-blue-200">Your trip is taking shape</p>
            <p className="mt-2 text-sm text-slate-400">
              Gathering recommendations and organizing your travel plan...
            </p>
          </div>
        </div>
      )}

      {/* Results */}
      {result && (
        <section
          id="trip-results"
          className="relative z-10 mx-auto max-w-7xl scroll-mt-6 space-y-6 px-5 pb-20 sm:px-8"
        >
          {/* Result overview */}
          <div className="overflow-hidden rounded-3xl border border-blue-400/15 bg-gradient-to-br from-blue-950/70 via-slate-900 to-slate-900 p-6 shadow-2xl shadow-black/20 sm:p-9">
            <div className="flex flex-col justify-between gap-6 lg:flex-row lg:items-end">
              <div>
                <div className="inline-flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/[0.07] px-3 py-1.5 text-xs font-semibold text-emerald-300">
                  <span>✓</span> YOUR TRIP PLAN
                </div>

                <h2 className="mt-5 break-words text-3xl font-black tracking-tight sm:text-5xl">
                  {origin} <span className="text-blue-400">→</span> {destination}
                </h2>

                <p className="mt-3 text-sm text-slate-400 sm:text-base">
                  {startDate} <span className="mx-2 text-slate-600">→</span> {endDate}
                  <span className="mx-2 text-slate-700">·</span>
                  {travelers} {travelers === 1 ? "traveler" : "travelers"}
                </p>
              </div>

              <div className="rounded-2xl border border-white/10 bg-black/20 p-5 lg:min-w-64">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
                  Estimated trip cost
                </p>
                <p className="mt-2 text-3xl font-black tracking-tight text-white sm:text-4xl">
                  {money(totalCost)}
                </p>
                <p className="mt-2 text-xs text-slate-500">
                  Your budget: {money(budgetValue)}
                </p>
              </div>
            </div>
          </div>

          {/* Flight, stay and budget cards */}
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            <div className="rounded-2xl border border-white/[0.09] bg-slate-900/75 p-5 transition hover:border-blue-400/30 sm:p-6">
              <div className="flex items-center justify-between">
                <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-500/10 text-xl">
                  ✈️
                </span>
                <span className="text-xs font-semibold uppercase tracking-[0.15em] text-slate-500">
                  Flight
                </span>
              </div>
              <h3 className="mt-5 text-lg font-bold">
                {result.selected_flight?.airline ?? "Flight option"}
              </h3>
              <p className="mt-2 text-2xl font-extrabold text-blue-300">
                {money(result.selected_flight?.price)}
              </p>
              <div className="mt-4 flex flex-wrap gap-2 text-xs text-slate-400">
                {result.selected_flight?.duration && (
                  <span className="rounded-lg bg-white/[0.04] px-3 py-2">
                    ◷ {result.selected_flight.duration}
                  </span>
                )}
                {result.selected_flight?.stops != null && (
                  <span className="rounded-lg bg-white/[0.04] px-3 py-2">
                    {result.selected_flight.stops === 0
                      ? "Non-stop"
                      : `${result.selected_flight.stops} stop(s)`}
                  </span>
                )}
              </div>
              <p className="mt-4 text-xs leading-5 text-slate-600">
                Flight prices are illustrative and require verification.
              </p>
            </div>

            <div className="rounded-2xl border border-white/[0.09] bg-slate-900/75 p-5 transition hover:border-blue-400/30 sm:p-6">
              <div className="flex items-center justify-between">
                <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-violet-500/10 text-xl">
                  🏨
                </span>
                <span className="text-xs font-semibold uppercase tracking-[0.15em] text-slate-500">
                  Stay
                </span>
              </div>
              <h3 className="mt-5 text-lg font-bold">
                {result.selected_stay?.name ?? "Accommodation option"}
              </h3>
              <p className="mt-2 text-2xl font-extrabold text-white">
                {money(result.selected_stay?.price_per_night)}
                <span className="ml-1 text-xs font-medium text-slate-500">/ night</span>
              </p>
              <div className="mt-4 space-y-2 text-sm text-slate-400">
                {result.selected_stay?.rating != null && (
                  <p>⭐ {result.selected_stay.rating}/5</p>
                )}
                {result.selected_stay?.location && (
                  <p>📍 {result.selected_stay.location}</p>
                )}
              </div>
              <p className="mt-4 text-xs leading-5 text-slate-600">
                Accommodation availability and rates are not live-verified.
              </p>
            </div>

            <div className="rounded-2xl border border-white/[0.09] bg-slate-900/75 p-5 transition hover:border-emerald-400/30 sm:p-6">
              <div className="flex items-center justify-between">
                <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-emerald-500/10 text-xl">
                  💰
                </span>
                <span className="text-xs font-semibold uppercase tracking-[0.15em] text-slate-500">
                  Budget overview
                </span>
              </div>
              <h3 className="mt-5 text-lg font-bold">Trip estimate</h3>
              <p className="mt-2 text-2xl font-extrabold text-white">
                {money(totalCost)}
              </p>

              <div className="mt-5">
                <div className="mb-2 flex justify-between gap-3 text-xs">
                  <span className="text-slate-500">Budget used</span>
                  <span className={totalCost > budgetValue ? "text-red-300" : "text-emerald-300"}>
                    {budgetPercent.toFixed(0)}%
                  </span>
                </div>
                <div
                  className="h-2 overflow-hidden rounded-full bg-white/[0.07]"
                  role="progressbar"
                  aria-label="Trip budget used"
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-valuenow={Math.round(budgetPercent)}
                >
                  <div
                    className={`h-full rounded-full transition-all ${
                      totalCost > budgetValue ? "bg-red-400" : "bg-emerald-400"
                    }`}
                    style={{ width: `${budgetPercent}%` }}
                  />
                </div>
                <p className={`mt-3 text-sm font-semibold ${
                  remaining < 0 ? "text-red-300" : "text-emerald-300"
                }`}>
                  {remaining < 0
                    ? `${money(Math.abs(remaining))} over budget`
                    : `${money(remaining)} remaining`}
                </p>
              </div>
            </div>
          </div>

          {/* Activities */}
          <Panel>
            <SectionHeading
              eyebrow="Discover"
              title="Recommended activities"
              description="Explore places selected for your interests and destination."
            />

            {Array.isArray(result.selected_activities) &&
            result.selected_activities.length > 0 ? (
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                {result.selected_activities.map((activity: any, index: number) => {
                  const category = String(activity.category ?? "").toLowerCase();
                  const icon = category.includes("history")
                    ? "🏛️"
                    : category.includes("shop")
                      ? "🛍️"
                      : category.includes("food")
                        ? "🍜"
                        : category.includes("nature")
                          ? "🌿"
                          : "📍";

                  return (
                    <article
                      key={`${activity.name ?? "activity"}-${index}`}
                      className="rounded-2xl border border-white/[0.08] bg-[#0a1020] p-5 transition hover:-translate-y-0.5 hover:border-blue-400/30"
                    >
                      <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-500/10 text-xl">
                        {icon}
                      </div>
                      <h4 className="mt-4 font-bold text-white">
                        {activity.name}
                      </h4>
                      <p className="mt-1 text-xs text-slate-500">
                        {activity.category}
                      </p>
                      <div className="mt-5 flex items-center justify-between gap-3 border-t border-white/[0.06] pt-4 text-xs">
                        <span className="text-slate-400">
                          ◷ {activity.duration}
                        </span>
                        <span className="font-semibold text-blue-300">
                          {Number(activity.price) === 0
                            ? "Free"
                            : money(activity.price)}
                        </span>
                      </div>
                    </article>
                  );
                })}
              </div>
            ) : (
              <p className="text-sm text-slate-400">No activities were returned for this trip.</p>
            )}
          </Panel>

          {/* Route */}
          <Panel>
            <SectionHeading
              eyebrow="Smart routing"
              title="Your travel route"
              description="A geographic estimate to help organize your selected stops."
            />

            <div className="flex flex-col gap-5 rounded-2xl border border-blue-400/15 bg-blue-500/[0.05] p-5 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-slate-400">Estimated route distance</p>
                <p className="mt-1 text-3xl font-black text-blue-300">
                  {result.total_route_distance_km ?? "—"}
                  <span className="ml-2 text-base font-semibold text-slate-400">km</span>
                </p>
              </div>
              <div className="max-w-lg text-xs leading-6 text-slate-400">
                <p className="font-semibold text-amber-300">⚠ Estimate, not navigation</p>
                <p className="mt-1">
                  {result.route_distance_type || "Straight-line estimate"}.
                  Actual road distances, travel times, and ferry routes may differ.
                </p>
              </div>
            </div>

            {Array.isArray(result.special_transport) &&
              result.special_transport.length > 0 && (
                <div className="mt-4 rounded-2xl border border-sky-400/15 bg-sky-500/[0.05] p-4">
                  <p className="font-semibold text-sky-200">
                    🚢 Special transport may be required
                  </p>
                  {result.special_transport.map((item: any, index: number) => (
                    <p key={index} className="mt-2 text-sm leading-6 text-slate-400">
                      <strong className="text-slate-200">{item.activity}</strong>{" "}
                      requires {item.transport}. Confirm availability and schedules before travel.
                    </p>
                  ))}
                </div>
              )}

            {Array.isArray(result.optimized_route) &&
              result.optimized_route.length > 0 && (
                <div className="mt-6 space-y-3">
                  {result.optimized_route.map((place: string, index: number) => (
                    <div
                      key={`${place}-${index}`}
                      className="flex items-center gap-4 rounded-xl border border-white/[0.07] bg-[#0a1020] p-4"
                    >
                      <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-blue-400/20 bg-blue-500/10 text-sm font-bold text-blue-300">
                        {String(index + 1).padStart(2, "0")}
                      </span>
                      <div className="min-w-0 flex-1">
                        <p className="font-semibold text-white">{place}</p>
                        <p className="mt-1 text-xs text-slate-500">
                          Stop {index + 1}
                        </p>
                      </div>
                      {index < result.optimized_route.length - 1 && (
                        <span className="text-slate-600">↓</span>
                      )}
                    </div>
                  ))}
                </div>
              )}

            {result.route_recommendation && (
              <div className="mt-5 rounded-2xl border border-violet-400/15 bg-violet-500/[0.04] p-5">
                <p className="text-xs font-bold uppercase tracking-[0.18em] text-violet-300">
                  🤖 Route analysis
                </p>
                <div className="mt-3 text-sm leading-7 text-slate-300">
                  {result.route_recommendation}
                </div>
              </div>
            )}
          </Panel>

          {/* Budget analysis */}
          <Panel>
            <SectionHeading
              eyebrow="Spend thoughtfully"
              title="Budget recommendations"
              description="Review the available analysis alongside the estimated costs above."
            />
            <div className="rounded-2xl border border-white/[0.07] bg-[#0a1020] p-5 sm:p-6">
              <div className="prose prose-invert max-w-none text-sm leading-7 text-slate-300">
                <ReactMarkdown
                  components={{
                    strong: ({ children }) => (
                      <strong className="font-semibold text-white">{children}</strong>
                    ),
                    p: ({ children }) => (
                      <p className="mb-3 last:mb-0">{children}</p>
                    ),
                    ul: ({ children }) => (
                      <ul className="my-3 list-disc space-y-2 pl-5">{children}</ul>
                    ),
                    li: ({ children }) => <li>{children}</li>,
                  }}
                >
                  {result.budget_analysis || "No budget analysis was provided."}
                </ReactMarkdown>
              </div>
            </div>
          </Panel>

          {/* Daily itinerary */}
          <Panel>
            <SectionHeading
              eyebrow="Your journey, day by day"
              title={result.itinerary?.trip_title || "Your travel itinerary"}
              description={result.itinerary?.summary}
            />

            {Array.isArray(result.itinerary?.days) &&
            result.itinerary.days.length > 0 ? (
              <div className="space-y-5">
                {result.itinerary.days.map((day: any) => (
                  <article
                    key={day.day}
                    className="overflow-hidden rounded-2xl border border-white/[0.08] bg-[#0a1020]"
                  >
                    <div className="flex flex-col justify-between gap-3 border-b border-white/[0.07] bg-white/[0.02] p-5 sm:flex-row sm:items-center">
                      <div>
                        <p className="text-xs font-bold uppercase tracking-[0.18em] text-blue-400">
                          Day {day.day}
                        </p>
                        <h4 className="mt-1 text-lg font-bold text-white">
                          {day.title}
                        </h4>
                      </div>
                      <span className="w-fit rounded-lg border border-white/[0.08] bg-white/[0.03] px-3 py-2 text-xs text-slate-400">
                        📅 {day.date}
                      </span>
                    </div>

                    {/* Weather */}
                    {day.weather && (
                      <div className="border-b border-white/[0.07] p-4 sm:p-5">
                        <div className="rounded-2xl border border-sky-400/15 bg-sky-500/[0.04] p-4 sm:p-5">
                          <div className="flex flex-col gap-5">
                            <div className="flex items-center gap-4">
                              <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-sky-400/10 text-3xl">
                                {getWeatherIcon(
                                  day.weather.condition,
                                  day.weather.rain_probability
                                )}
                              </div>
                              <div className="min-w-0">
                                <p className="text-xs font-bold uppercase tracking-[0.18em] text-sky-300">
                                  Weather forecast
                                </p>
                                <p className="mt-1 font-bold text-white">
                                  {day.weather.condition || "Weather information"}
                                </p>
                                <p className="mt-1 text-xs text-slate-500">
                                  Source: {day.weather.source || "Not specified"}
                                </p>
                              </div>
                            </div>

                            <div className="grid grid-cols-3 gap-3">
                              <div className="rounded-xl bg-black/20 p-3">
                                <p className="text-xs text-slate-500">Temperature</p>
                                <p className="mt-2 text-sm font-bold text-white sm:text-base">
                                  {day.weather.temperature != null
                                    ? `${day.weather.temperature}°C`
                                    : "Unavailable"}
                                </p>
                              </div>
                              <div className="rounded-xl bg-black/20 p-3">
                                <p className="text-xs text-slate-500">Rain chance</p>
                                <p className="mt-2 text-sm font-bold text-white sm:text-base">
                                  {day.weather.rain_probability != null
                                    ? `${day.weather.rain_probability}%`
                                    : "Unavailable"}
                                </p>
                              </div>
                              <div className="rounded-xl bg-black/20 p-3">
                                <p className="text-xs text-slate-500">Wind</p>
                                <p className="mt-2 text-sm font-bold text-white sm:text-base">
                                  {day.weather.wind ?? "Unavailable"}
                                </p>
                              </div>
                            </div>
                          </div>

                          <div className="mt-4 border-t border-white/[0.07] pt-4 text-xs leading-6 text-slate-400">
                            {day.weather.status === "unavailable" ||
                            day.weather.rain_probability == null
                              ? "Forecast data is unavailable for this date. Check a reliable forecast before planning outdoor activities."
                              : day.weather.rain_probability >= 50
                                ? "Higher rain probability. Consider indoor alternatives and check the latest forecast."
                                : day.weather.rain_probability >= 30
                                  ? "Some chance of rain. Keep your outdoor plans flexible."
                                  : "Lower rain probability in this forecast. Conditions may change, so check again before travelling."}
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Day activities */}
                    <div className="p-5 sm:p-6">
                      {Array.isArray(day.activities) &&
                      day.activities.length > 0 ? (
                        <div className="space-y-5">
                          {day.activities.map((activity: any, index: number) => (
                            <div
                              key={`${activity.title ?? "activity"}-${index}`}
                              className="flex gap-4"
                            >
                              <div className="flex shrink-0 flex-col items-center">
                                <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-500/10 text-lg">
                                  {String(activity.time ?? "")
                                    .toLowerCase()
                                    .includes("morning")
                                    ? "🌅"
                                    : String(activity.time ?? "")
                                        .toLowerCase()
                                        .includes("afternoon")
                                      ? "☀️"
                                      : "🌙"}
                                </span>
                                {index < day.activities.length - 1 && (
                                  <span className="mt-2 min-h-6 w-px flex-1 bg-white/10" />
                                )}
                              </div>

                              <div className="min-w-0 flex-1 pb-2">
                                <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                                  <div>
                                    <p className="text-xs font-semibold uppercase tracking-wider text-blue-300">
                                      {activity.time}
                                    </p>
                                    <h5 className="mt-1 text-base font-bold text-white">
                                      {activity.title}
                                    </h5>
                                  </div>
                                  <span className="w-fit rounded-lg border border-white/[0.07] bg-white/[0.03] px-3 py-1.5 text-xs font-semibold text-slate-300">
                                    {Number(activity.cost) === 0
                                      ? "Free"
                                      : money(activity.cost)}
                                  </span>
                                </div>
                                {activity.description && (
                                  <p className="mt-2 text-sm leading-6 text-slate-400">
                                    {activity.description}
                                  </p>
                                )}
                                {activity.location && (
                                  <p className="mt-3 text-xs text-slate-500">
                                    📍 {activity.location}
                                  </p>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-sm text-slate-400">
                          No activities were provided for this day.
                        </p>
                      )}
                    </div>
                  </article>
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-400">
                No daily itinerary was returned. Review the recommendations above.
              </p>
            )}
          </Panel>

          {/* Results footer */}
          <div className="flex flex-col items-center justify-center gap-3 rounded-3xl border border-white/[0.07] bg-slate-900/50 px-5 py-8 text-center">
            <span className="text-2xl">🌍</span>
            <p className="font-semibold text-white">Ready to plan another adventure?</p>
            <p className="text-sm text-slate-500">
              Adjust your destination, budget, or interests to create another plan.
            </p>
            <button
              type="button"
              onClick={resetTrip}
              className="mt-2 rounded-xl border border-blue-400/25 bg-blue-500/10 px-5 py-3 text-sm font-semibold text-blue-200 transition hover:bg-blue-500/20"
            >
              ↑ Plan another trip
            </button>
          </div>
        </section>
      )}

      {/* Footer */}
      <footer className="relative z-10 border-t border-white/[0.07]">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-3 px-5 py-7 text-center sm:flex-row sm:px-8 sm:text-left">
          <a href="#" className="font-bold tracking-tight text-slate-300">
            Trip<span className="text-blue-400">Mind</span>
          </a>
          <p className="text-xs leading-5 text-slate-600">
            AI-assisted travel planning. Prices and route distances are estimates, not confirmed bookings.
          </p>
          <a
            href="https://github.com/BhavyaSolanki31/TripMind"
            target="_blank"
            rel="noreferrer"
            className="text-xs font-medium text-slate-400 transition hover:text-blue-300"
          >
            View source on GitHub ↗
          </a>
        </div>
      </footer>
    </main>
  );
}

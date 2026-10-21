
# ✈️ TripMind — Multi-Agent AI Travel Planner

TripMind is a travel-planning application that generates budget-aware itineraries using specialized agents for flights, accommodation, activities, weather, budget analysis, and route optimization.

Users enter their origin, destination, travel dates, group size, budget, and interests. TripMind returns a structured trip plan with estimated expenses, daily activities, weather information, and route recommendations.

## ✨ Features

- **Trip Planning:** Generate itineraries based on destination, dates, travelers, and interests.
- **Flight Recommendations:** Display a selected flight with airline, estimated price, duration, and stops.
- **Accommodation Planning:** Include hotel recommendations and estimated nightly costs.
- **Activity Recommendations:** Suggest places and activities based on user interests.
- **Budget Analysis:** Calculate flight, hotel, and activity costs and show the remaining budget.
- **Weather Forecasts:** Retrieve daily forecast data through the Open-Meteo API, with graceful handling of unavailable forecasts.
- **Route Optimization:** Organize selected attractions into a recommended visit sequence and provide an estimated geographic distance.
- **Daily Itinerary:** Combine travel, check-in, sightseeing, and check-out into a day-by-day plan.
- **Input Validation:** Validate trip details and reject invalid dates, traveler counts, budgets, and other invalid inputs.
- **Automated Tests:** Test API behavior, input validation, budget calculations, and weather handling.

## 🏗️ Architecture

```text
User
  |
  v
Next.js Frontend
  |
  v
FastAPI Backend
  |
  v
Trip Orchestrator
  |
  +--> Flight Agent
  |
  +--> Stay Agent
  |
  +--> Activity Agent
  |
  +--> Weather Tool
  |
  +--> Budget Calculator
  |
  +--> Route Optimizer
  |
  v
Itinerary Generation
  |
  v
Structured Trip Response
  |
  v
Frontend Results
```

The frontend collects trip preferences and sends a request to the FastAPI backend. The backend coordinates trip-planning components, calculates estimated expenses, retrieves available weather data, and returns a structured itinerary for display.

## 🛠️ Tech Stack

### Backend
- Python
- FastAPI
- Pydantic
- LangGraph
- Uvicorn
- Pytest

### Frontend
- Next.js
- React
- TypeScript
- Tailwind CSS
- React Markdown

### Data and APIs
- Open-Meteo Forecast API
- Mock travel data for flight, hotel, and activity recommendations

## 📁 Project Structure

```text
TripMind/
├── agents/                  # Specialized planning agents
├── api/                     # FastAPI application
├── database/                # Database-related components
├── frontend/                # Next.js user interface
├── models/                  # Request and data models
├── orchestrator/             # Agent orchestration
├── outputs/                 # Generated outputs
├── tests/                   # Automated tests
├── tools/                   # Budget, weather, and utility tools
├── .env                     # Local environment variables
├── .gitignore
├── README.md
└── trip_result.json
```

## 🚀 Getting Started

### Prerequisites

- Python 3.12 or a compatible Python version
- Node.js and npm
- Git

### 1. Clone the repository

```bash
git clone https://github.com/BhavyaSolanki31/TripMind.git
cd TripMind
```

### 2. Set up the Python environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the backend dependencies using the dependency file available in the project. If a root `requirements.txt` has not been created yet, install the project's required packages before starting the backend.

### 3. Configure environment variables

Create a local `.env` file if required by your configuration. Add the necessary API keys for any enabled AI integrations.

Never commit API keys, passwords, or other secrets to GitHub.

### 4. Start the backend

From the project root:

```powershell
uvicorn api.main:app --reload
```

The API should be available at:

- API root: http://127.0.0.1:8000/
- Interactive API documentation: http://127.0.0.1:8000/docs

### 5. Start the frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 in your browser.

## 🔌 API Usage

### `POST /plan-trip`

Example request:

```json
{
  "origin": "Delhi",
  "destination": "Mumbai",
  "start_date": "2026-10-22",
  "end_date": "2026-10-25",
  "travelers": 2,
  "total_budget": 50000,
  "interests": [
    "historical places",
    "beaches",
    "food",
    "shopping"
  ]
}
```

The response includes the selected flight, accommodation, activities, estimated budget, route recommendations, weather data, and daily itinerary.

Use the interactive API documentation at `/docs` to submit requests and inspect the response schema.

## 🧪 Testing

Run the automated test suite from the project root:

```powershell
python -m pytest -q
```

The current test suite has **34 passing tests** covering the existing API, model validation, budget calculation, and weather behavior.

Run the weather tool independently with:

```powershell
python -m tools.weather_search
```

Run the budget calculator independently with:

```powershell
python -m tools.budget_calculator
```

## ⚠️ Current Limitations

- Flight, hotel, and activity recommendations use mock data and are not live booking offers.
- Prices are estimates and should not be treated as confirmed quotes.
- Weather forecasts may be unavailable outside the supported forecast window or when the API cannot return data.
- Route distances are geographic estimates, not verified road distances or complete travel times.
- Special transport, such as ferries, requires separate confirmation of schedules and availability.
- AI-powered planning depends on the configured model and its availability; deterministic fallback behavior may be used.

## 🔮 Future Improvements

- Integrate live flight and accommodation providers.
- Improve itinerary personalization and agent coordination.
- Add verified road routing, travel times, and public transport options.
- Add persistent trip history and saved itineraries.
- Expand automated tests and add frontend integration tests.
- Improve deployment, monitoring, and production configuration.

## 👩‍💻 Author

**Bhavya Solanki**

GitHub: [BhavyaSolanki31](https://github.com/BhavyaSolanki31)

---

Built as a multi-agent AI travel-planning project.

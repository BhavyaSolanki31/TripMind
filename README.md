
# TripMind — Multi-Agent AI Travel Planner

TripMind is a multi-agent travel planning application that generates personalized, budget-aware itineraries based on a user's destination, travel dates, budget, number of travelers, and interests.

The project uses specialized agents coordinated through LangGraph, a FastAPI backend, and a Next.js frontend to bring flight search, accommodation recommendations, activities, weather information, route estimates, and budget analysis into one workflow.

## Features

- **Multi-Agent Architecture:** Coordinates specialized agents for flights, stays, activities, budgeting, weather, route estimation, and itinerary generation.
- **Flight Recommendations:** Provides flight options based on the trip details.
- **Stay Recommendations:** Suggests accommodation options and estimates lodging costs.
- **Activity Planning:** Recommends activities based on the destination and user interests.
- **Budget Analysis:** Calculates estimated trip expenses and compares them with the user's budget.
- **Weather Information:** Retrieves available forecasts using the Open-Meteo API.
- **Route Estimation:** Estimates distances between selected locations.
- **AI Integration:** Supports Gemini-powered generation through the Google GenAI SDK, with a deterministic fallback.
- **Interactive Web Interface:** Lets users enter trip details and view the resulting itinerary.
- **Input Validation:** Validates trip requests and budget calculations.
- **Automated Tests:** Includes tests for API behavior, trip validation, budget calculations, and weather handling.

## Architecture

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
              LangGraph Orchestrator
                      |
       +--------------+--------------+
       |              |              |
       v              v              v
  Flight Agent    Stay Agent    Activity Agent
       |              |              |
       +--------------+--------------+
                      |
       +--------------+--------------+
       |              |              |
       v              v              v
  Budget Agent    Weather Agent   Route Agent
                      |
                      v
               Itinerary Agent
                      |
                      v
             Trip Plan and Results
```

The orchestrator coordinates the agents and combines their outputs into a trip plan. The exact execution flow is implemented in the backend graph.

## Tech Stack

### Backend
- Python
- FastAPI
- Uvicorn
- LangGraph
- Pydantic
- Google GenAI SDK
- python-dotenv

### Frontend
- Next.js
- React
- TypeScript
- Tailwind CSS

### External Services
- Open-Meteo API for weather forecasts
- Gemini API for optional AI-powered generation

### Testing
- pytest
- FastAPI TestClient
- httpx

## Project Structure

```text
TripMind/
├── agents/
│   ├── budget_agent.py
│   ├── flight_agent.py
│   ├── stay_agent.py
│   ├── activity_agent.py
│   ├── weather_agent.py
│   ├── route_agent.py
│   └── itinerary_agent.py
├── api/
│   └── main.py
├── database/
├── frontend/
│   ├── app/
│   └── package.json
├── models/
│   ├── llm.py
│   └── trip.py
├── orchestrator/
│   └── trip_graph.py
├── outputs/
├── tests/
│   ├── test_api.py
│   ├── test_budget_calculator.py
│   ├── test_trip_model.py
│   └── test_weather_search.py
├── tools/
│   ├── budget_calculator.py
│   ├── flight_search.py
│   ├── stay_search.py
│   ├── route_optimizer.py
│   └── weather_search.py
├── .env                  # Local secrets; do not commit
├── .gitignore
├── requirements.txt
├── README.md
└── trip_result.json
```

*Note: The structure above highlights the main project files. Additional files may exist in individual directories.*

## Getting Started

### Prerequisites

- Python 3.12 or a compatible Python version
- Node.js and npm
- Git
- A Gemini API key only if using the Gemini-powered functionality

### 1. Clone the Repository

```bash
git clone https://github.com/BhavyaSolanki31/TripMind.git
cd TripMind
```

### 2. Create a Python Virtual Environment

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Backend Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory.

Add your Gemini API key using the exact environment variable name read by `models/llm.py`.

Keep `.env` private. Never commit API keys or other credentials to GitHub.

The application can use its deterministic fallback when AI generation is disabled or unavailable, depending on the configured application behavior.

### 5. Start the Backend

From the project root, run:

```bash
uvicorn api.main:app --reload
```

The API should be available at:

- **API base URL:** http://127.0.0.1:8000
- **Interactive API documentation:** http://127.0.0.1:8000/docs

### 6. Start the Frontend

Open a second terminal and navigate to the frontend directory:

```bash
cd frontend
npm install
npm run dev
```

Open:

http://localhost:3000

Keep the backend running while using the frontend.

## API Usage

TripMind exposes a `POST /plan-trip` endpoint for generating a trip plan.

### Example Request

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

### Example with curl

```bash
curl -X POST "http://127.0.0.1:8000/plan-trip" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "Delhi",
    "destination": "Mumbai",
    "start_date": "2026-10-22",
    "end_date": "2026-10-25",
    "travelers": 2,
    "total_budget": 50000,
    "interests": ["historical places", "beaches", "food", "shopping"]
  }'
```

The response contains the generated trip plan and the available flight, accommodation, activity, budget, route, weather, and itinerary information.

Use the interactive API documentation at `/docs` to inspect the request schema and response structure.

## Running Tests

Run the test suite from the project root with the virtual environment activated:

```bash
python -m pytest -q
```

The current development test suite has **34 passing tests**. Test results may change as the project evolves.

## Current Limitations

- **Mock Travel Data:** Flight, accommodation, and activity options are based on mock project data rather than verified live booking inventory.
- **Estimated Routes:** Route distances are estimates, not verified road, walking, or ferry navigation routes. Some destinations may require separate transport, such as a ferry.
- **Weather Availability:** Forecasts depend on the Open-Meteo service and its forecast horizon. Weather data may be unavailable for past dates, invalid dates, or dates outside the supported forecast window.
- **AI Availability:** Gemini-powered generation depends on configuration, network access, API quotas, and service availability. The deterministic fallback may produce different results.
- **Cost Estimates:** Prices are illustrative estimates and should not be treated as confirmed booking prices.

## Future Improvements

- Integrate live flight and hotel inventory from authorized travel APIs.
- Add maps and real route-distance calculations.
- Improve activity ranking and personalization.
- Add persistent user preferences and saved itineraries.
- Expand automated tests and integration coverage.
- Add deployment, monitoring, and production configuration.
- Improve budget allocation and recommendations for different traveler profiles.

## Author

**Bhavya Solanki**

- GitHub: [BhavyaSolanki31](https://github.com/BhavyaSolanki31)
- Project Repository: [TripMind](https://github.com/BhavyaSolanki31/TripMind)

---

*TripMind is a portfolio project exploring multi-agent orchestration, API development, AI integration, and personalized travel planning.*

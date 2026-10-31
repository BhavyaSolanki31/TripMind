# ✈️ TripMind — Multi-Agent AI Travel Planner

<p align="center">
  <strong>Your next adventure, thoughtfully planned.</strong>
</p>

<p align="center">
  An AI-assisted travel planning application that brings personalized itineraries, budget analysis, activity recommendations, weather information, and route estimation together through a coordinated multi-agent architecture.
</p>

<p align="center">
  <a href="https://thetripmind.vercel.app"><strong>🌍 Live Demo</strong></a> ·
  <a href="https://tripmind-u1qu.onrender.com/docs"><strong>📚 API Documentation</strong></a> ·
  <a href="https://github.com/BhavyaSolanki31/TripMind"><strong>💻 GitHub Repository</strong></a>
</p>

---

## 🚀 Project Overview

TripMind is a multi-agent AI travel planning application that generates personalized, budget-aware itineraries based on a user's destination, travel dates, budget, number of travelers, and interests.

The application uses specialized agents coordinated through **LangGraph**, a **FastAPI** backend, and a **Next.js** frontend to combine flight recommendations, accommodation suggestions, activities, weather information, route estimates, and budget analysis into one workflow.

## ✨ Key Features

- **Multi-Agent Architecture:** Coordinates specialized agents for flights, stays, activities, budgeting, weather, route estimation, and itinerary generation.
- **Flight Recommendations:** Provides flight options based on trip details and traveler count.
- **Stay Recommendations:** Suggests accommodation options and estimates lodging costs.
- **Personalized Activity Planning:** Recommends activities based on destination and selected interests.
- **Smart Budget Analysis:** Calculates estimated expenses, category-wise allocations, and remaining budget.
- **Weather Integration:** Retrieves available weather forecasts through the Open-Meteo API, with graceful handling when forecasts are unavailable.
- **Route Estimation:** Estimates distances between selected activity locations.
- **AI Integration:** Supports Gemini-powered generation through the Google GenAI SDK, with deterministic fallback functionality.
- **Interactive Frontend:** Provides a responsive interface for entering trip details and exploring generated itineraries.
- **Automated Testing:** Includes tests for API behavior, trip validation, budget calculations, and weather handling.

## 🏗️ System Architecture

```text
                         USER
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
          +----------------+----------------+
          |                |                |
          v                v                v
     Flight Agent      Stay Agent      Activity Agent
          |                |                |
          +----------------+----------------+
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
     Budget Agent     Weather Agent     Route Agent
          |                |                |
          +----------------+----------------+
                           |
                           v
                    Itinerary Agent
                           |
                           v
                  Generated Trip Plan
```

The LangGraph orchestrator coordinates specialized agents and combines their outputs into a structured trip plan.

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Backend | FastAPI, Uvicorn |
| Agent Orchestration | LangGraph |
| Data Validation | Pydantic |
| AI Integration | Google GenAI SDK, Gemini |
| Frontend | Next.js, React, TypeScript |
| Styling | Tailwind CSS |
| Weather Service | Open-Meteo API |
| Testing | pytest, FastAPI TestClient, httpx |
| Backend Deployment | Render |
| Frontend Deployment | Vercel |
| Version Control | Git, GitHub |

## 📂 Project Structure

```text
TripMind/
│
├── agents/
│   ├── budget_agent.py
│   ├── flight_agent.py
│   ├── stay_agent.py
│   ├── activity_agent.py
│   ├── weather_agent.py
│   ├── route_agent.py
│   └── itinerary_agent.py
│
├── api/
│   └── main.py
│
├── database/
│
├── frontend/
│   ├── app/
│   └── package.json
│
├── models/
│   ├── llm.py
│   └── trip.py
│
├── orchestrator/
│   └── trip_graph.py
│
├── outputs/
│
├── tests/
│   ├── test_api.py
│   ├── test_budget_calculator.py
│   ├── test_trip_model.py
│   └── test_weather_search.py
│
├── tools/
│   ├── budget_calculator.py
│   ├── flight_search.py
│   ├── stay_search.py
│   ├── route_optimizer.py
│   └── weather_search.py
│
├── .gitignore
├── requirements.txt
├── README.md
└── trip_result.json
```

*Note: This structure highlights the main project files. Additional files may exist in individual directories.*

## 🌐 Live Deployment

TripMind is deployed using separate frontend and backend services.

| Component | Platform | Link |
|---|---|---|
| Frontend | Vercel | https://thetripmind.vercel.app |
| Backend API | Render | https://tripmind-u1qu.onrender.com |
| API Documentation | FastAPI Swagger UI | https://tripmind-u1qu.onrender.com/docs |
| Source Code | GitHub | https://github.com/BhavyaSolanki31/TripMind |

### Deployment Architecture

```text
             GitHub Repository
                     |
                     |
          +----------+----------+
          |                     |
          v                     v
     Vercel Frontend       Render Backend
       (Next.js)              (FastAPI)
          |                     |
          +----------API--------+
                     |
                     v
              TripMind Agents
                     |
                     v
               Trip Results
```

## ⚙️ Getting Started

### Prerequisites

- Python 3.12 or a compatible Python version
- Node.js and npm
- Git
- A Gemini API key if using Gemini-powered functionality

### 1. Clone the Repository

```bash
git clone https://github.com/BhavyaSolanki31/TripMind.git
cd TripMind
```

### 2. Create a Python Virtual Environment

**Windows PowerShell**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install Backend Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root.

Add your Gemini API key using the exact environment variable name expected by `models/llm.py`.

Keep `.env` private. Never commit API keys or credentials to GitHub.

The application supports deterministic fallback behavior when AI generation is disabled or unavailable, depending on the configured application behavior.

### 5. Start the Backend

From the project root:

```bash
uvicorn api.main:app --reload
```

Backend URLs:

- API: http://127.0.0.1:8000
- Interactive documentation: http://127.0.0.1:8000/docs

### 6. Start the Frontend

Open a second terminal:

```bash
cd frontend
npm install
```

Create a `.env.local` file inside the `frontend` directory:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

Start the development server:

```bash
npm run dev
```

Open http://localhost:3000.

Keep the backend running while using the frontend.

## 🔌 API Usage

TripMind exposes a `POST /plan-trip` endpoint to generate personalized trip plans.

### Example Request

```json
{
  "origin": "Delhi",
  "destination": "Mumbai",
  "start_date": "2026-11-01",
  "end_date": "2026-11-04",
  "travelers": 2,
  "total_budget": 50000,
  "interests": [
    "Food",
    "Shopping",
    "Nature"
  ]
}
```

### Example cURL Request

```bash
curl -X POST "http://127.0.0.1:8000/plan-trip" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "Delhi",
    "destination": "Mumbai",
    "start_date": "2026-11-01",
    "end_date": "2026-11-04",
    "travelers": 2,
    "total_budget": 50000,
    "interests": ["Food", "Shopping", "Nature"]
  }'
```

The response contains:

- Selected flight
- Recommended accommodation
- Personalized activities
- Optimized activity sequence
- Estimated route distance
- Budget breakdown and analysis
- Available weather information
- Day-wise itinerary

Visit the [interactive API documentation](https://tripmind-u1qu.onrender.com/docs) to inspect the request schema and response structure.

## 🧪 Testing

Run the automated test suite from the project root:

```bash
python -m pytest -q
```

**Latest verified result: 34 tests passed.**

The test suite covers API behavior, trip request validation, budget calculations, and weather handling.

## ⚠️ Current Limitations

- **Mock Travel Data:** Flight and accommodation listings use mock project data rather than verified live booking inventory. Activity recommendations also use project-defined data.
- **Estimated Routes:** Route distances are estimates, not verified road, walking, or ferry navigation routes. Special transport may require separate arrangements.
- **Weather Availability:** Weather forecasts depend on the Open-Meteo service, its forecast horizon, and request availability. Rate limiting or service errors can result in unavailable weather information. Trip generation can continue using graceful fallback responses.
- **AI Availability:** Gemini-powered generation depends on API configuration, network access, quotas, and service availability.
- **Illustrative Costs:** Prices are estimates and should not be treated as confirmed booking prices.

## 🔮 Future Improvements

- Integrate live flight and hotel inventory through authorized travel APIs.
- Improve weather reliability and fallback mechanisms.
- Add interactive maps and real route-distance calculations.
- Improve activity ranking and personalization.
- Introduce persistent user preferences and saved itineraries.
- Expand automated testing and integration coverage.
- Improve budget allocation and recommendations for different traveler profiles.
- Add monitoring and enhanced production observability.

## 👩‍💻 Author

**Bhavya Solanki**

- GitHub: [BhavyaSolanki31](https://github.com/BhavyaSolanki31)
- Project Repository: [TripMind](https://github.com/BhavyaSolanki31/TripMind)
- Live Application: [thetripmind.vercel.app](https://thetripmind.vercel.app)

---

<p align="center">
  <strong>TripMind — Travel smarter, explore farther. ✈️</strong>
</p>

<p align="center">
  A portfolio project exploring multi-agent orchestration, AI integration, API development, and personalized travel planning.
</p>

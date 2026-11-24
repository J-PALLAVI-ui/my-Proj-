# FujiNova (富士ノヴァ) — AI Tourism OS for Mount Fuji & Yamanashi

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3+-61DAFB.svg?style=flat&logo=react)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-5.4+-646CFF.svg?style=flat&logo=vite)](https://vitejs.dev/)
[![Three.js](https://img.shields.io/badge/Three.js-Digital--Twin-black.svg?style=flat&logo=three.js)](https://threejs.org/)
[![SQLite](https://img.shields.io/badge/SQLite-WAL--Mode-003B57.svg?style=flat&logo=sqlite)](https://www.sqlite.org/)
[![GTFS-JP](https://img.shields.io/badge/GTFS--JP-Fujikyu--Transit-blue.svg?style=flat)](https://www.fujikyu.co.jp/)

FujiNova is a full-stack, location-aware, crowd-sensitive tourism operating system for Mount Fuji, the Fuji Five Lakes (*Fujigoko*), and Yamanashi Prefecture, Japan. Its conversational AI travel companion is **Hana (華 / 伴)**.

---

## 🌟 Key Application Features

1. **Hana AI Agent (Conversational Travel Companion)**
   - Streaming Server-Sent Events (SSE) chat with profile extraction.
   - Dual-engine architecture: supports OpenAI (`gpt-4o-mini`, `gpt-4o`) and Google Gemini (`gemini-2.0-flash`, `gemini-3.8-flash`) with automatic rate-limit backoff and graceful failover.
   - Strict factual grounding in verified database records, preventing travel hallucinations.

2. **Bicriteria RAPTOR Public Transit Routing**
   - Direct integration with official Fujikyu Bus GTFS-JP feeds and the Fujikyu Railway Official Timetable (Rev. March 14, 2026).
   - Multimodal routing (train + bus + walking links) with exact timetable departure/arrival times, stops, and JPY fare calculations.

3. **CrowdSense System**
   - Real-time and simulated crowd density analysis across all 35 verified Fuji destinations.
   - Intelligent alternative recommendations that calculate crowd reduction percentage, distance, and preserve scenic Mount Fuji views.

4. **Adaptive Itinerary Planning**
   - Multi-day trip scheduling respecting traveler mobility constraints, pace, budget, and weather conditions.

5. **Live Region Intelligence & Digital Twin**
   - Verified seasonal weather, temperature ranges, and Mount Fuji visibility probabilities.
   - Interactive 3D Digital Twin map visualization powered by Three.js.

---

## 🏗️ System Architecture

```
FujiNova/
├── backend/
│   ├── app/
│   │   ├── agent/                 # Hana AI agent implementation (LangGraph/LangChain)
│   │   ├── api/                   # FastAPI routes (chat, crowd, routing, places, travel, health)
│   │   ├── core/                  # Database connection (SQLite WAL) and configuration
│   │   ├── models/                # Pydantic data schemas (place, traveller, crowd, transit)
│   │   └── services/              # Business logic:
│   │       ├── crowd/             # CrowdSense engine & alternative recommendation service
│   │       ├── itinerary/         # Multi-day itinerary generator
│   │       ├── live_info/         # Weather and travel advisory services
│   │       ├── llm/               # Model Router (OpenAI SDK & Google GenAI SDK adapters)
│   │       ├── rag/               # Regional knowledge base & retriever
│   │       └── routing/           # RAPTOR routing engine, GTFS loader, timetable models
│   ├── data/                      # 35 verified places dataset & seed script
│   ├── tests/                     # 54 comprehensive pytest unit & integration tests
│   └── requirements.txt           # Python dependencies
├── data/
│   └── gtfs/                      # Official Fujikyu Bus GTFS-JP feeds
├── frontend/
│   ├── src/
│   │   ├── components/            # React UI components (HanaWorkspace, CrowdDashboard, DigitalTwin3D, etc.)
│   │   ├── config.ts              # Centralized API configuration (supports local proxy & production URL)
│   │   ├── types/                 # TypeScript interfaces
│   │   └── App.tsx                # Main application view with 5 distinct workspaces
│   ├── package.json               # Node.js dependencies
│   └── vite.config.ts             # Vite development server & reverse proxy configuration
├── START_FUJINOVA.bat             # One-click Windows startup system
├── STOP_FUJINOVA.bat              # One-click clean shutdown script
├── RUN_FUJINOVA_GUIDE.md          # User-friendly Windows running guide
└── README.md                      # Complete project documentation
```

---

## 🚀 One-Click Windows Startup (Easiest Way)

You do **not** need to open multiple command prompts or run manual commands:

1. **Double-click `START_FUJINOVA.bat`** in the project root.
2. The launcher automatically:
   - Detects Python and Node.js.
   - Creates the virtual environment (`.venv`) if missing.
   - Installs backend dependencies if needed.
   - Installs frontend packages (`npm install`) if needed.
   - Sets up `.env` from `.env.example` without overwriting existing settings.
   - Initializes and seeds the SQLite database (`fujinova.db`).
   - Starts the FastAPI backend on `http://127.0.0.1:8000`.
   - Starts the React/Vite frontend on `http://localhost:5173`.
   - Verifies backend health and opens the web application in your default browser.

3. **To safely stop FujiNova:**
   - Double-click **`STOP_FUJINOVA.bat`**.

---

## 🛠️ Manual Development Setup

If you prefer running commands manually:

### Prerequisites
- Python 3.11, 3.12, 3.13, or 3.14 (64-bit)
- Node.js (v18+ or v20+ LTS recommended)
- Git

### Backend Setup

```cmd
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r backend\requirements.txt

# Initialize database
python -c "from backend.app.core.database import init_db; from backend.data.seed_places import seed_database; init_db(); seed_database()"

# Start FastAPI server
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend Setup

```cmd
cd frontend
npm install
npm run dev
```

Visit:
- **Frontend:** [http://localhost:5173](http://localhost:5173)
- **Backend API Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Backend Health Check:** [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)

---

## 🔑 AI Provider Configuration (.env)

FujiNova runs out of the box with intelligent fallback answers even if no API key is supplied. To enable live generative AI responses from Hana:

Open `.env` in the root folder and configure your preferred provider:

### Option A: OpenAI (Default)
```ini
FUJINOVA_PRIMARY_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini
```

### Option B: Google Gemini
```ini
FUJINOVA_PRIMARY_PROVIDER=google
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-2.0-flash
```

---

## 🧪 Testing and Verification

### Backend Tests (54 Automated Pytest Tests)
```cmd
.venv\Scripts\python.exe -m pytest backend/tests -v
```
All 54 tests pass, covering:
- Health & metadata endpoints
- Database initialization, WAL mode & 35 verified seed places
- LLM failover policies, rate limits, and fallback streaming
- RAPTOR GTFS-JP bus and railway timetable routing
- CrowdSense deterministic scenarios and recommendations
- Multi-day itinerary generation and conversation persistence

### Frontend Tests (Vitest & Production Build)
```cmd
cd frontend
npm run test
npm run build
```
- Vitest suite: 5 test files, 16 unit tests passing.
- Production build: TypeScript validation passed (`tsc --noEmit`), bundles cleanly into `dist/`.

---

## 🔒 Security Best Practices
- `.env` and local databases (`fujinova.db`) are strictly excluded via `.gitignore`.
- `.env.example` contains only placeholder values.
- Never commit private API keys or personal access tokens to GitHub.

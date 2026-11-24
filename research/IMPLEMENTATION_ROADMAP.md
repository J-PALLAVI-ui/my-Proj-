# FUJINOVA — Incremental Implementation Roadmap (Stages 0 to 6)

**Document Version:** 1.0.0  
**Status:** COMPLETE (Stage 0 Discovery)  
**Execution Paradigm:** Strict Test-Driven & Incremental Verification (No implementation proceeds without prior stage sign-off)  
**Author:** FujiNova Technical Project Lead & Engineering Manager  

---

## 1. Roadmap Architecture & Milestone Overview

```
+-----------------------------------------------------------------------------------------+
| [STAGE 0] COMPLETE RESEARCH & PROJECT DISCOVERY (Current Milestone)                     |
| Complete all 10 discovery reports, verify datasets, establish zero-hallucination rules. |
+-----------------------------------------------------------------------------------------+
                                             |
                                    [USER APPROVAL GATE]
                                             v
+-----------------------------------------------------------------------------------------+
| [STAGE 1] DATA ENGINEERING & LOCAL REPOSITORY INITIALIZATION                            |
| Ingest Fujikyu GTFS-JP, JR GTFS, compile 250+ Yamanashi POIs into SQLite with R*Tree.   |
+-----------------------------------------------------------------------------------------+
                                             |
                                             v
+-----------------------------------------------------------------------------------------+
| [STAGE 2] DETERMINISTIC TRANSIT & SPATIAL MICROSERVICES                                 |
| Implement embedded Python RAPTOR router, hybrid POI recommender, and HMAC QR authority. |
+-----------------------------------------------------------------------------------------+
                                             |
                                             v
+-----------------------------------------------------------------------------------------+
| [STAGE 3] AI AGENT RUNTIME & DYNAMIC INTERVIEW WORKFLOW                                 |
| Implement LangGraph StateGraph, Traveller Profile schema, Gemini 2.5 Flash tool binding.|
+-----------------------------------------------------------------------------------------+
                                             |
                                             v
+-----------------------------------------------------------------------------------------+
| [STAGE 4] FRONTEND APPLICATION & MAPLIBRE WEBGL EXPERIENCE                              |
| Build React/Vite SPA, MapLibre 3D map, streaming chat interface, and QR voucher scanner.|
+-----------------------------------------------------------------------------------------+
                                             |
                                             v
+-----------------------------------------------------------------------------------------+
| [STAGE 5] END-TO-END SYSTEM INTEGRATION & ADAPTIVE RE-ROUTING                           |
| Wire frontend to LangGraph SSE, test sudden weather/crowd disruptions & dynamic re-route|
+-----------------------------------------------------------------------------------------+
                                             |
                                             v
+-----------------------------------------------------------------------------------------+
| [STAGE 6] VERIFICATION, BENCHMARKING & PRODUCTION AUDIT                                 |
| Measure sub-500ms TTFT, zero route hallucinations, security audit of QR tokens.        |
+-----------------------------------------------------------------------------------------+
```

---

## 2. Stage-by-Stage Detailed Work Breakdown

### STAGE 0: Complete Research and Project Discovery (CURRENT STAGE)
* **Goal:** Thoroughly research models, datasets, transit feeds, open-source projects, and constraints before writing a single line of application code.
* **Key Deliverables:** 10 comprehensive markdown documents in `/research/`.
* **Exit Gate:** Complete presentation to user and explicit authorization to proceed to Stage 1.

---

### STAGE 1: Data Engineering, GTFS Ingestion & Local Database Setup
* **Objective:** Establish the deterministic ground-truth data layer. Clean, validate, and store all regional POIs and transit feeds locally.
* **Inputs:** 
  - Fujikyu Bus GTFS-JP (`bus.fujikyu.co.jp`)
  - JR East GTFS (`ckan.odpt.org`)
  - Yamanashi Prefecture Open Data (`dataplatform-yamanashi.jp`)
  - OpenStreetMap Overpass extraction for Fuji Five Lakes
* **Tasks:**
  1. Build Python ETL script (`scripts/ingest_gtfs.py`) to parse, validate, and load stops, routes, calendar, and stop_times into SQLite.
  2. Build POI curation pipeline (`scripts/ingest_places.py`) merging official Yamanashi datasets with OSM tags (opening hours, fees, stairs/wheelchair accessibility).
  3. Initialize SQLite database with WAL mode and `R*Tree` spatial index for coordinate queries.
  4. Create static verification tests ensuring 100% of major attractions (Chureito, Oishi Park, Saiko Nenba, Mt. Fuji 5th Stn) resolve to valid coordinates and nearby transit stops.
* **Exit Criteria:** `pytest` suite passes verifying zero broken foreign keys in GTFS tables and accurate geospatial spatial indexing.

---

### STAGE 2: Deterministic Engines (Routing, Recommendation & QR Security)
* **Objective:** Build isolated, deterministic backend microservices with zero LLM dependence.
* **Tasks:**
  1. **Python RAPTOR Engine:** Implement the round-based transit router. Test queries like:
     - `Shinjuku -> Kawaguchiko` (Outputs: Fuji Excursion direct or Chuo Line Ltd Express + Fujikyu Rail transfer at Otsuki).
     - `Kawaguchiko Station -> Oishi Park` (Outputs: Fujikyu Bus Red Line, Stop 1 to Stop 20, 28 minutes, ¥500).
  2. **Hybrid POI Recommender:** Implement content-based feature matching (interests, accessibility, pace) with spatial distance decay and diversity re-ranking.
  3. **Live Sensor Connectors:** JMA weather forecast parser and JARTIC national highway traffic volume client.
  4. **Cryptographic Demonstration Voucher Authority:** HMAC-SHA256 token generator, verification logic, and database-backed anti-replay nonce tracking.
* **Exit Criteria:** RAPTOR router returns bicriteria Pareto-optimal journeys in < 10 ms; QR voucher validation correctly rejects forged signatures and double-spend attempts.

---

### STAGE 3: Conversational AI Agent Core (LangGraph & Hana Persona)
* **Objective:** Implement Hana's adaptive interview workflow using LangGraph.
* **Tasks:**
  1. Define the `TravellerProfile` Pydantic state schema.
  2. Configure `StateGraph` nodes:
     - `IntentExtractor`: Parses user input into profile slots.
     - `CompletenessEvaluator`: Checks if enough information exists to propose an itinerary, or selects the single highest-value follow-up question.
     - `ToolOrchestrator`: Invokes deterministic services (`get_transit_route`, `find_places`, `check_weather`).
     - `ResponseSynthesizer`: Formulates Hana's polite, grounded conversational output.
  3. Bind Google Gemini 2.5 Flash via `google-genai` SDK with OpenAI GPT-4o-mini automatic fallback on HTTP 429/5xx.
  4. Attach LangGraph `SqliteSaver` checkpointer for persistent multi-turn thread memory.
* **Exit Criteria:** Agent successfully conducts an organic, non-scripted interview without repeating questions or hallucinating fake bus numbers.

---

### STAGE 4: Frontend Development & MapLibre WebGL Integration
* **Objective:** Build a responsive, mobile-first Web interface optimized for travellers.
* **Tasks:**
  1. Initialize React 18 + Vite + TypeScript application with Tailwind CSS and Radix UI.
  2. Integrate **MapLibre GL JS** with vector basemap (OpenFreeMap / PMTiles). Render 3D terrain pitch and interactive POI markers.
  3. Build the conversational chat drawer with real-time markdown streaming via Server-Sent Events (SSE).
  4. Build dynamic itinerary visualizer displaying day-by-day transit cards, walking segments, transfer alerts, and provenance badges.
  5. Build HTML5 QR code scanner and voucher presentation modal with clear "DEMONSTRATION ONLY" watermarks.
* **Exit Criteria:** App loads in < 1.2 seconds, renders 60 FPS vector map interactions on mobile browsers, and passes Lighthouse accessibility checks.

---

### STAGE 5: Full System Integration & Adaptive Re-Routing
* **Objective:** Connect frontend to backend and validate end-to-end user journeys under changing conditions.
* **Tasks:**
  1. Implement FastAPI SSE endpoint (`/api/v1/chat/stream`) streaming Hana's tokens and tool invocation events to the React UI.
  2. Implement **Dynamic Adaptation Simulation**:
     - Inject simulated weather event: Mount Fuji summit 100% cloud cover.
     - Verify Hana proactively alerts the traveller and suggests indoor cultural alternatives (e.g., Itchiku Kubota Art Museum) with revised bus timetables.
  3. Validate geolocation flow: manual location picker works seamlessly when browser GPS permission is denied.
* **Exit Criteria:** Successful end-to-end execution of the complete user journey walkthrough described in `PROJECT_VISION.md`.

---

### STAGE 6: Verification, Performance Profiling & Acceptance Audit
* **Objective:** Comprehensive audit against all strict engineering principles.
* **Audit Items:**
  1. **Hallucination Audit:** Automated test executing 50 diverse travel queries; verify 100% of mentioned bus lines, train stations, and fares match the GTFS database exactly.
  2. **Latency Profiling:** Measure Time to First Token (TTFT < 600 ms) and RAPTOR routing computation (< 10 ms).
  3. **Security Audit:** Confirm no PII is logged to disk, no biometric/facial recognition tools exist, and all QR vouchers are tamper-proof.
  4. **Hardware Verification:** Confirm memory usage under 10 GB total RAM and zero crashes on Windows 11 host.
* **Exit Criteria:** Final Acceptance Report signed off.

# FUJINOVA — Recommended Technology Stack & Engineering Specifications

**Document Version:** 1.0.0  
**Status:** COMPLETE (Stage 0 Discovery)  
**Host Environment:** Windows 11 (Ryzen 7 5800H, 16 GB RAM, RTX 3050 4 GB VRAM)  
**Author:** FujiNova Lead Systems Architect  

---

## 1. Architectural Philosophy & Guiding Principles

The FujiNova technology stack is designed around four non-negotiable architectural mandates:
1. **Zero-Overhead Local Footprint:** Must run smoothly on a 16 GB RAM Windows 11 laptop without requiring heavyweight Docker orchestration, multi-gigabyte JVM services, or background Kubernetes clusters.
2. **Determinism over Hallucination:** Clear decoupling between the probabilistic AI agent (Hana) and deterministic system modules (Transit Router, POI Database, Cryptographic QR Verifier).
3. **Low-Latency Streaming:** Sub-second conversational responses delivered through asynchronous WebSockets or Server-Sent Events (SSE).
4. **Zero Vendor Lock-In & Open Standards:** Built entirely on open formats (GTFS-JP, GeoJSON, PMTiles, ODbL, OpenTelemetry, SQLite).

---

## 2. Layer-by-Layer Technology Recommendations

```
+-----------------------------------------------------------------------------------------+
|                                    CLIENT TIER (PWA)                                    |
|                     React 18 / Vite + TypeScript + Tailwind CSS                         |
|           MapLibre GL JS (WebGL Map) + Lucide Icons + Radix UI Primitives               |
+-----------------------------------------------------------------------------------------+
                                             |
                                  [HTTP/2 + WebSockets / SSE]
                                             v
+-----------------------------------------------------------------------------------------+
|                                    APPLICATION BACKEND                                  |
|                             FastAPI (Python 3.11 / 3.12)                                |
|                        Uvicorn (Async ASGI) + Pydantic v2                               |
+-----------------------------------------------------------------------------------------+
       |                                   |                                     |
       v                                   v                                     v
+------------------+             +-------------------+                 +------------------+
|   AI AGENT TIER  |             |  TRANSIT ROUTING  |                 | PERSISTENCE TIER |
|  LangGraph Core  |             |   Python RAPTOR   |                 | SQLite (WAL Mode)|
| Gemini 2.5 Flash |             | Embedded In-Memory|                 | SpatiaLite/R*Tree|
|  (Fallback: 4o)  |             |  GTFS-JP Engines  |                 | Checkpoint Store |
+------------------+             +-------------------+                 +------------------+
```

---

### Layer 1: Frontend Application (Client Tier)
* **Framework:** **React 18 / 19 with Vite + TypeScript**
  - *Justification:* Vite provides instant Hot Module Replacement (HMR) and compiles in milliseconds on Windows. TypeScript guarantees type safety across complex trip state schemas.
* **Styling & Design System:** **Tailwind CSS + Radix UI Primitives**
  - *Justification:* Mobile-first utility styling. Radix UI provides accessible, unstyled primitives (dialogs, tooltips, sheets) essential for travel drawers and bottom-sheets on mobile screens.
* **Map & Spatial Visualization:** **MapLibre GL JS (v4.x)**
  - *Justification:* Open-source BSD-3-Clause WebGL vector map renderer. Provides buttery-smooth 60 FPS panning, multi-touch gestures, custom transit route line styling, and 3D terrain pitch showing Mount Fuji's topography without Mapbox API tokens or billing fees.
* **Map Basemap & Tiles:** **PMTiles (Protomaps) or OpenFreeMap**
  - *Justification:* OpenFreeMap (`https://openfreemap.org`) provides free vector basemaps with zero API keys or rate limits. Alternatively, a single 85 MB `.pmtiles` file can be served locally for 100% offline development.
* **Client Device Features:**
  - Standard HTML5 `navigator.geolocation` API with explicit user opt-in modal.
  - HTML5 Canvas QR code rendering (`qrcode.react`) and native camera QR scanner (`html5-qrcode`).

---

### Layer 2: Application Backend (API Tier)
* **Language:** **Python 3.11 / 3.12**
  - *Justification:* Standard language for modern AI agent development, GTFS parsing, and data manipulation. Python 3.11+ delivers 25–40% performance gains over 3.10 via the Faster CPython initiative.
* **API Framework:** **FastAPI + Uvicorn**
  - *Justification:* Native asynchronous event loop, automatic OpenAPI documentation, high concurrency, and seamless integration with Pydantic v2 for strict data validation.
* **Streaming Protocol:** **Server-Sent Events (SSE)** via `EventSourceResponse`
  - *Justification:* Simpler, lighter, and more firewall-resilient than bidirectional WebSockets for conversational text streaming and step-by-step itinerary generation.

---

### Layer 3: AI Agent & Conversational Workflow Tier
* **Workflow Framework:** **LangGraph (LangChain ecosystem)**
  - *Justification:* LangGraph's cyclic state graphs (`StateGraph`) are superior to linear DAGs (Directed Acyclic Graphs). It natively models conversational loops: interviewing the user -> evaluating completeness -> invoking tools -> asking clarification -> outputting itinerary.
* **Conversational Memory:** **LangGraph `SqliteSaver` / Memory Checkpointer**
  - *Justification:* Thread-level state persistence stored directly in local SQLite. Enables resuming conversations across browser refreshes without resending giant raw message histories.
* **Primary LLM:** **Google Gemini 2.5 Flash** (via `google-genai` SDK)
  - *Justification:* Sub-500ms TTFT, native tool calling, free development tier in Google AI Studio.
* **Fallback LLM:** **OpenAI GPT-4o-mini** (via `openai` SDK)
  - *Justification:* Strict JSON schema adherence, inexpensive emergency backup.

---

### Layer 4: Public Transit Routing & Spatial Engines
* **Transit Algorithm:** **RAPTOR (Round-Based Public Transit Routing)**
  - *Implementation:* Custom lightweight Python module inspired by `transnetlab/transit-routing`.
  - *Data Ingestion:* Ingests official Fujikyu Bus GTFS-JP and JR East GTFS. Pre-indexes departures and stops into contiguous in-memory numpy arrays / dictionaries upon FastAPI startup.
  - *Performance:* < 5 milliseconds per query; zero external server processes.
* **Spatial & Distance Engine:** **SQLite R*Tree / SpatiaLite + Turf.js (Client)**
  - *Justification:* SQLite's built-in `R*Tree` module provides sub-millisecond bounding box and nearest-neighbor lookups for all Yamanashi POIs.

---

### Layer 5: Persistence & Storage Tier
* **Primary Database:** **SQLite 3 in WAL (Write-Ahead Logging) Mode**
  - *Justification:* Zero-configuration, zero-RAM daemon. SQLite WAL mode supports concurrent readers alongside a single writer. More than fast enough for handling thousands of queries per second for single-machine development and initial deployment.
* **Data Schemas Managed in SQLite:**
  - `places` (Attractions, facilities, coordinates, opening hours, accessibility)
  - `transit_stops`, `transit_routes`, `transit_trips`, `transit_stop_times` (GTFS mirror)
  - `conversation_checkpoints` (LangGraph conversation memory)
  - `demonstration_passes` (Issued QR vouchers, signature hashes, redemption audit log)

---

### Layer 6: Security, Verification & Demonstration Pass Tier
* **Token Standard:** **HMAC-SHA256 Signed JSON Web Tokens (JWT) / PASETO**
  - *Payload Structure:*
    ```json
    {
      "pass_id": "FN-DEMO-2026-98124",
      "type": "DEMONSTRATION_DISPERSION_VOUCHER",
      "region": "Saiko_Iyashi_no_Sato",
      "traveller_hash": "a8fbc...219",
      "issued_at": 1731056400,
      "expires_at": 1731142800,
      "disclaimer": "DEMONSTRATION ONLY - NOT A VALID TRANSIT PASS OR COMMERCIAL TICKET",
      "nonce": "7c9e1...5b2"
    }
    ```
* **Anti-Replay Mechanism:** Each pass includes a cryptographically secure random `nonce`. When scanned by the demonstration redemption endpoint, the `nonce` is recorded in the `redeemed_passes` table. Any duplicate scan returns `ALREADY_REDEEMED`.
* **Visual Watermark:** Every QR code screen renders high-contrast striped banners reading: **"PROTOTYPE DEMONSTRATION VOUCHER — NON-COMMERCIAL"**.

---

## 3. Technology Evaluation Summary Matrix

| Domain | Selected Technology | Alternative Rejected | Rejection Rationale |
| :--- | :--- | :--- | :--- |
| **Frontend** | React 18 + Vite | Next.js (SSR) | Unnecessary Node.js server complexity for a client-driven map application; Vite SPA is faster to develop and deploy. |
| **Map Rendering** | MapLibre GL JS | Leaflet | Leaflet stutters on dense mobile vector tiles and lacks hardware-accelerated 3D terrain pitch. |
| **Vector Tiles** | OpenFreeMap / PMTiles | Mapbox / Google Maps | Avoids restrictive monthly API quotas, credit card gating, and per-tile billing charges. |
| **Transit Routing**| Python RAPTOR | OpenTripPlanner 2 | OTP2 requires Java 17+ JVM and 3–5 GB dedicated RAM; RAPTOR runs in 15 MB Python RAM. |
| **Database** | SQLite WAL | PostgreSQL + PostGIS | Eliminates Docker background service requirement on 16 GB laptop; SQLite R*Tree is completely adequate. |
| **Agent Engine** | LangGraph | Autogen / CrewAI | LangGraph provides explicit cyclic state control and granular checkpointing needed for structured interviews. |
| **Primary LLM** | Gemini 2.5 Flash | Claude 3.5 Sonnet | Sonnet is 30x more expensive and has no free development tier; Flash is sub-500ms and free for development. |

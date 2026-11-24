# FUJINOVA — Updated System Architecture & Responsibility Boundaries

**Document Version:** 2.1.0 (Stage 0.3 Final Readiness Revision)  
**Status:** AUDITED & VALIDATED  
**Validation Date:** November 2026  
**Auditor:** FujiNova Principal Enterprise Architect  

---

## 1. Architectural Principles & Boundary Governance

The FujiNova architecture is built on strict separation of concerns between probabilistic conversational AI and deterministic computational services:

1. **Dual Cloud Model Router with Decoupled Adapters:** The application interacts with models solely via an abstract `BaseLLMAdapter` interface. Swapping between primary (`gemini-3.8-flash`) and fallback (`gpt-4o-mini`) is driven by backend environment configuration (`.env`).
2. **Deterministic Service Layer:** Routing calculations, spatial proximity queries, coordinate lookups, and voucher signing run in isolated, pure-Python / SQLite components with **zero LLM improvisation**.
3. **Field-Level Data Provenance:** The persistence layer explicitly records the source, retrieval date, verification status, and freshness of every geographical and facility attribute.
4. **Zero-Overhead Local Development:** Runs smoothly within the 16 GB RAM and 4 GB VRAM budget of Windows 11 host without requiring Docker Desktop, Kubernetes, or background Java JVMs.

---

## 2. Updated System Architecture Diagram

```mermaid
flowchart TD
    subgraph CLIENT_LAYER["CLIENT TIER (Mobile PWA & Desktop Browser)"]
        UI["React 18 + Vite Responsive Shell"]
        MAP["MapLibre GL JS (WebGL Hardware-Accelerated 3D Map)"]
        CHAT_UI["Conversational Stream UI (SSE Client)"]
        GEO_CLIENT["Geolocation Adapter (Explicit User Opt-In / Manual Picker)"]
        QR_VIEW["QR Code Presentation & Scanner Modal"]
    end

    subgraph BACKEND_GATEWAY["API GATEWAY & ASGI SERVER (FastAPI / Uvicorn)"]
        ROUTER["FastAPI Asynchronous Router"]
        AUTH_MIDDLEWARE["CORS, Rate Limiter & Token Gate"]
        SSE_DISPATCHER["Server-Sent Events (SSE) Streamer"]
    end

    subgraph AGENT_ORCHESTRATION["AI AGENT TIER (LangGraph Runtime)"]
        STATE_GRAPH["LangGraph StateGraph Engine"]
        PROFILE_SCHEMA["TravellerProfile State Schema (Pydantic v2)"]
        CHECKPOINTER["Conversation Persistence (SqliteSaver)"]
        PROMPT_ENGINE["Hana Persona & Context Grounding"]
        TOOL_CONTROLLER["Deterministic Tool Invocation Guard"]
    end

    subgraph MODEL_ROUTING["RESILIENT MODEL ROUTER (Decoupled Adapters)"]
        ADAPTER_BASE["BaseLLMAdapter Interface"]
        PRIMARY_LLM["Primary: Google Gemini 3.8 Flash Adapter"]
        FALLBACK_LLM["Failover: OpenAI GPT-4o-mini Adapter (Automatic on 429/5xx)"]
    end

    subgraph DETERMINISTIC_SERVICES["DETERMINISTIC DOMAIN ENGINES (Zero Hallucination)"]
        RAPTOR["RAPTOR Transit Router (GTFS-JP + Transcribed Rail Timetable)"]
        GEO_DB["Spatial & POI Search Engine (SQLite R*Tree)"]
        WEATHER_SVC["Live Weather & Cloud Cover (JMA + Optical Webcams)"]
        TRAFFIC_SVC["Highway Traffic Volume Client (JARTIC xROAD WFS API)"]
        CROWD_MODEL["Heuristic Crowd Estimator (Time/Day/Season - NOT Live)"]
        QR_AUTHORITY["Demonstration Voucher Signer (HMAC-SHA256 + Anti-Replay Nonce)"]
    end

    subgraph PERSISTENCE_LAYER["LOCAL PERSISTENCE (SQLite WAL Mode - ~60 MB)"]
        DB_PLACES[("places (35 Verified Seed POIs, Field-Level Provenance)")]
        DB_TRANSIT[("transit_schedules (Fujikyu Bus + Railway Tables)")]
        DB_MEMORY[("conversation_checkpoints")]
        DB_VOUCHERS[("demonstration_vouchers & redeemed_nonces")]
    end

    %% Client Interactions
    UI --> CHAT_UI
    UI --> MAP
    UI --> GEO_CLIENT
    UI --> QR_VIEW

    CHAT_UI <-->|SSE Stream| SSE_DISPATCHER
    MAP <-->|GeoJSON Polylines| ROUTER
    QR_VIEW <-->|Verify Voucher| ROUTER

    %% Gateway to Agent
    SSE_DISPATCHER --> STATE_GRAPH
    ROUTER --> DETERMINISTIC_SERVICES

    %% Agent Core
    STATE_GRAPH <--> CHECKPOINTER
    CHECKPOINTER <--> DB_MEMORY
    STATE_GRAPH --> PROMPT_ENGINE
    PROMPT_ENGINE --> ADAPTER_BASE
    ADAPTER_BASE --> PRIMARY_LLM
    PRIMARY_LLM -.->|Circuit Breaker on 429/5xx/Timeout| FALLBACK_LLM
    STATE_GRAPH --> TOOL_CONTROLLER

    %% Tool Controller to Deterministic Engines
    TOOL_CONTROLLER -->|get_transit_route| RAPTOR
    TOOL_CONTROLLER -->|search_places| GEO_DB
    TOOL_CONTROLLER -->|check_weather| WEATHER_SVC
    TOOL_CONTROLLER -->|check_highway_traffic| TRAFFIC_SVC
    TOOL_CONTROLLER -->|estimate_crowd| CROWD_MODEL
    TOOL_CONTROLLER -->|issue_demo_voucher| QR_AUTHORITY

    %% Deterministic Engines to SQLite
    RAPTOR <--> DB_TRANSIT
    GEO_DB <--> DB_PLACES
    QR_AUTHORITY <--> DB_VOUCHERS
```

---

## 3. Strict Functional Responsibility Boundaries

```
+----------------------------------------------------------------------------------------------------+
|                                STRICT BOUNDARY OF RESPONSIBILITY                                   |
+----------------------------------------------------------------------------------------------------+
| DOMAIN / TASK               | ASSIGNED SUBSYSTEM   | FORBIDDEN ACTION                              |
+-----------------------------+----------------------+-----------------------------------------------+
| Conversational Interview    | Hana (LangGraph/LLM) | No hardcoded rigid question trees.            |
| Traveller Need Extraction   | Hana (Pydantic v2)   | No silent dropping of stated constraints.     |
| Destination Suggestion      | POI Search Engine    | Hana CANNOT suggest uncataloged places.       |
| Route & Timetable Planning  | RAPTOR Transit Engine| Hana CANNOT calculate or guess schedules.     |
| Transit Fare Computation    | RAPTOR Fare Tables   | Hana CANNOT invent or estimate ticket prices. |
| Weather & Mountain View     | JMA / Webcam Service | Hana CANNOT guess weather without sensor tool.|
| Road Congestion Assessment  | JARTIC Traffic / Rule| Hana CANNOT invent live traffic speeds.       |
| Attraction Crowd Status     | Crowd Heuristic Model| Hana CANNOT label an estimate as "Live".      |
| Demonstration Pass Issuing  | HMAC Token Authority | Hana CANNOT generate arbitrary pass codes.    |
+----------------------------------------------------------------------------------------------------+
```

---

## 4. Failure Handling & Circuit Breaker Architecture

A robust application must gracefully handle external network, quota, and operational failures:

```mermaid
sequenceDiagram
    autonumber
    actor User as Traveller
    participant Agent as LangGraph Orchestrator
    participant Router as Model Router (BaseLLMAdapter)
    participant Gemini as Google Gemini 3.8 Flash
    participant OpenAI as OpenAI GPT-4o-mini
    participant Tool as SQLite Place Search Tool

    User->>Agent: "Find quiet spots near Lake Kawaguchiko with no steep stairs."
    Agent->>Router: Dispatch prompt with tools
    Router->>Gemini: stream_chat(tools=[search_places])
    
    alt Primary Provider Rate Limited (HTTP 429)
        Gemini-->>Router: HTTP 429 Resource Exhausted (Daily cap or burst limit)
        Note over Router: Circuit Breaker Trips -> Check ALLOW_MULTI_VENDOR_FAILOVER
        Router->>OpenAI: stream_chat(tools=[search_places])
        OpenAI-->>Router: ToolCall: search_places(category="viewpoint", accessibility="VERIFIED_ACCESSIBLE")
    else Primary Provider Healthy
        Gemini-->>Router: ToolCall: search_places(category="viewpoint", accessibility="VERIFIED_ACCESSIBLE")
    end

    Router->>Tool: execute(search_places)
    Tool-->>Agent: Returns: Oishi Park, Yagizaki Park, Kawaguchiko Herbkan
    Agent-->>User: "I recommend Oishi Park and Yagizaki Park. Both feature flat, barrier-free paved paths along Lake Kawaguchiko with step-free access [Verified Official Town Guide]."
```

---

## 5. Security & Privacy Safeguards

1. **User Geolocation Privacy:**
   - Browser GPS is requested exclusively through a deliberate user click on an explicit consent dialog.
   - If permission is denied or dismissed, the app seamlessly defaults to an intuitive **Manual Location Selector** (e.g. "Select Station / Landmark").
   - User coordinates are processed ephemerally in session memory and **never logged to persistent disk or analytics servers**.
2. **Demonstration Voucher Tamper-Proofing:**
   - Demonstration QR passes are cryptographically signed using server-side HMAC-SHA256 with an ephemeral server secret.
   - Every pass contains a cryptographically random 128-bit `nonce`. Upon scanning, the nonce is stored in SQLite with a `REDEEMED` status. Any duplicate scan attempt returns `ALREADY_REDEEMED`.
   - Every voucher screen displays prominent high-contrast watermarks: **"DEMONSTRATION ONLY — NON-COMMERCIAL VOUCHER"**.
3. **No Biometric or Surveillance Tools:**
   - The application strictly contains zero facial recognition, camera biometric capture, or cross-site tracking libraries.

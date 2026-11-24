# FUJINOVA — System Architecture & Component Design Specification

**Document Version:** 1.0.0  
**Status:** COMPLETE (Stage 0 Discovery)  
**Author:** FujiNova Lead Enterprise Architect  

---

## 1. Architectural Overview

FujiNova employs a **Decoupled Agentic Hybrid Architecture**. The system establishes a strict boundary between the **Probabilistic AI Layer** (Hana's natural conversation, adaptive questioning, and intent parsing) and the **Deterministic Domain Layer** (transit routing, spatial lookups, cryptographic signing, and sensor queries).

Under no circumstances is the LLM permitted to perform mathematical pathfinding, timetable calculations, or signature verification. The AI agent acts strictly as an empathetic orchestrator that interfaces with validated backend micro-tools.

---

## 2. Comprehensive System Architecture Diagram

```mermaid
flowchart TD
    subgraph CLIENT_TIER["CLIENT TIER (Mobile PWA / Web Browser)"]
        UI["React 18 / Vite Responsive UI"]
        MAP["MapLibre GL JS (WebGL 3D Map)"]
        CHAT["Conversational Chat Stream (SSE)"]
        QR_SCAN["HTML5 QR Scanner & Renderer"]
        LOC["Browser Geolocation (Opt-in)"]
    end

    subgraph API_GATEWAY["API GATEWAY & ROUTER (FastAPI / Uvicorn)"]
        CORS["CORS & Request Limiter"]
        SSE_ENDPOINT["/api/v1/chat/stream (SSE)"]
        REST_ROUTES["/api/v1/transit, /api/v1/places, /api/v1/qr"]
    end

    subgraph AGENT_TIER["AI AGENT WORKFLOW ENGINE (LangGraph)"]
        STATE_GRAPH["LangGraph StateGraph Engine"]
        MEM_STORE["Conversation Memory Checkpointer (SqliteSaver)"]
        PROMPT_MGR["Hana Persona & Context Injection"]
        TOOL_CALLER["Pydantic Tool Invocation Controller"]
    end

    subgraph MODEL_TIER["AI INFERENCE RUNTIME"]
        GEMINI["Primary: Gemini 2.5 Flash (Google AI Studio)"]
        OPENAI["Fallback: OpenAI GPT-4o-mini"]
    end

    subgraph DETERMINISTIC_SERVICES["DETERMINISTIC SERVICE LAYER"]
        RAPTOR["RAPTOR Transit Routing Engine (GTFS-JP)"]
        RECSYS["POI Discovery & Hybrid Scorer (Content + Spatial)"]
        WEATHER["Live Weather & Fuji Visibility Service (JMA + Webcams)"]
        TRAFFIC["Highway Congestion Service (JARTIC xROAD API)"]
        QR_AUTH["QR Voucher Authority (HMAC-SHA256 Signer/Verifier)"]
    end

    subgraph DATA_STORAGE["PERSISTENCE LAYER (SQLite WAL Mode)"]
        DB_PLACES[("places & attractions (R*Tree Indexed)")]
        DB_GTFS[("gtfs_transit (Stops, Routes, Timetables)")]
        DB_MEMORY[("conversation_checkpoints")]
        DB_VOUCHERS[("demonstration_vouchers & nonces")]
    end

    %% Client to Gateway
    UI --> CHAT
    UI --> MAP
    UI --> QR_SCAN
    UI --> LOC
    CHAT <-->|Server-Sent Events| SSE_ENDPOINT
    MAP <-->|GeoJSON Overlays| REST_ROUTES
    QR_SCAN <-->|Validation Requests| REST_ROUTES

    %% Gateway to Agent & Services
    SSE_ENDPOINT --> STATE_GRAPH
    REST_ROUTES --> RAPTOR
    REST_ROUTES --> RECSYS
    REST_ROUTES --> QR_AUTH

    %% Agent Tier Connections
    STATE_GRAPH <--> MEM_STORE
    MEM_STORE <--> DB_MEMORY
    STATE_GRAPH --> PROMPT_MGR
    PROMPT_MGR --> GEMINI
    GEMINI -.->|Failover on 429| OPENAI
    STATE_GRAPH --> TOOL_CALLER

    %% Tool Caller to Services
    TOOL_CALLER --> RAPTOR
    TOOL_CALLER --> RECSYS
    TOOL_CALLER --> WEATHER
    TOOL_CALLER --> TRAFFIC
    TOOL_CALLER --> QR_AUTH

    %% Services to Data Storage
    RAPTOR <--> DB_GTFS
    RECSYS <--> DB_PLACES
    QR_AUTH <--> DB_VOUCHERS
```

---

## 3. Dynamic Conversational State Machine (LangGraph)

Hana does not follow a linear questionnaire. Instead, she executes a cyclic **Traveller State Schema Evaluation** loop:

```mermaid
stateDiagram-v2
    [*] --> IdleState
    IdleState --> ReceiveMessage: User sends message / location
    
    state ReceiveMessage {
        [*] --> ParseIntent
        ParseIntent --> UpdateTravellerState: Extract dates, pace, mobility, luggage
    }
    
    UpdateTravellerState --> EvaluateInformationCompleteness: Check required itinerary slots
    
    state EvaluateInformationCompleteness <<choice>>
    EvaluateInformationCompleteness --> FormulateAdaptiveQuestion: Slots Missing (e.g. party pace unknown)
    EvaluateInformationCompleteness --> SelectCandidateDestinations: Constraints Sufficient
    
    FormulateAdaptiveQuestion --> StreamResponseToUser: Ask single natural follow-up
    StreamResponseToUser --> IdleState
    
    state SelectCandidateDestinations {
        [*] --> QueryPOIDatabase: Filter by mobility, season, tags
        QueryPOIDatabase --> ApplyWeatherVisibilityFilter: Check Mt Fuji live cloud cover
        ApplyWeatherVisibilityFilter --> InvokeRAPTORRouter: Calculate exact timetable & transfers
    }
    
    SelectCandidateDestinations --> CheckCrowdAndTraffic: Ingest JARTIC / historical crowd level
    
    state CheckCrowdAndTraffic <<choice>>
    CheckCrowdAndTraffic --> ProposeAlternativeHiddenGem: Overcrowded / Chuo road jammed
    CheckCrowdAndTraffic --> AssembleGroundedItinerary: Feasible & Accessible
    
    ProposeAlternativeHiddenGem --> AssembleGroundedItinerary: Highlight quiet lake / craft venue
    AssembleGroundedItinerary --> StreamResponseToUser: Output itinerary with map coordinates
```

### The Traveller State Schema (Pydantic / LangGraph State)

```python
from typing import List, Optional
from pydantic import BaseModel, Field

class TravellerProfile(BaseModel):
    origin_station: Optional[str] = Field(None, description="Starting transit hub (e.g. Shinjuku, Otsuki, Kawaguchiko)")
    arrival_time: Optional[str] = Field(None, description="ISO time or HH:MM of arrival")
    departure_time: Optional[str] = Field(None, description="Must-return departure time")
    party_composition: Optional[str] = Field(None, description="solo, couple, family_with_kids, elderly")
    mobility_limitations: bool = Field(False, description="True if avoiding steep stairs or long walks")
    preferred_pace: str = Field("relaxed", description="relaxed (1-2 POIs/day) or active (3-5 POIs/day)")
    interests: List[str] = Field(default_factory=list, description="nature, photography, hot_springs, shrines, food, crafts")
    budget_tier: str = Field("standard", description="budget, standard, luxury")
    luggage_status: Optional[str] = Field(None, description="carrying_large_suitcases, daypack_only, coin_lockered")
    fuji_view_priority: int = Field(5, description="1 to 5 importance of seeing Mt. Fuji summit")
```

---

## 4. End-to-End Sequence: Real-Time Dynamic Re-Routing

This sequence illustrates how Hana handles a sudden weather disruption without hallucinating alternatives:

```mermaid
sequenceDiagram
    autonumber
    actor User as Traveller (Browser PWA)
    participant GW as FastAPI Gateway
    participant LG as LangGraph (Hana)
    participant WTH as Weather & Webcam Service
    participant REC as POI Recommender
    participant RPT as RAPTOR Router (GTFS)

    User->>GW: "We just finished lunch at Lake Kawaguchiko! Heading to Oishi Park."
    GW->>LG: Dispatch turn to LangGraph
    LG->>WTH: check_visibility(location="Kawaguchiko")
    WTH-->>LG: {status: "OVERCAST", summit_visible: false, cloud_ceiling_m: 900}
    
    Note over LG: Decision: Mt. Fuji is invisible at Oishi Park view deck.<br/>Re-route to high-value indoor cultural gem.
    
    LG->>REC: find_alternatives(near="Kawaguchiko", category="indoor_cultural", max_crowd=2)
    REC-->>LG: Recommended: Itchiku Kubota Art Museum & Kimono Gallery (Zero steps, 1.2km away)
    
    LG->>RPT: get_route(from="Kawaguchiko_Stn", to="Itchiku_Kubota_Museum", time="13:15")
    RPT-->>LG: Fujikyu Red Line Bus at 13:20 -> Stop 15 (13:38). Fare: ¥390.
    
    LG->>GW: Stream explanation + verified timetable + map route
    GW->>User: "Mount Fuji's summit is currently hidden behind low clouds at Oishi Park. Instead, I suggest visiting the Itchiku Kubota Art Museum just 18 minutes away..."
```

---

## 5. Security & Verification Architecture: The Demonstration QR Voucher

To demonstrate crowd dispersion incentives responsibly without issuing fake commercial currency, FujiNova implements a tamper-evident voucher workflow:

```mermaid
sequenceDiagram
    autonumber
    actor Traveller as Traveller App
    participant Server as FujiNova Backend (Voucher Authority)
    participant DB as SQLite Nonce Store
    actor Staff as Demo Verification Terminal

    Note over Traveller,Server: 1. Issuance (Incentive for Visiting Quiet Saiko Lake)
    Traveller->>Server: POST /api/v1/voucher/issue {destination: "Saiko_Iyashi_no_Sato"}
    Server->>Server: Generate cryptographically random Nonce (128-bit)
    Server->>Server: Sign payload with server HMAC-SHA256 secret key
    Server->>DB: Store Nonce with status = "ISSUED", timestamp, expiry
    Server-->>Traveller: Return Signed JWT + Demonstration Metadata
    Traveller->>Traveller: Render QR code with high-contrast DEMO WATERMARK

    Note over Traveller,Staff: 2. Verification at Attraction (Simulated)
    Staff->>Traveller: Scans QR code via camera scanner
    Staff->>Server: POST /api/v1/voucher/verify {token: "eyJhbGciOi..."}
    Server->>Server: Verify HMAC signature using secret key
    alt Signature Invalid
        Server-->>Staff: 400 Bad Request: "INVALID_SIGNATURE (Forged or Corrupted)"
    else Expired
        Server-->>Staff: 410 Gone: "VOUCHER_EXPIRED"
    else Nonce already recorded as REDEEMED
        Server-->>Staff: 409 Conflict: "ALREADY_REDEEMED (Double-spend rejected)"
    else Valid & Active
        Server->>DB: Update Nonce status = "REDEEMED", redeemed_at = NOW()
        Server-->>Staff: 200 OK: "VALID DEMONSTRATION VOUCHER (Sample Souvenir Postcard)"
    end
```

---

## 6. Architectural Boundary Enforcement Summary

1. **LLM Output Sanitization:** All LLM outputs must be parsed into strictly typed Pydantic models. Raw markdown emitted by the LLM is never parsed as a source of transit truth.
2. **Spatial Precision:** Coordinates use the WGS84 standard format (`float64`) truncated to 6 decimal places (~0.1 meter accuracy).
3. **Data Provenance:** Every response card rendered in the frontend must show its provenance badge (e.g. `[Verified via Fujikyu Bus GTFS March 2025]` or `[Historical Estimate]`).

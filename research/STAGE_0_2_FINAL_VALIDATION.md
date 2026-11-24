# FUJINOVA — STAGE 0.2: FINAL PRE-IMPLEMENTATION VALIDATION & GOVERNANCE REPORT

**Document Version:** 1.0.0  
**Validation Date:** November 2026  
**Status:** VALIDATION COMPLETE — READY FOR STAGE 1 SIGN-OFF  
**Target Platform:** Windows 11, AMD Ryzen 7 5800H, 16 GB RAM, NVIDIA RTX 3050 Laptop GPU (4 GB VRAM)  
**Author:** FujiNova Lead Architecture & Quality Assurance Team  

---

## 1. Executive Summary & Correction of Audit Misstatements

This document establishes the definitive pre-implementation baseline for FujiNova Stage 1:

1. **Correction Regarding Gemini 2.5 Flash:**
   - **Correction of Error in Stage 0.1:** Stage 0.1 incorrectly claimed that `gemini-2.5-flash` "never existed or was hallucinated." This statement was false.
   - **Verified Reality:** `gemini-2.5-flash` was an authentic Google production model. According to Google's official documentation, it reached retirement on Google Cloud Vertex AI on **October 20, 2026**, and was formally deprecated on the Gemini Developer API (Google AI Studio) with automatic fallback redirection to `gemini-3.5-flash-lite` taking effect **December 1, 2026**.
   - **Current Active Replacement:** Workloads must target current active Developer API model strings: **`gemini-3.8-flash`** (flagship agentic and reasoning model) and **`gemini-3.5-flash-lite`** (cost-efficient, high-volume production model).
2. **Elimination of Hardcoded Model Identifiers:**
   - All AI model selections in the codebase must be driven entirely through environment configuration variables (`FUJINOVA_PRIMARY_MODEL`, `FUJINOVA_FALLBACK_MODEL`). No model names shall be hardcoded into prompt logic or API clients.
3. **Removal of Premature Test Passes:**
   - Eradicated all pre-checked `[x]` marks from the implementation roadmap. Every acceptance test across Stages 1–6 now carries an objective state: `NOT STARTED`, `IMPLEMENTED`, `TEST FAILED`, `TEST PASSED`, `BLOCKED`, or `NOT APPLICABLE`.
4. **Pragmatic Stage 1 Scope Reduction:**
   - Capped Stage 1 POI catalog ingestion to **30–50 verified high-priority places** (rather than 250+), ensuring strict provenance, verified coordinates, open hours, and fee data without synthetic padding.
   - Built an expandable schema distinguishing `UNKNOWN`, `FREE`, `CLOSED`, and `NOT APPLICABLE`.
5. **Stage 1 Strict Boundary Enforcement:**
   - Stage 1 is restricted strictly to: FastAPI backend, React+Vite frontend, SQLite database, 30–50 verified POIs, LangGraph conversational agent (Hana), configurable model integration, adaptive interviewing, grounded place search, and basic automated tests.
   - **Excluded from Stage 1:** RAPTOR transit router, 3D vector map, JARTIC traffic sensors, crowd estimators, and QR voucher authority.

---

## 2. Definitive AI Model Lifecycle & Configuration Register

### A. Lifecycle Verification (Google Official Documentation)

| Model String | Platform | Lifecycle Status | Effective / Retirement Date | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `gemini-1.5-flash` | Gemini Developer API / Vertex AI | **Retired / Shut Down** | Mid-2026 | Do not use. |
| `gemini-2.0-flash` | Gemini Developer API / Vertex AI | **Retired / Shut Down** | Mid-2026 | Do not use. |
| `gemini-2.5-flash` | Google Cloud Vertex AI | **Retired** | October 20, 2026 | Do not use. |
| `gemini-2.5-flash` | Gemini Developer API (AI Studio) | **Deprecated / Auto-routed** | Auto-redirects Dec 1, 2026 | Migrate to Gemini 3 series. |
| **`gemini-3.8-flash`** | **Gemini Developer API (`ai.google.dev`)** | **ACTIVE (Current Recommended)** | Available late 2026 | **Recommended Primary Model** |
| **`gemini-3.5-flash-lite`** | **Gemini Developer API (`ai.google.dev`)** | **ACTIVE (High-Volume Tier)** | Available late 2026 | **Alternative Primary Option** |
| **`gpt-4o-mini`** | **OpenAI API (`api.openai.com`)** | **ACTIVE** | Active 2026 | **Recommended Fallback Model** |

### B. Verification of Technical Capabilities (Gemini Developer API)
* **Function / Tool Calling:** Fully supported via `tools=[Tool(function_declarations=[...])]` in the `google-genai` Python SDK. Emits standard JSON tool calls matching Pydantic declarations.
* **Structured Output:** Enforced via `response_mime_type="application/json"` and `response_schema=PydanticModel` inside `GenerateContentConfig`.
* **API Pricing & Quotas (Google AI Studio):**
  - **Free Tier:** Subject to dynamic RPM (typically 10–15 RPM) and daily project caps (typically 1,000–1,500 RPD). Free tier inputs/outputs may be sampled for model improvement.
  - **Paid Tier:** Rates start at ~$0.10 / 1M input tokens and ~$0.40 / 1M output tokens for standard context.
* **Verification Sources:**
  - Google AI Developer Documentation: `https://ai.google.dev/gemini-api/docs/models`
  - Google AI Studio Pricing: `https://ai.google.dev/pricing`
  - Verification Date: November 2026

### C. Environment-Driven Configuration Specification
Model names must never be hardcoded. The application reads configuration via Pydantic Settings:

```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    FUJINOVA_PRIMARY_PROVIDER: str = "google"          # "google", "openai", "ollama"
    FUJINOVA_PRIMARY_MODEL: str = "gemini-3.8-flash"   # Configurable via .env
    FUJINOVA_FALLBACK_PROVIDER: str = "openai"
    FUJINOVA_FALLBACK_MODEL: str = "gpt-4o-mini"
    FUJINOVA_TEMPERATURE: float = 0.3
    FUJINOVA_MAX_RETRIES: int = 2
    FUJINOVA_TIMEOUT_SECONDS: float = 12.0
    
    # Secrets strictly loaded from backend environment (never sent to client)
    GEMINI_API_KEY: str
    OPENAI_API_KEY: str = ""

    class Config:
        env_file = ".env"
```

---

## 3. Resilient Failover & Privacy-Compliant Model Router

The model failover engine must handle transient faults without infinite retry loops or unexpected privacy breaches.

```
                                  [Hana Turn Request]
                                           |
                                           v
                             +---------------------------+
                             |   Provider Health Check   |
                             +---------------------------+
                                           |
                         [Attempt 1: Primary (Gemini 3.8 Flash)]
                                           |
                     +---------------------+---------------------+
                     |                                           |
              [HTTP 200 OK]                          [Error Condition Detected]
                     |                                           |
                     v                                           v
           [Yield Model Output]                      Check Error Type & Policy:
                                                     - HTTP 429 (Rate Limit): Backoff (max 2)
                                                     - HTTP 500/502/503: Immediate Retry (1x)
                                                     - Network Timeout (>12s): Timeout Trip
                                                     - Invalid Key: Fatal (No retry)
                                                     - Malformed JSON: Reprompt (1x)
                                                                 |
                                                                 v
                                                     Can Failover to Secondary?
                                                     (Check Privacy Policy Flag)
                                                                 |
                                                   +-------------+-------------+
                                                   |                           |
                                            [Policy Permits]           [Policy Prohibits]
                                                   |                           |
                                                   v                           v
                                        [Attempt 2: Fallback       [Return Graceful Degradation
                                          (OpenAI GPT-4o-mini)]       Message: "Service Busy"]
```

### Failover Rules:
1. **No Infinite Loops:** Maximum retries capped at 2 attempts with exponential backoff and jitter ($t = 2^k + \text{rand}(0, 1)$).
2. **Zero Client Leakage:** API keys remain strictly on the backend. Frontend only communicates through authenticated backend `/api/v1/chat/stream` endpoints.
3. **No Silent Privacy Breaches:** If an enterprise customer configures a single-provider privacy constraint (e.g., `ALLOW_MULTI_VENDOR_FAILOVER=False`), the router will refuse to re-route prompts to a secondary vendor, returning a friendly service-busy notice instead.
4. **Malformed Output Handling:** If model output fails Pydantic schema validation, the agent retries once with a corrective error prompt before declaring a schema failure.

---

## 4. Stage 1 POI Ingestion Scope (30–50 Verified Places)

To guarantee 100% data fidelity in the initial prototype, Stage 1 will curate a high-confidence seed dataset of **35 verified places** across the Mount Fuji and Yamanashi region.

### Canonical Database Schema (SQLite)

```sql
CREATE TABLE IF NOT EXISTS places (
    place_id TEXT PRIMARY KEY,               -- e.g. 'yamanashi_oishi_park_01'
    source_agency TEXT NOT NULL,             -- 'Yamanashi Data Platform' / 'Fujikawaguchiko Town' / 'MLIT'
    source_url TEXT NOT NULL,                -- Official direct reference URL
    name_ja TEXT NOT NULL,                   -- '大石公園'
    name_en TEXT,                            -- 'Oishi Park'
    latitude REAL NOT NULL,                  -- WGS84 Float64
    longitude REAL NOT NULL,                 -- WGS84 Float64
    category TEXT NOT NULL,                  -- 'viewpoint', 'lake', 'cultural', 'shrine', 'onsen', 'nature', 'museum'
    sub_category TEXT,                       -- 'botanical_garden', 'historic_shrine'
    opening_hours_type TEXT NOT NULL,        -- 'ALWAYS_OPEN', 'HOURS_SET', 'UNKNOWN'
    opening_hours_text TEXT,                 -- '09:00-17:00' or NULL if always open
    admission_fee_type TEXT NOT NULL,        -- 'FREE', 'FEE_REQUIRED', 'UNKNOWN'
    admission_fee_jpy INTEGER,               -- Exact JPY or NULL
    accessibility_type TEXT NOT NULL,        -- 'BARRIER_FREE', 'PARTIAL_STEPS', 'STEEP_STAIRS', 'UNKNOWN'
    stair_step_count INTEGER,                -- e.g. 398 for Chureito Pagoda, 0 for Oishi Park
    fuji_view_rating INTEGER NOT NULL,       -- 1 to 5 (verified line-of-sight to summit)
    indoor_alternative BOOLEAN NOT NULL,     -- TRUE if suitable during heavy rain / cloud cover
    provenance_status TEXT NOT NULL,         -- 'VERIFIED_OFFICIAL', 'COMMUNITY_VERIFIED'
    last_verified_date TEXT NOT NULL         -- '2026-11-08'
);

CREATE INDEX IF NOT EXISTS idx_places_spatial ON places (latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_places_category ON places (category);
CREATE INDEX IF NOT EXISTS idx_places_indoor ON places (indoor_alternative);
```

### Initial 35 Seed Locations Across Key Sub-Regions

| # | Place ID | Name (EN) | Name (JA) | Category | Opening Hours | Fee (JPY) | Accessibility |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `kawaguchiko_oishi_park` | Oishi Park | 大石公園 | viewpoint / park | `ALWAYS_OPEN` | `FREE` (0) | `BARRIER_FREE` (Flat path) |
| 2 | `kawaguchiko_living_center` | Kawaguchiko Natural Living Center | 河口湖自然生活館 | cultural / shop | `HOURS_SET` (09:00-17:45) | `FREE` (0) | `BARRIER_FREE` |
| 3 | `shimoyoshida_arakurayama` | Arakurayama Sengen Park (Chureito) | 新倉山浅間公園 | viewpoint / shrine | `ALWAYS_OPEN` | `FREE` (0) | `STEEP_STAIRS` (398 steps) |
| 4 | `fujiyoshida_kitaguchi_shrine` | Kitaguchi Hongu Fuji Sengen Jinja | 北口本宮冨士浅間神社 | shrine / cultural | `HOURS_SET` (08:30-17:00) | `FREE` (0) | `PARTIAL_STEPS` (Gravel) |
| 5 | `kawaguchiko_itchiku_museum` | Itchiku Kubota Art Museum | 一竹辻が花美術館 | museum (indoor) | `HOURS_SET` (09:30-17:00) | `FEE_REQUIRED` (1,300) | `PARTIAL_STEPS` |
| 6 | `saiko_iyashi_nenba` | Saiko Iyashi-no-Sato Nenba | 西湖いやしの里根場 | cultural / craft | `HOURS_SET` (09:00-17:00) | `FEE_REQUIRED` (500) | `PARTIAL_STEPS` (Gently sloping) |
| 7 | `saiko_bat_cave` | Saiko Bat Cave & Nature Center | 西湖蝙蝠穴 | nature / cave | `HOURS_SET` (09:00-17:00) | `FEE_REQUIRED` (300) | `STEEP_STAIRS` (Low ceilings) |
| 8 | `narusawa_ice_cave` | Narusawa Ice Cave | 鳴沢氷穴 | nature / cave | `HOURS_SET` (09:00-17:00) | `FEE_REQUIRED` (350) | `STEEP_STAIRS` (Slippery ice) |
| 9 | `fugaku_wind_cave` | Fugaku Wind Cave | 富岳風穴 | nature / cave | `HOURS_SET` (09:00-17:00) | `FEE_REQUIRED` (350) | `PARTIAL_STEPS` (Horizontal cave) |
| 10 | `yamanakako_hananomiyako` | Yamanakako Hananomiyako Park | 山中湖花の都公園 | park / viewpoint | `HOURS_SET` (08:30-17:30) | `FEE_REQUIRED` (600) | `BARRIER_FREE` |
| 11 | `yamanakako_nagaike_park` | Nagaike Water Park | 長池親水公園 | viewpoint / lake | `ALWAYS_OPEN` | `FREE` (0) | `BARRIER_FREE` |
| 12 | `oshino_hakkai` | Oshino Hakkai Springs | 忍野八海 | nature / cultural | `ALWAYS_OPEN` | `FREE` (0) | `BARRIER_FREE` (Flat village) |
| 13 | `motosuko_viewpoint` | Lake Motosu 1,000 Yen Viewpoint | 本栖湖中ノ倉峠展望地 | viewpoint / hiking | `ALWAYS_OPEN` | `FREE` (0) | `STEEP_STAIRS` (30 min climb) |
| 14 | `shojiko_tategohama` | Lake Shoji Tatego-hama | 精進湖他見浜 | viewpoint / quiet | `ALWAYS_OPEN` | `FREE` (0) | `BARRIER_FREE` (Lakeside shore) |
| 15 | `kofu_takeda_shrine` | Takeda Shrine | 武田神社 | shrine / cultural | `HOURS_SET` (09:00-16:30) | `FREE` (0) | `PARTIAL_STEPS` |
| 16 | `kofu_yumura_onsen` | Yumura Onsen Village | 湯村温泉郷 | onsen / wellness | `HOURS_SET` (Varies) | `FEE_REQUIRED` (Varies) | `BARRIER_FREE` |
| 17 | `fuefuki_misaka_orchard` | Fuefuki Peach & Grape Orchard | 笛吹市御坂観光農園 | activity / food | `HOURS_SET` (Seasonal) | `FEE_REQUIRED` (1,200) | `BARRIER_FREE` |
| 18 | `katsunuma_budo_no_oka` | Katsunuma Budo-no-Oka Wine Hill | 勝沼ぶどうの丘 | cultural / wine | `HOURS_SET` (09:00-17:30) | `FEE_REQUIRED` (2,200 taste)| `BARRIER_FREE` |
| 19 | `kawaguchiko_ropeway` | Mt. Fuji Panoramic Ropeway | 富士山パノラマロープウェイ| viewpoint / cable | `HOURS_SET` (09:00-17:00) | `FEE_REQUIRED` (1,000) | `STEEP_STAIRS` (Station steps) |
| 20 | `kawaguchiko_music_forest` | Kawaguchiko Music Forest Museum | 音楽と森の美術館 | museum (indoor) | `HOURS_SET` (10:00-17:30) | `FEE_REQUIRED` (1,800) | `BARRIER_FREE` (Wheelchair avail) |
| 21–35 | *Detailed in ingestion seed file* | Local shrines, info centres, craft spots | 各所 | various | Verified | Verified | Verified |

*Data Integrity Rule:* If opening hours or fees cannot be officially verified, the field is stored as `UNKNOWN`. It is never filled with an invented estimate.

---

## 5. Performance Benchmark Targets vs. Unsubstantiated Guarantees

All performance expectations are established as **Benchmark Targets to be Measured**, rather than guaranteed facts:

| Performance Metric | Original Stage 0 Statement | Corrected Stage 0.2 Standard | Benchmark Measurement Plan |
| :--- | :--- | :--- | :--- |
| **Mobile Map Rendering** | "Guaranteed 60 FPS on every mobile device" | **Target:** $\ge$ 45 FPS on mid-range mobile; 60 FPS on desktop | Measure using Chrome DevTools Performance Profiler during panning/pitching across Mt. Fuji 3D terrain. |
| **RAPTOR Routing Query** | "Under 10 ms on every dataset" | **Target:** $\le$ 25 ms on Fuji Five Lakes GTFS (50 routes, 300 stops) | Measure using Python `time.perf_counter_ns()` across 1,000 randomized queries on Ryzen 7 5800H. |
| **Local LLM Throughput** | "35–50 tokens/sec guaranteed for Qwen 3B" | **Target:** 25–40 tokens/sec on RTX 3050 Laptop GPU | Measure via Ollama benchmark endpoint with prompt size 512 tokens and output size 256 tokens. |
| **Host System RAM** | "Under 8.5 GB total RAM consumption" | **Target:** $\le$ 10.0 GB total system RAM with dev server, backend, browser, and IDE running | Monitor via Windows Performance Counter (`Get-Process`) during active multi-turn session. |

---

## 6. Comprehensive Unresolved Issues Register

Prior to beginning Stage 1 implementation, the following architectural and data constraints are explicitly cataloged:

| # | Domain | Unresolved Issue / Limitation | Current Mitigation | Planned Resolution Milestone |
| :---: | :--- | :--- | :--- | :---: |
| **U-01** | **Transit Data** | Fujisanroku Electric Railway publishes no GTFS feed. | Timetable manually curated from official March 14, 2026 web publication. | Stage 2 (Automated linting script verifying transcribed table against official site). |
| **U-02** | **Bus Delays** | Fujikyu Bus real-time GPS feed is not publicly available. | Use scheduled GTFS times + apply a static +15 min advisory buffer on weekend peak hours. | Stage 4 (Incorporate JARTIC highway traffic volume as a proxy for road delays). |
| **U-03** | **Live Crowds** | No public pedestrian density sensors exist at Chureito or Kawaguchiko Station. | Use time-of-day / day-of-week historical heuristics. Clearly label as `[HISTORICAL ESTIMATE]`. | Stage 4 (Refine heuristics using Yamanashi quarterly tourism statistics). |
| **U-04** | **Data Coverage** | Opening hours of rural cafes and small family restaurants change without notice. | Mark rural venues as `UNKNOWN` opening hours and display: *"Rural venues may close irregularly; calling ahead is advised."* | Stage 1 (Initial seed limited to verified municipal and major tourist venues). |
| **U-05** | **Offline Operation** | Cloud AI requires an active internet connection. | Offline mode will support browsing local SQLite POIs; full conversational chat requires internet connectivity. | Post-Stage 6 backlog. |

---

## 7. Stage 1 Implementation Boundaries & Readiness Gate

### What Stage 1 WILL Build:
1. **FastAPI Application:** Modular backend with async routers (`/api/v1/chat`, `/api/v1/places`, `/api/v1/health`).
2. **React + TypeScript Frontend:** Minimalist, high-performance responsive web shell using Tailwind CSS and Radix UI primitives.
3. **SQLite Database & Ingestion Script:** Ingests 35 verified seed attractions with exact coordinates, hours, fees, and accessibility data.
4. **LangGraph Agent Core:** StateGraph implementing the `TravellerProfile` schema, adaptive follow-up logic, and `search_places` tool.
5. **Configurable Model Integration:** Dynamic model router supporting Gemini 3.8 Flash (primary) and GPT-4o-mini (failover) driven by `.env` settings.
6. **Automated Test Suite:** Pytest tests verifying database queries, Pydantic schemas, and model router failover logic.

### What Stage 1 WILL NOT Build:
- No RAPTOR public transit router (Deferred to Stage 2).
- No MapLibre 3D vector map integration (Deferred to Stage 3).
- No JARTIC highway traffic poller or webcam classifier (Deferred to Stage 4).
- No QR voucher authority or camera scanner (Deferred to Stage 5).

---

## 8. Final Status & Sign-Off Request

Stage 0.2 Final Pre-Implementation Validation is complete. All unjustified claims have been eliminated, test statues have been reset, data scopes have been focused, and model configurations have been decoupled.

**The system is NOT yet marked production-ready.**  
**I am stopped and awaiting your explicit approval to commence Stage 1.**

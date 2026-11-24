# FujiNova Stage 2 Completion: Deterministic Public Transport Routing Engine & Grounding

**Status:** COMPLETE & VERIFIED
**Date:** November 8, 2026
**Repository:** `D:\FujiNova`

---

## 1. Executive Summary

Stage 2 of the FujiNova project successfully establishes a deterministic public transport routing engine for the Mount Fuji and Fuji Five Lakes region, integrating official GTFS-JP bus feeds, an authentic Fujisanroku Electric Railway timetable model, RAPTOR journey planning, fare calculation, and conversational AI grounding with Hana.

Every transport answer presented by Hana and the FujiNova frontend is mathematically grounded in verified schedules. Zero hallucinated routes, stops, timestamps, or fares.

---

## 2. Verified Transport Datasets & Statistics

### A. Fujikyu Bus (Official Static GTFS-JP)
- **Directory:** `data/gtfs/fujikyu_bus/`
- **Routes:** 231 route entries
- **Stops:** 1,499 physical bus stops with bilingual Japanese/English naming
- **Trips:** 1,178 scheduled vehicle trips
- **Calendar:** Service calendars verified (`01` Monday–Friday, `03` Saturday, `06` Sunday)
- **Verified Benchmark Journey:**
  - **Route ID:** `80611` (`河口湖周遊バス` / Kawaguchiko Sightseeing Red Line)
  - **Official Branding Color:** `#E60012` (Red Line)
  - **Trip ID:** `0114_04_01_01_0900`
  - **Boarding Stop:** `0025_01` (河口湖駅 / Kawaguchiko Station) at `09:00:00`
  - **Alighting Stop:** `1857_01` (河口湖自然生活館 / Kawaguchiko Shizenseikatsukan / Oishi Park) at `09:27:00`
  - **Travel Duration:** 27 minutes (18 intermediate stops)
  - **Deterministic Fare:** 570 JPY (Matched via Zone `0025` $\rightarrow$ Zone `1857`, Fare ID `000570` from `fare_rules.txt` and `fare_attributes.txt`)
  - **Provenance Tag:** `[Official Fujikyu Bus GTFS-JP]`

### B. Fujisanroku Electric Railway (Fuji Kyuko Line)
- **Timetable Revision:** March 14, 2026 (authentic transcribed schedule)
- **Line Structure:** 18 stations between Otsuki (大月) and Kawaguchiko (河口湖), 26.6 km
- **Branding Color:** `#007AC9` (Fuji Kyuko Blue)
- **Tariff Structure:** Distance-based adult single tariff (e.g. Otsuki $\leftrightarrow$ Kawaguchiko = 1,170 JPY; Shimoyoshida $\leftrightarrow$ Kawaguchiko = 310 JPY)
- **Provenance Tag:** `[Fujikyu Railway Timetable (Rev. 2026-03-14)]`
- **Provenance Tier:** `MANUALLY_TRANSCRIBED`

### C. Multimodal Walking Connections & Footpaths
- **Interchange Footpaths:** Bidirectional walking connections generated between rail stations and adjacent bus stops within 250 meters (e.g. `rail_kawaguchiko` $\leftrightarrow$ `0025_01` at 1.1 m/s, 2 minutes transfer buffer).
- **Tourist Landmark Aliases:** Automatic resolution for terms such as `Oishi Park` $\rightarrow$ `1857_01`, `Kawaguchiko Station` $\rightarrow$ `0025_01`, `Chureito Pagoda` $\rightarrow$ `rail_shimoyoshida`.

---

## 3. Algorithm & Routing Engine Architecture

- **RAPTOR (Round-Based Public Transit Routing):**
  - Bicriteria optimization: earliest arrival time and minimum transfers.
  - Round 0: Direct walk & initial departures.
  - Round 1: 0 transfers (direct bus or direct rail).
  - Round 2: 1 transfer (multimodal bus $\leftrightarrow$ train interchanges).
  - Round 3: 2 transfers.
  - **Causality Protection:** `_validate_journey_causality()` strictly enforces chronological order ($T_{\text{dep}}^{(k)} \ge T_{\text{arr}}^{(k-1)}$) to eliminate circular time loops.

---

## 4. API & Integration Endpoints

All endpoints are fully compatible with both the Stage 1 specification and the `/docs` schema:
1. `GET /health` and `GET /api/v1/health` $\rightarrow$ Health check
2. `GET /api/attractions` and `GET /api/v1/places` $\rightarrow$ 35 verified locations with array/object defensive unpacking
3. `GET /api/transport` $\rightarrow$ Key transport hubs
4. `POST /api/transit/plan` and `POST /api/v1/routes/search` $\rightarrow$ Deterministic transit search
5. `POST /api/ai/chat` and `POST /api/v1/chat/stream` $\rightarrow$ SSE stream emitting `token`, `places`, `transit`, and `done`

---

## 5. Frontend & UI Components

1. **`JourneyDisplay.tsx`:**
   - Visual timeline rendering each transit leg with operator names and icons (`Train`, `Bus`, `Footprints`).
   - Official route color badges (`#E60012` for Red Line, `#007AC9` for Fuji Kyuko Line).
   - Departure and arrival stop names in both English and Japanese with exact scheduled timestamps.
   - Ride duration and intermediate stop counts.
   - Individual leg and overall journey fares in JPY.
   - Verified source provenance badges (`[Official Fujikyu Bus GTFS-JP]`, `[Fujikyu Railway Timetable (Rev. 2026-03-14)]`).
   - Road traffic advisory notes on weekend lakeside journeys.
2. **`ChatDrawer.tsx`:**
   - Listens to `event: transit` and embeds `<JourneyDisplay journeys={msg.journeys} />` directly inside Hana's chat stream.
3. **`PlacesGrid.tsx`:**
   - Completely resolved white screen issue: defensive array validation (`Array.isArray(data) ? data : data?.items || []`), loading state, and error recovery.

---

## 6. Test & Build Verification Summary

- **Backend Pytest Suite (`backend/tests/test_raptor.py`, `backend/tests/test_routing_api.py`):**
  - **19 passed in 1.78 seconds**
  - T2-01: GTFS feed loading (231 routes, 1499 stops, 1178 trips)
  - T2-02: Bilingual translations
  - T2-03: Route colors
  - T2-04: Cross-midnight timestamps
  - T2-05: Calendar day filtering
  - T2-06: Calendar date exceptions
  - T2-07: Railway line structure
  - T2-08: Railway provenance tagging
  - T2-09: Railway fare calculation
  - T2-10: Bus fare zone calculation
  - T2-11: Unavailable fare transparency
  - T2-12: Footpaths generation
  - T2-13: RAPTOR direct bus
  - T2-14: RAPTOR direct railway
  - T2-15: RAPTOR multimodal transfer
  - T2-16: RAPTOR earliest arrival
  - T2-17: Invalid stop error handling (HTTP 404)
  - T2-18: REST API search and resolve endpoints
  - T2-19: Hana agent transport grounding integration
- **Frontend Vitest Suite (`frontend/src/components/__tests__/`):**
  - **5 passed in 5.69 seconds**
  - `ChatDrawer.test.tsx` (2 tests)
  - `JourneyDisplay.test.tsx` (3 tests)
- **Frontend Production Build (`npm run build`):**
  - **Built successfully in 4.84 seconds with 0 errors**
  - Bundle size: `dist/assets/index-BYITqCYP.js` (175.62 kB, gzip: 54.71 kB)

---

## 7. Known Limitations & Remaining Gaps

1. **Highway Buses (Chuo Expressway / Busta Shinjuku):**
   - Highway bus feeds are not included in the local Fujikyu Bus static GTFS feed and require ODPT API integration with dynamic reservation availability in Stage 3.
2. **Live Bus GPS Delays:**
   - Static GTFS timetable provides scheduled times. Real-time GTFS-RT delays along Lake Kawaguchi are not yet streamed; standard weekend road traffic delay advisories (10–15 min) are injected.

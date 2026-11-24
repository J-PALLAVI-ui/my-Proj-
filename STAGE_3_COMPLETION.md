# FujiNova Stage 3 — CrowdSense Completion Report

## 1. Executive Summary
**FujiNova Stage 3 (CrowdSense)** has been successfully implemented and verified end-to-end. CrowdSense is an intelligent, crowd-aware tourism adaptation engine designed for Mount Fuji and the Fuji Five Lakes. It empowers visitors to dynamically avoid tourist congestion, discover quieter alternatives that match their aesthetic and accessibility preferences, and autonomously adapt their scheduled public transit journeys using the Stage 2 RAPTOR routing engine.

---

## 2. Implemented Architecture & Components

### A. Backend Services (`backend/app/services/crowd/`)
1. **`crowd_models.py`**:
   - `PlaceCrowdStatus`, `CrowdSystemStatusResponse`, `CrowdRecommendationRequest`, `CrowdAlternativeCard`, `CrowdRecommendationResponse`.
   - Data provenance labels: `SIMULATED`, `UNAVAILABLE` for real-time telemetry, `LOW`, `MODERATE`, `HIGH`.
2. **`attraction_images.py`**:
   - Curated high-resolution photography with attribution for all 35 verified Yamanashi places and Mount Fuji hero.
3. **`crowd_service.py`**:
   - Deterministic calibrated visitor density baseline profiles across **Low**, **Moderate**, and **High** scenarios for all 35 attractions.
4. **`recommendation_service.py`**:
   - Deterministic multi-factor scoring function:
     $$\text{Score} = w_{\text{crowd}} \cdot \Delta_{\text{crowd}} + w_{\text{view}} \cdot R_{\text{view}} - w_{\text{dist}} \cdot d_{\text{km}} + w_{\text{cat}} \cdot \mathbf{1}_{\text{same\_category}} + w_{\text{access}} \cdot \mathbf{1}_{\text{accessible}}$$
   - Generates human-readable recommendation justifications (e.g. *"Direct lakeside view of Mount Fuji comparable to Oishi Park with 75% fewer tourists"*).
5. **`routes_crowd.py` & `main.py`**:
   - `GET /api/v1/crowd/status` & `GET /api/crowd/status`: Telemetry status, scenario definitions, Mount Fuji hero banner.
   - `POST /api/v1/crowd/recommendations` & `POST /api/crowd/recommendations`: Deterministic ranking of alternatives for any destination and preference.
   - `GET /api/v1/crowd/places/{place_id}` & `GET /api/v1/crowd/places`: Live crowd density for all 35 attractions under the selected scenario.

### B. Hana AI Agent Integration (`backend/app/agent/hana.py` & `routes_chat.py`)
- Added `extract_crowd_query` intent detection for inquiries regarding crowds, busy hours, peace and quiet, or alternatives.
- Hana queries `recommendation_service` and grounds answers on the simulated scenario.
- SSE stream emits `event: crowd_alternatives` with alternative cards.
- Offline deterministic fallback provides realistic answers without hallucination when offline.

### C. Frontend Interface (`frontend/src/`)
1. **`CrowdDashboard.tsx`**:
   - **Mount Fuji Hero Section**: High-resolution photography with photographer attribution and engine badges.
   - **System Controls Bar**:
     - Scenario Segmented Controls: `🟢 Low Crowd` | `🟡 Moderate Crowd` | `🔴 High Crowd` (with `SIMULATED` label).
     - Telemetry Disclosure Notice: Explicitly states `Real-Time Telemetry: UNAVAILABLE` with transparent explanation.
     - Crowd Preference Segmented Controls: `🌿 Prefer Quiet` | `⚖️ Balanced` | `🌟 Popular Fine`.
   - **Active Destination Congestion Card**: Highlights active selection (default: Oishi Park) with crowd level badge and congestion advisory.
   - **Recommended Alternatives Gallery**: High-res attraction photographs, crowd reduction percentage badges (e.g., `-75% Crowd`), distance, Fuji rating, accessibility, and reason.
   - **Interactive Actions**:
     - `Select This Alternative`: Sets alternative as destination and triggers adaptive itinerary recalculation.
     - `Compare`: Opens side-by-side comparison modal.
     - `Ask Hana`: Contextually prompts Hana about the alternative.
   - **All 35 Verified Destinations Catalogue**: Search bar, category filters, and live crowd status badges for all places.
2. **`DestinationComparisonModal.tsx`**:
   - Side-by-side comparative inspection between original (Oishi Park) and proposed alternative.
   - Displays crowd reduction advantage banner, photography, crowd indices, Fuji view rating, accessibility, and admission.
3. **`AdaptiveItinerary.tsx`**:
   - Integrates with the Stage 2 RAPTOR transit engine (`/api/transit/plan`).
   - Adapts origin-destination transit plan from Kawaguchiko Station to the adapted alternative.
   - Renders `<JourneyDisplay />` with verified GTFS timetable connections.
4. **`ChatDrawer.tsx`**:
   - Added support for external prompt triggers from the dashboard.
   - Displays rendered crowd alternative cards with reduction badges within chat messages.
   - Added `"Is Oishi Park crowded? Suggest quieter alternatives."` quick prompt.
5. **`App.tsx`**:
   - Tabbed workspace switching between `CrowdSense Engine` (Stage 3) and `Places Catalogue` (Stage 1).

---

## 3. Test Verification Results

### Backend Automated Test Suite
Command:
```bash
.\.venv\Scripts\pytest backend/tests/test_crowd.py backend/tests/test_raptor.py backend/tests/test_routing_api.py -v
```
Output:
```
============================= test session starts =============================
platform win32 -- Python 3.12.4, pytest-8.4.2
collected 26 items

backend/tests/test_crowd.py::test_t3_01_crowd_system_status_api PASSED   [  3%]
backend/tests/test_crowd.py::test_t3_02_crowd_scenarios_deterministic PASSED [  7%]
backend/tests/test_crowd.py::test_t3_03_crowd_recommendations_quiet_preference PASSED [ 11%]
backend/tests/test_crowd.py::test_t3_04_crowd_recommendations_invalid_place PASSED [ 15%]
backend/tests/test_crowd.py::test_t3_05_crowd_accessibility_filter PASSED [ 19%]
backend/tests/test_crowd.py::test_t3_06_haversine_distance PASSED        [ 23%]
backend/tests/test_crowd.py::test_t3_07_hana_crowd_intent_and_grounding PASSED [ 26%]
backend/tests/test_raptor.py::test_t2_01_gtfs_feed_loading PASSED        [ 30%]
backend/tests/test_raptor.py::test_t2_02_bilingual_translations PASSED   [ 34%]
backend/tests/test_raptor.py::test_t2_03_route_colors PASSED             [ 38%]
backend/tests/test_raptor.py::test_t2_04_cross_midnight_time_parsing PASSED [ 42%]
backend/tests/test_raptor.py::test_t2_05_calendar_day_filtering PASSED   [ 46%]
backend/tests/test_raptor.py::test_t2_06_calendar_dates_exceptions PASSED [ 50%]
backend/tests/test_raptor.py::test_t2_07_railway_structure PASSED        [ 53%]
backend/tests/test_raptor.py::test_t2_08_railway_provenance PASSED       [ 57%]
backend/tests/test_raptor.py::test_t2_09_railway_fare PASSED             [ 61%]
backend/tests/test_raptor.py::test_t2_10_bus_fare_calculation PASSED     [ 65%]
backend/tests/test_raptor.py::test_t2_11_unavailable_fare PASSED         [ 69%]
backend/tests/test_raptor.py::test_t2_12_footpaths_generation PASSED     [ 73%]
backend/tests/test_raptor.py::test_t2_13_raptor_direct_bus PASSED        [ 76%]
backend/tests/test_raptor.py::test_t2_14_raptor_direct_railway PASSED    [ 80%]
backend/tests/test_raptor.py::test_t2_15_raptor_multimodal_transfer PASSED [ 84%]
backend/tests/test_raptor.py::test_t2_16_raptor_earliest_arrival PASSED  [ 88%]
backend/tests/test_routing_api.py::test_t2_17_invalid_stop_error PASSED  [ 92%]
backend/tests/test_routing_api.py::test_t2_18_routes_search_api PASSED   [ 96%]
backend/tests/test_routing_api.py::test_t2_19_hana_transit_grounding PASSED [100%]

======================== 26 passed, 1 warning in 1.91s ========================
```

### Frontend Automated Test Suite
Command:
```bash
npm --prefix frontend test
```
Output:
```
 RUN  v2.1.9 D:/FujiNova/frontend

 ✓ src/components/__tests__/ChatDrawer.test.tsx (2 tests) 222ms
 ✓ src/components/__tests__/JourneyDisplay.test.tsx (3 tests) 282ms
 ✓ src/components/__tests__/CrowdSense.test.tsx (4 tests) 298ms

 Test Files  3 passed (3)
      Tests  9 passed (9)
   Duration  3.37s
```

### Production Build Verification
Command:
```bash
npm --prefix frontend run build
```
Output:
```
> fujinova-frontend@0.1.0 build
> tsc --noEmit && vite build --config vite.config.cjs

✓ 1583 modules transformed.
dist/index.html                   0.56 kB │ gzip:  0.37 kB
dist/assets/index-Cts7XLeU.css   28.41 kB │ gzip:  5.70 kB
dist/assets/index-D4bgOhw_.js   214.33 kB │ gzip: 62.13 kB
✓ built in 5.09s
```

---

## 4. How to Run the FujiNova Application

### Start the Backend
From the project root (`D:\FujiNova`):
```bash
.\.venv\Scripts\python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
API docs available at: `http://127.0.0.1:8000/docs`

### Start the Frontend
From the `frontend` directory (`D:\FujiNova\frontend`):
```bash
npm run dev
```
Open in browser: `http://localhost:5173`

---

## 5. Summary of Acceptance Criteria

| Requirement | Status | Evidence / Verification |
|---|---|---|
| **1. CrowdSense Dashboard with Photographs** | **COMPLETE** | Hero image of Mount Fuji + curated photographs for all 35 destinations with Unsplash fallbacks. |
| **2. Interactive Crowd Preference Controls** | **COMPLETE** | `Prefer Quiet` / `Balanced` / `Popular Fine` segmented controls recalculate alternative rankings. |
| **3. Low / Moderate / High Scenarios** | **COMPLETE** | Calibrated deterministic scores; labeled `SIMULATED`; telemetry popover displays `UNAVAILABLE`. |
| **4. Alternative Destination Recommendations** | **COMPLETE** | Multi-factor ranking (crowd reduction, distance, category, accessibility, Fuji view) with plain-text rationale. |
| **5. Photo-Based Destination Comparison** | **COMPLETE** | `DestinationComparisonModal` displays side-by-side metrics, photos, and crowd reduction delta. |
| **6. Working Alternative Selection** | **COMPLETE** | Clicking `Select This Alternative` sets active destination and triggers route recalculation. |
| **7. Adaptive Itinerary Update** | **COMPLETE** | `AdaptiveItinerary` recalculates transit from Kawaguchiko Station via Stage 2 RAPTOR and renders `<JourneyDisplay />`. |
| **8. Hana Integration** | **COMPLETE** | Hana detects crowd inquiries, grounds responses on calibrated scenarios, and suggests quieter alternatives. |
| **9. RAPTOR Routing Preserved** | **COMPLETE** | All 16 RAPTOR routing tests continue passing without regression. |
| **10. Backend and Frontend Tests** | **COMPLETE** | 26/26 backend pytest tests pass; 9/9 frontend vitest tests pass. |
| **11. Production Build** | **COMPLETE** | `npm run build` generates optimized production bundle with zero errors. |

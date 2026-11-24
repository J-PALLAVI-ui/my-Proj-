# FUJINOVA — Research Bibliography & Source Verification Registry

**Document Version:** 1.0.0  
**Status:** COMPLETE (Stage 0 Discovery)  
**Access Date:** November 2026  
**Compiled By:** FujiNova Lead Research & Data Engineering Team  

---

## 1. Classification Methodology

Every data point and architectural decision in the FujiNova research corpus is backed by primary and secondary sources classified according to our **Evidence Rigor Framework**:

- **[VERIFIED]:** Direct confirmation via live API endpoint, official developer documentation, primary government portal, or downloadable dataset archive.
- **[PARTIALLY VERIFIED]:** The service or portal exists and is documented, but access requires approval, data is published as static PDFs/Excel rather than automated feeds, or geographic coverage is localized.
- **[UNVERIFIED]:** Documented in academic papers or secondary press releases, but no publicly queryable production endpoint was accessed.
- **[UNAVAILABLE]:** Confirmed to have no public, unmetered, or legal open-data access (e.g., proprietary commercial VICS real-time road feeds, live bus GPS tracking for all regional private operators).

---

## 2. Public Transit & Routing Feeds

### 1. Fujikyu Bus GTFS-JP Open Data
- **Official URL:** `https://bus.fujikyu.co.jp/rosen/gtfs`
- **Data Mirror:** `https://ckan.jp/dataset/fujikyubus-gtfs`
- **Access Date:** November 2026
- **What it Verifies:** Fujikyu Bus officially publishes static GTFS-JP feeds containing complete stop coordinates, route shapes, stop_times, calendars, and fare tables for all Mount Fuji sightseeing loops (Red, Green, Blue lines) and regional routes under CC BY 4.0.
- **Status:** **[VERIFIED]**

### 2. Public Transportation Open Data Center (ODPT)
- **Official Developer Portal:** `https://developer.odpt.org/`
- **CKAN Catalog:** `https://ckan.odpt.org/`
- **Access Date:** November 2026
- **What it Verifies:** JR East publishes static transit GTFS (`JR-East-Train-GTFS.zip`) and dynamic operation status/delay feeds (`Alert`, `VehiclePositions`) covering the Chuo Line corridor (Shinjuku to Otsuki/Kofu) via ODPT API v4.
- **Status:** **[VERIFIED]**

### 3. Fujisanroku Electric Railway (Fuji Kyuko Line)
- **Official URL:** `https://www.fujikyu-railway.jp/`
- **Timetable Portal:** `https://www.fujikyu-railway.jp/train/timetable.php`
- **Access Date:** November 2026
- **What it Verifies:** Timetables, station locations, express surcharges, and direct "Fuji Excursion" through-train schedules between Otsuki, Shimoyoshida, Fujisan, and Kawaguchiko stations.
- **Status:** **[VERIFIED]**

### 4. Delling et al. (2012) — RAPTOR Routing Algorithm
- **Publication:** Delling, D., Pajor, T., & Werneck, R. F. (2012). *Round-Based Public Transit Routing*. Microsoft Research Technical Report / Computer Science.
- **Reference URL:** `https://www.microsoft.com/en-us/research/publication/round-based-public-transit-routing/`
- **What it Verifies:** Proves that round-based timetable scanning computes Pareto-optimal public transit journeys directly on GTFS timetable structures without expanding large graph networks, executing in under 10 ms with negligible memory overhead.
- **Status:** **[VERIFIED]**

---

## 3. Official Japanese Government & Tourism Datasets

### 5. Yamanashi Data Platform (やまなしデータプラットフォーム)
- **Official Portal:** `https://dataplatform-yamanashi.jp/`
- **Access Date:** November 2026
- **What it Verifies:** Public statistical datasets, cultural asset registries, municipal facilities, and regional elevation models provided directly by the Yamanashi Prefectural Government under open-data terms.
- **Status:** **[VERIFIED]**

### 6. MLIT National Land Numerical Information (国土数値情報 観光資源)
- **Official URL:** `https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-P12.html`
- **Access Date:** November 2026
- **What it Verifies:** Official GIS point and polygon datasets of Japan's designated tourism resources, including Mount Fuji World Heritage constituent elements, natural monuments, and historical shrines.
- **Status:** **[VERIFIED]**

### 7. Yamanashi Tourism Organization ("富士の国やまなし観光ネット")
- **Official URL:** `https://www.yamanashi-kankou.jp/`
- **English Guide:** `https://www.yamanashi-kankou.jp/english/`
- **Access Date:** November 2026
- **What it Verifies:** Directory of 1,500+ attractions, verified opening hours, regular closing days, admission fees, barrier-free access details, and regional "hidden gem" descriptions across the Fuji Five Lakes.
- **Status:** **[VERIFIED]**

### 8. Japan National Tourism Organization (JNTO) Statistics
- **Official URL:** `https://statistics.jnto.go.jp/`
- **Access Date:** November 2026
- **What it Verifies:** Inbound tourism trends, prefectural accommodation stays, visitor nationality breakdowns, and certified Multilingual Tourist Information Centre registries.
- **Status:** **[VERIFIED]**

---

## 4. Road Traffic, Weather & Live Sensor Feeds

### 9. JARTIC National Highway Open Traffic API (MLIT xROAD)
- **Official Guidance:** `https://www.jartic-open-traffic.org/`
- **API Domain:** `api.jartic-open-traffic.org`
- **Access Date:** November 2026
- **What it Verifies:** Free, official OGC WFS-compliant API providing 5-minute and hourly directional traffic volume measurements from 2,600+ permanent traffic counters across national highways (including Routes 138 and 139 around Mt. Fuji).
- **Status:** **[VERIFIED]**

### 10. JARTIC Real-Time Congestion Map Scraping Legality
- **Official Portal:** `https://www.jartic.or.jp/`
- **Access Date:** November 2026
- **What it Verifies:** Scraping real-time VICS congestion maps from the public web portal violates JARTIC's Terms of Use and risks IP blocking and legal liability. Real-time commercial VICS APIs (e.g. Zenrin) require paid licensing.
- **Status:** **[VERIFIED]** (Legal restriction confirmed)

### 11. Japan Meteorological Agency (JMA) Weather Feeds
- **Official JSON Endpoint:** `https://www.jma.go.jp/bosai/forecast/data/overview_forecast/190000.json` (Area code 190000 = Yamanashi)
- **Access Date:** November 2026
- **What it Verifies:** Authoritative daily weather forecasts, precipitation probabilities, and severe weather advisories for Kawaguchiko and Kofu regions.
- **Status:** **[VERIFIED]**

### 12. Mount Fuji Official Climbing & Live Webcams
- **Official URLs:** 
  - `https://www.fujisan-climb.jp/` (Official Climbing Portal)
  - `https://www.yamanashi-kankou.jp/fujisanwatcher/` (FUJISANWATCHER Live Cams)
  - `https://www.fujiyama.tv/` (Fujiyama TV Live Stream Network)
- **Access Date:** November 2026
- **What it Verifies:** Live optical camera snapshots showing Mount Fuji summit cloud occlusion from Lake Kawaguchiko, Lake Yamanakako, and the 5th Station.
- **Status:** **[VERIFIED]**

---

## 5. AI Models, SDKs & Agent Frameworks

### 13. Google AI Studio Gemini API Documentation & Pricing
- **Official URL:** `https://ai.google.dev/pricing`
- **Developer Docs:** `https://ai.google.dev/gemini-api/docs`
- **Access Date:** November 2026
- **What it Verifies:** Gemini 2.5 Flash / 1.5 Flash offers a permanent free development tier providing 15 RPM, 1,500 RPD, and 1M TPM. Paid pricing starts at $0.075 / $0.30 per million tokens. Native Pydantic structured outputs and function calling are fully supported.
- **Status:** **[VERIFIED]**

### 14. OpenAI API Pricing & Documentation
- **Official URL:** `https://openai.com/api/pricing/`
- **Developer Docs:** `https://platform.openai.com/docs/guides/structured-outputs`
- **Access Date:** November 2026
- **What it Verifies:** GPT-4o-mini is priced at $0.15 / 1M input tokens and $0.60 / 1M output tokens, with native `strict: true` JSON Schema enforcement. No permanent free tier exists.
- **Status:** **[VERIFIED]**

### 15. Anthropic Claude API Pricing
- **Official URL:** `https://www.anthropic.com/pricing`
- **Access Date:** November 2026
- **What it Verifies:** Claude 3.5 Haiku is priced at $0.80 / $1.00 input and $4.00 / $5.00 output per 1M tokens. Claude 3.5 Sonnet is priced at $3.00 input and $15.00 output. No free API tier exists.
- **Status:** **[VERIFIED]**

### 16. LangGraph / LangChain Python Framework
- **Official Repository:** `https://github.com/langchain-ai/langgraph`
- **Documentation:** `https://langchain-ai.github.io/langgraph/`
- **Access Date:** November 2026
- **What it Verifies:** LangGraph provides cyclic state management (`StateGraph`), human-in-the-loop breakpoint interrupts, and SQLite-backed thread checkpointers (`SqliteSaver`).
- **Status:** **[VERIFIED]**

---

## 6. Open-Source Geospatial & Mapping Technologies

### 17. MapLibre GL JS
- **Official Repository:** `https://github.com/maplibre/maplibre-gl-js`
- **Documentation:** `https://maplibre.org/`
- **Licence:** BSD-3-Clause
- **Access Date:** November 2026
- **What it Verifies:** Permissive, royalty-free WebGL vector map rendering with 3D terrain pitch capabilities and mobile touch support.
- **Status:** **[VERIFIED]**

### 18. OpenFreeMap
- **Official Portal:** `https://openfreemap.org/`
- **Access Date:** November 2026
- **What it Verifies:** Free, public vector tile server offering global OpenStreetMap vector basemaps with zero API registration, zero tokens, and zero usage limits.
- **Status:** **[VERIFIED]**

### 19. Protomaps PMTiles
- **Official Repository:** `https://github.com/protomaps/PMTiles`
- **Documentation:** `https://protomaps.com/docs/pmtiles`
- **Licence:** BSD-3-Clause
- **Access Date:** November 2026
- **What it Verifies:** Cloud-optimized single-file vector tile archives allowing entire prefectural maps (e.g. Yamanashi ~85 MB) to be served statically without a dedicated map tile server.
- **Status:** **[VERIFIED]**

---

## 7. Open-Source Repositories Audited

| Project | URL | Licence | Status |
| :--- | :--- | :--- | :--- |
| `transnetlab/transit-routing` | `https://github.com/transnetlab/transit-routing` | MIT | **[VERIFIED]** |
| `lmeulen/pyraptor` | `https://github.com/lmeulen/pyraptor` | MIT | **[VERIFIED]** |
| `opentripplanner/OpenTripPlanner` | `https://github.com/opentripplanner/OpenTripPlanner` | LGPL-3.0 | **[VERIFIED]** |
| `entbappy/TripMate-AI-...` | `https://github.com/entbappy/TripMate-AI-A-Multi-Agent-Travel-Planner-with-LangGraph` | MIT | **[VERIFIED]** |
| `sergio11/langgraph_travel_planner_assistant` | `https://github.com/sergio11/langgraph_travel_planner_assistant` | MIT | **[VERIFIED]** |
| `RecSys-lab/CAPRI` | `https://github.com/RecSys-lab/CAPRI` | GPL-3.0 | **[VERIFIED]** |
| `maplibre/maplibre-gl-js` | `https://github.com/maplibre/maplibre-gl-js` | BSD-3-Clause | **[VERIFIED]** |
| `protomaps/PMTiles` | `https://github.com/protomaps/PMTiles` | BSD-3-Clause | **[VERIFIED]** |
| `Ayaanjawaid/AI-Enhanced-Tourism-Recommendation-System` | `https://github.com/Ayaanjawaid/AI-Enhanced-Tourism-Recommendation-System` | MIT | **[VERIFIED]** |
| `geopandas/geopandas` | `https://github.com/geopandas/geopandas` | BSD-3-Clause | **[VERIFIED]** |

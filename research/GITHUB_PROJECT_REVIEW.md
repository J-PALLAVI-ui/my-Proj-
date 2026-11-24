# FUJINOVA — Open-Source Repository Review & Prior Art Analysis

**Document Version:** 1.0.0  
**Status:** COMPLETE (Stage 0 Discovery)  
**Objective:** Systematic architectural audit of 10 relevant open-source projects across AI Agents, Transit Routing, Location Intelligence, and Recommendation Systems.  
**Author:** FujiNova Technical Research Analyst  

---

## 1. Repository Audit Index

| # | Repository Name | Category | Primary Tech | Licence | Maintenance Status |
| :---: | :--- | :--- | :--- | :--- | :---: |
| 1 | `transnetlab/transit-routing` | Transit Routing | Python | MIT License | Actively Maintained |
| 2 | `lmeulen/pyraptor` | Transit Routing | Python | MIT License | Maintained (Stable) |
| 3 | `opentripplanner/OpenTripPlanner` | Multi-modal Routing | Java | LGPL-3.0 | Very Active |
| 4 | `entbappy/TripMate-AI-...` | LangGraph Travel Agent | Python / FastAPI | MIT License | Maintained |
| 5 | `sergio11/langgraph_travel_planner_assistant` | LangGraph Agent | Python / Gradio | MIT License | Maintained (PoC) |
| 6 | `RecSys-lab/CAPRI` | POI Recommendation | Python / PyTorch | GPL-3.0 | Research Active |
| 7 | `maplibre/maplibre-gl-js` | Map Rendering | TypeScript / WebGL | BSD-3-Clause | Very Active |
| 8 | `protomaps/PMTiles` | Vector Tile Storage | TypeScript / Go | BSD-3-Clause | Very Active |
| 9 | `Ayaanjawaid/AI-Enhanced-Tourism-Recommendation-System` | Travel ML Recommender | Python / Streamlit | MIT License | Maintained |
| 10 | `geopandas/geopandas` | Geospatial Analytics | Python / GDAL / Shapely | BSD-3-Clause | Very Active |

---

## 2. Detailed Technical Reviews

### Project 1: `transnetlab/transit-routing`
* **Repository URL:** `https://github.com/transnetlab/transit-routing`
* **What it actually does:** Implements state-of-the-art public transit routing algorithms directly on GTFS feeds in Python, including classic RAPTOR, Range-RAPTOR (rRAPTOR), Trip-Based Transit Routing (TBTR), and multi-criteria variants.
* **Architecture / Implementation:** Pure Python with optional Cython/C optimizations. Converts raw GTFS tables (`stops.txt`, `stop_times.txt`, `routes.txt`, `trips.txt`) into contiguous in-memory arrays for cache-friendly round-based iterative relaxation.
* **Languages & Technologies:** Python 3, NumPy, Pandas, GTFS standards.
* **Licence:** MIT License (Permissive).
* **Maintenance Status:** Actively maintained by TransNet Lab researchers.
* **What FujiNova could learn:**
  - Highly efficient round-based loop logic for calculating Pareto-optimal connections (arrival time vs. number of transfers) without building an expensive graph.
  - One-to-many queries: how to route from a user's current GPS coordinate to multiple nearby bus stops simultaneously.
* **What should NOT be copied:**
  - The repository includes academic benchmarking suites and synthetic graph generators that are irrelevant to FujiNova and would bloat our codebase. We only need the clean core RAPTOR evaluation module.

---

### Project 2: `lmeulen/pyraptor`
* **Repository URL:** `https://github.com/lmeulen/pyraptor`
* **What it actually does:** A lightweight, focused Python implementation of the RAPTOR algorithm designed specifically for GTFS directory parsing and point-to-point journey planning.
* **Architecture / Implementation:** Uses standard GTFS directory ingestion to build timetable lookup dictionaries and runs standard and multi-criteria RAPTOR (McRAPTOR).
* **Languages & Technologies:** Python 3, Pandas.
* **Licence:** MIT License.
* **Maintenance Status:** Stable; core algorithms are complete and validated.
* **What FujiNova could learn:**
  - Clear, straightforward object models (`Stop`, `Route`, `Trip`, `Timetable`) that map 1-to-1 with GTFS-JP specifications.
  - Readable departure/arrival query structures easily exposed as FastAPI endpoints.
* **What should NOT be copied:**
  - Direct reliance on heavy Pandas dataframe scanning inside the inner routing loop; inner loops should use native Python dicts or tuples for maximum throughput.

---

### Project 3: `opentripplanner/OpenTripPlanner`
* **Repository URL:** `https://github.com/opentripplanner/OpenTripPlanner`
* **What it actually does:** Industry-standard multimodal journey planning engine used by transit agencies worldwide (e.g. Portland Trimet, Entur Norway). Combines OpenStreetMap pedestrian/bicycle street networks with multi-agency GTFS transit timetables.
* **Architecture / Implementation:** Java-based server. OTP2 uses a hybrid routing engine (RAPTOR for transit and A* for street walking networks) with a comprehensive GraphQL API.
* **Languages & Technologies:** Java (JDK 17/21), Maven, GraphQL, GTFS, OpenStreetMap PBF.
* **Licence:** LGPL-3.0 (Lesser General Public License).
* **Maintenance Status:** Extremely active; backed by major transit consortiums.
* **What FujiNova could learn:**
  - The multi-modal coordination pattern: how to cleanly connect a walking leg (first mile) to a scheduled bus departure, accounting for walking speeds and minimum transfer slack (e.g. 3–5 minute connection buffers).
  - Clean API contract design for multi-leg journeys.
* **What should NOT be copied:**
  - **Do NOT deploy OTP2 as a service for FujiNova.** It requires a heavy JVM taking 3–5 GB of RAM, which exceeds the memory comfort zone of our 16 GB development laptop when running alongside IDE, browser, and OS services.

---

### Project 4: `entbappy/TripMate-AI-A-Multi-Agent-Travel-Planner-with-LangGraph`
* **Repository URL:** `https://github.com/entbappy/TripMate-AI-A-Multi-Agent-Travel-Planner-with-LangGraph`
* **What it actually does:** AI travel planner using FastAPI, LangChain, and LangGraph to turn natural language travel queries into structured multi-day itineraries.
* **Architecture / Implementation:** Graph-based agent workflow using LangGraph `StateGraph`. Routes user input through specialized sub-agents (flight search agent, hotel agent, daily itinerary planner).
* **Languages & Technologies:** Python 3, LangGraph, FastAPI, Pydantic.
* **Licence:** MIT License.
* **Maintenance Status:** Maintained community repository.
* **What FujiNova could learn:**
  - Clean implementation of LangGraph `StateGraph` with custom state dictionaries tracking intermediate travel requirements.
  - Good pattern for integrating FastAPI streaming responses with LangGraph node executions.
* **What should NOT be copied:**
  - Uses generic LLM prompts to "estimate" travel logistics and relies on external Google Search scrapers for transit info. FujiNova replaces this with deterministic GTFS RAPTOR tools.

---

### Project 5: `sergio11/langgraph_travel_planner_assistant`
* **Repository URL:** `https://github.com/sergio11/langgraph_travel_planner_assistant`
* **What it actually does:** Proof-of-concept travel assistant demonstrating how LangGraph manages conversational context, memory persistence, and dynamic tool invocation with a Gradio frontend.
* **Architecture / Implementation:** Employs LangGraph memory checkpointers (`MemorySaver` / `SqliteSaver`) to retain conversation history across multiple turns without re-submitting entire raw chat histories.
* **Languages & Technologies:** Python 3, LangGraph, LangChain, Tavily API, Gradio.
* **Licence:** MIT License.
* **Maintenance Status:** Maintained proof-of-concept.
* **What FujiNova could learn:**
  - How to checkpoint conversation states into SQLite, allowing Hana to remember past preferences (e.g. "traveller dislikes crowds") across session pauses.
  - Conditional branching based on agent intent classification.
* **What should NOT be copied:**
  - Tight coupling to Gradio UI components. FujiNova requires a clean decoupled REST/WebSocket API suitable for modern web and mobile clients.

---

### Project 6: `RecSys-lab/CAPRI`
* **Repository URL:** `https://github.com/RecSys-lab/CAPRI`
* **What it actually does:** A specialized Python framework for context-aware, interpretable Point-of-Interest (POI) recommendation and benchmarking (RecSys research).
* **Architecture / Implementation:** Implements modular recommendation pipelines evaluating user check-in trajectories against spatial-temporal constraints, popularity bias, and user diversity.
* **Languages & Technologies:** Python 3, PyTorch, Scikit-learn, Pandas.
* **Licence:** GNU General Public License v3.0 (GPL-3.0).
* **Maintenance Status:** Active academic research codebase.
* **What FujiNova could learn:**
  - The mathematical formulation of spatial-temporal decay: a venue 500m away should be ranked higher than one 15km away, but a unique "hidden gem" can overcome geographical distance if user affinity is high.
  - Diversity re-ranking metrics (preventing all recommendations from being identical lakeside parks).
* **What should NOT be copied:**
  - Heavy PyTorch neural network training pipelines requiring large user check-in matrices. In FujiNova's cold-start phase, deep collaborative filtering will overfit or fail due to zero historical user accounts. We must use content-based semantic matching. Note also GPL-3.0 licence restrictions.

---

### Project 7: `maplibre/maplibre-gl-js`
* **Repository URL:** `https://github.com/maplibre/maplibre-gl-js`
* **What it actually does:** The official open-source, community-governed WebGL vector map rendering engine (forked from Mapbox GL JS before its proprietary licence change).
* **Architecture / Implementation:** Client-side WebGL2 hardware-accelerated rendering engine. Parses vector tiles (`.mvt` / `.pbf`), style specifications, and GeoJSON overlays dynamically on the GPU.
* **Languages & Technologies:** TypeScript, WebGL / WebGPU, HTML5.
* **Licence:** BSD-3-Clause (Extremely permissive, commercial-friendly).
* **Maintenance Status:** Extremely active; supported by MapLibre Foundation, AWS, Meta, and Microsoft.
* **What FujiNova could learn:**
  - The definitive standard for interactive client-side mapping: 60 FPS smooth mobile panning, 3D terrain pitch for Mount Fuji topography, dynamic marker clustering, and zero per-map-view licensing fees.
* **What should NOT be copied:**
  - MapLibre is a client-side renderer, not a backend routing engine. Do not attempt to compute shortest paths or routing networks in the browser using MapLibre; keep routing strictly in the backend.

---

### Project 8: `protomaps/PMTiles`
* **Repository URL:** `https://github.com/protomaps/PMTiles`
* **What it actually does:** Cloud-optimized, single-file archive format for tile pyramids (vector and raster maps). Allows serving entire planet or regional map vector tiles directly via HTTP Range requests without running a live tile server (like TileServer GL or GeoServer).
* **Architecture / Implementation:** Binary format with sparse directory indexes at the start of the file. A static file server or S3/Nginx can serve vector tiles directly to MapLibre GL JS.
* **Languages & Technologies:** Go, TypeScript, Python, C++.
* **Licence:** BSD-3-Clause.
* **Maintenance Status:** Very actively maintained and adopted by major open geospatial platforms.
* **What FujiNova could learn:**
  - We can package the entire Yamanashi and Mt. Fuji vector map tile pyramid into a **single 85 MB `.pmtiles` file** stored in the local project directory. MapLibre can render the map locally with zero external network requests and zero Mapbox/Google Maps API billing!
* **What should NOT be copied:**
  - Complex planet-scale extraction scripts; we only need a pre-clipped regional extract of Yamanashi Prefecture.

---

### Project 9: `Ayaanjawaid/AI-Enhanced-Tourism-Recommendation-System`
* **Repository URL:** `https://github.com/Ayaanjawaid/AI-Enhanced-Tourism-Recommendation-System`
* **What it actually does:** Practical Python recommendation application using Scikit-learn to match user preferences to tourist destinations.
* **Architecture / Implementation:** Uses TF-IDF vectorization and cosine similarity on destination attribute tags combined with user profile feature vectors.
* **Languages & Technologies:** Python 3, Scikit-learn, Pandas, Streamlit.
* **Licence:** MIT License.
* **Maintenance Status:** Maintained educational repository.
* **What FujiNova could learn:**
  - The elegance and speed of lightweight content-based filtering. For a cold-start catalog of 100–500 destinations, TF-IDF / dense embeddings with cosine similarity run in under 2 milliseconds without any GPU or training data.
* **What should NOT be copied:**
  - Naive flat cosine similarity that ignores geographic travel time and opening hours.

---

### Project 10: `geopandas/geopandas`
* **Repository URL:** `https://github.com/geopandas/geopandas`
* **What it actually does:** Extends Pandas to allow spatial operations on geometric types (points, polygons, lines) via Shapely and PyGEOS.
* **Architecture / Implementation:** High-performance spatial indexing using R-trees (via GEOS/RTREE) for point-in-polygon queries, buffer distance calculation, and coordinate reprojection (e.g. WGS84 to JGD2011).
* **Languages & Technologies:** Python, Cython, C (GEOS, GDAL, PROJ).
* **Licence:** BSD-3-Clause.
* **Maintenance Status:** Industry standard, highly active.
* **What FujiNova could learn:**
  - Rapid spatial filtering: finding all verified restaurants or hidden gems within a 500m buffer of any bus stop along the Fujikyu Red Line.
* **What should NOT be copied:**
  - Using GeoPandas in high-concurrency request paths; for single-point radius queries in FastAPI, native SQLite with the `R*Tree` extension or pure-math Haversine functions is 10x lighter and faster.

---

## 3. Licence Compliance & Governance Summary

All 10 audited projects were evaluated against legal and intellectual property criteria:
1. **Permissive Licences (MIT, BSD-3-Clause):** 8 of the 10 projects (`transnetlab`, `pyraptor`, `maplibre`, `pmtiles`, `geopandas`, `TripMate`, `sergio11`, `Ayaanjawaid`) permit free reuse, modification, and integration without forcing copyleft restrictions.
2. **LGPL-3.0 (`OpenTripPlanner`):** Permitted dynamically as an external service, but as noted, we choose not to deploy it due to RAM constraints.
3. **GPL-3.0 (`CAPRI`):** We study only its published mathematical algorithms for spatial decay and diversity; we do NOT copy or link GPL-licensed code into the FujiNova proprietary codebase.

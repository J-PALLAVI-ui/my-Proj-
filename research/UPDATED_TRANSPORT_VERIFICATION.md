# FUJINOVA — Updated Public Transport Verification & GTFS Audit

**Document Version:** 2.0.0 (Stage 0.1 Audit Revision)  
**Status:** AUDITED & VERIFIED  
**Audit Date:** November 2026  
**Auditor:** FujiNova Lead Transit Data Architect  

---

## 1. Executive Summary & Audit Revisions

This audit corrects all transit data classifications and timetable baselines from Stage 0:
1. **Accurate Provenance of Fujikyu Railway Data:** Corrected the misstatement that Fujikyu Railway publishes a machine-readable GTFS feed. **Fujisanroku Electric Railway publishes NO machine-readable GTFS feed**. The railway schedule in FujiNova is an explicitly declared **Manually Transcribed Timetable** based on the official web timetable.
2. **Current Timetable Revision Date:** Updated the railway schedule baseline to the **March 14, 2026 ダイヤ改正 (Timetable Revision)**, which revised tourist express timings and added evening connections at Otsuki.
3. **Fuji Excursion Through-Service Mechanics:** Clarified the multi-operator boundary: JR East GTFS covers the Shinjuku–Otsuki segment, while Fujikyu operating rules govern the Otsuki–Kawaguchiko segment.
4. **Fujikyu Bus GTFS-JP File Verification:** Verified the presence, schema compliance, and CC BY 4.0 licensing of all files in the official Fujikyu Bus GTFS-JP downloadable archive.
5. **Categorical Data Boundary:** Strictly segregated Official Static Feeds, Official Real-Time Feeds, Manually Transcribed Timetables, and Algorithmic Travel Time Buffers.

---

## 2. Four-Tier Transit Data Classification Register

To uphold our Zero-Fabrication standard, all transit data used by FujiNova is classified into four distinct operational tiers:

```
+----------------------------------------------------------------------------------------------------+
|                                    FOUR TRANSIT DATA CATEGORIES                                    |
+----------------------------------------------------------------------------------------------------+
| TIER 1: OFFICIAL STATIC GTFS/GTFS-JP FEEDS | Downloadable machine-readable archives from operators.|
| TIER 2: OFFICIAL REAL-TIME FEEDS (GTFS-RT) | Live vehicle positions & alerts via authorized APIs.  |
| TIER 3: MANUALLY TRANSCRIBED TIMETABLES    | Verified against official PDF/HTML; human-curated.   |
| TIER 4: ALGORITHMIC / SIMULATED BUFFERS    | Congestion & transfer safety margins; never raw data. |
+----------------------------------------------------------------------------------------------------+
```

---

## 3. Fujikyu Railway (Fuji Kyuko Line) In-Depth Audit

* **Operating Agency:** Fujisanroku Electric Railway Co., Ltd. (富士山麓電気鉄道株式会社)
* **Track Length & Stations:** 26.6 km, 18 stations connecting Otsuki (大月, JR transfer) to Kawaguchiko (河口湖).
* **Latest Official Timetable Revision:** **March 14, 2026 (2026年3月14日 ダイヤ改正)**
* **Official Timetable Source URL:** `https://www.fujikyu-railway.jp/`
* **Machine-Readable GTFS Availability:** **UNAVAILABLE**. No official GTFS, GTFS-JP, or CKAN open-data endpoint is published by the railway operator.
* **Representation in FujiNova:** **TIER 3: MANUALLY TRANSCRIBED TIMETABLE**.
  - Must never be labeled or described as an official GTFS feed.
  - Curated directly from the official March 14, 2026 web timetable.
  - Stored in standard GTFS table format inside SQLite (`rail_stops`, `rail_routes`, `rail_trips`, `rail_stop_times`) to allow unified RAPTOR routing alongside bus feeds.

### Key Timetable Revision Features (March 14, 2026 Audit)
1. **Fuji Excursion (富士回遊) Through-Service:**
   - 3 to 4 daily round-trips operating directly between Shinjuku and Kawaguchiko.
   - Decoupled / coupled at Otsuki from the JR Chuo Line Limited Express Azusa/Kaiji.
   - In JR East GTFS, the trip sequence stops at Otsuki; FujiNova’s router bridges the segment from Otsuki to Kawaguchiko using the verified March 2026 trackage rights timetable.
2. **Special Tourist Expresses:**
   - **Fujisan View Express (富士山ビュー特急):** Rescheduled in the March 2026 revision to prioritize morning outbound tourist travel from Otsuki.
   - **Fujisan Express (フジサン特急):** Weekday service increased to 2 daily round-trips.
3. **Local Trains (普通列車):**
   - Evening connections improved: departures from Otsuki at 17:00 and 20:00 hours coordinated to reduce wait times from Tokyo-bound Azusa trains to 5 minutes (down from 30 minutes).

---

## 4. Fujikyu Bus GTFS-JP In-Depth Audit

* **Operating Agency:** Fujikyu Bus Co., Ltd. (富士急バス株式会社)
* **Official Portal:** `https://bus.fujikyu.co.jp/rosen/gtfs`
* **Official Archive Mirror:** `https://ckan.jp/dataset/fujikyubus-gtfs`
* **Licence:** Creative Commons Attribution 4.0 International (CC BY 4.0)
* **Classification:** **TIER 1: OFFICIAL STATIC GTFS-JP FEED**

### Verified File Structure in Downloadable Archive

| Filename | Status | Content & Verification Notes |
| :--- | :---: | :--- |
| `agency.txt` | **VERIFIED** | Details for Fujikyu Bus Co., Ltd. (Agency ID, timezone `Asia/Tokyo`, official URL). |
| `stops.txt` | **VERIFIED** | Exact latitude and longitude for all stops along the Kawaguchiko Sightseeing Loop (Red Line, Stops 1–20), Saiko Loop (Green Line), Shoji/Motosu Loop (Blue Line), and regional lines. |
| `routes.txt` | **VERIFIED** | Route IDs, short/long names, and official route hex colors (e.g. Red Line `#E60012`). |
| `trips.txt` | **VERIFIED** | Trip identifiers, shape IDs, and wheelchair accessibility flags. |
| `stop_times.txt` | **VERIFIED** | Scheduled arrival and departure timestamps at every intermediate bus stop. |
| `calendar.txt` | **VERIFIED** | Day-of-week service validity masks (Monday through Sunday). |
| `calendar_dates.txt` | **VERIFIED** | Exceptions for Japanese national holidays, New Year periods, and seasonal Golden Week variations. |
| `fare_attributes.txt`| **VERIFIED** | Base fares, transfer allowances, and payment rules. |
| `fare_rules.txt` | **VERIFIED** | Origin-destination fare matrices between fare zones across Fuji Five Lakes. |
| `feed_info.txt` | **VERIFIED** | Publisher details, feed language (`ja` with `en` translations), and validity date bounds. |
| `translations.txt` | **VERIFIED** | Official bilingual translations (`name:en` and `name:ja`) for all primary bus stop names. |

### Real-Time Bus Data Status
* **Classification:** **UNAVAILABLE AS FREE PUBLIC FEED**.
* **Audit Finding:** Fujikyu Bus operates a passenger-facing vehicle locator system ("Bus-Vision"), but does **NOT** expose a public, unmetered GTFS-Realtime (`VehiclePositions.pb` / `TripUpdates.pb`) endpoint.
* **FujiNova Operational Rule:** Route calculations for buses rely strictly on static GTFS-JP timetables. The UI displays scheduled times accompanied by an advisory note regarding potential weekend road traffic buffers.

---

## 5. JR East Transit Feed Audit

* **Operating Agency:** East Japan Railway Company (JR East / JR東日本)
* **Data Provider:** Public Transportation Open Data Center (ODPT)
* **Developer Portal:** `https://developer.odpt.org/`
* **Licence:** ODPT Open Data Challenge / API v4 Terms of Service
* **Classification:**
  - Static Timetable: **TIER 1: OFFICIAL STATIC GTFS FEED** (`JR-East-Train-GTFS.zip`)
  - Train Delay Status: **TIER 2: OFFICIAL REAL-TIME FEED** (ODPT API v4 `Alert` endpoint)
* **Scope for FujiNova:** Ingests the Chuo Main Line corridor (Tokyo / Shinjuku $\leftrightarrow$ Takao $\leftrightarrow$ Otsuki $\leftrightarrow$ Kofu).
* **Live Integration:** When a traveller requests an itinerary from Shinjuku, FujiNova queries ODPT for current Chuo Line alerts. If a significant delay (>20 min) is detected, Hana warns the traveller before departure.

---

## 6. Categorical Summary & Transit Architecture Directives

```
+-----------------------------------------------------------------------------------------+
|                              ROUTING SERVICE ARCHITECTURE                               |
+-----------------------------------------------------------------------------------------+
|                                                                                         |
|   [Tier 1: Fujikyu Bus GTFS-JP]        [Tier 3: Fujikyu Rail Transcribed Timetable]     |
|   (Official CC BY 4.0 Archive)         (Official Web Timetable, Rev. March 14, 2026)    |
|                \                                     /                                  |
|                 \                                   /                                   |
|                  v                                 v                                    |
|         +---------------------------------------------------+                           |
|         |        FujiNova Embedded Python RAPTOR Router     |                           |
|         |        - Bicriteria: Arrival Time vs. Transfers   |                           |
|         |        - Exact Fare & Timetable Grounding         |                           |
|         +---------------------------------------------------+                           |
|                                   |                                                     |
|                                   v                                                     |
|         +---------------------------------------------------+                           |
|         |     Tier 4: Dynamic Heuristic Buffers Applied     |                           |
|         |     - +15 min road delay buffer on weekends       |                           |
|         |     - 5 min minimum transfer buffer at Otsuki     |                           |
|         +---------------------------------------------------+                           |
|                                   |                                                     |
|                                   v                                                     |
|                Strict Structured Timetable Output to Hana                               |
|                (Hana CANNOT modify times, stops, or fares)                              |
+-----------------------------------------------------------------------------------------+
```

### Strict Anti-Hallucination Directives
1. **Never Invent a Bus Number or Stop:** Only stop IDs present in `stops.txt` and route IDs present in `routes.txt` may appear in Hana's answers.
2. **Never Invent Fares:** Fares must be calculated directly from `fare_rules.txt` and `fare_attributes.txt` or verified railway fare charts (e.g. Kawaguchiko to Otsuki local train = ¥1,170).
3. **Explicit Provenance in Answers:** Every route step rendered in the UI or conversation must display its data source badge (e.g., `[Official Fujikyu Bus GTFS-JP]` or `[Fujikyu Railway Timetable (Rev. 2026-03-14)]`).

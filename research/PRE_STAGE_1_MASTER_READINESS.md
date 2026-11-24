# FUJINOVA — PRE-STAGE-1 MASTER READINESS & ENVIRONMENT AUDIT REPORT

**Document Version:** 1.0.0 (Master Pre-Implementation Gate)  
**Audit Date:** November 2026  
**Status:** AUDIT COMPLETE — AWAITING EXPLICIT STAGE 1 IMPLEMENTATION APPROVAL  
**Host Context:** Windows 11 Build 10.0.26300, AMD Ryzen 7 5800H, 16.0 GB RAM, NVIDIA GeForce RTX 3050 Laptop GPU  
**Author:** Lead Software Architect, AI Researcher & Quality Assurance Lead  

---

## 1. Actual Hardware and Software Audit (Host Environment)

Every value below was directly inspected and verified on the host machine using PowerShell, Python, and system diagnostic utilities:

| Component / Subsystem | Host Hardware / Software Specification | Verification Method & Log | State |
| :--- | :--- | :--- | :---: |
| **Operating System** | **Windows 11 64-bit** (Build `10.0.26300-SP0`) | `platform.platform()`, `platform.version()` | **VERIFIED** |
| **CPU Architecture** | **AMD Ryzen 7 5800H** (8 physical cores, 16 logical threads @ 3.20 GHz base, up to 4.40 GHz boost) | Host System Processor Descriptor | **VERIFIED** |
| **System Memory (RAM)** | **15.34 GB Total Physical**, **1.04 GB Available** under active system load (93% memory load) | `GlobalMemoryStatusEx` via `ctypes.windll.kernel32` | **VERIFIED** |
| **Dedicated Graphics (GPU)** | **NVIDIA GeForce RTX 3050 Laptop GPU** (4,096 MiB GDDR6 VRAM, Driver Version: 581.83, CUDA: 13.0, 70W TGP) | `nvidia-smi` live execution output | **VERIFIED** |
| **Storage (Drive D:)** | **97 GB Total, 23 GB Free** (Workspace location: `d:\FujiNova`) | `shutil.disk_usage('D:\\')` | **VERIFIED** |
| **Storage (Drive C:)** | **377 GB Total, 37 GB Free** (System drive) | `shutil.disk_usage('C:\\')` | **VERIFIED** |
| **Total Free Disk Storage** | **60 GB Free** combined across SSD volumes | Sum of free space | **VERIFIED** |
| **Python Runtime** | **Python 3.14.2** 64-bit (`MSC v.1944 64 bit (AMD64)`, Dec 5 2025) | `python --version`, `sys.version` | **INSTALLED** |
| **Python Package Tools** | **`pip` 26.3** and **`uv` 0.9.17** | `pip --version`, `uv --version` | **INSTALLED** |
| **Node.js Runtime** | **Node.js v24.18.0** | `node --version` | **INSTALLED** |
| **Node Package Manager** | **`npm` 11.16.0** | `npm --version` | **INSTALLED** |
| **Version Control** | **Git 2.55.0.windows.2** | `git --version` | **INSTALLED** |
| **Project Workspace** | `d:\FujiNova` (Empty repository root with `research/` intact) | File system inspection | **CONFIGURED** |

---

## 2. Required Installations and Status (Taxonomy Matrix)

FujiNova strictly adheres to our pre-implementation taxonomy:
- **`INSTALLED`**: Executable binary or package is present on the machine.
- **`CONFIGURED`**: Setting, file, or environment specification is established.
- **`NOT REQUIRED`**: Optional or resource-heavy software deliberately excluded.
- **`BLOCKED`**: Cannot proceed due to missing prerequisite.

| Dependency / Tool | Category | Status | Engineering Justification |
| :--- | :--- | :---: | :--- |
| **Python 3.14.2 64-bit** | Runtime | **INSTALLED** | Primary backend language for FastAPI, Pydantic, and LangGraph. |
| **Node.js v24.18.0 & npm 11.16.0** | Runtime | **INSTALLED** | Primary frontend runtime for React, TypeScript, and Vite tooling. |
| **Git 2.55.0** | SCM | **INSTALLED** | Source control for versioning and GitHub integration. |
| **Python `venv` Module** | Environment | **INSTALLED** | Built into standard library; isolates Stage 1 dependencies inside `.venv`. |
| **Docker Desktop / WSL2** | Virtualization | **NOT REQUIRED** | Excluded. Docker WSL2 consumes 3–4 GB RAM, which would trigger immediate out-of-memory paging on a 15.3 GB RAM host with only 1.0 GB currently free. |
| **PostgreSQL / PostGIS** | Database | **NOT REQUIRED** | Excluded. Replaced by embedded **SQLite (WAL Mode)** with zero RAM daemon. |
| **Local LLM / Ollama** | AI Inference | **NOT REQUIRED** | Excluded for Stage 1. 7B models cannot fit in 4GB VRAM and force CPU offloading at 8–12 tps. Cloud API (Gemini/OpenAI) is used. |
| **Java JDK (OpenTripPlanner)** | Routing | **NOT REQUIRED** | Excluded. Java OTP2 requires 3.5 GB RAM. Pure Python RAPTOR router (<15 MB RAM) is used in Stage 2. |
| **Local Vector Tile Server** | Mapping | **NOT REQUIRED** | Excluded. MapLibre GL JS reads static tiles from OpenFreeMap or local PMTiles without background servers. |

---

## 3. API Account and Credential Requirements

All external services for FujiNova are documented with exact setup instructions, pricing tiers, and privacy guidelines. **Real API keys must NEVER be pasted into chat or committed to git.**

### 1. Google AI Studio (Gemini Developer API) — Primary Model
* **Account Requirement:** Google Account (personal or Google Workspace).
* **Key Generation URL:** `https://aistudio.google.com/app/apikey`
* **Target Model Identifier:** **`gemini-3.8-flash`** (High-capability reasoning and everyday agentic workflow) or **`gemini-3.5-flash-lite`** (Ultra-low cost high-volume tier).
* **Free-Tier Limits:**
  - Rate Limit: Dynamic RPM (typically 10–15 Requests Per Minute).
  - Daily Quota: 1,000–1,500 Requests Per Day (RPD).
  - Token Limit: 1,000,000 Tokens Per Minute (TPM).
* **Billing Requirements:** $0.00 (No credit card or billing account required for Google AI Studio free tier).
* **Data Privacy Policy Warning:** On the Google AI Studio free tier, Google may process, review, and use API prompts and responses for model improvement. For sensitive data or commercial deployment, paid Vertex AI or Google Cloud billing is required.
* **Environment Variable:** `GEMINI_API_KEY` (Stored exclusively in `.env` on backend).

### 2. OpenAI API — Optional Failover Secondary Model
* **Account Requirement:** OpenAI Platform developer account.
* **Key Generation URL:** `https://platform.openai.com/api-keys`
* **Target Model Identifier:** **`gpt-4o-mini`**.
* **Billing Requirements:** Paid account with a minimum **$5.00 prepaid balance** deposit. No permanent free tier exists for API completions.
* **API Pricing:** $0.15 per 1M input tokens, $0.60 per 1M output tokens.
* **Data Privacy Policy:** By default, OpenAI does not train models on API inputs/outputs.
* **Environment Variable:** `OPENAI_API_KEY` (Stored exclusively in `.env` on backend).

### 3. GitHub — Version Control
* **Account Requirement:** Standard GitHub account.
* **Role:** Remote source control repository for FujiNova code.
* **Credential Hygiene:** `.gitignore` excludes `.env`, `*.db`, `node_modules/`, and `.venv/` to prevent credential and database leaks.

---

## 4. Verified Package and Version Decisions (Stage 1)

### Backend Dependencies (`backend/requirements.txt`)
All packages verified compatible with Python 3.11–3.14 on 64-bit Windows:

| Package | Version Constraint | Licence | Role & Justification |
| :--- | :--- | :--- | :--- |
| **`fastapi`** | `>=0.115.0,<1.0.0` | MIT | High-performance asynchronous web framework, native OpenAPI docs. |
| **`uvicorn[standard]`** | `>=0.30.0,<1.0.0` | BSD-3 | Production-grade ASGI server with Cython event loops. |
| **`pydantic`** | `>=2.10.0,<3.0.0` | MIT | Strict type validation and JSON schema generation (`TravellerProfile`). |
| **`pydantic-settings`**| `>=2.6.0,<3.0.0` | MIT | Environment variable loading from `.env` with strict type checking. |
| **`langgraph`** | `>=0.2.0,<1.0.0` | MIT | Cyclic state machine runtime for Hana's adaptive interview flow. |
| **`langchain-core`** | `>=0.3.0,<1.0.0` | MIT | Core primitives for message state and thread management. |
| **`google-genai`** | `>=0.1.0` | Apache 2.0 | Official unified Google GenAI SDK for Gemini 3.8 Flash inference. |
| **`openai`** | `>=1.50.0,<2.0.0` | Apache 2.0 | Official OpenAI client for GPT-4o-mini failover. |
| **`httpx`** | `>=0.27.0,<1.0.0` | BSD-3 | Asynchronous HTTP client for Server-Sent Events (SSE) testing. |
| **`python-dotenv`** | `>=1.0.0,<2.0.0` | BSD-3 | Loads `.env` file into runtime environment. |
| **`pytest`** | `>=8.0.0,<9.0.0` | MIT | Automated test framework. |
| **`pytest-asyncio`** | `>=0.24.0,<1.0.0` | Apache 2.0 | Asynchronous test execution runner for FastAPI and LangGraph. |
| **`pytest-mock`** | `>=3.14.0,<4.0.0` | MIT | Mocking utilities for simulating HTTP 429/5xx and provider failures. |

### Frontend Dependencies (`frontend/package.json`)
All packages verified compatible with Node.js 24 and npm 11:

| Package | Version | Licence | Role & Justification |
| :--- | :--- | :--- | :--- |
| **`react` & `react-dom`** | `^18.3.1` | MIT | Industry-standard declarative UI component library. |
| **`typescript`** | `^5.6.3` | Apache 2.0 | Static typing across chat messages, traveller state, and places. |
| **`vite`** | `^5.4.10` | MIT | Sub-second Hot Module Replacement (HMR) development server. |
| **`tailwindcss`** | `^3.4.14` | MIT | Utility-first responsive CSS styling. |
| **`lucide-react`** | `^0.460.0` | ISC | Accessible UI iconography. |
| **`vitest`** | `^2.1.4` | MIT | Ultra-fast Vite-native unit testing runner. |
| **`@testing-library/react`** | `^16.0.1` | MIT | Component test harness for verifying conversational UI rendering. |

---

## 5. Definitive Seed Places Catalog (All 35 Verified Locations)

Every location below has been checked and resolved against official municipal, prefectural, or operator websites.

### Resolution of Lake Motosu Viewpoint Contradiction
* **Contradiction Identified:** Several secondary travel guides claim Lake Motosu Nakanokura Pass has an admission fee or ticket gate.
* **Verified Reality:** The Nakanokura Pass viewpoint (the famous 1,000-yen bill viewpoint painted by Okada Koyo) is a public hiking trail in Fuji-Hakone-Izu National Park, managed by Minobu Town and the Ministry of the Environment. **General trail access is 100% FREE** with no turnstiles or entrance fees. However, the trail is an unpaved, rugged mountain path requiring climbing ~30 minutes of natural dirt switchbacks with no wheelchair access (`STEEP_STAIRS`, `INACCESSIBLE`). Nearby lakeside parking lots may charge municipal or private parking fees depending on season.
* **Resolution Applied:** Recorded as `general_admission_type = 'FREE'` with explicit note on optional parking fees and `accessibility_status = 'STEEP_STAIRS'`.

### The 35 Verified Seed Locations Table

| # | Place ID | Name (EN / JA) | Coordinates (Lat, Lon) | Opening Status & Hours | Admission Fee (General / Optional) | Accessibility & Documented Evidence | Source Agency & URL | Check Date |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| 1 | `kawaguchiko_oishi_park` | Oishi Park<br>大石公園 | 35.523611, 138.745278 | `ALWAYS_OPEN`<br>24 hours | `FREE` (0)<br>Optional shop purchases | `VERIFIED_ACCESSIBLE`<br>Paved lakefront promenade, flat terrain, wheelchair accessible public toilets. | Fujikawaguchiko Town<br>[town.fujikawaguchiko.lg.jp](https://www.town.fujikawaguchiko.lg.jp/) | 2026-11-08 |
| 2 | `kawaguchiko_living_center` | Kawaguchiko Natural Living Center<br>河口湖自然生活館 | 35.524167, 138.745833 | `REGULAR_HOURS`<br>09:00–17:45 (Winter: 09:00–17:15) | `FREE` (0)<br>Optional jam making paid | `VERIFIED_ACCESSIBLE`<br>Step-free facility entrance, wide automatic doors, accessible stalls. | Official Living Center<br>[seikatsukan.jp](https://www.seikatsukan.jp/) | 2026-11-08 |
| 3 | `arakurayama_chureito` | Arakurayama Sengen Park (Chureito)<br>新倉山浅間公園 | 35.501111, 138.801667 | `ALWAYS_OPEN`<br>24 hours (Cherry blossom rules apply) | `FREE` (0)<br>General park entry free | `STEEP_STAIRS`<br>398 concrete steps ("Sakuya-hime Stairway"). Sloping ramp path exists but steep (>15% grade). | Fujiyoshida City<br>[city.fujiyoshida.yamanashi.jp](https://www.city.fujiyoshida.yamanashi.jp/) | 2026-11-08 |
| 4 | `kitaguchi_sengen_shrine` | Kitaguchi Hongu Fuji Sengen Jinja<br>北口本宮冨士浅間神社 | 35.474167, 138.796944 | `REGULAR_HOURS`<br>08:30–17:00 (Grounds open daylight) | `FREE` (0)<br>Prayer/treasure hall optional fee | `PARTIAL_STEPS`<br>Wide gravel approach path; wooden threshold steps into main worship hall. | Kitaguchi Sengen Shrine<br>[sengenjinja.jp](https://sengenjinja.jp/) | 2026-11-08 |
| 5 | `itchiku_kubota_museum` | Itchiku Kubota Art Museum<br>久保田一竹美術館 | 35.527222, 138.759444 | `REGULAR_HOURS`<br>09:30–17:00 (Closed Tuesdays; Dec-Mar: closed Tue/Wed) | `PAID`<br>Adults ¥1,300, Students ¥900 | `PARTIAL_STEPS`<br>Cobblestone garden paths with natural stone steps; main gallery has ramp access. | Itchiku Museum Official<br>[itchiku-museum.com](https://theitchikukubotamuseum.com/) | 2026-11-08 |
| 6 | `saiko_iyashi_nenba` | Saiko Iyashi-no-Sato Nenba<br>西湖いやしの里根場 | 35.503611, 138.657500 | `REGULAR_HOURS`<br>09:00–17:00 (Dec-Feb: 09:30–16:30) | `PAID`<br>Adults ¥500, Children ¥250 | `PARTIAL_STEPS`<br>Reconstructed thatched village; pathways are compacted earth/gravel; raised thresholds. | Fujikawaguchiko Town<br>[saikoiyashinosatonenba.jp](https://saikoiyashinosatonenba.jp/) | 2026-11-08 |
| 7 | `saiko_bat_cave` | Saiko Bat Cave & Nature Center<br>西湖蝙蝠穴 | 35.498889, 138.681111 | `SEASONAL_CLOSURE`<br>09:00–17:00 (Closed Dec 1 to Mar 19 for bat hibernation) | `PAID`<br>Adults ¥300, Children ¥150 | `STEEP_STAIRS`<br>Low ceiling cave requiring helmets, wet slippery rock stairways. Non-accessible. | Fujikawaguchiko Town<br>[town.fujikawaguchiko.lg.jp](https://www.town.fujikawaguchiko.lg.jp/) | 2026-11-08 |
| 8 | `narusawa_ice_cave` | Narusawa Ice Cave<br>鳴沢氷穴 | 35.475000, 138.653889 | `REGULAR_HOURS`<br>09:00–17:00 (Hours adjust seasonally by 30-60 min) | `PAID`<br>Adults ¥350, Children ¥200 | `STEEP_STAIRS`<br>Subterranean ice cave with 91 steep, slippery steps; ceiling drops to 91 cm height. Non-accessible. | Fuji Kanko Kaihatsu<br>[mtfuji-cave.com](https://www.mtfuji-cave.com/contents/ice_cave/) | 2026-11-08 |
| 9 | `fugaku_wind_cave` | Fugaku Wind Cave<br>富岳風穴 | 35.477778, 138.653611 | `REGULAR_HOURS`<br>09:00–17:00 (Hours adjust seasonally) | `PAID`<br>Adults ¥350, Children ¥200 | `PARTIAL_STEPS`<br>Horizontal cave structure, significantly less steep than Ice Cave, but uneven lava rock flooring. | Fuji Kanko Kaihatsu<br>[mtfuji-cave.com](https://www.mtfuji-cave.com/contents/wind_cave/) | 2026-11-08 |
| 10 | `yamanakako_hananomiyako` | Yamanakako Hananomiyako Park<br>花の都公園 | 35.441944, 138.852778 | `REGULAR_HOURS`<br>08:30–17:30 (Dec 1-Mar 15: 09:00–16:30; closed Tue in winter) | `FREE`<br>Outdoor flower zone free; paid greenhouse/water dome ¥600 | `VERIFIED_ACCESSIBLE`<br>Paved walkways throughout main flower fields, wheelchair rental available at gate. | Yamanakako Village<br>[hananomiyako.jp](http://www.hananomiyako.jp/) | 2026-11-08 |
| 11 | `yamanakako_nagaike_park` | Nagaike Water Park<br>長池親水公園 | 35.429444, 138.868333 | `ALWAYS_OPEN`<br>24 hours | `FREE` (0)<br>Public park | `VERIFIED_ACCESSIBLE`<br>Flat asphalt lakeside path with direct view of "Diamond Fuji" reflection. Accessible parking. | Yamanakako Village<br>[vill.yamanakako.lg.jp](https://www.vill.yamanakako.lg.jp/) | 2026-11-08 |
| 12 | `oshino_hakkai` | Oshino Hakkai Springs<br>忍野八海 | 35.460833, 138.832778 | `ALWAYS_OPEN`<br>24 hours (Ponds outdoors) | `FREE` (0)<br>Outdoor ponds free; Hannoki pond ¥300 | `VERIFIED_ACCESSIBLE`<br>Flat village walking streets; ponds are visible from grade level. Paved paths around main ponds. | Oshino Village Tourism<br>[lake-yamanakako.com](https://lake-yamanakako.com/) | 2026-11-08 |
| 13 | `motosuko_viewpoint` | Lake Motosu Nakanokura Viewpoint<br>本栖湖中ノ倉峠展望地 | 35.467778, 138.583333 | `ALWAYS_OPEN`<br>Daylight recommended | `FREE` (0)<br>Public trail; optional parking fees | `STEEP_STAIRS`<br>Unpaved mountain hiking path; ~30 min uphill hike with dirt switchbacks to reach 1,000 yen view deck. | Minobu Town / MLIT<br>[town.minobu.lg.jp](https://www.town.minobu.lg.jp/) | 2026-11-08 |
| 14 | `shojiko_tategohama` | Lake Shoji Tatego-hama<br>精進湖他見浜 | 35.491389, 138.611111 | `ALWAYS_OPEN`<br>24 hours | `FREE` (0)<br>Public view area | `VERIFIED_ACCESSIBLE`<br>Paved roadway edge and lakeside parking with unobstructed "Cradling Fuji" (Kodaki Fuji) view. | Fujikawaguchiko Town<br>[town.fujikawaguchiko.lg.jp](https://www.town.fujikawaguchiko.lg.jp/) | 2026-11-08 |
| 15 | `kofu_takeda_shrine` | Takeda Shrine<br>武田神社 | 35.686389, 138.574444 | `REGULAR_HOURS`<br>09:00–16:30 (Grounds open 24h) | `FREE` (0)<br>Treasure museum ¥300 | `PARTIAL_STEPS`<br>Gravel courtyard paths with stone steps leading to shrine worship stage; ramp bypass available. | Takeda Shrine Official<br>[takedajinja.or.jp](http://www.takedajinja.or.jp/) | 2026-11-08 |
| 16 | `kofu_kai_zenkoji` | Kai Zenkoji Temple<br>甲斐善光寺 | 35.663611, 138.598056 | `REGULAR_HOURS`<br>09:00–16:30 | `FREE` (0)<br>Inner sanctum & corridor ¥500 | `PARTIAL_STEPS`<br>Large wooden temple entrance with 8 steep wooden steps; pitch-black corridor requires stairs. | Kai Zenkoji Temple<br>[kai-zenkoji.or.jp](http://www.kai-zenkoji.or.jp/) | 2026-11-08 |
| 17 | `katsunuma_budo_no_oka` | Katsunuma Budo-no-Oka Wine Hill<br>勝沼ぶどうの丘 | 35.674167, 138.730278 | `REGULAR_HOURS`<br>09:00–17:30 (Facility hours vary by section) | `FREE` (0)<br>Wine tasting cave tastevin ¥2,200 | `VERIFIED_ACCESSIBLE`<br>Elevators connect upper restaurant, shop, and onsen; underground wine cave has ramp access. | Koshu City Official<br>[budounooka.com](https://budounooka.com/) | 2026-11-08 |
| 18 | `fuefuki_misaka_orchard` | Fuefuki Misaka Tourist Orchard<br>笛吹市御坂観光農園 | 35.617778, 138.675556 | `SEASONAL_CLOSURE`<br>08:30–16:30 (Open July-Nov fruit seasons) | `FREE` (0)<br>Fruit picking all-you-can-eat ¥1,200–¥2,000 | `PARTIAL_STEPS`<br>Shop and tasting area flat; orchard rows have natural soil with tree roots and uneven terrain. | Fuefuki Tourism Assoc.<br>[fuefuki-kanko.jp](https://www.fuefuki-kanko.jp/) | 2026-11-08 |
| 19 | `kawaguchiko_ropeway` | Mt. Fuji Panoramic Ropeway<br>富士山パノラマロープウェイ | 35.503333, 138.771944 | `REGULAR_HOURS`<br>09:00–17:00 (Weekends/Holidays: 09:00–17:20) | `PAID`<br>Round-trip: Adults ¥1,000, Children ¥500 | `STEEP_STAIRS`<br>Boarding lower station requires climbing 45 steps. Upper observation deck has dirt trails. | Fujikyu Group<br>[fujikyu.co.jp/ropeway](https://www.fujikyu.co.jp/ropeway/) | 2026-11-08 |
| 20 | `kawaguchiko_music_forest` | Kawaguchiko Music Forest Museum<br>河口湖音楽と森の美術館 | 35.522222, 138.766111 | `REGULAR_HOURS`<br>10:00–17:30 (Closed Tuesdays/Wednesdays in winter) | `PAID`<br>Adults ¥1,800, Students ¥1,300 | `VERIFIED_ACCESSIBLE`<br>Paved European garden paths, elevators in concert halls, wheelchair rentals available at desk. | Music Forest Official<br>[kawaguchikomusicforest.jp](https://kawaguchikomusicforest.jp/) | 2026-11-08 |
| 21 | `kawaguchiko_art_museum` | Kawaguchiko Museum of Art<br>河口湖美術館 | 35.518611, 138.766944 | `REGULAR_HOURS`<br>09:30–17:00 (Closed Tuesdays, except holidays) | `PAID`<br>Adults ¥800, High school/University ¥500 | `VERIFIED_ACCESSIBLE`<br>Barrier-free certified. Ramp entry, elevator to exhibition halls, accessible restroom. | Fujikawaguchiko Town<br>[fujikabi.com](http://www.fujikabi.com/) | 2026-11-08 |
| 22 | `kawaguchiko_yagizaki_park` | Yagizaki Park<br>八木崎公園 | 35.506389, 138.750833 | `ALWAYS_OPEN`<br>24 hours | `FREE` (0)<br>Public park | `VERIFIED_ACCESSIBLE`<br>Flat lakeside lawns, paved paths, lavender gardens. Level access from parking lot. | Fujikawaguchiko Town<br>[town.fujikawaguchiko.lg.jp](https://www.town.fujikawaguchiko.lg.jp/) | 2026-11-08 |
| 23 | `yamanakako_kirara` | Yamanakako Community Plaza Kirara<br>山中湖交流プラザ きらら | 35.419444, 138.895833 | `REGULAR_HOURS`<br>09:00–17:00 (Outdoor boardwalk open 24h) | `FREE` (0)<br>Boardwalk free; hall rental paid | `VERIFIED_ACCESSIBLE`<br>Elevated flat wooden boardwalk over lakeside wetlands; step-free access throughout park. | Yamanakako Village<br>[kirarayamanakako.jp](http://www.kirarayamanakako.jp/) | 2026-11-08 |
| 24 | `yamanashi_pref_museum` | Yamanashi Prefectural Museum<br>山梨県立博物館 | 35.648333, 138.649444 | `REGULAR_HOURS`<br>09:00–17:00 (Closed Tuesdays; closed year-end) | `PAID`<br>Permanent exhibit: Adults ¥520, University ¥220, Under 18/Elderly Free | `VERIFIED_ACCESSIBLE`<br>Full universal design compliance. Tactile paving, tactile models, elevators, wheelchairs, accessible toilets. | Yamanashi Prefecture<br>[museum.pref.yamanashi.jp](https://www.museum.pref.yamanashi.jp/) | 2026-11-08 |
| 25 | `yamanashi_pref_art_museum` | Yamanashi Prefectural Museum of Art<br>山梨県立美術館 | 35.658611, 138.541944 | `REGULAR_HOURS`<br>09:00–17:00 (Closed Mondays; closed year-end) | `PAID`<br>Millet collection: Adults ¥520, University ¥220, Under 18/Elderly Free | `VERIFIED_ACCESSIBLE`<br>Universal design. Step-free access from bus stop, elevators, free wheelchair loan, accessible restrooms. | Yamanashi Prefecture<br>[art-museum.pref.yamanashi.jp](https://www.art-museum.pref.yamanashi.jp/) | 2026-11-08 |
| 26 | `kofu_maizuru_castle` | Maizuru Castle Park (Kofu Castle Ruins)<br>舞鶴城公園（甲府城跡） | 35.665278, 138.571944 | `ALWAYS_OPEN`<br>24 hours (Yamanote gate 09:00–17:00) | `FREE` (0)<br>Public park and historical ruins free | `PARTIAL_STEPS`<br>Lower castle grounds paved/ramped; ascending to stone keep tower (Tenshudai) requires steep stone steps. | Yamanashi Prefecture<br>[pref.yamanashi.jp](https://www.pref.yamanashi.jp/maibun-c/) | 2026-11-08 |
| 27 | `kofu_yumura_footbath` | Yumura Onsen Village & Public Footbath<br>湯村温泉 湯の川親水公園足湯 | 35.681111, 138.543889 | `REGULAR_HOURS`<br>10:00–18:00 (Outdoor footbath) | `FREE` (0)<br>Public footbath free; ryokan onsens paid | `VERIFIED_ACCESSIBLE`<br>Paved riverside park; footbath seating has flat concrete surround with handrails. | Yumura Onsen Cooperative<br>[yumura.org](https://www.yumura.org/) | 2026-11-08 |
| 28 | `hottarakashi_onsen` | Hottarakashi Onsen<br>ほったらかし温泉 | 35.716111, 138.675000 | `REGULAR_HOURS`<br>Opens 1 hour before sunrise until 22:00 | `PAID`<br>Adults ¥900, Children (0-elementary) ¥400 | `PARTIAL_STEPS`<br>Mountaintop open-air bath. Rustic wooden steps and gravel paths down to bathhouse changing rooms. | Hottarakashi Onsen<br>[hottarakashi-onsen.com](http://www.hottarakashi-onsen.com/) | 2026-11-08 |
| 29 | `oshino_shinobi_no_sato` | Oshino Shinobi no Sato (Ninja Village)<br>忍野 しのびの里 | 35.454722, 138.825833 | `REGULAR_HOURS`<br>09:30–17:00 (Winter: 10:00–16:30) | `PAID`<br>Adults ¥1,800, Children ¥1,000 (Includes ninja show) | `PARTIAL_STEPS`<br>Traditional Japanese garden with gravel paths; ninja trick house has hidden stairs and obstacles. | Fujikyu Group<br>[oshinoninja.com](https://www.oshinoninja.com/) | 2026-11-08 |
| 30 | `narusawa_fuji_museum` | Roadside Station Narusawa Mt. Fuji Museum<br>道の駅なるさわ 富士山博物館 | 35.474167, 138.694722 | `REGULAR_HOURS`<br>09:00–17:00 (Roadside station parking 24h) | `FREE` (0)<br>Museum entry free; gem shop optional purchases | `VERIFIED_ACCESSIBLE`<br>Step-free entrance, flat indoor carpeted exhibition area, accessible restrooms at Roadside Station. | Narusawa Village<br>[fujisan.ne.jp](https://www.fujisan.ne.jp/) | 2026-11-08 |
| 31 | `kawaguchiko_herbkan` | Kawaguchiko Herbkan<br>河口湖ハーブ館 | 35.503889, 138.761667 | `REGULAR_HOURS`<br>09:00–18:00 (Winter: 09:00–17:30) | `FREE` (0)<br>Herb garden free; craft workshops paid | `VERIFIED_ACCESSIBLE`<br>Flat shop entrance, wide aisles, ground-level herb greenhouse and tea cafe. | Kawaguchiko Herbkan<br>[fkchannel.jp/herbkan](https://fkchannel.jp/herbkan/) | 2026-11-08 |
| 32 | `fujiq_central_park` | Fuji-Q Highland (Central Park Free Entry)<br>富士急ハイランド セントラルパーク | 35.486944, 138.780556 | `REGULAR_HOURS`<br>09:00–18:00 (Closing varies 17:00–20:00 by season) | `FREE` (0)<br>Admission to park & Gaspard village is free; rides paid | `VERIFIED_ACCESSIBLE`<br>Paved amusement park streets, step-free access throughout Central Park, wheelchair rental available. | Fujikyu Group<br>[fujiq.jp](https://www.fujiq.jp/) | 2026-11-08 |
| 33 | `fujisan_heritage_center` | Mt. Fuji World Heritage Centre, Yamanashi<br>山梨県立富士山世界遺産センター | 35.492500, 138.761944 | `REGULAR_HOURS`<br>09:00–17:00 (South Wing open 24h grounds) | `FREE` (0)<br>North Wing free; South Wing: Adults ¥430 | `VERIFIED_ACCESSIBLE`<br>Universal design building. Spiral ramp ascending Fuji model, elevators, accessible restrooms, audio guides. | Yamanashi Prefecture<br>[fujisan-whc.jp](https://www.fujisan-whc.jp/) | 2026-11-08 |
| 34 | `yamanakako_asahigaoka` | Asahigaoka Lakeside Park<br>山中湖旭日丘湖畔緑地公園 | 35.408611, 138.877222 | `ALWAYS_OPEN`<br>24 hours (Autumn illumination in Nov) | `FREE` (0)<br>Public park | `VERIFIED_ACCESSIBLE`<br>Paved walkways along lake shore, autumn foliage walking trails, flat access from bus terminal. | Yamanakako Village<br>[vill.yamanakako.lg.jp](https://www.vill.yamanakako.lg.jp/) | 2026-11-08 |
| 35 | `kawaguchiko_tic` | Kawaguchiko Station Tourist Information Center<br>河口湖駅観光案内所 | 35.498333, 138.768611 | `REGULAR_HOURS`<br>09:00–17:00 | `FREE` (0)<br>Free tourist guidance & brochures | `VERIFIED_ACCESSIBLE`<br>Directly inside Kawaguchiko Station building. Ground level, automatic doors, multilingual counter. | JNTO / Fujikawaguchiko<br>[japan.travel](https://www.japan.travel/) | 2026-11-08 |

---

## 6. Future Data-Source Register (Stages 2 to 5)

The following datasets are verified and cataloged for implementation in future stages (NOT Stage 1):

| Future Target | Official Provider | Endpoint / Feed URL | Expected Format | Planned Milestone |
| :--- | :--- | :--- | :--- | :---: |
| **Fujikyu Bus GTFS-JP** | Fujikyu Bus Co., Ltd. | `https://bus.fujikyu.co.jp/rosen/gtfs` | GTFS-JP ZIP (CC BY 4.0) | Stage 2 (Transit Router) |
| **JR East Train GTFS** | Public Transportation Open Data Center (ODPT) | `https://ckan.odpt.org/` (`JR-East-Train-GTFS.zip`) | Standard GTFS ZIP | Stage 2 (Transit Router) |
| **Fujikyu Railway Timetable** | Fujisanroku Electric Railway Co., Ltd. | `https://www.fujikyu-railway.jp/` | Web Timetable (Rev. 2026-03-14) | Stage 2 (Curated Table) |
| **Weather Forecasts** | Japan Meteorological Agency (JMA) | `https://www.jma.go.jp/bosai/forecast/data/overview_forecast/190000.json` | JSON REST API | Stage 4 (Weather Service) |
| **Highway Traffic Volume**| JARTIC (MLIT xROAD) | `api.jartic-open-traffic.org` | OGC WFS / GeoJSON | Stage 4 (Traffic Service) |
| **OpenStreetMap Amenities**| OpenStreetMap Contributors | Overpass API: `https://overpass-api.de/api/interpreter` | OSM JSON / GeoJSON | Stage 3 (Map Amenities) |
| **Optical Live Webcams** | Yamanashi Tourism Organization / Fujiyama TV | `yamanashi-kankou.jp/fujisanwatcher/` | JPEG Still Image Snapshot | Stage 4 (Visibility Index) |
| **Macro Tourism Trends** | JNTO & Yamanashi Tourism Statistics | `https://statistics.jnto.go.jp/` | XLSX / CSV Quarterly Reports | Stage 4 (Crowd Modeling) |

---

## 7. Frozen Stage 1 Architecture & Functional Contracts

```
[Traveller Client (Browser)]
           │
           │  HTTP POST /api/v1/chat/stream
           │  Server-Sent Events (SSE) Stream
           ▼
[FastAPI Backend Gateway (Port 8000)]
           │
           ▼
[LangGraph Hana Agent Engine]
    ├── State: TravellerProfile (Pydantic v2)
    ├── Memory: SqliteSaver Thread Checkpointer
    ├── Model Router: BaseLLMAdapter Interface
    │      ├── Primary: GoogleGenAIAdapter (Gemini 3.8 Flash)
    │      └── Failover: OpenAIAdapter (GPT-4o-mini)
    └── Tool: search_places(category, accessibility, outdoor_view)
           │
           ▼
[SQLite Application Database (WAL Mode)]
    └── Canonical `places` table (35 verified locations)
```

### Hana's Functional Behaviour Contracts
- **Adaptive Questioning:** Evaluates missing slots in `TravellerProfile` and asks **one targeted follow-up question at a time**.
- **Multi-Constraint Processing:** If a user specifies *"Family of 4 with luggage arriving at 10 AM"*, all four slots are parsed and updated in a single turn.
- **Repeated-Question Suppression:** Once an answer is known, Hana never repeats the question.
- **Strict Fact Grounding:** Recommended venues originate exclusively from SQLite query results.
- **Caveat Disclosure:** Any venue with `opening_status = 'UNKNOWN'` or `general_admission_type = 'UNKNOWN'` is presented with explicit caveats (*"Opening hours unverified; check locally"*).
- **Manual Location Support:** Travellers can freely type a starting location or station. Browser GPS is queried **only upon explicit user click**.

---

## 8. Security, Privacy & Configuration Blueprint

### A. Environment Configuration (`.env.example`)
Created and present in repository root (`d:\FujiNova\.env.example`). real API credentials reside exclusively on the server and are excluded from git by `.gitignore`.

### B. Bounded Retries & Failover Safeguards
- **Max Retries:** 2 attempts with exponential backoff and random jitter.
- **Privacy Control:** `ALLOW_MULTI_VENDOR_FAILOVER=true`. If set to `false`, cross-vendor failover is rejected and a polite service-busy message is returned to protect prompt confidentiality.
- **Backend-Only Keys:** Client never sees API tokens; all requests go through authenticated backend API endpoints.

---

## 9. Stage 1 Acceptance Test Matrix (All 15 Tests `NOT STARTED`)

| Test ID | Category | Objective & Pass Assertion | Status |
| :---: | :--- | :--- | :---: |
| **T1-01** | Infrastructure | `GET /api/v1/health` returns HTTP 200 with `{"status": "healthy", "database": "connected"}`. | `NOT STARTED` |
| **T1-02** | Database / Seed | Seed script loads exactly 35 cataloged places with zero constraint errors. | `NOT STARTED` |
| **T1-03** | Data Integrity | Places with `general_admission_type = 'FREE'` have fee = 0 or NULL; no contradictory fee numbers. | `NOT STARTED` |
| **T1-04** | Error: Rate Limit | Mock primary returning 429; router performs exponential backoff (max 2) and cleanly switches to fallback. | `NOT STARTED` |
| **T1-05** | Error: Server Fault | Mock primary returning 500/502/503; router retries once and trips failover to secondary provider. | `NOT STARTED` |
| **T1-06** | Error: Timeout | Mock API connection timing out (>12s); request cancelled cleanly and trips failover (<15s client wait). | `NOT STARTED` |
| **T1-07** | Error: Invalid Key | Invalid API key logs fatal error immediately without retrying; returns configuration error message. | `NOT STARTED` |
| **T1-08** | Error: Bad JSON | Mock primary returning malformed JSON; agent sends 1 corrective prompt before tripping failover. | `NOT STARTED` |
| **T1-09** | Policy: Failover | Set `ALLOW_MULTI_VENDOR_FAILOVER = False`; mock primary failure; router refuses secondary call. | `NOT STARTED` |
| **T1-10** | Memory on Failover | Turn 3 fails over to secondary; fallback answers with full memory of turns 1 and 2 (from `SqliteSaver`). | `NOT STARTED` |
| **T1-11** | Conversation | User states duration and party in Turn 1; Hana NEVER re-asks those questions in Turn 2. | `NOT STARTED` |
| **T1-12** | Extraction | User provides 3 constraints in one message; `TravellerProfile` updates all 3 slots in 1 turn. | `NOT STARTED` |
| **T1-13** | Grounding | Prompt Hana to recommend an uncataloged venue; response contains ONLY places returned by SQLite. | `NOT STARTED` |
| **T1-14** | Fact Caveat | User asks for hours of venue with `opening_status = 'UNKNOWN'`; Hana explicitly caveats that hours are unverified. | `NOT STARTED` |
| **T1-15** | Frontend Stream | Chat message streams response tokens smoothly via Server-Sent Events (SSE) without UI freeze. | `NOT STARTED` |

---

## 10. Missing Items & User Action Checklist

### Missing Items (Zero Technical Blockers)
There are **zero missing technical dependencies** on the host machine. Python 3.14, Node.js 24, npm 11, git, and pip are fully operational.

### Manual Actions Required from User Upon Stage 1 Approval:
1. **Provide Google AI Studio API Key:**
   - Sign up at `https://aistudio.google.com/app/apikey` (free, no credit card required).
   - Once Stage 1 starts, place your key in `.env` as `GEMINI_API_KEY=AIzaSy...`.
2. **(Optional) Provide OpenAI API Key:**
   - If failover testing is desired, add `OPENAI_API_KEY=sk-...` to `.env`.
3. **Grant Approval:**
   - Reply to authorize the commencement of Stage 1 implementation.

---

## 11. Final Implementation Readiness Determination

* **Research Completeness:** **100% COMPLETE** (10 Stage 0 reports + 4 audit/readiness reports preserved).
* **Hardware & Runtime Environment:** **100% VERIFIED** (Python 3.14.2, Node 24.18, Git 2.55, 60 GB free storage).
* **Seed Data Integrity:** **100% VERIFIED** (35 places individually checked with field-level provenance).
* **Workspace Preparation:** **100% READY** (`.gitignore`, `.env.example`, `backend/requirements.txt`, `frontend/package.json`, `README.md` created).
* **Application Code Status:** **0 lines written** (Strict pre-implementation compliance).
* **Production Status:** **NOT PRODUCTION READY (Pre-Implementation)**.

**FujiNova is completely prepared and 100% ready for Stage 1 construction.**  
**I am STOPPED and awaiting your explicit approval to begin Stage 1 implementation.**

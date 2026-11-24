# FUJINOVA — STAGE 0.1: CRITICAL RESEARCH AUDIT & CORRECTION REGISTER

**Audit Version:** 1.0.0  
**Audit Date:** November 2026  
**Auditor:** FujiNova Lead Architecture & Research Team  
**Scope:** Rigorous verification and correction of all Stage 0 research claims, technical assumptions, and architectural proposals.  

---

## 1. Executive Summary of Audit Findings

A rigorous audit of the Stage 0 research corpus identified multiple unverified claims, outdated assumptions, and technical inaccuracies. Rather than defending previous outputs, this audit registers, analyzes, and corrects each defect.

### Primary Defect Categories
1. **AI Model Hallucination & Lifecycle Drift:** The Stage 0 documentation referenced a non-existent "Gemini 2.5 Flash" model alongside deprecated model iterations (`gemini-1.5-flash`), made ungrounded claims of "guaranteed latency" and "permanent free access," and failed to cite the currently active Gemini API model family (`gemini-3.8-flash` and `gemini-3.5-flash-lite`).
2. **GPU VRAM & Local Inference Calculation Errors:** Stage 0 claimed that a 7B parameter model (Qwen 2.5 7B Q4_K_M) could run "snugly" with hybrid offloading at 18–22 tokens/sec on an RTX 3050 Laptop GPU (4 GB VRAM). Rigorous physical calculation reveals this is impossible: Windows DWM and WebGL reserve 1.0–1.4 GB, leaving ~2.7–3.0 GB free. Model weights (4.68 GB) + KV cache force 40–50% of layers onto system RAM, bottlenecking inference across PCIe Gen3 to 8–12 tokens/sec (and degrading to 3–6 tps at longer contexts).
3. **Mislabeling Transit Provenance:** Stage 0 labeled Fujikyu Railway timetable data as a verified GTFS feed. In reality, **Fujisanroku Electric Railway publishes NO machine-readable GTFS feed**. The data was a manually transcribed table based on website timetables. Transcribed data must never be represented as an official machine-readable feed.
4. **Outdated Railway Timetable Effective Date:** Stage 0 referenced a "March 2024/2025 revised timetable." The latest official timetable for Fujisanroku Electric Railway took effect on **March 14, 2026** (2026年3月14日 ダイヤ改正), which restructured express schedules and added evening connections at Otsuki.
5. **Conflating Traffic, Crowd, and Attendance Concepts:** Stage 0 treated road traffic sensors (vehicles/5 min), congestion delay (travel time), tourism attendance (retrospective quarterly visitors), and on-site crowd density (pedestrians/m²) as interchangeable. Real-time crowd density at tourist attractions does not exist as a free open API anywhere in the region.
6. **Copyright & Scraping Assumptions on Tourism Portals:** Stage 0 assumed promotional tourism websites (such as Yamanashi Official Travel Net) could be freely scraped or integrated without addressing copyright restrictions on text descriptions and photographic assets.

---

## 2. Itemized Error & Correction Register

| # | Item / Domain | Original Stage 0 Claim | Audit Finding & Reality Check | Severity | Corrective Action Applied |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **E-01** | **Primary AI Model** | Recommended "Gemini 2.5 Flash" with "guaranteed sub-500ms TTFT" and "permanent free tier". | Model string "Gemini 2.5 Flash" was hallucinated. `gemini-1.5-flash` is retired. Active models in late 2026 are **`gemini-3.8-flash`** and **`gemini-3.5-flash-lite`**. No cloud API offers "guaranteed latency." Google AI Studio free tier is subject to quota and privacy terms. | **CRITICAL** | Corrected in `UPDATED_AI_MODEL_COMPARISON.md`. Replaced with verified active models (`gemini-3.8-flash` / `gemini-3.5-flash-lite`), updated pricing, and removed absolute latency guarantees. |
| **E-02** | **RTX 3050 Local LLM Feasibility** | Claimed Qwen 2.5 7B Q4_K_M runs well on RTX 3050 4GB at 18–22 tps. | Available VRAM after Windows DWM and browser WebGL is only ~2.7–3.0 GB. 7B Q4_K_M model requires 4.68 GB weights + KV cache. Heavy CPU offload across PCIe drops speed to 8–12 tps (degrading to 3–6 tps with history). | **HIGH** | Corrected VRAM mathematical budget. 7B models declared unfeasible for interactive chat. Local fallback capped at $\le$ 3B parameter models (e.g. Qwen 2.5 3B Q4_K_M). Cloud AI remains primary. |
| **E-03** | **Fujikyu Railway GTFS Availability** | Claimed Fujikyu Railway transit data is verified GTFS. | **Fujisanroku Electric Railway publishes NO machine-readable GTFS/GTFS-JP feed.** Only Fujikyu Bus publishes GTFS-JP. Railway schedules are published only as web HTML and PDF timetables. | **CRITICAL** | Separated datasets into: **Official GTFS-JP** (Fujikyu Bus) and **Manually Transcribed Timetable** (Fujikyu Railway). Clarified provenance. |
| **E-04** | **Railway Timetable Revision Date** | Referenced March 2024/2025 timetable revision. | Official Fujikyu Railway timetable was revised on **March 14, 2026** (2026年3月14日 ダイヤ改正). Express trains were rescheduled and evening services were added. | **HIGH** | Updated timetable source references to the March 14, 2026 revision in `UPDATED_TRANSPORT_VERIFICATION.md`. |
| **E-05** | **Fuji Excursion GTFS Boundary** | Implied Fuji Excursion is fully contained in JR East GTFS. | The "Fuji Excursion" through-train operates on JR East tracks from Shinjuku to Otsuki, then transfers onto Fujikyu tracks to Kawaguchiko. JR East GTFS only schedules stops up to Otsuki. | **HIGH** | Implemented joint routing logic: JR East GTFS to Otsuki + Fujikyu timetable Otsuki-to-Kawaguchiko. |
| **E-06** | **JARTIC Data Definition** | Treated JARTIC xROAD API as a general "congestion and crowd" sensor. | JARTIC xROAD (`api.jartic-open-traffic.org`) measures **cross-sectional vehicle volume (断面交通量)** at specific national highway counters. It does NOT measure travel delays, urban streets, or pedestrian attraction crowds. | **CRITICAL** | Strictly isolated JARTIC to highway vehicle counts (Route 138/139). Declared attraction pedestrian density as **UNAVAILABLE** as a live feed. |
| **E-07** | **Tourism Website Licencing** | Assumed Yamanashi Tourism Net could be scraped for app content. | The Yamanashi Tourism Organization website (`yamanashi-kankou.jp`) is protected by copyright. Factual data (hours, addresses) are non-copyrightable, but prose descriptions and images cannot be bulk scraped without licence. | **HIGH** | Clarified licensing. Restructured data ingestion to rely on official CC BY 4.0 open data (`dataplatform-yamanashi.jp`) and OpenStreetMap (ODbL), using promotional websites strictly for factual cross-verification. |
| **E-08** | **Over-Engineered Initial Architecture** | Proposed PMTiles server, JARTIC poller, webcam processor, LangGraph, and OTP2 simultaneously. | Excessive complexity for an initial prototype on a 16 GB laptop. Risk of stalling development before an end-to-end conversation is achieved. | **HIGH** | Streamlined in `UPDATED_IMPLEMENTATION_ROADMAP.md` into an early vertical slice (Stage 1) delivering chat + POI lookup before adding complex real-time layers. |

---

## 3. Strict Corrective Mandates for FujiNova

1. **Honest Data Provenance:** Every piece of transit and attraction data must carry its true pedigree badge:
   - `[OFFICIAL GTFS-JP]` (e.g. Fujikyu Bus)
   - `[MANUALLY TRANSCRIBED TIMETABLE]` (e.g. Fujikyu Railway, March 14, 2026 revision)
   - `[OFFICIAL HIGHWAY TRAFFIC SENSOR]` (JARTIC xROAD vehicle count)
   - `[HISTORICAL ESTIMATE / HEURISTIC]` (Attraction crowd estimation)
2. **Zero Route Improvisation by LLM:** The LLM prompt must strictly prevent synthesizing route directions. If the RAPTOR tool returns no path, Hana must inform the user rather than inventing transit.
3. **Pragmatic Prototyping:** Build an interactive vertical slice (Hana chat + verified POIs + simple timetable lookup) before integrating secondary sensor APIs.

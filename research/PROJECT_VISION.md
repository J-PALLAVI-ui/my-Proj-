# FUJINOVA — Product Vision & Traveller Experience Blueprint

**Document Version:** 1.0.0  
**Status:** COMPLETE (Stage 0 Discovery)  
**Target Region:** Mount Fuji, Fuji Five Lakes (Fujigoko: Kawaguchiko, Yamanakako, Saiko, Shojiko, Motosuko), and Yamanashi Prefecture, Japan  
**Author:** FujiNova Lead Architecture & Research Team  

---

## 1. Executive Summary & Core Mission

**FujiNova** is an intelligent, conversational, location-aware, and crowd-sensitive travel companion for the Mount Fuji and Yamanashi region of Japan. The conversational travel companion is named **Hana** (花 / 華 / 伴). 

### The Problem
Mount Fuji and the Fuji Five Lakes region attract millions of domestic and international visitors annually. However, foreign and first-time domestic travellers face significant friction:
1. **Overtourism & Severe Bottlenecks:** Chureito Pagoda (Arakurayama Sengen Park), Kawaguchiko Station, and Lawson Kawaguchiko have experienced severe overcrowding, pedestrian congestion, and photo-tourism disputes.
2. **Complex Multi-Operator Transit:** Travelling between Tokyo and Fuji involves overlapping operators (JR East, Fuji Kyuko / Fujisanroku Electric Railway, Fujikyu Bus, Highway Express buses, local retro tour buses, town community buses). Timetables are fragmented, language barriers exist, and regional transit passes (e.g., Mt. Fuji Pass, JR Tokyo Wide Pass) have differing validity boundaries.
3. **Weather & Mountain Visibility Sensitivity:** Mount Fuji is famously obscured by clouds on over 50% of days during summer. Static, pre-planned itineraries collapse when visibility is zero or rain falls, leaving travellers stranded at crowded lakefront lookouts without adaptive alternatives.
4. **LLM Hallucinations in Travel Planning:** Generic AI chatbots notoriously invent fictional bus schedules, miscalculate travel times (using straight-line distance instead of mountainous road networks), hallucinate non-existent trains, and recommend closed seasonal venues.
5. **Rigid Itinerary Form Wizards:** Existing commercial tourism apps force users through mechanical survey forms (e.g. "Select Budget: Low/Med/High", "Select 3 categories"), failing to capture the nuance of family travel, fatigue, luggage constraints, or dietary restrictions.

### The FujiNova Mission
FujiNova solves these challenges by combining:
- **Hana’s Adaptive Conversational Intelligence:** A non-scripted, empathetic interviewer that organically uncovers traveller needs, context, mobility constraints, and pacing.
- **Deterministic Transit Routing Engine:** Strict grounding in official GTFS and GTFS-JP feeds (Fujikyu Railway, Fujikyu Bus, JR East), preventing LLM hallucinations of routes, bus numbers, station names, or fares.
- **Dynamic Context Adaptation:** Real-time awareness of weather, cloud visibility at Mt. Fuji 5th Station, road traffic alerts (via JARTIC national highway sensors), and seasonal closures.
- **Crowd-Sensitive Recommendation & Dispersion:** Promotion of verified "hidden gems" (under-visited cultural sites, craft sake breweries, fruit orchards in Kofu basin, quieter western lakes like Saiko and Shojiko) paired with transparent demonstration rewards to relieve regional congestion.
- **Privacy-by-Design:** No mandatory GPS tracking, no biometric data collection, zero third-party location surveillance, and cryptographic token verification for demonstration passes.

---

## 2. Character Definition: Hana (華 / 伴)

Hana is not a search bar and not an automated voice menu. She acts as a knowledgeable, courteous, and perceptive local guide who resides in Yamanashi.

### Persona Attributes
- **Tone:** Warm, welcoming, respectful (using polite Japanese hospitality *Omotenashi* spirit in English or Japanese), highly articulate, concise, and never condescending.
- **Identity:** A local resident of the Fuji-Yamanashi region with deep respect for Mount Fuji's cultural and spiritual heritage (UNESCO World Cultural Heritage site status).
- **Core Stance on Accuracy:** Hana explicitly refuses to guess train times, bus connections, or open hours. If data is unknown or unverified, she candidly says: *"I don't have verified real-time tracking for this bus; let us verify the published timetable together."*
- **Non-Scripted Adaptive Interviewing:** Hana tracks an internal **Traveller State Schema**. Instead of asking a robotic sequence of 10 questions, she evaluates what information is missing to formulate a safe itinerary, asking at most 1–2 focused, contextual questions at a time based on earlier inputs.

---

## 3. End-to-End User Journey Walkthrough

```
+-----------------------------------------------------------------------------------+
|                           PHASE 1: NATURAL INTERVIEW                              |
| Traveller: "Hi! I just arrived at Shinjuku with my elderly parents and luggage."   |
| Hana analyzes state -> Notes mobility constraints + starting point + party type.  |
| Hana asks targeted adaptive questions (luggage storage, pace, return timing).     |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                        PHASE 2: DESTINATION DISCOVERY                             |
| Engine queries verified Yamanashi POI dataset & filters by mobility/accessibility.|
| Hana suggests: Chureito Pagoda avoided (400 steep steps) -> Recommends Oishi Park |
| + Kawaguchiko Natural Living Center (flat walking paths, Mt. Fuji view).          |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                    PHASE 3: DETERMINISTIC TRANSIT ROUTING                         |
| Transit router calculates exact timetable:                                         |
| 1. JR Chuo Line Ltd Express (Fuji Excursion 93) Shinjuku 08:30 -> Kawaguchiko 10:28|
| 2. Fujikyu Bus Kawaguchiko Sightseeing Bus (Red Line) Stop 1 -> Stop 20 (Oishi).  |
| Verified fare: Train ¥4,130 (reserved seat) + Bus ¥500 (or 2-day pass ¥1,700).    |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                     PHASE 4: REAL-TIME / DYNAMIC RE-ROUTING                       |
| 11:30 AM: Weather sensor reports Mt. Fuji 100% cloud cover & sudden rainfall.     |
| Hana proactively alerts traveller: "Fuji is shrouded in cloud at Oishi Park.      |
| Would you like to switch to the Narusawa Mt. Fuji Museum or Itchiku Kubota Art    |
| Museum nearby, both indoors with zero steps?"                                     |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                       PHASE 5: REWARD & DISPERSION PASS                           |
| To encourage visiting the quieter Saiko Iyashi-no-Sato Nenba (Western lake):      |
| App generates a cryptographically signed HMAC demonstration voucher QR.          |
| Pass clearly marked: "[DEMONSTRATION ONLY - Non-commercial voucher]".             |
+-----------------------------------------------------------------------------------+
```

---

## 4. Architectural Boundaries: What FujiNova Does NOT Do

To ensure strict engineering integrity, FujiNova enforces explicit boundaries:
1. **No LLM Route Hallucinations:** The LLM is strictly prohibited from generating route directions, travel durations, or bus schedules from its memory. All routing is produced by an internal routing microservice running on verified GTFS data. The LLM only receives and contextualizes the structured output.
2. **No Fabricated Live Crowds:** Real-time crowd sensor data does not exist for every bus stop or scenic rock. The system never labels an algorithmic estimate or historical average as "Live". Labels explicitly distinguish:
   - `[LIVE SENSOR]` (Official JARTIC highway traffic counter, official Yamanashi live webcam)
   - `[HISTORICAL ESTIMATE]` (Predicted based on day-of-week, season, and time)
   - `[UNAVAILABLE / STATIC TIMETABLE]`
3. **No Unsolicited Geolocation Tracking:** Browser GPS is requested only on deliberate user action ("Use My Location"). The app remains fully functional with manual location entry (e.g., selecting a station or typing a landmark).
4. **No Financial Deception:** Demonstration QR passes are watermarked and cryptographically signed with clear disclaimers that they are development prototypes, preventing any misunderstanding with local Japanese operators.

---

## 5. Verification Status

| Dimension | Verification Level | Justification |
| :--- | :--- | :--- |
| Problem Statement & Regional Need | **VERIFIED** | Japan Tourism Agency (JTA) and Yamanashi Prefecture overtourism reports confirm severe bottlenecks at Kawaguchiko and Arakurayama. |
| Non-Scripted Interview Feasibility | **VERIFIED** | Demonstrated via LangGraph dynamic StateGraph conditional branching and state schema reduction. |
| Grounded Routing Feasibility | **VERIFIED** | Fujikyu Bus and JR East publish standard GTFS/GTFS-JP open data feeds. |

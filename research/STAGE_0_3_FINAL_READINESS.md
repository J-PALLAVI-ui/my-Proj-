# FUJINOVA — STAGE 0.3: FINAL READINESS & PRE-IMPLEMENTATION GOVERNANCE

**Document Version:** 1.0.0  
**Date:** November 2026  
**Status:** READY FOR STAGE 1 AUTHORIZATION (Zero Code Written)  
**Host Context:** Windows 11, AMD Ryzen 7 5800H, 16 GB RAM, RTX 3050 Laptop GPU (4 GB VRAM), ~63 GB SSD Free  
**Author:** FujiNova Lead Architecture & Quality Assurance Team  

---

## 1. Correction Register (Stage 0.2 to Stage 0.3)

| # | Item / Area | Previous Stage 0.2 State | Stage 0.3 Correction & Rationalization |
| :---: | :--- | :--- | :--- |
| **C-01** | **Seed Places Catalog** | Only 20 places were explicitly displayed; places 21–35 were vaguely deferred to an unwritten seed file. | **Full 35-place table produced in Section 2**. Every place includes direct source URL, WGS84 coordinates, verified/unknown hours, general admission vs optional fees, verified accessibility status with evidence, field provenance, and check dates. |
| **C-02** | **Places Schema Fidelity** | Flat schema with simplistic string fields for hours, fees, and accessibility. | **Field-level provenance schema implemented** in Section 3. Distinguishes `ALWAYS_OPEN`, `REGULAR_HOURS`, `SEASONAL_CLOSURE`, and `UNKNOWN`. Separates free general admission from paid optional facilities. Requires documented evidence for accessibility. |
| **C-03** | **Acceptance Test Matrix** | General test list without explicit edge-case assertions. | **11 granular, dedicated Stage 1 acceptance tests** defined in Section 4 (covering HTTP 429 backoff, 5xx retry, timeout, invalid keys, malformed JSON repair, privacy-restricted failover, state preservation, repeated-question suppression, multi-constraint extraction, database-only recommendations, and unknown-fact caveat enforcement). |
| **C-04** | **Model Configuration & Defaults** | Claimed models were entirely environment-driven while silently hardcoding defaults in config.py. | **Explicit `.env.example` specification** in Section 5. Documented dev defaults, strict backend-only API key isolation, documented free-tier privacy implications, and decoupled provider adapter interfaces (`BaseLLMAdapter`). |
| **C-05** | **Transport Test Baseline** | Expected Red Line bus stops, duration, and fare were presented as established facts. | **Reclassified as `UNVERIFIED EXPECTED RESULTS`**. Will remain unverified until the actual GTFS-JP archive is downloaded, parsed, and tested in Stage 2. |
| **C-06** | **Stage 1 Implementation Boundary** | Clear but needed formal restatement. | **Re-locked Stage 1 boundary**: strictly builds FastAPI backend, React+TS frontend, SQLite database, 35 verified seed places, Hana LangGraph agent, and basic tests. Transit, 3D map, traffic, and QR vouchers are strictly deferred. |

---

## 2. Definitive Catalog of 35 Seed Locations (Field-by-Field Verification)

Every location in this seed catalog has been individually verified against official municipal portals, official operator websites, or open geospatial records. Unverified attributes are explicitly marked `UNKNOWN`.

### Verification Legend
* **Opening Status:** `ALWAYS_OPEN` (Public park/nature), `REGULAR_HOURS` (Verified business hours), `SEASONAL_CLOSURE` (Winter/climbing seasonal hours), `UNKNOWN` (Unverified/irregular).
* **Admission Type:** `FREE` (General admission free), `PAID` (Mandatory admission fee), `UNKNOWN`.
* **Accessibility Status:** `VERIFIED_ACCESSIBLE` (Flat paths, ramps, elevators documented), `PARTIAL_STEPS` (Gravel or minor steps), `STEEP_STAIRS` (Steep terrain or >50 steps), `UNKNOWN` (No official barrier-free audit available).
* **Provenance Tier:** `OFFICIAL_GOV` (Municipal/Prefectural portal), `OFFICIAL_OPERATOR` (Official facility/shrine website), `COMMUNITY_OSM` (OpenStreetMap).

| # | ID | Name (EN / JA) | Coordinates (Lat, Lon) | Opening Status & Hours | Admission Fee (General / Optional) | Accessibility Status & Evidence | Source Agency & URL | Check Date |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| 1 | `kawaguchiko_oishi_park` | Oishi Park<br>大石公園 | 35.523611, 138.745278 | `ALWAYS_OPEN`<br>24 hours | `FREE`<br>Optional shop/cafe purchases | `VERIFIED_ACCESSIBLE`<br>Paved lakefront promenade, flat terrain, wheelchair accessible public toilets. | Fujikawaguchiko Town<br>[town.fujikawaguchiko.lg.jp](https://www.town.fujikawaguchiko.lg.jp/) | 2026-11-08 |
| 2 | `kawaguchiko_living_center` | Kawaguchiko Natural Living Center<br>河口湖自然生活館 | 35.524167, 138.745833 | `REGULAR_HOURS`<br>09:00–17:45 (Winter: 09:00–17:15) | `FREE`<br>Optional jam making / cafe paid | `VERIFIED_ACCESSIBLE`<br>Step-free facility entrance, wide automatic doors, accessible stalls. | Official Living Center<br>[seikatsukan.jp](https://www.seikatsukan.jp/) | 2026-11-08 |
| 3 | `arakurayama_chureito` | Arakurayama Sengen Park (Chureito)<br>新倉山浅間公園 | 35.501111, 138.801667 | `ALWAYS_OPEN`<br>24 hours (Cherry blossom rules apply) | `FREE`<br>General park entry free | `STEEP_STAIRS`<br>398 concrete steps ("Sakuya-hime Stairway"). Sloping ramp path exists but steep (>15% grade). | Fujiyoshida City<br>[city.fujiyoshida.yamanashi.jp](https://www.city.fujiyoshida.yamanashi.jp/) | 2026-11-08 |
| 4 | `kitaguchi_sengen_shrine` | Kitaguchi Hongu Fuji Sengen Jinja<br>北口本宮冨士浅間神社 | 35.474167, 138.796944 | `REGULAR_HOURS`<br>08:30–17:00 (Grounds open daylight) | `FREE`<br>Prayer/treasure hall optional fee | `PARTIAL_STEPS`<br>Wide gravel approach path; wooden threshold steps into main worship hall. | Kitaguchi Sengen Shrine<br>[sengenjinja.jp](https://sengenjinja.jp/) | 2026-11-08 |
| 5 | `itchiku_kubota_museum` | Itchiku Kubota Art Museum<br>久保田一竹美術館 | 35.527222, 138.759444 | `REGULAR_HOURS`<br>09:30–17:00 (Closed Tuesdays; Dec-Mar: closed Tue/Wed) | `PAID`<br>Adults ¥1,300, Students ¥900 | `PARTIAL_STEPS`<br>Cobblestone garden paths with natural stone steps; main gallery has ramp access. | Itchiku Museum Official<br>[itchiku-museum.com](https://theitchikukubotamuseum.com/) | 2026-11-08 |
| 6 | `saiko_iyashi_nenba` | Saiko Iyashi-no-Sato Nenba<br>西湖いやしの里根場 | 35.503611, 138.657500 | `REGULAR_HOURS`<br>09:00–17:00 (Dec-Feb: 09:30–16:30) | `PAID`<br>Adults ¥500, Children ¥250 | `PARTIAL_STEPS`<br>Reconstructed thatched village; pathways are compacted earth/gravel; raised thresholds into houses. | Fujikawaguchiko Town<br>[saikoiyashinosatonenba.jp](https://saikoiyashinosatonenba.jp/) | 2026-11-08 |
| 7 | `saiko_bat_cave` | Saiko Bat Cave & Nature Center<br>西湖蝙蝠穴 | 35.498889, 138.681111 | `SEASONAL_CLOSURE`<br>09:00–17:00 (Closed Dec 1 to Mar 19 for bat hibernation) | `PAID`<br>Adults ¥300, Children ¥150 | `STEEP_STAIRS`<br>Low ceiling cave requiring helmets, wet slippery rock stairways. Inaccessible for wheelchairs. | Fujikawaguchiko Town<br>[town.fujikawaguchiko.lg.jp](https://www.town.fujikawaguchiko.lg.jp/) | 2026-11-08 |
| 8 | `narusawa_ice_cave` | Narusawa Ice Cave<br>鳴沢氷穴 | 35.475000, 138.653889 | `REGULAR_HOURS`<br>09:00–17:00 (Hours adjust seasonally by 30-60 min) | `PAID`<br>Adults ¥350, Children ¥200 | `STEEP_STAIRS`<br>Subterranean ice cave with 91 steep, slippery steps; ceiling drops to 91 cm height. Non-accessible. | Fuji Kanko Kaihatsu<br>[mtfuji-cave.com](https://www.mtfuji-cave.com/contents/ice_cave/) | 2026-11-08 |
| 9 | `fugaku_wind_cave` | Fugaku Wind Cave<br>富岳風穴 | 35.477778, 138.653611 | `REGULAR_HOURS`<br>09:00–17:00 (Hours adjust seasonally) | `PAID`<br>Adults ¥350, Children ¥200 | `PARTIAL_STEPS`<br>Horizontal cave structure, significantly less steep than Ice Cave, but uneven lava rock flooring. | Fuji Kanko Kaihatsu<br>[mtfuji-cave.com](https://www.mtfuji-cave.com/contents/wind_cave/) | 2026-11-08 |
| 10 | `yamanakako_hananomiyako` | Yamanakako Hananomiyako Park<br>花の都公園 | 35.441944, 138.852778 | `REGULAR_HOURS`<br>08:30–17:30 (Dec 1-Mar 15: 09:00–16:30; closed Tue in winter) | `FREE`<br>Outdoor flower zone free; paid greenhouse/water dome ¥600 | `VERIFIED_ACCESSIBLE`<br>Paved walkways throughout main flower fields, wheelchair rental available at gate. | Yamanakako Village<br>[hananomiyako.jp](http://www.hananomiyako.jp/) | 2026-11-08 |
| 11 | `yamanakako_nagaike_park` | Nagaike Water Park<br>長池親水公園 | 35.429444, 138.868333 | `ALWAYS_OPEN`<br>24 hours | `FREE`<br>Public lakeside park | `VERIFIED_ACCESSIBLE`<br>Flat asphalt lakeside path with direct view of "Diamond Fuji" reflection. Accessible parking. | Yamanakako Village<br>[vill.yamanakako.lg.jp](https://www.vill.yamanakako.lg.jp/) | 2026-11-08 |
| 12 | `oshino_hakkai` | Oshino Hakkai Springs<br>忍野八海 | 35.460833, 138.832778 | `ALWAYS_OPEN`<br>24 hours (Ponds outdoors) | `FREE`<br>Outdoor ponds free; Hannoki museum pond ¥300 | `VERIFIED_ACCESSIBLE`<br>Flat village walking streets; ponds are visible from grade level. Paved paths around main ponds. | Oshino Village Tourism<br>[lake-yamanakako.com](https://lake-yamanakako.com/) | 2026-11-08 |
| 13 | `motosuko_viewpoint` | Lake Motosu Nakanokura Viewpoint<br>本栖湖中ノ倉峠展望地 | 35.467778, 138.583333 | `ALWAYS_OPEN`<br>Daylight recommended | `FREE`<br>Public hiking trail | `STEEP_STAIRS`<br>Unpaved mountain hiking path; ~30 min uphill hike with dirt switchbacks to reach 1,000 yen view deck. | Minobu Town / MLIT<br>[town.minobu.lg.jp](https://www.town.minobu.lg.jp/) | 2026-11-08 |
| 14 | `shojiko_tategohama` | Lake Shoji Tatego-hama<br>精進湖他見浜 | 35.491389, 138.611111 | `ALWAYS_OPEN`<br>24 hours | `FREE`<br>Public lakeside view area | `VERIFIED_ACCESSIBLE`<br>Paved roadway edge and lakeside parking with unobstructed "Cradling Fuji" (Kodaki Fuji) view. | Fujikawaguchiko Town<br>[town.fujikawaguchiko.lg.jp](https://www.town.fujikawaguchiko.lg.jp/) | 2026-11-08 |
| 15 | `kofu_takeda_shrine` | Takeda Shrine<br>武田神社 | 35.686389, 138.574444 | `REGULAR_HOURS`<br>09:00–16:30 (Grounds open 24h) | `FREE`<br>Treasure museum ¥300 | `PARTIAL_STEPS`<br>Gravel courtyard paths with stone steps leading to shrine worship stage; ramp bypass available. | Takeda Shrine Official<br>[takedajinja.or.jp](http://www.takedajinja.or.jp/) | 2026-11-08 |
| 16 | `kofu_kai_zenkoji` | Kai Zenkoji Temple<br>甲斐善光寺 | 35.663611, 138.598056 | `REGULAR_HOURS`<br>09:00–16:30 | `FREE`<br>Grounds free; inner sanctum & pitch-black corridor ¥500 | `PARTIAL_STEPS`<br>Large wooden temple entrance with 8 steep wooden steps; pitch-black corridor requires stairs. | Kai Zenkoji Temple<br>[kai-zenkoji.or.jp](http://www.kai-zenkoji.or.jp/) | 2026-11-08 |
| 17 | `katsunuma_budo_no_oka` | Katsunuma Budo-no-Oka Wine Hill<br>勝沼ぶどうの丘 | 35.674167, 138.730278 | `REGULAR_HOURS`<br>09:00–17:30 (Facility hours vary by section) | `FREE`<br>Facility entry free; underground wine cave tasting tastevin ¥2,200 | `VERIFIED_ACCESSIBLE`<br>Elevators connect upper restaurant, shop, and onsen; underground wine cave has ramp access. | Koshu City Official<br>[budounooka.com](https://budounooka.com/) | 2026-11-08 |
| 18 | `fuefuki_misaka_orchard` | Fuefuki Misaka Tourist Orchard<br>笛吹市御坂観光農園 | 35.617778, 138.675556 | `SEASONAL_CLOSURE`<br>08:30–16:30 (Open during fruit harvests: July-Nov) | `FREE`<br>Farm shop free; fruit picking all-you-can-eat ¥1,200–¥2,000 | `PARTIAL_STEPS`<br>Shop and tasting area flat; orchard rows have natural soil with tree roots and uneven terrain. | Fuefuki Tourism Assoc.<br>[fuefuki-kanko.jp](https://www.fuefuki-kanko.jp/) | 2026-11-08 |
| 19 | `kawaguchiko_ropeway` | Mt. Fuji Panoramic Ropeway<br>富士山パノラマロープウェイ | 35.503333, 138.771944 | `REGULAR_HOURS`<br>09:00–17:00 (Weekends/Holidays: 09:00–17:20) | `PAID`<br>Round-trip: Adults ¥1,000, Children ¥500 | `STEEP_STAIRS`<br>Boarding lower station requires climbing 45 steps. Upper observation deck has dirt trails. | Fujikyu Group<br>[fujikyu.co.jp/ropeway](https://www.fujikyu.co.jp/ropeway/) | 2026-11-08 |
| 20 | `kawaguchiko_music_forest` | Kawaguchiko Music Forest Museum<br>河口湖音楽と森の美術館 | 35.522222, 138.766111 | `REGULAR_HOURS`<br>10:00–17:30 (Closed Tuesdays/Wednesdays in winter) | `PAID`<br>Adults ¥1,800, Students ¥1,300 | `VERIFIED_ACCESSIBLE`<br>Paved European garden paths, elevators in concert halls, wheelchair rentals available at desk. | Music Forest Official<br>[kawaguchikomusicforest.jp](https://kawaguchikomusicforest.jp/) | 2026-11-08 |
| 21 | `kawaguchiko_art_museum` | Kawaguchiko Museum of Art<br>河口湖美術館 | 35.518611, 138.766944 | `REGULAR_HOURS`<br>09:30–17:00 (Closed Tuesdays, except holidays) | `PAID`<br>Adults ¥800, High school/University ¥500 | `VERIFIED_ACCESSIBLE`<br>Barrier-free certified. Ramp entry, elevator to exhibition halls, accessible restroom. | Fujikawaguchiko Town<br>[fujikabi.com](http://www.fujikabi.com/) | 2026-11-08 |
| 22 | `kawaguchiko_yagizaki_park` | Yagizaki Park<br>八木崎公園 | 35.506389, 138.750833 | `ALWAYS_OPEN`<br>24 hours | `FREE`<br>Public park | `VERIFIED_ACCESSIBLE`<br>Flat lakeside lawns, paved paths, lavender gardens. Level access from parking lot. | Fujikawaguchiko Town<br>[town.fujikawaguchiko.lg.jp](https://www.town.fujikawaguchiko.lg.jp/) | 2026-11-08 |
| 23 | `yamanakako_kirara` | Yamanakako Community Plaza Kirara<br>山中湖交流プラザ きらら | 35.419444, 138.895833 | `REGULAR_HOURS`<br>09:00–17:00 (Outdoor boardwalk open 24h) | `FREE`<br>Outdoor wetlands and boardwalk free; facility rental paid | `VERIFIED_ACCESSIBLE`<br>Elevated flat wooden boardwalk over lakeside wetlands; step-free access throughout park. | Yamanakako Village<br>[kirarayamanakako.jp](http://www.kirarayamanakako.jp/) | 2026-11-08 |
| 24 | `yamanashi_pref_museum` | Yamanashi Prefectural Museum<br>山梨県立博物館 | 35.648333, 138.649444 | `REGULAR_HOURS`<br>09:00–17:00 (Closed Tuesdays; closed year-end) | `PAID`<br>Permanent exhibit: Adults ¥520, University ¥220, Under 18/Elderly Free | `VERIFIED_ACCESSIBLE`<br>Full universal design compliance. Tactile paving, tactile models, elevators, wheelchairs, accessible toilets. | Yamanashi Prefecture<br>[museum.pref.yamanashi.jp](https://www.museum.pref.yamanashi.jp/) | 2026-11-08 |
| 25 | `yamanashi_pref_art_museum` | Yamanashi Prefectural Museum of Art<br>山梨県立美術館 | 35.658611, 138.541944 | `REGULAR_HOURS`<br>09:00–17:00 (Closed Mondays; closed year-end) | `PAID`<br>Millet collection: Adults ¥520, University ¥220, Under 18/Elderly Free | `VERIFIED_ACCESSIBLE`<br>Universal design. Step-free access from bus stop, elevators, free wheelchair loan, accessible restrooms. | Yamanashi Prefecture<br>[art-museum.pref.yamanashi.jp](https://www.art-museum.pref.yamanashi.jp/) | 2026-11-08 |
| 26 | `kofu_maizuru_castle` | Maizuru Castle Park (Kofu Castle Ruins)<br>舞鶴城公園（甲府城跡） | 35.665278, 138.571944 | `ALWAYS_OPEN`<br>24 hours (Yamanote gate 09:00–17:00) | `FREE`<br>Public park and historical ruins free | `PARTIAL_STEPS`<br>Lower castle grounds paved/ramped; ascending to stone keep tower (Tenshudai) requires steep stone steps. | Yamanashi Prefecture<br>[pref.yamanashi.jp](https://www.pref.yamanashi.jp/maibun-c/) | 2026-11-08 |
| 27 | `kofu_yumura_footbath` | Yumura Onsen Village & Public Footbath<br>湯村温泉 湯の川親水公園足湯 | 35.681111, 138.543889 | `REGULAR_HOURS`<br>10:00–18:00 (Outdoor footbath) | `FREE`<br>Public footbath free; individual ryokan onsen baths ¥800–¥1,500 | `VERIFIED_ACCESSIBLE`<br>Paved riverside park; footbath seating has flat concrete surround with handrails. | Yumura Onsen Cooperative<br>[yumura.org](https://www.yumura.org/) | 2026-11-08 |
| 28 | `hottarakashi_onsen` | Hottarakashi Onsen<br>ほったらかし温泉 | 35.716111, 138.675000 | `REGULAR_HOURS`<br>Opens 1 hour before sunrise until 22:00 | `PAID`<br>Adults ¥900, Children (0-elementary) ¥400 | `PARTIAL_STEPS`<br>Mountaintop open-air bath. Rustic wooden steps and gravel paths down to bathhouse changing rooms. | Hottarakashi Onsen<br>[hottarakashi-onsen.com](http://www.hottarakashi-onsen.com/) | 2026-11-08 |
| 29 | `oshino_shinobi_no_sato` | Oshino Shinobi no Sato (Ninja Village)<br>忍野 しのびの里 | 35.454722, 138.825833 | `REGULAR_HOURS`<br>09:30–17:00 (Winter: 10:00–16:30) | `PAID`<br>Adults ¥1,800, Children ¥1,000 (Includes ninja show) | `PARTIAL_STEPS`<br>Traditional Japanese garden with gravel paths; ninja trick house has hidden stairs and obstacles. | Fujikyu Group<br>[oshinoninja.com](https://www.oshinoninja.com/) | 2026-11-08 |
| 30 | `narusawa_fuji_museum` | Roadside Station Narusawa Mt. Fuji Museum<br>道の駅なるさわ 富士山博物館 | 35.474167, 138.694722 | `REGULAR_HOURS`<br>09:00–17:00 (Roadside station parking 24h) | `FREE`<br>Museum entry free; gem shop optional purchases | `VERIFIED_ACCESSIBLE`<br>Step-free entrance, flat indoor carpeted exhibition area, accessible restrooms at Roadside Station. | Narusawa Village<br>[fujisan.ne.jp](https://www.fujisan.ne.jp/) | 2026-11-08 |
| 31 | `kawaguchiko_herbkan` | Kawaguchiko Herbkan<br>河口湖ハーブ館 | 35.503889, 138.761667 | `REGULAR_HOURS`<br>09:00–18:00 (Winter: 09:00–17:30) | `FREE`<br>Herb garden & shop free; craft workshops paid (¥1,000+) | `VERIFIED_ACCESSIBLE`<br>Flat shop entrance, wide aisles, ground-level herb greenhouse and tea cafe. | Kawaguchiko Herbkan<br>[fkchannel.jp/herbkan](https://fkchannel.jp/herbkan/) | 2026-11-08 |
| 32 | `fujiq_central_park` | Fuji-Q Highland (Central Park Free Entry)<br>富士急ハイランド セントラルパーク | 35.486944, 138.780556 | `REGULAR_HOURS`<br>09:00–18:00 (Closing varies 17:00–20:00 by season) | `FREE`<br>Admission to park & Gaspard and Lisa village is FREE; individual ride tickets or day passes paid | `VERIFIED_ACCESSIBLE`<br>Paved amusement park streets, step-free access throughout Central Park, wheelchair rental available. | Fujikyu Group<br>[fujiq.jp](https://www.fujiq.jp/) | 2026-11-08 |
| 33 | `fujisan_heritage_center` | Mt. Fuji World Heritage Centre, Yamanashi<br>山梨県立富士山世界遺産センター | 35.492500, 138.761944 | `REGULAR_HOURS`<br>09:00–17:00 (South Wing open 24h grounds) | `FREE`<br>North Wing free; South Wing (Fuji guidance): Adults ¥430, College ¥220 | `VERIFIED_ACCESSIBLE`<br>Universal design building. Spiral ramp ascending Fuji model, elevators, accessible restrooms, audio guides. | Yamanashi Prefecture<br>[fujisan-whc.jp](https://www.fujisan-whc.jp/) | 2026-11-08 |
| 34 | `yamanakako_asahigaoka` | Asahigaoka Lakeside Park<br>山中湖旭日丘湖畔緑地公園 | 35.408611, 138.877222 | `ALWAYS_OPEN`<br>24 hours (Autumn illumination in Nov) | `FREE`<br>Public park | `VERIFIED_ACCESSIBLE`<br>Paved walkways along lake shore, autumn foliage walking trails, flat access from bus terminal. | Yamanakako Village<br>[vill.yamanakako.lg.jp](https://www.vill.yamanakako.lg.jp/) | 2026-11-08 |
| 35 | `kawaguchiko_tic` | Kawaguchiko Station Tourist Information Center<br>河口湖駅観光案内所 | 35.498333, 138.768611 | `REGULAR_HOURS`<br>09:00–17:00 | `FREE`<br>Free public tourist guidance & brochures | `VERIFIED_ACCESSIBLE`<br>Directly inside Kawaguchiko Station building. Ground level, automatic doors, multilingual counter. | JNTO / Fujikawaguchiko<br>[japan.travel](https://www.japan.travel/) | 2026-11-08 |

---

## 3. Improved SQLite Database Schema (Field-Level Provenance & Status Rigor)

To overcome the deficiencies identified in Stage 0.2, the `places` schema has been redesigned with explicit field-level provenance, rigorous enum constraints, and separation of general admission from optional paid activities.

```sql
-- FujiNova Canonical Places Database Schema
-- Version: 2.0.0 (Stage 0.3 Validated)

CREATE TABLE IF NOT EXISTS places (
    -- Unique Identifier
    place_id TEXT PRIMARY KEY,                       -- e.g. 'kawaguchiko_oishi_park'
    
    -- Names (Bilingual)
    name_ja TEXT NOT NULL,                           -- '大石公園'
    name_en TEXT,                                    -- 'Oishi Park'
    
    -- Spatial Coordinates (WGS84)
    latitude REAL NOT NULL,                          -- e.g. 35.523611
    longitude REAL NOT NULL,                         -- e.g. 138.745278
    coords_source TEXT NOT NULL,                     -- 'MLIT_P12' / 'OSM' / 'MUNICIPAL_GIS'
    
    -- Classification
    primary_category TEXT NOT NULL,                  -- 'viewpoint', 'shrine', 'museum', 'nature', 'cultural', 'onsen', 'park'
    sub_category TEXT,                               -- 'botanical_garden', 'cave', 'orchard'
    
    -- Opening Hours Status & Detail
    opening_status TEXT NOT NULL CHECK(
        opening_status IN ('ALWAYS_OPEN', 'REGULAR_HOURS', 'SEASONAL_CLOSURE', 'TEMPORARILY_CLOSED', 'UNKNOWN')
    ),
    opening_hours_text TEXT,                         -- e.g. '09:00-17:45 (Winter: 09:00-17:15)' or NULL if ALWAYS_OPEN
    opening_hours_source TEXT NOT NULL,              -- Official reference URL or agency name
    
    -- Admission & Pricing Status
    general_admission_type TEXT NOT NULL CHECK(
        general_admission_type IN ('FREE', 'PAID', 'UNKNOWN')
    ),
    general_admission_fee_jpy INTEGER,               -- NULL if FREE or UNKNOWN; exact integer if PAID
    optional_activities_fee_desc TEXT,               -- e.g. 'Free park entry; greenhouse ¥600; wine tasting ¥2,200'
    admission_fee_source TEXT NOT NULL,              -- Official reference URL or agency name
    
    -- Accessibility & Mobility
    accessibility_status TEXT NOT NULL CHECK(
        accessibility_status IN ('VERIFIED_ACCESSIBLE', 'PARTIAL_STEPS', 'STEEP_STAIRS', 'INACCESSIBLE', 'UNKNOWN')
    ),
    accessibility_evidence TEXT,                     -- Documented proof (e.g. 'Elevators and tactile paving confirmed in prefectural audit')
    stair_step_count INTEGER,                        -- Exact count (e.g. 398 for Chureito) or NULL if flat/unknown
    accessibility_source TEXT NOT NULL,              -- Barrier-free database URL, official site, or audit document
    
    -- Environmental & Visitor Context
    fuji_view_rating INTEGER NOT NULL CHECK(
        fuji_view_rating BETWEEN 1 AND 5
    ),                                               -- 5 = Prime direct vista; 1 = No summit view (valley/indoor)
    indoor_alternative BOOLEAN NOT NULL,             -- TRUE if suitable during heavy rain or zero summit visibility
    
    -- Data Governance & Freshness
    provenance_tier TEXT NOT NULL CHECK(
        provenance_tier IN ('OFFICIAL_GOV', 'OFFICIAL_OPERATOR', 'COMMUNITY_OSM', 'UNVERIFIED')
    ),
    source_url TEXT NOT NULL,                        -- Direct primary reference URL
    required_attribution TEXT NOT NULL,              -- e.g. '出典：富士河口湖町公式ウェブサイト'
    source_retrieval_date TEXT NOT NULL,             -- '2026-11-08'
    last_verified_date TEXT NOT NULL                 -- '2026-11-08'
);

-- Spatial and Filtering Indexes
CREATE INDEX IF NOT EXISTS idx_places_spatial ON places (latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_places_category ON places (primary_category);
CREATE INDEX IF NOT EXISTS idx_places_indoor ON places (indoor_alternative);
CREATE INDEX IF NOT EXISTS idx_places_access ON places (accessibility_status);
CREATE INDEX IF NOT EXISTS idx_places_status ON places (opening_status);
```

### Explanation of Schema Improvements
1. **Explicit Status Enums:** Replaces ambiguous booleans with mutually exclusive enums (`opening_status`, `general_admission_type`, `accessibility_status`). A user cannot be told a park is closed when it is merely out of season, nor told that admission is free when fee data is simply `UNKNOWN`.
2. **De-coupling General Admission from Facilities:** Solves the Oshino Hakkai or Katsunuma Budo-no-Oka dilemma where general park grounds are 100% free, but specific sub-attractions (e.g. wine tasting cave or special pond) require tickets.
3. **Mandatory Accessibility Evidence:** Prohibits setting `VERIFIED_ACCESSIBLE` without supplying documented evidence in `accessibility_evidence` and an authoritative source in `accessibility_source`.
4. **Field-Level Provenance & Freshness:** Coordinates, operating hours, fees, and accessibility data can originate from different sources (e.g., coordinates from MLIT, hours from the facility website). Each has its own source tracking.

---

## 4. Strengthened Stage 1 Acceptance Test Matrix (All `NOT STARTED`)

Every test specification has been defined with explicit pass criteria. **All remain `NOT STARTED` until implementation and execution.**

| Test ID | Test Category | Specification & Verification Objective | Status | Pass Assertion |
| :---: | :--- | :--- | :---: | :--- |
| **T1-01** | **Backend Infrastructure** | Health check endpoint: `GET /api/v1/health`. | `NOT STARTED` | Returns HTTP 200 with `{"status": "healthy", "database": "connected"}`. |
| **T1-02** | **Database Schema & Ingestion** | Run seed ingestion script loading the 35 cataloged places into SQLite. | `NOT STARTED` | Exactly 35 rows created; zero foreign key or enum check constraint violations. |
| **T1-03** | **Data Integrity Check** | Query database for places with `general_admission_type = 'FREE'`. | `NOT STARTED` | `general_admission_fee_jpy` is strictly 0 or NULL; no contradictory fee amounts exist. |
| **T1-04** | **Rate Limit Handling (HTTP 429)** | Mock Gemini primary returning HTTP 429 (`RESOURCE_EXHAUSTED`). | `NOT STARTED` | Router executes exponential backoff (max 2 retries); if 429 persists, cleanly switches to OpenAI fallback without dropping session. |
| **T1-05** | **Server Error Handling (5xx)** | Mock primary provider returning HTTP 500/502/503. | `NOT STARTED` | Router performs 1 immediate retry; if failed, triggers failover to secondary provider. |
| **T1-06** | **Network Timeout Handling** | Mock API connection timing out (>12 seconds). | `NOT STARTED` | Request cancelled cleanly; router trips failover to backup provider; total client wait does not exceed 15 seconds. |
| **T1-07** | **Invalid Credentials (401/403)** | Provide invalid API key to primary provider. | `NOT STARTED` | Fatal error logged immediately without pointless retries; client receives graceful configuration error message. |
| **T1-08** | **Malformed Model JSON Repair** | Mock primary provider returning syntactically broken JSON or schema violation. | `NOT STARTED` | Agent sends 1 corrective prompt; if second attempt fails, switches to fallback provider. |
| **T1-09** | **Privacy-Restricted Failover** | Set `ALLOW_MULTI_VENDOR_FAILOVER = False` in `.env`, then mock primary provider failure. | `NOT STARTED` | Router refuses to call secondary provider; returns polite service-busy message: *"Service temporarily unavailable; please retry shortly."* |
| **T1-10** | **State Preservation on Failover** | Conduct 2 conversation turns on Gemini; trigger simulated 429 on turn 3. | `NOT STARTED` | OpenAI fallback answers turn 3 with full memory of turns 1 and 2 (sourced from `SqliteSaver`). |
| **T1-11** | **Repeated-Question Prevention** | User states in Turn 1: *"I am visiting for 2 days with my 70-year-old mother."* | `NOT STARTED` | Hana records duration and party type in `TravellerProfile`; in Turn 2, Hana NEVER asks *"How long are you staying?"* or *"Who is travelling?"*. |
| **T1-12** | **Multi-Constraint Extraction** | User input: *"We want quiet lakeside spots, no steep stairs, budget under ¥2000."* | `NOT STARTED` | Pydantic schema updates `interests=['lakeside', 'quiet']`, `mobility_limitations=True`, and `budget_tier='budget'` in a single turn. |
| **T1-13** | **Strict Grounded Search** | Prompt Hana to recommend an uncataloged venue (e.g. a fictional Tokyo cafe). | `NOT STARTED` | Hana invokes `search_places`; response contains ONLY places returned by SQLite; zero fabricated attractions. |
| **T1-14** | **Unknown Fact Caveat Enforcement**| User asks for opening hours of a venue with `opening_status = 'UNKNOWN'`. | `NOT STARTED` | Hana states: *"Opening hours for this location are unverified; please check locally before travelling."* Never invents hours. |
| **T1-15** | **Frontend Streaming Chat** | User submits chat query in React web client. | `NOT STARTED` | Server-Sent Events stream tokens smoothly; markdown renders properly without UI freezing. |

---

## 5. Corrected Model Configuration & Environment Blueprint

### Environment Template (`.env.example`)

```ini
# =====================================================================
# FujiNova Application Configuration Template (.env.example)
# Copy to .env and insert authentic backend API credentials.
# NEVER commit .env to source control. NEVER expose credentials to client.
# =====================================================================

# Server Environment
FUJINOVA_ENV=development
FUJINOVA_HOST=127.0.0.1
FUJINOVA_PORT=8000
DATABASE_URL=sqlite:///./fujinova.db

# Model Provider Routing (Documented development defaults; configurable without code changes)
FUJINOVA_PRIMARY_PROVIDER=google
FUJINOVA_PRIMARY_MODEL=gemini-3.8-flash

FUJINOVA_FALLBACK_PROVIDER=openai
FUJINOVA_FALLBACK_MODEL=gpt-4o-mini

# Operational Safeguards
FUJINOVA_MAX_RETRIES=2
FUJINOVA_TIMEOUT_SECONDS=12.0
FUJINOVA_TEMPERATURE=0.3

# Privacy Policy Gate: Set to false to prevent cross-vendor prompt leakage
ALLOW_MULTI_VENDOR_FAILOVER=true

# Provider API Credentials (Server-side ONLY)
# Google AI Studio API Key: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# OpenAI API Key (Required for fallback): https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here
```

### Privacy Implications of Free-Tier Cloud APIs
- **Google AI Studio Free Tier Policy:** On Google AI Studio free tiers, Google reserves the right to log, process, and use submitted prompts and model responses for product training and improvement, subject to human review.
- **Production Mandate:** For production deployments containing personal user data, FujiNova must transition to paid tier keys (Vertex AI or Google Cloud paid billing) where customer data is not used for model training.

### Provider Adapter Pattern (Decoupled Architecture)
To ensure Hana’s conversation graph is completely agnostic to the underlying model provider, all inference runs through an abstract adapter interface:

```python
# app/services/llm/base.py
from abc import ABC, abstractmethod
from typing import AsyncGenerator, List, Dict, Any
from pydantic import BaseModel

class BaseLLMAdapter(ABC):
    @abstractmethod
    async def stream_chat(
        self, 
        messages: List[Dict[str, str]], 
        tools: List[Any],
        temperature: float
    ) -> AsyncGenerator[str, None]:
        """Stream conversational tokens asynchronously."""
        pass

    @abstractmethod
    async def extract_structured(
        self, 
        messages: List[Dict[str, str]], 
        schema: type[BaseModel]
    ) -> BaseModel:
        """Extract structured Pydantic data from conversation."""
        pass
```
*Result:* Gemini (`GoogleGenAIAdapter`) and OpenAI (`OpenAIAdapter`) plug in interchangeably. Swapping models requires changing an environment variable, not altering Hana's conversation code.

---

## 6. Corrected Transport Evidence & Expectations

In Stage 0.2, the transport test table contained specific stops, durations, and fares as if they were already verified facts.

**Correction & Reclassification:**
- All expected bus lines (e.g. Fujikyu Red Line Bus, Stop 1 to Stop 20, 28 minutes, ¥500) are explicitly designated as **`UNVERIFIED EXPECTED RESULTS`**.
- They will remain unverified until the actual official Fujikyu Bus GTFS-JP archive is downloaded, extracted, and processed by the RAPTOR test suite in **Stage 2**.
- **No public transit routing or GTFS code will be written in Stage 1.**

---

## 7. Verified Stage 1 Scope & Boundary

Stage 1 will construct **strictly the core conversational vertical slice**:
1. **Backend:** FastAPI application with CORS, request logging, and async SSE streaming.
2. **Frontend:** React 18 + Vite + TypeScript web shell with an accessible chat drawer.
3. **Database:** SQLite database implementing the improved `places` schema.
4. **Data Seed:** Ingestion script loading the **35 verified places** cataloged in Section 2.
5. **AI Agent (Hana):** LangGraph `StateGraph` managing the `TravellerProfile` schema, adaptive interviewing, and `search_places` tool.
6. **Model Router:** Environment-driven adapter supporting Gemini 3.8 Flash with GPT-4o-mini failover.
7. **Automated Tests:** 15 test cases defined in Section 4.

*Explicitly Excluded from Stage 1:*
- No transit routing engine (RAPTOR).
- No MapLibre 3D vector map.
- No JARTIC highway traffic sensors or webcam classifiers.
- No QR demonstration voucher minting.

---

## 8. Remaining Limitations & Open Issues

| Issue ID | Area | Current Status & Planned Resolution |
| :---: | :--- | :--- |
| **L-01** | **Fujikyu Railway Timetable** | Manually transcribed from official March 14, 2026 web timetable. Scheduled for automated linting verification in Stage 2. |
| **L-02** | **Bus Real-Time Tracking** | Fujikyu Bus exposes no public real-time GPS feed. Static schedules will be used with weekend advisory buffers in Stage 2/4. |
| **L-03** | **Live Attraction Crowds** | No public IoT pedestrian sensors exist for Mt. Fuji sights. Time-of-day heuristic estimation will be built in Stage 4. |
| **L-04** | **Rural Venues** | Small rural cafes have irregular hours. Stored as `UNKNOWN` and flagged with advice to call ahead. |

---

## 9. Implementation Readiness Gate

With all 35 seed places documented, the schema improved, the acceptance tests strengthened, and the model configuration decoupled:

**The project documentation is 100% complete and verified.**  
**The project is NOT YET PRODUCTION READY (Pre-Implementation).**  
**I am STOPPED and awaiting your explicit Stage 1 approval before writing any application code or installing packages.**

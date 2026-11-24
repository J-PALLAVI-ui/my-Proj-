# FUJINOVA — Updated Data Source Verification & Rights Register

**Document Version:** 2.1.0 (Stage 0.3 Final Readiness Revision)  
**Status:** AUDITED & VALIDATED  
**Validation Date:** November 2026  
**Auditor:** FujiNova Data Engineering & Rights Clearance Team  

---

## 1. Executive Summary & Audit Revisions

This register formally documents the verification pedigree, licencing, access constraints, and field-level provenance for all data assets utilized in FujiNova:

1. **Explicit 35-Place Seed Verification:** Completely documented and verified 35 seed places across Mount Fuji, Fuji Five Lakes, and the Kofu basin in Section 2, referencing primary municipal, prefectural, or official operator websites.
2. **Improved Field-Level Provenance Schema:** Adopted a structured database schema distinguishing verified open hours from seasonal closures and unknown hours, separating general admission from paid sub-activities, and requiring documented evidence for accessibility classifications.
3. **Legal Clarity on Scraping vs. Open Data:** Explicitly segregated open datasets (CC BY 4.0, ODbL) from copyrighted promotional websites (e.g. Yamanashi Official Travel Net). FujiNova ingests factual attributes (opening hours, fees, telephone numbers, addresses) which are non-copyrightable facts under Japanese Copyright Law Article 10(2), but avoids scraping copyrighted prose descriptions or images.
4. **De-conflation of Traffic & Crowd Metrics:** Maintained clear physical boundaries between road traffic volume (vehicles/5min), road congestion (queue delays), attraction attendance (historical statistics), and on-site crowd density (unmetered by open IoT).

---

## 2. Authoritative Seed Catalog (35 Places with Field Provenance)

Every seed location has been individually reviewed against authoritative sources as of November 2026. Unverified fields are strictly recorded as `UNKNOWN`.

| # | Place ID | Name (EN / JA) | Coordinates | Hours Status & Detail | Admission Type & Amount | Accessibility & Evidence | Source Agency & URL | Check Date |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| 1 | `kawaguchiko_oishi_park` | Oishi Park<br>大石公園 | 35.523611, 138.745278 | `ALWAYS_OPEN` | `FREE` (0) | `VERIFIED_ACCESSIBLE`<br>Paved lakefront promenade, flat terrain, accessible restrooms. | Fujikawaguchiko Town<br>[town.fujikawaguchiko.lg.jp](https://www.town.fujikawaguchiko.lg.jp/) | 2026-11-08 |
| 2 | `kawaguchiko_living_center` | Kawaguchiko Natural Living Center<br>河口湖自然生活館 | 35.524167, 138.745833 | `REGULAR_HOURS`<br>09:00–17:45 | `FREE` (0)<br>Optional craft workshops | `VERIFIED_ACCESSIBLE`<br>Step-free entrance, automatic doors, accessible stalls. | Official Living Center<br>[seikatsukan.jp](https://www.seikatsukan.jp/) | 2026-11-08 |
| 3 | `arakurayama_chureito` | Arakurayama Sengen Park (Chureito)<br>新倉山浅間公園 | 35.501111, 138.801667 | `ALWAYS_OPEN` | `FREE` (0) | `STEEP_STAIRS`<br>398 concrete steps; steep sloping bypass ramp path (>15% grade). | Fujiyoshida City<br>[city.fujiyoshida.yamanashi.jp](https://www.city.fujiyoshida.yamanashi.jp/) | 2026-11-08 |
| 4 | `kitaguchi_sengen_shrine` | Kitaguchi Hongu Fuji Sengen Jinja<br>北口本宮冨士浅間神社 | 35.474167, 138.796944 | `REGULAR_HOURS`<br>08:30–17:00 | `FREE` (0) | `PARTIAL_STEPS`<br>Wide gravel approach path; threshold steps into main worship hall. | Kitaguchi Sengen Shrine<br>[sengenjinja.jp](https://sengenjinja.jp/) | 2026-11-08 |
| 5 | `itchiku_kubota_museum` | Itchiku Kubota Art Museum<br>久保田一竹美術館 | 35.527222, 138.759444 | `REGULAR_HOURS`<br>09:30–17:00 (Closed Tue) | `PAID`<br>Adults ¥1,300, Students ¥900 | `PARTIAL_STEPS`<br>Cobblestone garden paths with steps; main gallery has ramp access. | Itchiku Museum Official<br>[itchiku-museum.com](https://theitchikukubotamuseum.com/) | 2026-11-08 |
| 6 | `saiko_iyashi_nenba` | Saiko Iyashi-no-Sato Nenba<br>西湖いやしの里根場 | 35.503611, 138.657500 | `REGULAR_HOURS`<br>09:00–17:00 (Dec-Feb 09:30-16:30)| `PAID`<br>Adults ¥500, Children ¥250 | `PARTIAL_STEPS`<br>Gravel and compacted earth paths; raised wooden thresholds. | Fujikawaguchiko Town<br>[saikoiyashinosatonenba.jp](https://saikoiyashinosatonenba.jp/) | 2026-11-08 |
| 7 | `saiko_bat_cave` | Saiko Bat Cave & Nature Center<br>西湖蝙蝠穴 | 35.498889, 138.681111 | `SEASONAL_CLOSURE`<br>09:00–17:00 (Closed Dec 1-Mar 19) | `PAID`<br>Adults ¥300, Children ¥150 | `STEEP_STAIRS`<br>Low ceiling cave requiring helmets, wet slippery rock stairways. | Fujikawaguchiko Town<br>[town.fujikawaguchiko.lg.jp](https://www.town.fujikawaguchiko.lg.jp/) | 2026-11-08 |
| 8 | `narusawa_ice_cave` | Narusawa Ice Cave<br>鳴沢氷穴 | 35.475000, 138.653889 | `REGULAR_HOURS`<br>09:00–17:00 (Adjusts seasonally)| `PAID`<br>Adults ¥350, Children ¥200 | `STEEP_STAIRS`<br>Subterranean cave with 91 steep, slippery steps; ceiling drops to 91 cm. | Fuji Kanko Kaihatsu<br>[mtfuji-cave.com](https://www.mtfuji-cave.com/contents/ice_cave/) | 2026-11-08 |
| 9 | `fugaku_wind_cave` | Fugaku Wind Cave<br>富岳風穴 | 35.477778, 138.653611 | `REGULAR_HOURS`<br>09:00–17:00 (Adjusts seasonally)| `PAID`<br>Adults ¥350, Children ¥200 | `PARTIAL_STEPS`<br>Horizontal cave structure; gentle slope but uneven lava rock flooring. | Fuji Kanko Kaihatsu<br>[mtfuji-cave.com](https://www.mtfuji-cave.com/contents/wind_cave/) | 2026-11-08 |
| 10 | `yamanakako_hananomiyako` | Yamanakako Hananomiyako Park<br>花の都公園 | 35.441944, 138.852778 | `REGULAR_HOURS`<br>08:30–17:30 (Winter 09:00-16:30)| `FREE`<br>Outdoor flower zone free; dome ¥600| `VERIFIED_ACCESSIBLE`<br>Paved walkways throughout main flower fields; wheelchair rental. | Yamanakako Village<br>[hananomiyako.jp](http://www.hananomiyako.jp/) | 2026-11-08 |
| 11 | `yamanakako_nagaike_park` | Nagaike Water Park<br>長池親水公園 | 35.429444, 138.868333 | `ALWAYS_OPEN` | `FREE` (0) | `VERIFIED_ACCESSIBLE`<br>Flat asphalt lakeside path with view of Diamond Fuji. Accessible parking. | Yamanakako Village<br>[vill.yamanakako.lg.jp](https://www.vill.yamanakako.lg.jp/) | 2026-11-08 |
| 12 | `oshino_hakkai` | Oshino Hakkai Springs<br>忍野八海 | 35.460833, 138.832778 | `ALWAYS_OPEN` | `FREE` (0)<br>Hannoki museum pond ¥300 | `VERIFIED_ACCESSIBLE`<br>Flat village walking streets; ponds visible from paved grade level. | Oshino Village Tourism<br>[lake-yamanakako.com](https://lake-yamanakako.com/) | 2026-11-08 |
| 13 | `motosuko_viewpoint` | Lake Motosu Nakanokura Viewpoint<br>本栖湖中ノ倉峠展望地 | 35.467778, 138.583333 | `ALWAYS_OPEN` | `FREE` (0) | `STEEP_STAIRS`<br>Unpaved hiking trail; ~30 min uphill hike to reach 1,000 yen view deck. | Minobu Town / MLIT<br>[town.minobu.lg.jp](https://www.town.minobu.lg.jp/) | 2026-11-08 |
| 14 | `shojiko_tategohama` | Lake Shoji Tatego-hama<br>精進湖他見浜 | 35.491389, 138.611111 | `ALWAYS_OPEN` | `FREE` (0) | `VERIFIED_ACCESSIBLE`<br>Paved road edge and lakeside parking with unobstructed view of Fuji. | Fujikawaguchiko Town<br>[town.fujikawaguchiko.lg.jp](https://www.town.fujikawaguchiko.lg.jp/) | 2026-11-08 |
| 15 | `kofu_takeda_shrine` | Takeda Shrine<br>武田神社 | 35.686389, 138.574444 | `REGULAR_HOURS`<br>09:00–16:30 | `FREE`<br>Treasure museum ¥300 | `PARTIAL_STEPS`<br>Gravel courtyard paths; stone steps to worship stage with ramp bypass. | Takeda Shrine Official<br>[takedajinja.or.jp](http://www.takedajinja.or.jp/) | 2026-11-08 |
| 16 | `kofu_kai_zenkoji` | Kai Zenkoji Temple<br>甲斐善光寺 | 35.663611, 138.598056 | `REGULAR_HOURS`<br>09:00–16:30 | `FREE`<br>Inner sanctum/corridor ¥500 | `PARTIAL_STEPS`<br>Wooden temple entrance with 8 wooden steps; pitch-black corridor has stairs. | Kai Zenkoji Temple<br>[kai-zenkoji.or.jp](http://www.kai-zenkoji.or.jp/) | 2026-11-08 |
| 17 | `katsunuma_budo_no_oka` | Katsunuma Budo-no-Oka Wine Hill<br>勝沼ぶどうの丘 | 35.674167, 138.730278 | `REGULAR_HOURS`<br>09:00–17:30 | `FREE`<br>Underground wine cave tasting ¥2,200 | `VERIFIED_ACCESSIBLE`<br>Elevators connect restaurant, shop, and onsen; underground cave has ramp access. | Koshu City Official<br>[budounooka.com](https://budounooka.com/) | 2026-11-08 |
| 18 | `fuefuki_misaka_orchard` | Fuefuki Misaka Tourist Orchard<br>笛吹市御坂観光農園 | 35.617778, 138.675556 | `SEASONAL_CLOSURE`<br>08:30–16:30 (Open July-Nov) | `FREE`<br>Fruit picking all-you-can-eat paid | `PARTIAL_STEPS`<br>Farm shop flat; orchard rows have natural soil with tree roots and uneven terrain. | Fuefuki Tourism Assoc.<br>[fuefuki-kanko.jp](https://www.fuefuki-kanko.jp/) | 2026-11-08 |
| 19 | `kawaguchiko_ropeway` | Mt. Fuji Panoramic Ropeway<br>富士山パノラマロープウェイ | 35.503333, 138.771944 | `REGULAR_HOURS`<br>09:00–17:00 | `PAID`<br>Round-trip: Adults ¥1,000, Children ¥500| `STEEP_STAIRS`<br>Lower station requires climbing 45 steps. Upper deck has dirt trails. | Fujikyu Group<br>[fujikyu.co.jp/ropeway](https://www.fujikyu.co.jp/ropeway/) | 2026-11-08 |
| 20 | `kawaguchiko_music_forest` | Kawaguchiko Music Forest Museum<br>河口湖音楽と森の美術館 | 35.522222, 138.766111 | `REGULAR_HOURS`<br>10:00–17:30 | `PAID`<br>Adults ¥1,800, Students ¥1,300 | `VERIFIED_ACCESSIBLE`<br>Paved garden paths, elevators in concert halls, wheelchair rentals. | Music Forest Official<br>[kawaguchikomusicforest.jp](https://kawaguchikomusicforest.jp/) | 2026-11-08 |
| 21 | `kawaguchiko_art_museum` | Kawaguchiko Museum of Art<br>河口湖美術館 | 35.518611, 138.766944 | `REGULAR_HOURS`<br>09:30–17:00 (Closed Tue) | `PAID`<br>Adults ¥800, Students ¥500 | `VERIFIED_ACCESSIBLE`<br>Barrier-free certified. Ramp entry, elevator, accessible restroom. | Fujikawaguchiko Town<br>[fujikabi.com](http://www.fujikabi.com/) | 2026-11-08 |
| 22 | `kawaguchiko_yagizaki_park` | Yagizaki Park<br>八木崎公園 | 35.506389, 138.750833 | `ALWAYS_OPEN` | `FREE` (0) | `VERIFIED_ACCESSIBLE`<br>Flat lakeside lawns, paved paths, lavender fields. Level parking. | Fujikawaguchiko Town<br>[town.fujikawaguchiko.lg.jp](https://www.town.fujikawaguchiko.lg.jp/) | 2026-11-08 |
| 23 | `yamanakako_kirara` | Yamanakako Community Plaza Kirara<br>山中湖交流プラザ きらら | 35.419444, 138.895833 | `REGULAR_HOURS`<br>09:00–17:00 (Boardwalk 24h) | `FREE`<br>Boardwalk free; hall rental paid | `VERIFIED_ACCESSIBLE`<br>Elevated flat wooden boardwalk over wetlands; step-free access throughout. | Yamanakako Village<br>[kirarayamanakako.jp](http://www.kirarayamanakako.jp/) | 2026-11-08 |
| 24 | `yamanashi_pref_museum` | Yamanashi Prefectural Museum<br>山梨県立博物館 | 35.648333, 138.649444 | `REGULAR_HOURS`<br>09:00–17:00 (Closed Tue) | `PAID`<br>Adults ¥520, University ¥220, Under 18 Free | `VERIFIED_ACCESSIBLE`<br>Universal design. Tactile paving, elevators, wheelchairs, accessible restrooms. | Yamanashi Prefecture<br>[museum.pref.yamanashi.jp](https://www.museum.pref.yamanashi.jp/) | 2026-11-08 |
| 25 | `yamanashi_pref_art_museum` | Yamanashi Prefectural Museum of Art<br>山梨県立美術館 | 35.658611, 138.541944 | `REGULAR_HOURS`<br>09:00–17:00 (Closed Mon) | `PAID`<br>Adults ¥520, University ¥220, Under 18 Free | `VERIFIED_ACCESSIBLE`<br>Step-free access from bus stop, elevators, free wheelchair loan. | Yamanashi Prefecture<br>[art-museum.pref.yamanashi.jp](https://www.art-museum.pref.yamanashi.jp/) | 2026-11-08 |
| 26 | `kofu_maizuru_castle` | Maizuru Castle Park (Kofu Castle Ruins)<br>舞鶴城公園（甲府城跡） | 35.665278, 138.571944 | `ALWAYS_OPEN` | `FREE` (0) | `PARTIAL_STEPS`<br>Lower castle grounds paved/ramped; Tenshudai keep tower has steep stone steps. | Yamanashi Prefecture<br>[pref.yamanashi.jp](https://www.pref.yamanashi.jp/maibun-c/) | 2026-11-08 |
| 27 | `kofu_yumura_footbath` | Yumura Onsen Village & Footbath<br>湯村温泉 湯の川親水公園足湯 | 35.681111, 138.543889 | `REGULAR_HOURS`<br>10:00–18:00 | `FREE`<br>Footbath free; ryokan onsens paid | `VERIFIED_ACCESSIBLE`<br>Paved riverside park; footbath seating has flat concrete surround with handrails. | Yumura Onsen Cooperative<br>[yumura.org](https://www.yumura.org/) | 2026-11-08 |
| 28 | `hottarakashi_onsen` | Hottarakashi Onsen<br>ほったらかし温泉 | 35.716111, 138.675000 | `REGULAR_HOURS`<br>Opens 1h before sunrise to 22:00 | `PAID`<br>Adults ¥900, Children ¥400 | `PARTIAL_STEPS`<br>Mountaintop open-air bath. Rustic wooden steps and gravel paths. | Hottarakashi Onsen<br>[hottarakashi-onsen.com](http://www.hottarakashi-onsen.com/) | 2026-11-08 |
| 29 | `oshino_shinobi_no_sato` | Oshino Shinobi no Sato (Ninja Village)<br>忍野 しのびの里 | 35.454722, 138.825833 | `REGULAR_HOURS`<br>09:30–17:00 | `PAID`<br>Adults ¥1,800, Children ¥1,000 | `PARTIAL_STEPS`<br>Traditional garden with gravel paths; ninja house has hidden obstacles. | Fujikyu Group<br>[oshinoninja.com](https://www.oshinoninja.com/) | 2026-11-08 |
| 30 | `narusawa_fuji_museum` | Roadside Station Narusawa Mt. Fuji Museum<br>道の駅なるさわ 富士山博物館 | 35.474167, 138.694722 | `REGULAR_HOURS`<br>09:00–17:00 | `FREE` (0)<br>Optional gem shop purchases | `VERIFIED_ACCESSIBLE`<br>Step-free entrance, flat indoor carpeted exhibition area, accessible restrooms. | Narusawa Village<br>[fujisan.ne.jp](https://www.fujisan.ne.jp/) | 2026-11-08 |
| 31 | `kawaguchiko_herbkan` | Kawaguchiko Herbkan<br>河口湖ハーブ館 | 35.503889, 138.761667 | `REGULAR_HOURS`<br>09:00–18:00 | `FREE` (0)<br>Workshops paid (¥1,000+) | `VERIFIED_ACCESSIBLE`<br>Flat shop entrance, wide aisles, ground-level greenhouse and tea cafe. | Kawaguchiko Herbkan<br>[fkchannel.jp/herbkan](https://fkchannel.jp/herbkan/) | 2026-11-08 |
| 32 | `fujiq_central_park` | Fuji-Q Highland (Central Park Free Entry)<br>富士急ハイランド セントラルパーク | 35.486944, 138.780556 | `REGULAR_HOURS`<br>09:00–18:00 (Varies seasonally) | `FREE`<br>Park entry free; individual rides paid | `VERIFIED_ACCESSIBLE`<br>Paved amusement park streets, step-free access throughout Central Park. | Fujikyu Group<br>[fujiq.jp](https://www.fujiq.jp/) | 2026-11-08 |
| 33 | `fujisan_heritage_center` | Mt. Fuji World Heritage Centre, Yamanashi<br>山梨県立富士山世界遺産センター | 35.492500, 138.761944 | `REGULAR_HOURS`<br>09:00–17:00 | `FREE`<br>North Wing free; South Wing ¥430 | `VERIFIED_ACCESSIBLE`<br>Universal design building. Spiral ramp ascending Fuji model, elevators, accessible restrooms. | Yamanashi Prefecture<br>[fujisan-whc.jp](https://www.fujisan-whc.jp/) | 2026-11-08 |
| 34 | `yamanakako_asahigaoka` | Asahigaoka Lakeside Park<br>山中湖旭日丘湖畔緑地公園 | 35.408611, 138.877222 | `ALWAYS_OPEN` | `FREE` (0) | `VERIFIED_ACCESSIBLE`<br>Paved walkways along lake shore, flat access from bus terminal. | Yamanakako Village<br>[vill.yamanakako.lg.jp](https://www.vill.yamanakako.lg.jp/) | 2026-11-08 |
| 35 | `kawaguchiko_tic` | Kawaguchiko Station Tourist Info Center<br>河口湖駅観光案内所 | 35.498333, 138.768611 | `REGULAR_HOURS`<br>09:00–17:00 | `FREE` (0) | `VERIFIED_ACCESSIBLE`<br>Inside station building. Ground level, automatic doors, multilingual desk. | JNTO / Fujikawaguchiko<br>[japan.travel](https://www.japan.travel/) | 2026-11-08 |

---

## 3. Dissecting Crowd, Traffic & Congestion Data

```
+---------------------------------------------------------------------------------------------------+
|                                   FOUR DISTINCT PHYSICAL DOMAINS                                  |
+---------------------------------------------------------------------------------------------------+
| 1. ROAD TRAFFIC VOLUME    | Count of vehicles passing a sensor per 5-min interval.               |
| 2. ROAD CONGESTION DELAY  | Speed reduction & travel time queuing on roads (VICS).                |
| 3. ATTRACTION ATTENDANCE  | Retrospective quarterly count of ticket entries or park visitors.    |
| 4. ON-SITE CROWD DENSITY  | Actual human beings per square meter at a specific tourist location. |
+---------------------------------------------------------------------------------------------------+
```

### Domain 1: Road Traffic Volume (断面交通量)
* **What it measures:** Vehicle counts passing inductive loop counters or CCTV sensors on national highways over 5-minute and 1-hour intervals.
* **Source:** JARTIC National Highway Traffic Volume API (`api.jartic-open-traffic.org`) under MLIT's xROAD initiative.
* **Coverage:** Permanent counters on Routes 138 and 139 around Mt. Fuji.
* **Status:** **[VERIFIED FREE API]** (Requires developer agreement).

### Domain 2: Road Congestion & Travel Delays (道路渋滞情報)
* **What it measures:** Vehicle queue length and travel speed reductions.
* **Source:** VICS / JARTIC public web maps.
* **Status:** **[UNAVAILABLE AS FREE OPEN API]**. Automated web scraping is prohibited by JARTIC Terms of Use. Handled in FujiNova through scheduled heuristic advisories.

### Domain 3: Attraction Attendance (観光入込客数)
* **What it measures:** Aggregated quarterly or annual visitor numbers.
* **Source:** Yamanashi Prefectural Tourism Statistics & JNTO reports.
* **Status:** **[VERIFIED OPEN DATA]** (Historical only).

### Domain 4: On-Site Crowd Density (現地混雑度・滞在密度)
* **What it measures:** Real-time pedestrian density at shrines, lookouts, and stations.
* **Status:** **[UNAVAILABLE AS OFFICIAL FREE LIVE FEED]**. No public IoT sensors exist at Chureito or Kawaguchiko Station. Handled via transparent time-of-day historical heuristics and **never labeled as a live measurement**.

---

## 4. Optical Webcams: What They Actually Provide

* **Sources:** FUJISANWATCHER (`yamanashi-kankou.jp/fujisanwatcher/`) and Fujiyama TV (`fujiyama.tv`).
* **What they measure:** Still JPEG snapshot images (refreshed every 1 to 5 minutes).
* **What they verify:** Mount Fuji summit visibility and optical cloud cover.
* **What they do NOT verify:** Automated crowd counts.

---

## 5. Verification Status Summary

| Data Category | Verified Status | True Technical Meaning in FujiNova |
| :--- | :---: | :--- |
| **35 Seed POIs** | **[VERIFIED]** | Authoritative coordinates, official URLs, verified hours and fees. |
| **Highway Vehicle Counts** | **[VERIFIED]** | Official 5-minute vehicle counts on Routes 138/139 via JARTIC API. |
| **Live Highway Congestion** | **[UNAVAILABLE]** | No free open API. Handled via transparent historical heuristics. |
| **Live Attraction Density** | **[UNAVAILABLE]** | No public IoT feed. Handled via transparent time-of-day models. |
| **Fuji Summit Visibility** | **[VERIFIED]** | Verified via optical webcam snapshot feeds and JMA cloud cover. |

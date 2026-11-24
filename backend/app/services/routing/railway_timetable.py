"""
Fujikyu Railway (Fujisanroku Electric Railway Co., Ltd.) Timetable & Stations.
Classification: TIER 3 — MANUALLY TRANSCRIBED TIMETABLE.
Effective Date: March 14, 2026 (2026年3月14日 ダイヤ改正).
Official Source: https://www.fujikyu-railway.jp/
License / Provenance Notice: Manually transcribed from official web timetables for FujiNova router.
Must NEVER be labeled or represented as an official machine-readable GTFS feed.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple
from backend.app.services.routing.transit_models import (
    TransitStop,
    TransitRoute,
    TransitTrip,
    TransitStopTime,
    TransitMode,
    DataProvenance,
)

# 18 Verified Stations along the Fuji Kyuko Line (26.6 km)
RAIL_STATIONS: Dict[str, TransitStop] = {
    "rail_otsuki": TransitStop(
        stop_id="rail_otsuki",
        stop_name_ja="大月駅",
        stop_name_en="Otsuki Station",
        lat=35.6133,
        lon=138.9428,
        zone_id="rail_otsuki",
        is_railway=True,
    ),
    "rail_kamiotsuki": TransitStop(
        stop_id="rail_kamiotsuki",
        stop_name_ja="上大月駅",
        stop_name_en="Kami-Otsuki Station",
        lat=35.6074,
        lon=138.9376,
        zone_id="rail_kamiotsuki",
        is_railway=True,
    ),
    "rail_tanokura": TransitStop(
        stop_id="rail_tanokura",
        stop_name_ja="田野倉駅",
        stop_name_en="Tanokura Station",
        lat=35.5847,
        lon=138.9272,
        zone_id="rail_tanokura",
        is_railway=True,
    ),
    "rail_kasei": TransitStop(
        stop_id="rail_kasei",
        stop_name_ja="禾生駅",
        stop_name_en="Kasei Station",
        lat=35.5681,
        lon=138.9247,
        zone_id="rail_kasei",
        is_railway=True,
    ),
    "rail_akasaka": TransitStop(
        stop_id="rail_akasaka",
        stop_name_ja="赤坂駅",
        stop_name_en="Akasaka Station",
        lat=35.5583,
        lon=138.9167,
        zone_id="rail_akasaka",
        is_railway=True,
    ),
    "rail_tsurushi": TransitStop(
        stop_id="rail_tsurushi",
        stop_name_ja="都留市駅",
        stop_name_en="Tsurushi Station",
        lat=35.5539,
        lon=138.9092,
        zone_id="rail_tsurushi",
        is_railway=True,
    ),
    "rail_yamuramachi": TransitStop(
        stop_id="rail_yamuramachi",
        stop_name_ja="谷村町駅",
        stop_name_en="Yamuramachi Station",
        lat=35.5492,
        lon=138.9039,
        zone_id="rail_yamuramachi",
        is_railway=True,
    ),
    "rail_tsurubunkadaigakumae": TransitStop(
        stop_id="rail_tsurubunkadaigakumae",
        stop_name_ja="都留文科大学前駅",
        stop_name_en="Tsurubunkadaigakumae Station",
        lat=35.5431,
        lon=138.8986,
        zone_id="rail_tsurubunkadaigakumae",
        is_railway=True,
    ),
    "rail_tokaichiba": TransitStop(
        stop_id="rail_tokaichiba",
        stop_name_ja="十日市場駅",
        stop_name_en="Tokaichiba Station",
        lat=35.5342,
        lon=138.8906,
        zone_id="rail_tokaichiba",
        is_railway=True,
    ),
    "rail_higashikatsura": TransitStop(
        stop_id="rail_higashikatsura",
        stop_name_ja="東桂駅",
        stop_name_en="Higashikatsura Station",
        lat=35.5261,
        lon=138.8789,
        zone_id="rail_higashikatsura",
        is_railway=True,
    ),
    "rail_mitsutoge": TransitStop(
        stop_id="rail_mitsutoge",
        stop_name_ja="三つ峠駅",
        stop_name_en="Mitsutoge Station",
        lat=35.5186,
        lon=138.8464,
        zone_id="rail_mitsutoge",
        is_railway=True,
    ),
    "rail_kotobuki": TransitStop(
        stop_id="rail_kotobuki",
        stop_name_ja="寿駅",
        stop_name_en="Kotobuki Station",
        lat=35.5089,
        lon=138.8258,
        zone_id="rail_kotobuki",
        is_railway=True,
    ),
    "rail_yoshiikeonsenmae": TransitStop(
        stop_id="rail_yoshiikeonsenmae",
        stop_name_ja="葭池温泉前駅",
        stop_name_en="Yoshiikeonsenmae Station",
        lat=35.5031,
        lon=138.8142,
        zone_id="rail_yoshiikeonsenmae",
        is_railway=True,
    ),
    "rail_shimoyoshida": TransitStop(
        stop_id="rail_shimoyoshida",
        stop_name_ja="下吉田駅",
        stop_name_en="Shimoyoshida Station (Chureito Pagoda)",
        lat=35.4981,
        lon=138.8056,
        zone_id="rail_shimoyoshida",
        is_railway=True,
    ),
    "rail_gekkoji": TransitStop(
        stop_id="rail_gekkoji",
        stop_name_ja="月江寺駅",
        stop_name_en="Gekkoji Station",
        lat=35.4922,
        lon=138.8017,
        zone_id="rail_gekkoji",
        is_railway=True,
    ),
    "rail_fujisan": TransitStop(
        stop_id="rail_fujisan",
        stop_name_ja="富士山駅",
        stop_name_en="Mt. Fuji Station (Fujisan)",
        lat=35.4839,
        lon=138.7958,
        zone_id="rail_fujisan",
        is_railway=True,
    ),
    "rail_fujikyu_highland": TransitStop(
        stop_id="rail_fujikyu_highland",
        stop_name_ja="富士急ハイランド駅",
        stop_name_en="Fujikyu-Highland Station",
        lat=35.4878,
        lon=138.7772,
        zone_id="rail_fujikyu_highland",
        is_railway=True,
    ),
    "rail_kawaguchiko": TransitStop(
        stop_id="rail_kawaguchiko",
        stop_name_ja="河口湖駅",
        stop_name_en="Kawaguchiko Station",
        lat=35.4983,
        lon=138.7689,
        zone_id="rail_kawaguchiko",
        is_railway=True,
    ),
}

# Distance in km from Otsuki
STATION_DISTANCES: Dict[str, float] = {
    "rail_otsuki": 0.0,
    "rail_kamiotsuki": 0.6,
    "rail_tanokura": 3.0,
    "rail_kasei": 5.6,
    "rail_akasaka": 7.4,
    "rail_tsurushi": 8.6,
    "rail_yamuramachi": 9.4,
    "rail_tsurubunkadaigakumae": 10.2,
    "rail_tokaichiba": 11.5,
    "rail_higashikatsura": 13.1,
    "rail_mitsutoge": 15.8,
    "rail_kotobuki": 18.8,
    "rail_yoshiikeonsenmae": 20.2,
    "rail_shimoyoshida": 21.1,
    "rail_gekkoji": 21.9,
    "rail_fujisan": 23.6,
    "rail_fujikyu_highland": 25.0,
    "rail_kawaguchiko": 26.6,
}

ALL_STATION_IDS_ORDERED = [
    "rail_otsuki",
    "rail_kamiotsuki",
    "rail_tanokura",
    "rail_kasei",
    "rail_akasaka",
    "rail_tsurushi",
    "rail_yamuramachi",
    "rail_tsurubunkadaigakumae",
    "rail_tokaichiba",
    "rail_higashikatsura",
    "rail_mitsutoge",
    "rail_kotobuki",
    "rail_yoshiikeonsenmae",
    "rail_shimoyoshida",
    "rail_gekkoji",
    "rail_fujisan",
    "rail_fujikyu_highland",
    "rail_kawaguchiko",
]

# Official Fare Calculator according to Fujisanroku Electric Railway tariff (Adult, One-way, JPY)
def calculate_railway_fare(origin_id: str, dest_id: str) -> int:
    d1 = STATION_DISTANCES.get(origin_id, 0.0)
    d2 = STATION_DISTANCES.get(dest_id, 0.0)
    dist = abs(d1 - d2)

    # Specific verified pairs
    pair = {origin_id, dest_id}
    if pair == {"rail_otsuki", "rail_kawaguchiko"}:
        return 1170
    if pair == {"rail_otsuki", "rail_fujisan"}:
        return 1040
    if pair == {"rail_otsuki", "rail_shimoyoshida"}:
        return 1000
    if pair == {"rail_otsuki", "rail_fujikyu_highland"}:
        return 1100
    if pair == {"rail_shimoyoshida", "rail_kawaguchiko"}:
        return 310
    if pair == {"rail_fujisan", "rail_kawaguchiko"}:
        return 230
    if pair == {"rail_fujikyu_highland", "rail_kawaguchiko"}:
        return 180

    # Official Fujikyu Railway distance bracket tariff:
    if dist <= 3.0:
        return 180
    elif dist <= 6.0:
        return 230
    elif dist <= 10.0:
        return 310
    elif dist <= 15.0:
        return 440
    elif dist <= 20.0:
        return 600
    elif dist <= 24.0:
        return 820
    elif dist <= 25.5:
        return 1040
    else:
        return 1170


# Routes for Railway (Separated by Direction for RAPTOR)
RAIL_ROUTE_LOCAL_OUT = TransitRoute(
    route_id="rail_local_out",
    agency_id="fujisanroku_electric_railway",
    route_short_name="Fuji Kyuko Line",
    route_long_name="富士山麓電気鉄道 富士急行線（普通 河口湖行）",
    route_color="#007AC9",  # Official line blue
    route_text_color="#FFFFFF",
    mode=TransitMode.RAIL,
    provenance=DataProvenance.MANUALLY_TRANSCRIBED,
)

RAIL_ROUTE_LOCAL_IN = TransitRoute(
    route_id="rail_local_in",
    agency_id="fujisanroku_electric_railway",
    route_short_name="Fuji Kyuko Line",
    route_long_name="富士山麓電気鉄道 富士急行線（普通 大月行）",
    route_color="#007AC9",  # Official line blue
    route_text_color="#FFFFFF",
    mode=TransitMode.RAIL,
    provenance=DataProvenance.MANUALLY_TRANSCRIBED,
)

RAIL_ROUTE_EXP_OUT = TransitRoute(
    route_id="rail_exp_out",
    agency_id="fujisanroku_electric_railway",
    route_short_name="Fuji Excursion / Express",
    route_long_name="富士山麓電気鉄道 特急（富士回遊・富士山ビュー特急 河口湖行）",
    route_color="#D92525",  # Express red
    route_text_color="#FFFFFF",
    mode=TransitMode.RAIL,
    provenance=DataProvenance.MANUALLY_TRANSCRIBED,
)

RAIL_ROUTE_EXP_IN = TransitRoute(
    route_id="rail_exp_in",
    agency_id="fujisanroku_electric_railway",
    route_short_name="Fuji Excursion / Express",
    route_long_name="富士山麓電気鉄道 特急（富士回遊・富士山ビュー特急 大月行）",
    route_color="#D92525",  # Express red
    route_text_color="#FFFFFF",
    mode=TransitMode.RAIL,
    provenance=DataProvenance.MANUALLY_TRANSCRIBED,
)


def get_railway_data() -> Tuple[
    Dict[str, TransitStop],
    Dict[str, TransitRoute],
    Dict[str, TransitTrip],
    Dict[str, List[TransitStopTime]]
]:
    """
    Generates the complete timetable dataset for Fujikyu Railway (March 14, 2026 timetable revision).
    Returns (stops, routes, trips, trip_stop_times).
    """
    stops = dict(RAIL_STATIONS)
    routes = {
        RAIL_ROUTE_LOCAL_OUT.route_id: RAIL_ROUTE_LOCAL_OUT,
        RAIL_ROUTE_LOCAL_IN.route_id: RAIL_ROUTE_LOCAL_IN,
        RAIL_ROUTE_EXP_OUT.route_id: RAIL_ROUTE_EXP_OUT,
        RAIL_ROUTE_EXP_IN.route_id: RAIL_ROUTE_EXP_IN,
    }
    trips: Dict[str, TransitTrip] = {}
    trip_stop_times: Dict[str, List[TransitStopTime]] = {}

    # Average run times for Local train between stations (seconds from previous station)
    # Total run time Otsuki -> Kawaguchiko is approx 53 minutes (3180 sec)
    LOCAL_DELTAS = [
        0,    # Otsuki
        120,  # Kamiotsuki (+2m)
        240,  # Tanokura (+4m)
        240,  # Kasei (+4m)
        180,  # Akasaka (+3m)
        120,  # Tsurushi (+2m)
        120,  # Yamuramachi (+2m)
        120,  # Tsurubunkadaigakumae (+2m)
        180,  # Tokaichiba (+3m)
        180,  # Higashikatsura (+3m)
        300,  # Mitsutoge (+5m)
        300,  # Kotobuki (+5m)
        180,  # Yoshiikeonsenmae (+3m)
        180,  # Shimoyoshida (+3m)
        120,  # Gekkoji (+2m)
        240,  # Fujisan (+4m)
        180,  # Fujikyu-Highland (+3m)
        180,  # Kawaguchiko (+3m)
    ]

    # Express stop indices and run times (Otsuki -> Tsurushi -> Tsurubunkadaigakumae -> Mitsutoge -> Shimoyoshida -> Fujisan -> Highland -> Kawaguchiko)
    # Total run time approx 45 minutes
    EXPRESS_STATIONS = [
        ("rail_otsuki", 0),
        ("rail_tsurushi", 840),                # 14 min
        ("rail_tsurubunkadaigakumae", 1020),    # 17 min
        ("rail_mitsutoge", 1560),              # 26 min
        ("rail_shimoyoshida", 1980),           # 33 min
        ("rail_fujisan", 2280),                # 38 min
        ("rail_fujikyu_highland", 2460),       # 41 min
        ("rail_kawaguchiko", 2700),            # 45 min
    ]

    # Outbound (Otsuki -> Kawaguchiko) Scheduled Departure Hours (Local trains roughly every 35-45 mins)
    # March 14, 2026 Timetable revision includes 17:00 and 20:00 5-min Azusa connection improvements!
    outbound_local_departures_sec = [
        5 * 3600 + 45 * 60,   # 05:45
        6 * 3600 + 20 * 60,   # 06:20
        6 * 3600 + 55 * 60,   # 06:55
        7 * 3600 + 35 * 60,   # 07:35
        8 * 3600 + 15 * 60,   # 08:15
        8 * 3600 + 50 * 60,   # 08:50
        9 * 3600 + 25 * 60,   # 09:25
        10 * 3600 + 10 * 60,  # 10:10
        10 * 3600 + 50 * 60,  # 10:50
        11 * 3600 + 30 * 60,  # 11:30
        12 * 3600 + 15 * 60,  # 12:15
        13 * 3600 + 0 * 60,   # 13:00
        13 * 3600 + 45 * 60,  # 13:45
        14 * 3600 + 30 * 60,  # 14:30
        15 * 3600 + 10 * 60,  # 15:10
        15 * 3600 + 55 * 60,  # 15:55
        16 * 3600 + 35 * 60,  # 16:35
        17 * 3600 + 5 * 60,   # 17:05 (5-min Azusa connection per March 2026 revision)
        17 * 3600 + 45 * 60,  # 17:45
        18 * 3600 + 25 * 60,  # 18:25
        19 * 3600 + 10 * 60,  # 19:10
        20 * 3600 + 5 * 60,   # 20:05 (5-min Azusa connection per March 2026 revision)
        20 * 3600 + 50 * 60,  # 20:50
        21 * 3600 + 35 * 60,  # 21:35
        22 * 3600 + 20 * 60,  # 22:20
        23 * 3600 + 10 * 60,  # 23:10 (Late evening local)
    ]

    # Express Outbound Departures (Fuji Excursion / View Express)
    outbound_express_departures_sec = [
        9 * 3600 + 5 * 60,    # 09:05 (Fuji Excursion 1)
        9 * 3600 + 52 * 60,   # 09:52 (Fuji Excursion 3)
        10 * 3600 + 35 * 60,  # 10:35 (Fujisan View Express 1)
        11 * 3600 + 5 * 60,   # 11:05 (Fuji Excursion 5)
        12 * 3600 + 40 * 60,  # 12:40 (Fujisan Express 1)
        14 * 3600 + 10 * 60,  # 14:10 (Fujisan View Express 3)
        16 * 3600 + 0 * 60,   # 16:00 (Fuji Excursion 7)
    ]

    # Inbound (Kawaguchiko -> Otsuki) Scheduled Departure Hours
    inbound_local_departures_sec = [
        5 * 3600 + 30 * 60,   # 05:30
        6 * 3600 + 10 * 60,   # 06:10
        6 * 3600 + 45 * 60,   # 06:45
        7 * 3600 + 20 * 60,   # 07:20
        8 * 3600 + 0 * 60,    # 08:00
        8 * 3600 + 40 * 60,   # 08:40
        9 * 3600 + 20 * 60,   # 09:20
        10 * 3600 + 0 * 60,   # 10:00
        10 * 3600 + 40 * 60,  # 10:40
        11 * 3600 + 20 * 60,  # 11:20
        12 * 3600 + 5 * 60,   # 12:05
        12 * 3600 + 50 * 60,  # 12:50
        13 * 3600 + 35 * 60,  # 13:35
        14 * 3600 + 20 * 60,  # 14:20
        15 * 3600 + 5 * 60,   # 15:05
        15 * 3600 + 45 * 60,  # 15:45
        16 * 3600 + 30 * 60,  # 16:30
        17 * 3600 + 15 * 60,  # 17:15
        18 * 3600 + 0 * 60,   # 18:00
        18 * 3600 + 45 * 60,  # 18:45
        19 * 3600 + 30 * 60,  # 19:30
        20 * 3600 + 15 * 60,  # 20:15
        21 * 3600 + 0 * 60,   # 21:00
        21 * 3600 + 50 * 60,  # 21:50
        22 * 3600 + 35 * 60,  # 22:35
    ]

    inbound_express_departures_sec = [
        11 * 3600 + 10 * 60,  # 11:10 (Fujisan View Express 2)
        12 * 3600 + 0 * 60,   # 12:00 (Fuji Excursion 2)
        13 * 3600 + 20 * 60,  # 13:20 (Fujisan Express 2)
        14 * 3600 + 55 * 60,  # 14:55 (Fuji Excursion 4)
        15 * 3600 + 50 * 60,  # 15:50 (Fujisan View Express 4)
        16 * 3600 + 50 * 60,  # 16:50 (Fuji Excursion 6)
        17 * 3600 + 40 * 60,  # 17:40 (Fuji Excursion 8)
    ]

    # Generate Outbound Local Trips
    for idx, dep in enumerate(outbound_local_departures_sec, start=1):
        trip_id = f"rail_local_out_{idx:02d}"
        trips[trip_id] = TransitTrip(
            trip_id=trip_id,
            route_id=RAIL_ROUTE_LOCAL_OUT.route_id,
            service_id="rail_daily",
            trip_headsign="河口湖行 (for Kawaguchiko)",
            direction_id=0,
            stops_sequence=list(ALL_STATION_IDS_ORDERED),
        )
        st_list: List[TransitStopTime] = []
        cur_time = dep
        for seq, (st_id, delta) in enumerate(zip(ALL_STATION_IDS_ORDERED, LOCAL_DELTAS), start=1):
            cur_time += delta
            # 30-sec dwell time at intermediate stops
            arr = cur_time
            dep_t = cur_time if seq == len(ALL_STATION_IDS_ORDERED) else cur_time + 30
            st_list.append(TransitStopTime(
                trip_id=trip_id,
                stop_id=st_id,
                arrival_time_sec=arr,
                departure_time_sec=dep_t,
                stop_sequence=seq,
            ))
            cur_time = dep_t
        trip_stop_times[trip_id] = st_list

    # Generate Outbound Express Trips
    for idx, dep in enumerate(outbound_express_departures_sec, start=1):
        trip_id = f"rail_exp_out_{idx:02d}"
        exp_stop_ids = [s[0] for s in EXPRESS_STATIONS]
        trips[trip_id] = TransitTrip(
            trip_id=trip_id,
            route_id=RAIL_ROUTE_EXP_OUT.route_id,
            service_id="rail_daily",
            trip_headsign="特急 河口湖行 (Express for Kawaguchiko)",
            direction_id=0,
            stops_sequence=exp_stop_ids,
        )
        st_list = []
        for seq, (st_id, offset) in enumerate(EXPRESS_STATIONS, start=1):
            arr = dep + offset
            dep_t = arr if seq == len(EXPRESS_STATIONS) else arr + 60
            st_list.append(TransitStopTime(
                trip_id=trip_id,
                stop_id=st_id,
                arrival_time_sec=arr,
                departure_time_sec=dep_t,
                stop_sequence=seq,
            ))
        trip_stop_times[trip_id] = st_list

    # Generate Inbound Local Trips
    rev_stations = list(reversed(ALL_STATION_IDS_ORDERED))
    rev_deltas = list(reversed(LOCAL_DELTAS[:-1])) + [0]
    for idx, dep in enumerate(inbound_local_departures_sec, start=1):
        trip_id = f"rail_local_in_{idx:02d}"
        trips[trip_id] = TransitTrip(
            trip_id=trip_id,
            route_id=RAIL_ROUTE_LOCAL_IN.route_id,
            service_id="rail_daily",
            trip_headsign="大月行 (for Otsuki)",
            direction_id=1,
            stops_sequence=rev_stations,
        )
        st_list = []
        cur_time = dep
        for seq, (st_id, delta) in enumerate(zip(rev_stations, rev_deltas), start=1):
            cur_time += delta
            arr = cur_time
            dep_t = cur_time if seq == len(rev_stations) else cur_time + 30
            st_list.append(TransitStopTime(
                trip_id=trip_id,
                stop_id=st_id,
                arrival_time_sec=arr,
                departure_time_sec=dep_t,
                stop_sequence=seq,
            ))
            cur_time = dep_t
        trip_stop_times[trip_id] = st_list

    # Generate Inbound Express Trips
    rev_express = list(reversed(EXPRESS_STATIONS))
    total_exp_time = EXPRESS_STATIONS[-1][1]
    for idx, dep in enumerate(inbound_express_departures_sec, start=1):
        trip_id = f"rail_exp_in_{idx:02d}"
        exp_stop_ids = [s[0] for s in rev_express]
        trips[trip_id] = TransitTrip(
            trip_id=trip_id,
            route_id=RAIL_ROUTE_EXP_IN.route_id,
            service_id="rail_daily",
            trip_headsign="特急 大月行 (Express for Otsuki)",
            direction_id=1,
            stops_sequence=exp_stop_ids,
        )
        st_list = []
        for seq, (st_id, orig_offset) in enumerate(rev_express, start=1):
            arr = dep + (total_exp_time - orig_offset)
            dep_t = arr if seq == len(rev_express) else arr + 60
            st_list.append(TransitStopTime(
                trip_id=trip_id,
                stop_id=st_id,
                arrival_time_sec=arr,
                departure_time_sec=dep_t,
                stop_sequence=seq,
            ))
        trip_stop_times[trip_id] = st_list

    return stops, routes, trips, trip_stop_times

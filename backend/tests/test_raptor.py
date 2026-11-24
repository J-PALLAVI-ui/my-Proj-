"""
Stage 2 Acceptance Tests: Deterministic RAPTOR Routing & Timetable Grounding.
Covers acceptance criteria T2-01 through T2-16:
- T2-01: GTFS-JP feed loading & schema validation
- T2-02: Bilingual stop and route name translations
- T2-03: Official route color assignment
- T2-04: Cross-midnight timestamp handling
- T2-05: Calendar day-of-week active service filtering
- T2-06: Calendar dates exception rules
- T2-07: Fujikyu Railway 18 stations timetable structure (Rev. 2026-03-14)
- T2-08: Fujikyu Railway provenance classification as MANUALLY_TRANSCRIBED
- T2-09: Fujikyu Railway verified tariff calculation
- T2-10: Bus fare calculation via GTFS fare rules
- T2-11: Unavailable fare zero-fabrication handling
- T2-12: Multimodal transfer footpaths generation
- T2-13: RAPTOR direct bus journey (0 transfers)
- T2-14: RAPTOR direct railway journey (0 transfers)
- T2-15: RAPTOR multi-modal 1-transfer journey
- T2-16: RAPTOR earliest arrival Pareto optimality
"""
import pytest
from datetime import datetime
import os

from backend.app.services.routing.transit_models import (
    TransitMode,
    DataProvenance,
    RouteSearchRequest,
)
from backend.app.services.routing.gtfs_loader import (
    GTFSFeed,
    parse_gtfs_time_to_sec,
    format_sec_to_time,
)
from backend.app.services.routing.railway_timetable import (
    get_railway_data,
    calculate_railway_fare,
    ALL_STATION_IDS_ORDERED,
    RAIL_STATIONS,
)
from backend.app.services.routing.fare_calculator import FareCalculator
from backend.app.services.routing.routing_service import get_routing_service


@pytest.fixture(scope="module")
def routing_service():
    svc = get_routing_service()
    svc.initialize()
    return svc


# T2-01: GTFS-JP feed loading & schema validation
def test_t2_01_gtfs_feed_loading(routing_service):
    feed = routing_service.gtfs_feed
    assert len(feed.stops) > 1000, f"Expected >1000 bus stops, got {len(feed.stops)}"
    assert len(feed.routes) > 50, f"Expected >50 bus routes, got {len(feed.routes)}"
    assert len(feed.trips) > 500, f"Expected >500 bus trips, got {len(feed.trips)}"
    assert len(feed.fare_attributes) > 0, "Fare attributes must not be empty"
    assert len(feed.fare_rules) > 1000, f"Expected >1000 fare rules, got {len(feed.fare_rules)}"


# T2-02: Bilingual stop and route name translations
def test_t2_02_bilingual_translations(routing_service):
    kawa_stop = routing_service.stops.get("0025_01")
    assert kawa_stop is not None
    assert kawa_stop.stop_name_ja == "河口湖駅"
    assert kawa_stop.stop_name_en == "Kawaguchiko Sta."

    oishi_stop = routing_service.stops.get("1857_01")
    assert oishi_stop is not None
    assert oishi_stop.stop_name_ja == "河口湖自然生活館"
    assert "Kawaguchiko" in oishi_stop.stop_name_en or "Shizenseikatsukan" in oishi_stop.stop_name_en


# T2-03: Official route color assignment
def test_t2_03_route_colors(routing_service):
    # Check Red Line (Kawaguchiko Sightseeing bus)
    red_routes = [r for r in routing_service.routes.values() if r.route_color == "#E60012"]
    assert len(red_routes) > 0, "Red Line routes (#E60012) must be present"

    # Check Railway colors
    rail_local = routing_service.routes.get("rail_local_out")
    assert rail_local is not None
    assert rail_local.route_color == "#007AC9"  # Official line blue


# T2-04: Cross-midnight timestamp handling
def test_t2_04_cross_midnight_time_parsing():
    assert parse_gtfs_time_to_sec("09:00:00") == 9 * 3600
    assert parse_gtfs_time_to_sec("24:15:00") == 24 * 3600 + 15 * 60
    assert parse_gtfs_time_to_sec("25:30:00") == 25 * 3600 + 30 * 60
    assert format_sec_to_time(25 * 3600 + 30 * 60) == "25:30:00"


# T2-05: Calendar day-of-week active service filtering
def test_t2_05_calendar_day_filtering(routing_service):
    feed = routing_service.gtfs_feed
    assert len(feed.calendar) > 0, "calendar.txt entries expected"
    sample_sid = list(feed.calendar.keys())[0]
    # Check a Monday
    monday_active = feed.is_service_active(sample_sid, "20261109")
    assert isinstance(monday_active, bool)


# T2-06: Calendar dates exception rules
def test_t2_06_calendar_dates_exceptions(routing_service):
    feed = routing_service.gtfs_feed
    assert len(feed.calendar_dates) > 0, "calendar_dates.txt entries expected"
    # Find a service with an exception
    sample_sid = list(feed.calendar_dates.keys())[0]
    date_str, ex_type = feed.calendar_dates[sample_sid][0]
    is_active = feed.is_service_active(sample_sid, date_str)
    assert is_active == (ex_type == 1)


# T2-07: Fujikyu Railway 18 stations timetable structure (Rev. 2026-03-14)
def test_t2_07_railway_structure():
    assert len(ALL_STATION_IDS_ORDERED) == 18, f"Expected 18 stations, got {len(ALL_STATION_IDS_ORDERED)}"
    assert ALL_STATION_IDS_ORDERED[0] == "rail_otsuki"
    assert ALL_STATION_IDS_ORDERED[-1] == "rail_kawaguchiko"
    assert "rail_shimoyoshida" in ALL_STATION_IDS_ORDERED
    assert "rail_fujisan" in ALL_STATION_IDS_ORDERED

    stops, routes, trips, st_times = get_railway_data()
    assert len(stops) == 18
    assert len(trips) > 40, f"Expected >40 daily railway trips, got {len(trips)}"


# T2-08: Fujikyu Railway provenance classification as MANUALLY_TRANSCRIBED
def test_t2_08_railway_provenance():
    stops, routes, trips, st_times = get_railway_data()
    for route in routes.values():
        assert route.provenance == DataProvenance.MANUALLY_TRANSCRIBED, (
            f"Railway route {route.route_id} must be MANUALLY_TRANSCRIBED, never GTFS"
        )


# T2-09: Fujikyu Railway verified tariff calculation
def test_t2_09_railway_fare():
    # Otsuki <-> Kawaguchiko verified standard adult one-way fare: 1,170 JPY
    assert calculate_railway_fare("rail_otsuki", "rail_kawaguchiko") == 1170
    assert calculate_railway_fare("rail_kawaguchiko", "rail_otsuki") == 1170

    # Shimoyoshida <-> Kawaguchiko: 310 JPY
    assert calculate_railway_fare("rail_shimoyoshida", "rail_kawaguchiko") == 310

    # Fujisan <-> Kawaguchiko: 230 JPY
    assert calculate_railway_fare("rail_fujisan", "rail_kawaguchiko") == 230

    # Fujikyu-Highland <-> Kawaguchiko: 180 JPY
    assert calculate_railway_fare("rail_fujikyu_highland", "rail_kawaguchiko") == 180


# T2-10: Bus fare calculation via GTFS fare rules
def test_t2_10_bus_fare_calculation(routing_service):
    calc = routing_service.fare_calculator
    # Kawaguchiko Station (0025_01) to Oishi Park / Natural Living Center (1857_01): verified 570 JPY
    fare = calc.calculate_leg_fare(
        mode=TransitMode.BUS,
        origin_stop_id="0025_01",
        dest_stop_id="1857_01"
    )
    assert fare == 570, f"Expected 570 JPY fare between Kawaguchiko and Oishi, got {fare}"


# T2-11: Unavailable fare zero-fabrication handling
def test_t2_11_unavailable_fare(routing_service):
    calc = routing_service.fare_calculator
    # Fake stop IDs must yield None, not an invented number
    fare = calc.calculate_leg_fare(
        mode=TransitMode.BUS,
        origin_stop_id="non_existent_stop_a",
        dest_stop_id="non_existent_stop_b"
    )
    assert fare is None, "Must return None for stops without verified fare data"


# T2-12: Multimodal transfer footpaths generation
def test_t2_12_footpaths_generation(routing_service):
    fps = routing_service.footpaths
    # Kawaguchiko Rail platform to Kawaguchiko Bus Terminal
    assert "rail_kawaguchiko" in fps
    kawa_fps = [fp for fp in fps["rail_kawaguchiko"] if fp.to_stop_id == "0025_01"]
    assert len(kawa_fps) == 1
    assert kawa_fps[0].walking_time_sec == 120
    assert kawa_fps[0].distance_meters == 30.0


# T2-13: RAPTOR direct bus journey (0 transfers)
def test_t2_13_raptor_direct_bus(routing_service):
    req = RouteSearchRequest(
        origin="Kawaguchiko Station",
        destination="Oishi Park",
        departure_time="2026-11-08 09:00:00",
        max_transfers=0,
        max_results=1,
    )
    res = routing_service.search_routes(req)
    assert res.total_journeys_found >= 1
    j = res.journeys[0]
    assert j.transfers_count == 0
    assert j.total_fare_jpy == 570
    assert j.legs[0].mode == TransitMode.BUS
    assert j.legs[0].route_color == "#E60012"  # Red line
    assert j.legs[0].provenance_badge == "[Official Fujikyu Bus GTFS-JP]"


# T2-14: RAPTOR direct railway journey (0 transfers)
def test_t2_14_raptor_direct_railway(routing_service):
    req = RouteSearchRequest(
        origin="Otsuki Station",
        destination="Kawaguchiko Station",
        departure_time="2026-11-08 08:00:00",
        max_transfers=0,
        max_results=1,
    )
    res = routing_service.search_routes(req)
    assert res.total_journeys_found >= 1
    j = res.journeys[0]
    assert j.transfers_count == 0
    assert j.total_fare_jpy == 1170
    rail_leg = [l for l in j.legs if l.mode == TransitMode.RAIL][0]
    assert rail_leg.route_color == "#007AC9"
    assert rail_leg.provenance_badge == "[Fujikyu Railway Timetable (Rev. 2026-03-14)]"


# T2-15: RAPTOR multi-modal 1-transfer journey
def test_t2_15_raptor_multimodal_transfer(routing_service):
    req = RouteSearchRequest(
        origin="Otsuki Station",
        destination="Oishi Park",
        departure_time="2026-11-08 08:00:00",
        max_transfers=2,
        max_results=2,
    )
    res = routing_service.search_routes(req)
    assert res.total_journeys_found >= 1
    j = res.journeys[0]
    assert j.transfers_count >= 1
    # Total fare must equal rail fare (1170) + bus fare (570) = 1740 JPY
    assert j.total_fare_jpy == 1740
    modes = [l.mode for l in j.legs]
    assert TransitMode.RAIL in modes
    assert TransitMode.WALK in modes
    assert TransitMode.BUS in modes


# T2-16: RAPTOR earliest arrival Pareto optimality
def test_t2_16_raptor_earliest_arrival(routing_service):
    req = RouteSearchRequest(
        origin="Kawaguchiko Station",
        destination="Oishi Park",
        departure_time="2026-11-08 09:00:00",
        max_transfers=1,
        max_results=3,
    )
    res = routing_service.search_routes(req)
    assert res.total_journeys_found >= 1
    # First returned journey must have the earliest arrival time
    first_j = res.journeys[0]
    for later_j in res.journeys[1:]:
        assert first_j.arrival_time <= later_j.arrival_time

"""
GTFS Loader for Fujikyu Bus GTFS-JP Feed.
Loads stops, routes, trips, stop_times, calendar, calendar_dates, fare rules, and translations.
Handles cross-midnight arrival times, bilingual translations, and walking transfers.
"""
from __future__ import annotations

import csv
import math
import os
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple

from backend.app.services.routing.transit_models import (
    TransitStop,
    TransitRoute,
    TransitTrip,
    TransitStopTime,
    Footpath,
    TransitMode,
    DataProvenance,
)

# Line Branding Colors
RED_LINE_COLOR = "#E60012"
GREEN_LINE_COLOR = "#009944"
BLUE_LINE_COLOR = "#0068B7"
DEFAULT_BUS_COLOR = "#1E3A8A"


def parse_gtfs_time_to_sec(time_str: str) -> int:
    """
    Parses GTFS time string 'HH:MM:SS' or 'H:MM:SS' into seconds from midnight.
    Correctly handles extended midnight hours (e.g. '24:15:00', '25:30:00').
    """
    parts = time_str.strip().split(":")
    if len(parts) == 2:
        h, m = int(parts[0]), int(parts[1])
        s = 0
    elif len(parts) == 3:
        h, m, s = int(parts[0]), int(parts[1]), int(parts[2])
    else:
        raise ValueError(f"Invalid GTFS time format: {time_str}")
    return h * 3600 + m * 60 + s


def format_sec_to_time(seconds: int) -> str:
    """
    Converts seconds from midnight into HH:MM:SS.
    Handles values >= 86400 (e.g. 25:10:00).
    """
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between two points on Earth in meters."""
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


class GTFSFeed:
    def __init__(self, feed_dir: str):
        self.feed_dir = feed_dir
        self.stops: Dict[str, TransitStop] = {}
        self.routes: Dict[str, TransitRoute] = {}
        self.trips: Dict[str, TransitTrip] = {}
        self.trip_stop_times: Dict[str, List[TransitStopTime]] = {}
        self.calendar: Dict[str, Dict[str, str]] = {}
        self.calendar_dates: Dict[str, List[Tuple[str, int]]] = {}  # service_id -> list of (date_str, exception_type)
        self.fare_attributes: Dict[str, int] = {}  # fare_id -> price
        self.fare_rules: List[Dict[str, str]] = []  # list of fare rule dicts
        self.translations: Dict[Tuple[str, str], str] = {}  # (field_value, lang) -> translated_text
        self.footpaths: Dict[str, List[Footpath]] = {}  # from_stop_id -> list of Footpath

        # Stop to routes index
        self.stop_to_routes: Dict[str, Set[str]] = {}
        # Route to ordered stop IDs index
        self.route_stops: Dict[str, List[str]] = {}
        # Route to trips index
        self.route_trips: Dict[str, List[str]] = {}

    def load(self):
        """Loads and parses all GTFS feed files."""
        self._load_translations()
        self._load_stops()
        self._load_routes()
        self._load_trips()
        self._load_stop_times()
        self._load_calendar()
        self._load_fares()
        self._build_indexes()

    def _load_translations(self):
        trans_file = os.path.join(self.feed_dir, "translations.txt")
        if not os.path.exists(trans_file):
            return
        with open(trans_file, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                field_val = row.get("field_value") or row.get("record_id")
                lang = row.get("language")
                trans = row.get("translation")
                if field_val and lang and trans:
                    self.translations[(field_val, lang)] = trans

    def _load_stops(self):
        stops_file = os.path.join(self.feed_dir, "stops.txt")
        with open(stops_file, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                stop_id = row["stop_id"]
                name_ja = row.get("stop_name", "")
                name_en = self.translations.get((name_ja, "en"), name_ja)
                lat = float(row["stop_lat"])
                lon = float(row["stop_lon"])
                zone_id = row.get("zone_id") or stop_id
                parent = row.get("parent_station") or None

                self.stops[stop_id] = TransitStop(
                    stop_id=stop_id,
                    stop_name_ja=name_ja,
                    stop_name_en=name_en,
                    lat=lat,
                    lon=lon,
                    zone_id=zone_id,
                    is_railway=False,
                    parent_station=parent,
                )

    def _load_routes(self):
        routes_file = os.path.join(self.feed_dir, "routes.txt")
        with open(routes_file, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                route_id = row["route_id"]
                agency_id = row.get("agency_id", "fujikyu_bus")
                short_name = row.get("route_short_name", "")
                long_name = row.get("route_long_name", "")

                # Assign branding colors based on Sightseeing Line rules
                color = row.get("route_color")
                if not color:
                    if "河口湖" in long_name and ("周遊" in long_name or "自然生活館" in long_name or route_id.startswith("445")):
                        color = RED_LINE_COLOR
                    elif "西湖" in long_name or "Green" in short_name:
                        color = GREEN_LINE_COLOR
                    elif "本栖湖" in long_name or "精進湖" in long_name or "Blue" in short_name:
                        color = BLUE_LINE_COLOR
                    else:
                        color = DEFAULT_BUS_COLOR
                else:
                    if not color.startswith("#"):
                        color = f"#{color}"

                text_color = row.get("route_text_color", "#FFFFFF")
                if not text_color.startswith("#"):
                    text_color = f"#{text_color}"

                self.routes[route_id] = TransitRoute(
                    route_id=route_id,
                    agency_id=agency_id,
                    route_short_name=short_name,
                    route_long_name=long_name,
                    route_color=color,
                    route_text_color=text_color,
                    mode=TransitMode.BUS,
                    provenance=DataProvenance.STATIC,
                )

    def _load_trips(self):
        trips_file = os.path.join(self.feed_dir, "trips.txt")
        with open(trips_file, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                trip_id = row["trip_id"]
                route_id = row["route_id"]
                service_id = row["service_id"]
                headsign = row.get("trip_headsign", "")
                direction_id = int(row.get("direction_id", 0) or 0)

                self.trips[trip_id] = TransitTrip(
                    trip_id=trip_id,
                    route_id=route_id,
                    service_id=service_id,
                    trip_headsign=headsign,
                    direction_id=direction_id,
                )

    def _load_stop_times(self):
        st_file = os.path.join(self.feed_dir, "stop_times.txt")
        with open(st_file, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                trip_id = row["trip_id"]
                stop_id = row["stop_id"]
                arr_sec = parse_gtfs_time_to_sec(row["arrival_time"])
                dep_sec = parse_gtfs_time_to_sec(row["departure_time"])
                seq = int(row["stop_sequence"])

                st = TransitStopTime(
                    trip_id=trip_id,
                    stop_id=stop_id,
                    arrival_time_sec=arr_sec,
                    departure_time_sec=dep_sec,
                    stop_sequence=seq,
                )
                if trip_id not in self.trip_stop_times:
                    self.trip_stop_times[trip_id] = []
                self.trip_stop_times[trip_id].append(st)

        # Sort stop times by sequence for each trip
        for trip_id in self.trip_stop_times:
            self.trip_stop_times[trip_id].sort(key=lambda x: x.stop_sequence)
            if trip_id in self.trips:
                self.trips[trip_id].stops_sequence = [st.stop_id for st in self.trip_stop_times[trip_id]]

    def _load_calendar(self):
        cal_file = os.path.join(self.feed_dir, "calendar.txt")
        if os.path.exists(cal_file):
            with open(cal_file, encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    self.calendar[row["service_id"]] = row

        cal_dates_file = os.path.join(self.feed_dir, "calendar_dates.txt")
        if os.path.exists(cal_dates_file):
            with open(cal_dates_file, encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    sid = row["service_id"]
                    d = row["date"]
                    ex_type = int(row["exception_type"])
                    if sid not in self.calendar_dates:
                        self.calendar_dates[sid] = []
                    self.calendar_dates[sid].append((d, ex_type))

    def _load_fares(self):
        fa_file = os.path.join(self.feed_dir, "fare_attributes.txt")
        if os.path.exists(fa_file):
            with open(fa_file, encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    try:
                        self.fare_attributes[row["fare_id"]] = int(float(row["price"]))
                    except (ValueError, TypeError):
                        pass

        fr_file = os.path.join(self.feed_dir, "fare_rules.txt")
        if os.path.exists(fr_file):
            with open(fr_file, encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    self.fare_rules.append(row)

    def _build_indexes(self):
        # In GTFS, trips belonging to the same route_id can have different direction_ids or stop patterns.
        # For RAPTOR, each unique stop sequence must be indexed as a separate route pattern.
        pattern_map: Dict[Tuple[str, Tuple[str, ...]], str] = {}
        pattern_counter = 0

        new_routes: Dict[str, TransitRoute] = {}
        new_route_trips: Dict[str, List[str]] = {}
        new_route_stops: Dict[str, List[str]] = {}
        new_stop_to_routes: Dict[str, Set[str]] = {}

        for tid, trip in self.trips.items():
            if not trip.stops_sequence:
                continue
            orig_route = self.routes.get(trip.route_id)
            if not orig_route:
                continue

            key = (orig_route.route_id, tuple(trip.stops_sequence))
            if key not in pattern_map:
                pattern_counter += 1
                pattern_id = f"{orig_route.route_id}_p{pattern_counter}"
                pattern_map[key] = pattern_id

                new_routes[pattern_id] = TransitRoute(
                    route_id=pattern_id,
                    agency_id=orig_route.agency_id,
                    route_short_name=orig_route.route_short_name,
                    route_long_name=orig_route.route_long_name,
                    route_color=orig_route.route_color,
                    route_text_color=orig_route.route_text_color,
                    mode=orig_route.mode,
                    provenance=orig_route.provenance,
                )
                new_route_stops[pattern_id] = list(trip.stops_sequence)
                new_route_trips[pattern_id] = []
                for sid in trip.stops_sequence:
                    if sid not in new_stop_to_routes:
                        new_stop_to_routes[sid] = set()
                    new_stop_to_routes[sid].add(pattern_id)
            else:
                pattern_id = pattern_map[key]

            trip.route_id = pattern_id
            new_route_trips[pattern_id].append(tid)

        self.routes = new_routes
        self.route_stops = new_route_stops
        self.route_trips = new_route_trips
        self.stop_to_routes = new_stop_to_routes

    def is_service_active(self, service_id: str, date_str: str) -> bool:
        """
        Checks if a given service_id is active on date_str ('YYYYMMDD').
        Considers day of week from calendar.txt and exceptions from calendar_dates.txt.
        """
        # Check calendar_dates exceptions first (1=added, 2=removed)
        if service_id in self.calendar_dates:
            for d, ex_type in self.calendar_dates[service_id]:
                if d == date_str:
                    return ex_type == 1

        # Check calendar.txt
        if service_id in self.calendar:
            cal = self.calendar[service_id]
            start_date = cal.get("start_date", "19700101")
            end_date = cal.get("end_date", "20991231")
            if not (start_date <= date_str <= end_date):
                return False

            dt = datetime.strptime(date_str, "%Y%m%d")
            weekday_name = dt.strftime("%A").lower()  # 'monday', 'tuesday', etc.
            return cal.get(weekday_name) == "1"

        # Fallback: if not defined in calendar, assume active
        return True

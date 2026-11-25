"""
Routing Service for FujiNova.
Orchestrates GTFS Bus Feeds, Fujikyu Railway Timetable, Footpaths, Fare Calculations,
and RAPTOR journey planning.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Set, Tuple

from backend.app.services.routing.transit_models import (
    TransitStop,
    TransitRoute,
    TransitTrip,
    TransitStopTime,
    Footpath,
    TransitMode,
    DataProvenance,
    JourneyLegSchema,
    JourneySchema,
    RouteSearchRequest,
    RouteSearchResponse,
    TransitStopSchema,
    NearbyStopSchema,
)
from backend.app.services.routing.gtfs_loader import (
    GTFSFeed,
    format_sec_to_time,
    parse_gtfs_time_to_sec,
    haversine_distance_meters,
)
from backend.app.services.routing.railway_timetable import get_railway_data
from backend.app.services.routing.fare_calculator import FareCalculator
from backend.app.services.routing.raptor import RaptorRouter

TOKYO_TZ = timezone(timedelta(hours=9))

# Well-known aliases and landmark mappings for tourists
TOURIST_LANDMARKS = {
    "chureito": "rail_shimoyoshida",
    "chureito pagoda": "rail_shimoyoshida",
    "忠霊塔": "rail_shimoyoshida",
    "新倉山浅間公園": "rail_shimoyoshida",
    "arakurayama": "rail_shimoyoshida",
    "arakurayama sengen park": "rail_shimoyoshida",
    "oishi": "1857_01",
    "oishi park": "1857_01",
    "大石公園": "1857_01",
    "河口湖自然生活館": "1857_01",
    "kawaguchiko natural living center": "1857_01",
    "natural living center": "1857_01",
    "kawaguchiko station": "0025_01",
    "河口湖駅": "0025_01",
    "kawaguchiko": "0025_01",
    "lake kawaguchiko": "0025_01",
    "fujisan station": "rail_fujisan",
    "富士山駅": "rail_fujisan",
    "mt fuji station": "rail_fujisan",
    "fujiyoshida": "rail_shimoyoshida",
    "富士吉田": "rail_shimoyoshida",
    "otsuki": "rail_otsuki",
    "otsuki station": "rail_otsuki",
    "大月駅": "rail_otsuki",
    "fuji-q": "rail_fujikyu_highland",
    "fuji-q highland": "rail_fujikyu_highland",
    "fujikyu highland": "rail_fujikyu_highland",
    "富士急ハイランド": "rail_fujikyu_highland",
}


class RoutingService:
    def __init__(self, gtfs_dir: str):
        self.gtfs_dir = gtfs_dir
        self.gtfs_feed = GTFSFeed(gtfs_dir)

        # Unified transit data
        self.stops: Dict[str, TransitStop] = {}
        self.routes: Dict[str, TransitRoute] = {}
        self.trips: Dict[str, TransitTrip] = {}
        self.trip_stop_times: Dict[str, List[TransitStopTime]] = {}
        self.stop_to_routes: Dict[str, Set[str]] = {}
        self.route_stops: Dict[str, List[str]] = {}
        self.footpaths: Dict[str, List[Footpath]] = {}

        self.fare_calculator: Optional[FareCalculator] = None
        self._is_initialized = False

    def initialize(self):
        """Loads and integrates Bus and Railway transit data."""
        if self._is_initialized:
            return

        # 1. Load Bus GTFS
        self.gtfs_feed.load()

        # Copy bus data to unified structures
        self.stops.update(self.gtfs_feed.stops)
        self.routes.update(self.gtfs_feed.routes)
        self.trips.update(self.gtfs_feed.trips)
        self.trip_stop_times.update(self.gtfs_feed.trip_stop_times)
        for sid, rids in self.gtfs_feed.stop_to_routes.items():
            self.stop_to_routes[sid] = set(rids)
        for rid, sids in self.gtfs_feed.route_stops.items():
            self.route_stops[rid] = list(sids)

        # 2. Load Railway Data (Fujisanroku Electric Railway, March 14, 2026 timetable revision)
        rail_stops, rail_routes, rail_trips, rail_st_times = get_railway_data()
        self.stops.update(rail_stops)
        self.routes.update(rail_routes)
        self.trips.update(rail_trips)
        self.trip_stop_times.update(rail_st_times)

        # Index railway routes
        for rid, r_obj in rail_routes.items():
            rail_trip_ids = [tid for tid, tr in rail_trips.items() if tr.route_id == rid]
            if rail_trip_ids:
                longest_tid = max(rail_trip_ids, key=lambda tid: len(rail_trips[tid].stops_sequence))
                self.route_stops[rid] = list(rail_trips[longest_tid].stops_sequence)
                for sid in self.route_stops[rid]:
                    if sid not in self.stop_to_routes:
                        self.stop_to_routes[sid] = set()
                    self.stop_to_routes[sid].add(rid)

        # 3. Generate Inter-modal Footpaths / Walking Connections
        self._generate_footpaths()

        # 4. Initialize Fare Calculator
        self.fare_calculator = FareCalculator(
            stops=self.stops,
            fare_attributes=self.gtfs_feed.fare_attributes,
            fare_rules=self.gtfs_feed.fare_rules,
        )

        self._is_initialized = True

    def _generate_footpaths(self):
        """Generates walking connections between railway stations and adjacent bus stops."""
        def add_bidirectional_footpath(st1: str, st2: str, dist_m: float, walk_sec: int):
            if st1 in self.stops and st2 in self.stops:
                existing_1 = [fp for fp in self.footpaths.get(st1, []) if fp.to_stop_id == st2]
                if not existing_1:
                    self.footpaths.setdefault(st1, []).append(
                        Footpath(from_stop_id=st1, to_stop_id=st2, walking_time_sec=walk_sec, distance_meters=dist_m)
                    )
                existing_2 = [fp for fp in self.footpaths.get(st2, []) if fp.to_stop_id == st1]
                if not existing_2:
                    self.footpaths.setdefault(st2, []).append(
                        Footpath(from_stop_id=st2, to_stop_id=st1, walking_time_sec=walk_sec, distance_meters=dist_m)
                    )

        # Specific major multimodal hubs:
        # Kawaguchiko Station: Rail Platform <-> Bus Terminal (30m, 120s transfer)
        add_bidirectional_footpath("rail_kawaguchiko", "0025_01", 30.0, 120)
        # Mt. Fuji (Fujisan) Station: Rail Platform <-> Bus Terminal (50m, 180s transfer)
        add_bidirectional_footpath("rail_fujisan", "0001_01", 50.0, 180)
        # Shimoyoshida Station: Rail Platform <-> Bus Stop (40m, 120s transfer)
        if "0003_02" in self.stops:
            add_bidirectional_footpath("rail_shimoyoshida", "0003_02", 40.0, 120)
        if "0003_01" in self.stops:
            add_bidirectional_footpath("rail_shimoyoshida", "0003_01", 40.0, 120)

        # Algorithmic proximity footpaths for stops within 250m (walking speed 1.1 m/s)
        # We index key stops to avoid O(N^2) over all 1500 stops
        key_stops = [s for s in self.stops.values() if s.is_railway or s.stop_id.startswith("0025") or s.stop_id.startswith("0001") or "周遊" in s.stop_name_ja]
        for i, s1 in enumerate(key_stops):
            for s2 in key_stops[i + 1:]:
                if s1.stop_id == s2.stop_id:
                    continue
                # If both are railway stations, no walking footpath
                if s1.is_railway and s2.is_railway:
                    continue
                d = haversine_distance_meters(s1.lat, s1.lon, s2.lat, s2.lon)
                if d <= 250.0:
                    walk_sec = max(60, int(d / 1.1))
                    add_bidirectional_footpath(s1.stop_id, s2.stop_id, d, walk_sec)

    def resolve_stop(self, query: str) -> Optional[TransitStop]:
        """Resolves user query string into a TransitStop."""
        if not self._is_initialized:
            self.initialize()

        q = query.strip()
        q_lower = q.lower()

        # 1. Direct Stop ID match
        if q in self.stops:
            return self.stops[q]

        # 2. Check well-known tourist landmarks
        if q_lower in TOURIST_LANDMARKS:
            target_id = TOURIST_LANDMARKS[q_lower]
            if target_id in self.stops:
                return self.stops[target_id]

        # 3. Exact match on Japanese or English stop name
        for s in self.stops.values():
            if q == s.stop_name_ja or q_lower == s.stop_name_en.lower():
                return s

        # 4. Partial substring match
        # Prioritize railway stations or major bus terminals
        candidates = []
        for s in self.stops.values():
            if q in s.stop_name_ja or q_lower in s.stop_name_en.lower():
                candidates.append(s)

        if candidates:
            # Sort: railway stations first, then shorter names
            candidates.sort(key=lambda s: (not s.is_railway, len(s.stop_name_ja)))
            return candidates[0]

        return None

    def search_routes(self, request: RouteSearchRequest) -> RouteSearchResponse:
        """Executes end-to-end route search and returns grounded response."""
        if not self._is_initialized:
            self.initialize()

        origin_stop = self.resolve_stop(request.origin)
        dest_stop = self.resolve_stop(request.destination)

        if not origin_stop:
            raise ValueError(f"Origin stop or landmark '{request.origin}' could not be identified.")
        if not dest_stop:
            raise ValueError(f"Destination stop or landmark '{request.destination}' could not be identified.")

        # Parse departure time and date in Asia/Tokyo
        now_tokyo = datetime.now(TOKYO_TZ)
        search_date_str = now_tokyo.strftime("%Y%m%d")
        departure_sec = now_tokyo.hour * 3600 + now_tokyo.minute * 60 + now_tokyo.second

        if request.departure_time:
            time_input = request.departure_time.strip()
            # Check if includes date
            if "T" in time_input or " " in time_input:
                try:
                    dt = datetime.fromisoformat(time_input.replace(" ", "T"))
                    search_date_str = dt.strftime("%Y%m%d")
                    departure_sec = dt.hour * 3600 + dt.minute * 60 + dt.second
                except ValueError:
                    pass
            elif ":" in time_input:
                # "HH:MM" or "HH:MM:SS"
                departure_sec = parse_gtfs_time_to_sec(time_input)

        # Filter active trips by calendar date
        active_trips: Set[str] = set()
        for tid, trip in self.trips.items():
            if trip.service_id.startswith("rail_"):
                # Railway daily service
                active_trips.add(tid)
            else:
                if self.gtfs_feed.is_service_active(trip.service_id, search_date_str):
                    active_trips.add(tid)

        # If no bus trips are active on this specific date (e.g. searching on weekend or off-season)
        # and no explicit departure_time was provided, use standard weekday timetable (2026-11-09 09:00:00)
        bus_active = sum(1 for tid in active_trips if not tid.startswith("rail_"))
        if bus_active == 0 and not request.departure_time:
            search_date_str = "20261109"
            departure_sec = 9 * 3600  # 09:00:00
            for tid, trip in self.trips.items():
                if not trip.service_id.startswith("rail_") and self.gtfs_feed.is_service_active(trip.service_id, search_date_str):
                    active_trips.add(tid)

        # Instantiate RAPTOR router with active trips
        router = RaptorRouter(
            stops=self.stops,
            routes=self.routes,
            trips=self.trips,
            trip_stop_times=self.trip_stop_times,
            stop_to_routes=self.stop_to_routes,
            route_stops=self.route_stops,
            footpaths=self.footpaths,
            active_trips_filter=active_trips,
        )

        raw_journeys = router.plan_journey(
            origin_stop_id=origin_stop.stop_id,
            dest_stop_id=dest_stop.stop_id,
            departure_time_sec=departure_sec,
            max_transfers=request.max_transfers,
        )

        # Check if we should search from connected hubs if no direct journey found
        # (e.g. if origin was rail station and bus stop was 30m away)
        if not raw_journeys:
            for fp in self.footpaths.get(origin_stop.stop_id, []):
                alt_raw = router.plan_journey(
                    origin_stop_id=fp.to_stop_id,
                    dest_stop_id=dest_stop.stop_id,
                    departure_time_sec=departure_sec + fp.walking_time_sec,
                    max_transfers=request.max_transfers,
                )
                if alt_raw:
                    for aj in alt_raw:
                        # Prepend walk leg
                        walk_leg = {
                            "type": "walk",
                            "from_stop_id": origin_stop.stop_id,
                            "to_stop_id": fp.to_stop_id,
                            "start_time_sec": departure_sec,
                            "end_time_sec": departure_sec + fp.walking_time_sec,
                            "duration_sec": fp.walking_time_sec,
                        }
                        aj["legs"].insert(0, walk_leg)
                        raw_journeys.append(aj)

        # Format journeys into schemas
        formatted_journeys: List[JourneySchema] = []
        for idx, rj in enumerate(raw_journeys[:request.max_results], start=1):
            schema_journey = self._build_journey_schema(
                journey_id=f"journey_{idx:02d}",
                raw_legs=rj["legs"],
                search_date_str=search_date_str,
            )
            if schema_journey:
                formatted_journeys.append(schema_journey)

        return RouteSearchResponse(
            origin=TransitStopSchema(
                stop_id=origin_stop.stop_id,
                stop_name_ja=origin_stop.stop_name_ja,
                stop_name_en=origin_stop.stop_name_en,
                lat=origin_stop.lat,
                lon=origin_stop.lon,
                is_railway=origin_stop.is_railway,
            ),
            destination=TransitStopSchema(
                stop_id=dest_stop.stop_id,
                stop_name_ja=dest_stop.stop_name_ja,
                stop_name_en=dest_stop.stop_name_en,
                lat=dest_stop.lat,
                lon=dest_stop.lon,
                is_railway=dest_stop.is_railway,
            ),
            query_departure_time=format_sec_to_time(departure_sec)[:5],
            search_date=search_date_str,
            journeys=formatted_journeys,
            total_journeys_found=len(formatted_journeys),
            generated_at=now_tokyo.isoformat(),
        )

    def _build_journey_schema(
        self,
        journey_id: str,
        raw_legs: List[dict],
        search_date_str: str,
    ) -> Optional[JourneySchema]:
        """Converts raw RAPTOR legs into a fully grounded JourneySchema with fares and badges."""
        if not raw_legs:
            return None

        legs_schemas: List[JourneyLegSchema] = []
        total_fare = 0
        has_unknown_fare = False
        badges: Set[str] = set()
        warnings: List[str] = []
        transfers_count = 0

        dt = datetime.strptime(search_date_str, "%Y%m%d")
        is_weekend = dt.weekday() >= 5

        for leg in raw_legs:
            leg_type = leg["type"]
            if leg_type == "walk":
                orig_s = self.stops[leg["from_stop_id"]]
                dest_s = self.stops[leg["to_stop_id"]]
                dur_min = max(1, leg["duration_sec"] // 60)
                dep_str = format_sec_to_time(leg["start_time_sec"])[:5]
                arr_str = format_sec_to_time(leg["end_time_sec"])[:5]

                legs_schemas.append(JourneyLegSchema(
                    mode=TransitMode.WALK,
                    operator="Walk",
                    route_short_name="Walk",
                    route_long_name=f"Walk {int(leg.get('duration_sec', 120) * 1.1)}m to {dest_s.stop_name_en}",
                    route_color="#757575",
                    route_text_color="#FFFFFF",
                    origin_stop_id=orig_s.stop_id,
                    origin_stop_name=orig_s.stop_name_ja,
                    origin_stop_name_en=orig_s.stop_name_en,
                    departure_time=dep_str,
                    departure_timestamp_sec=leg["start_time_sec"],
                    destination_stop_id=dest_s.stop_id,
                    destination_stop_name=dest_s.stop_name_ja,
                    destination_stop_name_en=dest_s.stop_name_en,
                    arrival_time=arr_str,
                    arrival_timestamp_sec=leg["end_time_sec"],
                    duration_minutes=dur_min,
                    intermediate_stops_count=0,
                    intermediate_stops=[],
                    fare_jpy=0,
                    provenance=DataProvenance.ESTIMATED,
                    provenance_badge="[Walking Connection]",
                ))
            elif leg_type == "transit":
                trip = self.trips[leg["trip_id"]]
                route = self.routes[trip.route_id]
                orig_s = self.stops[leg["board_stop_id"]]
                dest_s = self.stops[leg["alight_stop_id"]]

                dur_min = max(1, (leg["alight_time_sec"] - leg["board_time_sec"]) // 60)
                dep_str = format_sec_to_time(leg["board_time_sec"])[:5]
                arr_str = format_sec_to_time(leg["alight_time_sec"])[:5]

                # Intermediate stops
                trip_stops = trip.stops_sequence
                intermediate_names = []
                if orig_s.stop_id in trip_stops and dest_s.stop_id in trip_stops:
                    i1 = trip_stops.index(orig_s.stop_id)
                    i2 = trip_stops.index(dest_s.stop_id)
                    if i1 < i2:
                        for sid in trip_stops[i1 + 1: i2]:
                            if sid in self.stops:
                                intermediate_names.append(self.stops[sid].stop_name_en)

                # Fare calculation
                leg_fare = self.fare_calculator.calculate_leg_fare(
                    mode=route.mode,
                    origin_stop_id=orig_s.stop_id,
                    dest_stop_id=dest_s.stop_id,
                    route_id=route.route_id,
                )
                if leg_fare is not None:
                    total_fare += leg_fare
                else:
                    has_unknown_fare = True

                # Provenance and Operator
                if route.mode == TransitMode.RAIL:
                    operator_name = "Fujikyu Railway"
                    prov_badge = "[Fujikyu Railway Timetable (Rev. 2026-03-14)]"
                    badges.add(prov_badge)
                    advisory = "Operated by Fujisanroku Electric Railway. Otsuki station provides 5-min connection to JR Chuo Line."
                else:
                    operator_name = "Fujikyu Bus"
                    prov_badge = "[Official Fujikyu Bus GTFS-JP]"
                    badges.add(prov_badge)
                    advisory = None
                    if is_weekend:
                        advisory = "Weekend advisory: Bus may experience 10-15 min traffic delay along the lake."
                        if advisory not in warnings:
                            warnings.append(advisory)

                legs_schemas.append(JourneyLegSchema(
                    mode=route.mode,
                    operator=operator_name,
                    route_id=route.route_id.split("_p")[0],
                    route_short_name=route.route_short_name or ("Red Line" if route.route_color == "#E60012" else route.route_id.split("_p")[0]),
                    route_long_name=route.route_long_name,
                    route_color=route.route_color,
                    route_text_color=route.route_text_color,
                    trip_headsign=trip.trip_headsign,
                    origin_stop_id=orig_s.stop_id,
                    origin_stop_name=orig_s.stop_name_ja,
                    origin_stop_name_en=orig_s.stop_name_en,
                    departure_time=dep_str,
                    departure_timestamp_sec=leg["board_time_sec"],
                    destination_stop_id=dest_s.stop_id,
                    destination_stop_name=dest_s.stop_name_ja,
                    destination_stop_name_en=dest_s.stop_name_en,
                    arrival_time=arr_str,
                    arrival_timestamp_sec=leg["alight_time_sec"],
                    duration_minutes=dur_min,
                    intermediate_stops_count=len(intermediate_names),
                    intermediate_stops=intermediate_names,
                    fare_jpy=leg_fare,
                    provenance=route.provenance,
                    provenance_badge=prov_badge,
                    advisory_notes=advisory,
                ))

        # Count vehicle transfers (transit legs - 1)
        transit_legs_count = sum(1 for l in legs_schemas if l.mode != TransitMode.WALK)
        transfers_count = max(0, transit_legs_count - 1)

        first_leg = legs_schemas[0]
        last_leg = legs_schemas[-1]
        total_duration = max(1, (last_leg.arrival_timestamp_sec - first_leg.departure_timestamp_sec) // 60)

        return JourneySchema(
            journey_id=journey_id,
            departure_time=first_leg.departure_time,
            arrival_time=last_leg.arrival_time,
            total_duration_minutes=total_duration,
            transfers_count=transfers_count,
            total_fare_jpy=None if has_unknown_fare else total_fare,
            legs=legs_schemas,
            provenance_badges=list(badges),
            warnings=warnings,
        )

    def find_nearby_stops(
        self,
        lat: float,
        lon: float,
        max_distance_meters: float = 2000.0,
        limit: int = 5
    ) -> List[NearbyStopSchema]:
        """Finds closest transit stops and railway stations to the given coordinates."""
        if not self._is_initialized:
            self.initialize()

        scored = []
        for stop in self.stops.values():
            d = haversine_distance_meters(lat, lon, stop.lat, stop.lon)
            if d <= max_distance_meters:
                walk_sec = max(30, int(d / 1.1))
                scored.append((d, stop, walk_sec))

        scored.sort(key=lambda x: x[0])
        results: List[NearbyStopSchema] = []
        seen_names = set()
        for d, stop, walk_sec in scored:
            name_key = stop.stop_name_ja
            if name_key in seen_names and len(scored) > limit:
                continue
            seen_names.add(name_key)
            results.append(NearbyStopSchema(
                stop_id=stop.stop_id,
                stop_name_ja=stop.stop_name_ja,
                stop_name_en=stop.stop_name_en,
                lat=stop.lat,
                lon=stop.lon,
                distance_meters=round(d, 1),
                walking_time_seconds=walk_sec,
                is_railway=stop.is_railway,
            ))
            if len(results) >= limit:
                break
        return results

    def search_route_from_location(
        self,
        user_lat: float,
        user_lon: float,
        destination_query: str,
        departure_time_str: Optional[str] = None,
        max_transfers: int = 2,
        max_results: int = 3
    ) -> RouteSearchResponse:
        """Calculates route from user's current GPS location to destination."""
        if not self._is_initialized:
            self.initialize()

        nearby = self.find_nearby_stops(user_lat, user_lon, max_distance_meters=3000.0, limit=3)
        if not nearby:
            nearby = self.find_nearby_stops(user_lat, user_lon, max_distance_meters=20000.0, limit=1)
        if not nearby:
            raise ValueError("No verified Fujikyu transit stops found near your location.")

        closest_stop = nearby[0]
        walk_to_stop_sec = closest_stop.walking_time_seconds
        walk_to_stop_dist = closest_stop.distance_meters

        now = datetime.now(TOKYO_TZ)
        if departure_time_str:
            dep_sec = parse_gtfs_time_to_sec(departure_time_str.split(" ")[-1])
        else:
            dep_sec = now.hour * 3600 + now.minute * 60 + now.second

        board_time_sec = dep_sec + walk_to_stop_sec
        board_time_str = format_sec_to_time(board_time_sec)

        req = RouteSearchRequest(
            origin=closest_stop.stop_id,
            destination=destination_query,
            departure_time=board_time_str,
            max_transfers=max_transfers,
            max_results=max_results
        )
        base_response = self.search_routes(req)

        enhanced_journeys: List[JourneySchema] = []
        for j in base_response.journeys:
            walk_leg = JourneyLegSchema(
                mode=TransitMode.WALK,
                operator="Walking",
                route_id="walk_origin",
                route_short_name="Walk",
                route_long_name=f"Walk to {closest_stop.stop_name_en}",
                route_color="#64748B",
                route_text_color="#FFFFFF",
                trip_headsign=closest_stop.stop_name_ja,
                origin_stop_id="current_location",
                origin_stop_name="現在地",
                origin_stop_name_en="Your Current Location",
                departure_time=format_sec_to_time(dep_sec),
                departure_timestamp_sec=dep_sec,
                destination_stop_id=closest_stop.stop_id,
                destination_stop_name=closest_stop.stop_name_ja,
                destination_stop_name_en=closest_stop.stop_name_en,
                arrival_time=board_time_str,
                arrival_timestamp_sec=board_time_sec,
                duration_minutes=max(1, walk_to_stop_sec // 60),
                intermediate_stops_count=0,
                intermediate_stops=[],
                fare_jpy=0,
                provenance=DataProvenance.CALCULATED,
                provenance_badge="Verified GPS Walk",
                advisory_notes=f"Walk {round(walk_to_stop_dist)}m ({max(1, walk_to_stop_sec // 60)} min) to boarding stop.",
            )
            new_legs = [walk_leg] + j.legs
            new_duration = j.total_duration_minutes + max(1, walk_to_stop_sec // 60)
            enhanced_j = j.model_copy(update={
                "departure_time": format_sec_to_time(dep_sec),
                "total_duration_minutes": new_duration,
                "legs": new_legs
            })
            enhanced_journeys.append(enhanced_j)

        user_origin_schema = TransitStopSchema(
            stop_id="current_location",
            stop_name_ja="現在地",
            stop_name_en="Your Current Location",
            lat=user_lat,
            lon=user_lon,
            is_railway=False
        )

        return base_response.model_copy(update={
            "origin": user_origin_schema,
            "journeys": enhanced_journeys,
            "total_journeys_found": len(enhanced_journeys)
        })


# Global singleton instance for application reuse
_routing_service_instance: Optional[RoutingService] = None

def get_routing_service() -> RoutingService:
    global _routing_service_instance
    if _routing_service_instance is None:
        gtfs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../data/gtfs/fujikyu_bus"))
        _routing_service_instance = RoutingService(gtfs_dir=gtfs_dir)
        _routing_service_instance.initialize()
    return _routing_service_instance

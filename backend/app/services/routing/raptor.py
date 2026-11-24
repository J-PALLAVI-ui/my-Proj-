"""
RAPTOR: Round-Based Public Transit Routing Engine for FujiNova.
Implements the multi-criteria bicriteria RAPTOR algorithm (Earliest Arrival Time & Number of Transfers).
Operates over unified GTFS Bus feeds and Fujikyu Railway timetable with walking transfer footpaths.
"""
from __future__ import annotations

from dataclasses import dataclass
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
)
from backend.app.services.routing.gtfs_loader import format_sec_to_time


@dataclass
class BoardingParent:
    trip_id: str
    board_stop_id: str
    board_time_sec: int
    alight_stop_id: str
    alight_time_sec: int


@dataclass
class FootpathParent:
    from_stop_id: str
    to_stop_id: str
    start_time_sec: int
    end_time_sec: int
    duration_sec: int


class RaptorRouter:
    def __init__(
        self,
        stops: Dict[str, TransitStop],
        routes: Dict[str, TransitRoute],
        trips: Dict[str, TransitTrip],
        trip_stop_times: Dict[str, List[TransitStopTime]],
        stop_to_routes: Dict[str, Set[str]],
        route_stops: Dict[str, List[str]],
        footpaths: Dict[str, List[Footpath]],
        active_trips_filter: Optional[Set[str]] = None,
    ):
        self.stops = stops
        self.routes = routes
        self.trips = trips
        self.trip_stop_times = trip_stop_times
        self.stop_to_routes = stop_to_routes
        self.route_stops = route_stops
        self.footpaths = footpaths
        self.active_trips_filter = active_trips_filter

        # Precompute trip stop times index: trip_id -> stop_id -> TransitStopTime
        self._trip_stop_map: Dict[str, Dict[str, TransitStopTime]] = {}
        for tid, st_list in self.trip_stop_times.items():
            self._trip_stop_map[tid] = {st.stop_id: st for st in st_list}

        # Precompute sorted trips for each route by departure time at the route's first stop
        self._route_sorted_trips: Dict[str, List[str]] = {}
        for rid, trip_ids in self.routes.items():
            valid_tids = [tid for tid in self.trips if self.trips[tid].route_id == rid]
            if self.active_trips_filter is not None:
                valid_tids = [tid for tid in valid_tids if tid in self.active_trips_filter]

            # Sort by departure time of their first stop
            def first_dep(tid: str) -> int:
                st_list = self.trip_stop_times.get(tid, [])
                return st_list[0].departure_time_sec if st_list else 99999999

            valid_tids.sort(key=first_dep)
            self._route_sorted_trips[rid] = valid_tids

    def plan_journey(
        self,
        origin_stop_id: str,
        dest_stop_id: str,
        departure_time_sec: int,
        max_transfers: int = 2,
    ) -> List[dict]:
        """
        Executes RAPTOR algorithm from origin_stop_id to dest_stop_id.
        Returns raw journey representations for each Pareto-optimal round.
        """
        if origin_stop_id not in self.stops or dest_stop_id not in self.stops:
            return []

        if origin_stop_id == dest_stop_id:
            return []

        # Rounds up to max_transfers + 1 (Round 0 is 0 transfers / initial, Round 1 is 0 transfers trip, Round 2 is 1 transfer, etc.)
        max_rounds = max_transfers + 1

        # tau[k][stop_id] -> earliest arrival time in round k
        INF = 999999999
        tau: List[Dict[str, int]] = [{} for _ in range(max_rounds + 1)]
        tau_star: Dict[str, int] = {sid: INF for sid in self.stops}

        for k in range(max_rounds + 1):
            for sid in self.stops:
                tau[k][sid] = INF

        # Parents for back-tracing: parent[k][stop_id]
        parents: List[Dict[str, Optional[BoardingParent]]] = [{} for _ in range(max_rounds + 1)]
        footpath_parents: List[Dict[str, Optional[FootpathParent]]] = [{} for _ in range(max_rounds + 1)]

        # Initialize Round 0
        tau[0][origin_stop_id] = departure_time_sec
        tau_star[origin_stop_id] = departure_time_sec

        # Apply immediate walking transfers from origin in Round 0
        marked_stops: Set[str] = {origin_stop_id}
        for fp in self.footpaths.get(origin_stop_id, []):
            arr = departure_time_sec + fp.walking_time_sec
            if arr < tau[0][fp.to_stop_id]:
                tau[0][fp.to_stop_id] = arr
                tau_star[fp.to_stop_id] = arr
                footpath_parents[0][fp.to_stop_id] = FootpathParent(
                    from_stop_id=origin_stop_id,
                    to_stop_id=fp.to_stop_id,
                    start_time_sec=departure_time_sec,
                    end_time_sec=arr,
                    duration_sec=fp.walking_time_sec,
                )
                marked_stops.add(fp.to_stop_id)

        # Main RAPTOR Rounds
        for k in range(1, max_rounds + 1):
            # Copy arrival times from previous round
            for sid in self.stops:
                tau[k][sid] = tau[k - 1][sid]

            # Step 1: Accumulate routes serving marked stops
            routes_to_scan: Dict[str, str] = {}  # route_id -> earliest marked stop_id along this route
            for stop_id in marked_stops:
                for rid in self.stop_to_routes.get(stop_id, set()):
                    r_stops = self.route_stops.get(rid, [])
                    if stop_id not in r_stops:
                        continue
                    if rid not in routes_to_scan:
                        routes_to_scan[rid] = stop_id
                    else:
                        cur_earliest = routes_to_scan[rid]
                        if r_stops.index(stop_id) < r_stops.index(cur_earliest):
                            routes_to_scan[rid] = stop_id

            marked_stops = set()

            # Step 2: Scan each route
            for rid, earliest_stop in routes_to_scan.items():
                r_stops = self.route_stops.get(rid, [])
                if earliest_stop not in r_stops:
                    continue

                start_idx = r_stops.index(earliest_stop)
                cur_trip_id: Optional[str] = None
                board_stop_id: Optional[str] = None
                board_time_sec: int = 0

                for i in range(start_idx, len(r_stops)):
                    stop_p = r_stops[i]

                    # 1. Alighting check: if currently on a trip, update arrival time at stop_p
                    if cur_trip_id is not None:
                        st = self._trip_stop_map.get(cur_trip_id, {}).get(stop_p)
                        if st is not None:
                            arr_time = st.arrival_time_sec
                            if arr_time < min(tau_star[stop_p], tau_star[dest_stop_id]):
                                tau[k][stop_p] = arr_time
                                tau_star[stop_p] = arr_time
                                parents[k][stop_p] = BoardingParent(
                                    trip_id=cur_trip_id,
                                    board_stop_id=board_stop_id,
                                    board_time_sec=board_time_sec,
                                    alight_stop_id=stop_p,
                                    alight_time_sec=arr_time,
                                )
                                marked_stops.add(stop_p)

                    # 2. Boarding check: can we board an earlier or new trip at stop_p?
                    prev_arr = tau[k - 1].get(stop_p, INF)
                    if prev_arr < INF:
                        # Find earliest trip departing stop_p >= prev_arr (with minimum transfer buffer 60s if transferring)
                        min_dep = prev_arr if k == 1 and stop_p == origin_stop_id else prev_arr + 60

                        candidate_trip = self._find_earliest_trip(rid, stop_p, min_dep)
                        if candidate_trip is not None:
                            # If we don't have a trip yet, or if candidate trip departs stop_p earlier/better
                            cand_st = self._trip_stop_map[candidate_trip][stop_p]
                            if cur_trip_id is None:
                                cur_trip_id = candidate_trip
                                board_stop_id = stop_p
                                board_time_sec = cand_st.departure_time_sec
                            else:
                                cur_st = self._trip_stop_map[cur_trip_id].get(stop_p)
                                if cur_st and cand_st.departure_time_sec < cur_st.departure_time_sec:
                                    cur_trip_id = candidate_trip
                                    board_stop_id = stop_p
                                    board_time_sec = cand_st.departure_time_sec

            # Step 3: Walking transfers / footpaths for stops marked in this round
            footpath_marked = set()
            for stop_id in marked_stops:
                base_time = tau[k][stop_id]
                for fp in self.footpaths.get(stop_id, []):
                    arr_walk = base_time + fp.walking_time_sec
                    if arr_walk < tau[k].get(fp.to_stop_id, INF):
                        tau[k][fp.to_stop_id] = arr_walk
                        tau_star[fp.to_stop_id] = min(tau_star[fp.to_stop_id], arr_walk)
                        footpath_parents[k][fp.to_stop_id] = FootpathParent(
                            from_stop_id=stop_id,
                            to_stop_id=fp.to_stop_id,
                            start_time_sec=base_time,
                            end_time_sec=arr_walk,
                            duration_sec=fp.walking_time_sec,
                        )
                        footpath_marked.add(fp.to_stop_id)

            marked_stops.update(footpath_marked)
            if not marked_stops:
                break

        # Reconstruct journeys from destination for each round
        raw_journeys = []
        seen_arrival_times = set()

        for k in range(1, max_rounds + 1):
            arr_time = tau[k].get(dest_stop_id, INF)
            if arr_time < INF:
                # Only if this round actually has an entry reaching dest
                if parents[k].get(dest_stop_id) is None and footpath_parents[k].get(dest_stop_id) is None:
                    continue

                if arr_time in seen_arrival_times:
                    continue

                journey_legs = self._reconstruct_journey(
                    origin_stop_id, dest_stop_id, k, parents, footpath_parents, tau
                )
                if journey_legs and self._validate_journey_causality(journey_legs):
                    seen_arrival_times.add(arr_time)
                    raw_journeys.append({
                        "round": k,
                        "arrival_time_sec": arr_time,
                        "legs": journey_legs,
                    })

        # Sort journeys by arrival time, then by number of legs
        raw_journeys.sort(key=lambda j: (j["arrival_time_sec"], len(j["legs"])))
        return raw_journeys

    def _validate_journey_causality(self, legs: List[dict]) -> bool:
        """Ensures all legs are chronologically valid and connected."""
        if not legs:
            return False
        for i, leg in enumerate(legs):
            dep = leg.get("board_time_sec", leg.get("start_time_sec", 0))
            arr = leg.get("alight_time_sec", leg.get("end_time_sec", 0))
            if arr < dep:
                return False
            if i > 0:
                prev_leg = legs[i - 1]
                prev_arr = prev_leg.get("alight_time_sec", prev_leg.get("end_time_sec", 0))
                if dep < prev_arr:
                    return False
        return True

    def _find_earliest_trip(self, route_id: str, stop_id: str, min_departure_sec: int) -> Optional[str]:
        """Finds the earliest trip on route_id departing stop_id >= min_departure_sec."""
        for tid in self._route_sorted_trips.get(route_id, []):
            st = self._trip_stop_map.get(tid, {}).get(stop_id)
            if st is not None and st.departure_time_sec >= min_departure_sec:
                return tid
        return None

    def _reconstruct_journey(
        self,
        origin_stop_id: str,
        dest_stop_id: str,
        target_round: int,
        parents: List[Dict[str, Optional[BoardingParent]]],
        footpath_parents: List[Dict[str, Optional[FootpathParent]]],
        tau: List[Dict[str, int]],
    ) -> List[dict]:
        """Backtraces through round parents to construct ordered journey legs."""
        legs = []
        cur_stop = dest_stop_id
        cur_k = target_round

        while cur_k > 0 and cur_stop != origin_stop_id:
            # Check if arrival was via footpath in cur_k
            fp = footpath_parents[cur_k].get(cur_stop)
            if fp is not None:
                legs.append({
                    "type": "walk",
                    "from_stop_id": fp.from_stop_id,
                    "to_stop_id": fp.to_stop_id,
                    "start_time_sec": fp.start_time_sec,
                    "end_time_sec": fp.end_time_sec,
                    "duration_sec": fp.duration_sec,
                })
                cur_stop = fp.from_stop_id

            # Find the round r <= cur_k that brought us to cur_stop via transit
            target_arr = tau[cur_k].get(cur_stop)
            found_round = None
            for r in range(cur_k, 0, -1):
                bp_cand = parents[r].get(cur_stop)
                if bp_cand is not None and bp_cand.alight_time_sec == target_arr:
                    found_round = r
                    break

            if found_round is not None:
                bp = parents[found_round][cur_stop]
                legs.append({
                    "type": "transit",
                    "trip_id": bp.trip_id,
                    "board_stop_id": bp.board_stop_id,
                    "board_time_sec": bp.board_time_sec,
                    "alight_stop_id": bp.alight_stop_id,
                    "alight_time_sec": bp.alight_time_sec,
                })
                cur_stop = bp.board_stop_id
                cur_k = found_round - 1
            else:
                cur_k -= 1

        # Check Round 0 footpath from origin if any
        if cur_stop != origin_stop_id:
            fp0 = footpath_parents[0].get(cur_stop)
            if fp0 is not None and fp0.from_stop_id == origin_stop_id:
                legs.append({
                    "type": "walk",
                    "from_stop_id": fp0.from_stop_id,
                    "to_stop_id": fp0.to_stop_id,
                    "start_time_sec": fp0.start_time_sec,
                    "end_time_sec": fp0.end_time_sec,
                    "duration_sec": fp0.duration_sec,
                })
                cur_stop = origin_stop_id

        legs.reverse()
        return legs

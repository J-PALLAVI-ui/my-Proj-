"""
Deterministic Transit Fare Calculator for FujiNova.
Calculates exact adult one-way fares using official GTFS fare_rules.txt / fare_attributes.txt
and the verified Fujikyu Railway tariff matrix (March 14, 2026 revision).
Strict Zero-Hallucination rule: Never invent a fare if data is missing.
"""
from __future__ import annotations

from typing import Dict, List, Optional
from backend.app.services.routing.transit_models import TransitMode, TransitStop
from backend.app.services.routing.railway_timetable import calculate_railway_fare


class FareCalculator:
    def __init__(
        self,
        stops: Dict[str, TransitStop],
        fare_attributes: Dict[str, int],
        fare_rules: List[Dict[str, str]],
    ):
        self.stops = stops
        self.fare_attributes = fare_attributes
        self.fare_rules = fare_rules

        # Fast lookup map: (route_id, origin_zone, dest_zone) -> price
        # and fallback (origin_zone, dest_zone) -> price
        self.route_zone_fare_map: Dict[tuple, int] = {}
        self.zone_fare_map: Dict[tuple, int] = {}

        self._index_fare_rules()

    def _index_fare_rules(self):
        for rule in self.fare_rules:
            fare_id = rule.get("fare_id")
            price = self.fare_attributes.get(fare_id)
            if price is None:
                continue

            orig = rule.get("origin_id")
            dest = rule.get("destination_id")
            route_id = rule.get("route_id")

            if orig and dest:
                if route_id:
                    self.route_zone_fare_map[(route_id, orig, dest)] = price
                if (orig, dest) not in self.zone_fare_map:
                    self.zone_fare_map[(orig, dest)] = price

    def calculate_leg_fare(
        self,
        mode: TransitMode,
        origin_stop_id: str,
        dest_stop_id: str,
        route_id: Optional[str] = None,
    ) -> Optional[int]:
        """
        Calculates exact adult one-way fare for a single journey leg.
        Returns integer JPY fare, or None if unavailable/not applicable.
        """
        if mode == TransitMode.WALK:
            return 0

        if mode == TransitMode.RAIL:
            return calculate_railway_fare(origin_stop_id, dest_stop_id)

        if mode == TransitMode.BUS:
            orig_stop = self.stops.get(origin_stop_id)
            dest_stop = self.stops.get(dest_stop_id)
            if not orig_stop or not dest_stop:
                return None

            orig_zone = orig_stop.zone_id or origin_stop_id
            dest_zone = dest_stop.zone_id or dest_stop_id

            # Normalize route_id if pattern suffix exists
            base_route_id = route_id.split("_p")[0] if route_id else None

            # 1. Exact match with route_id and zones
            if base_route_id and (base_route_id, orig_zone, dest_zone) in self.route_zone_fare_map:
                return self.route_zone_fare_map[(base_route_id, orig_zone, dest_zone)]

            # 2. Match with zones across all routes
            if (orig_zone, dest_zone) in self.zone_fare_map:
                return self.zone_fare_map[(orig_zone, dest_zone)]

            # 3. Check symmetric reverse zone (bus fares in Japan are usually symmetric)
            if (dest_zone, orig_zone) in self.zone_fare_map:
                return self.zone_fare_map[(dest_zone, orig_zone)]

            # If origin and destination are identical stop or zone
            if orig_zone == dest_zone:
                return 0

            # Fare rule not present in GTFS feed
            return None

        return None

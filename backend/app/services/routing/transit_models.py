"""
Transit Data Models for FujiNova Deterministic Routing Engine.
Defines core data structures for stops, routes, trips, timetables, journeys, and API schemas.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


class TransitMode(str, Enum):
    BUS = "bus"
    RAIL = "rail"
    WALK = "walk"


class DataProvenance(str, Enum):
    STATIC = "STATIC"  # Official static GTFS-JP feed
    REALTIME = "REALTIME"  # Live feed (GTFS-RT)
    MANUALLY_TRANSCRIBED = "MANUALLY_TRANSCRIBED"  # Verified official timetable (e.g. Fujikyu Rail Rev. 2026-03-14)
    ESTIMATED = "ESTIMATED"  # Algorithmic buffer / walking calculation


@dataclass
class TransitStop:
    stop_id: str
    stop_name_ja: str
    stop_name_en: str
    lat: float
    lon: float
    zone_id: Optional[str] = None
    is_railway: bool = False
    parent_station: Optional[str] = None


@dataclass
class TransitRoute:
    route_id: str
    agency_id: str
    route_short_name: str
    route_long_name: str
    route_color: str  # Hex format, e.g. #E60012
    route_text_color: str  # Hex format, e.g. #FFFFFF
    mode: TransitMode = TransitMode.BUS
    provenance: DataProvenance = DataProvenance.STATIC


@dataclass
class TransitTrip:
    trip_id: str
    route_id: str
    service_id: str
    trip_headsign: str
    direction_id: int = 0
    stops_sequence: List[str] = field(default_factory=list)  # list of stop_ids in order


@dataclass
class TransitStopTime:
    trip_id: str
    stop_id: str
    arrival_time_sec: int  # Seconds since midnight (can be >= 86400 for late night)
    departure_time_sec: int  # Seconds since midnight
    stop_sequence: int


@dataclass
class Footpath:
    from_stop_id: str
    to_stop_id: str
    walking_time_sec: int
    distance_meters: float


# Pydantic Schemas for API & Agent Integration

class JourneyLegSchema(BaseModel):
    mode: TransitMode = Field(..., description="Transit mode: bus, rail, or walk")
    operator: str = Field(..., description="Operating company name (e.g. Fujikyu Bus, Fujikyu Railway, Walk)")
    route_id: Optional[str] = Field(None, description="Official GTFS or internal route ID")
    route_short_name: Optional[str] = Field(None, description="Route code or line abbreviation (e.g. Red Line)")
    route_long_name: Optional[str] = Field(None, description="Official route long name")
    route_color: str = Field("#757575", description="Official line color hex (e.g. #E60012 for Red Line)")
    route_text_color: str = Field("#FFFFFF", description="Official line text color hex")
    trip_headsign: Optional[str] = Field(None, description="Direction or destination headsign")

    origin_stop_id: str = Field(..., description="Departure stop or station ID")
    origin_stop_name: str = Field(..., description="Departure stop name in Japanese")
    origin_stop_name_en: str = Field(..., description="Departure stop name in English")
    departure_time: str = Field(..., description="Scheduled departure time in HH:MM or HH:MM:SS (Asia/Tokyo)")
    departure_timestamp_sec: int = Field(..., description="Departure seconds from midnight")

    destination_stop_id: str = Field(..., description="Arrival stop or station ID")
    destination_stop_name: str = Field(..., description="Arrival stop name in Japanese")
    destination_stop_name_en: str = Field(..., description="Arrival stop name in English")
    arrival_time: str = Field(..., description="Scheduled arrival time in HH:MM or HH:MM:SS (Asia/Tokyo)")
    arrival_timestamp_sec: int = Field(..., description="Arrival seconds from midnight")

    duration_minutes: int = Field(..., description="Duration of this leg in minutes")
    intermediate_stops_count: int = Field(0, description="Number of intermediate stops passed")
    intermediate_stops: List[str] = Field(default_factory=list, description="List of intermediate stop names")

    fare_jpy: Optional[int] = Field(None, description="One-way adult fare in JPY (None if free walk or unknown)")
    provenance: DataProvenance = Field(..., description="Data provenance tier")
    provenance_badge: str = Field(..., description="Human-readable provenance tag")
    advisory_notes: Optional[str] = Field(None, description="Special notes, e.g. road traffic buffer, Otsuki connection")


class JourneySchema(BaseModel):
    journey_id: str = Field(..., description="Unique journey identifier")
    departure_time: str = Field(..., description="First departure time in HH:MM")
    arrival_time: str = Field(..., description="Final arrival time in HH:MM")
    total_duration_minutes: int = Field(..., description="Total journey duration in minutes")
    transfers_count: int = Field(0, description="Number of transfers between vehicles")
    total_fare_jpy: Optional[int] = Field(None, description="Total adult fare in JPY (None if incomplete fare data)")
    legs: List[JourneyLegSchema] = Field(..., description="Ordered list of journey legs")
    provenance_badges: List[str] = Field(default_factory=list, description="Unique data sources used in this journey")
    warnings: List[str] = Field(default_factory=list, description="Advisories (e.g. transfer buffers, weekend road traffic)")


class RouteSearchRequest(BaseModel):
    origin: str = Field(..., description="Origin stop name, station name, or ID (e.g. 'Kawaguchiko Station' or '河口湖駅')")
    destination: str = Field(..., description="Destination stop name, station name, or ID (e.g. 'Oishi Park' or '河口湖自然生活館')")
    departure_time: Optional[str] = Field(
        None,
        description="Departure time in ISO format or 'YYYY-MM-DD HH:MM:SS' or 'HH:MM'. Defaults to current Asia/Tokyo time."
    )
    max_transfers: int = Field(2, ge=0, le=4, description="Maximum number of vehicle transfers allowed")
    max_results: int = Field(3, ge=1, le=10, description="Maximum number of route alternatives to return")


class TransitStopSchema(BaseModel):
    stop_id: str
    stop_name_ja: str
    stop_name_en: str
    lat: float
    lon: float
    is_railway: bool


class RouteSearchResponse(BaseModel):
    origin: TransitStopSchema
    destination: TransitStopSchema
    query_departure_time: str
    search_date: str
    journeys: List[JourneySchema]
    total_journeys_found: int
    generated_at: str
    disclaimer: str = (
        "Timetables are grounded in official Fujikyu Bus GTFS-JP feeds and "
        "Fujikyu Railway Official Timetable (Rev. March 14, 2026). "
        "Actual bus arrivals may vary due to weekend road conditions."
    )

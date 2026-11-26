"""Tests for the dynamic Discovery / Route / Timetable / Recalibration engine (Scenarios A-F)."""
import pytest
from fastapi.testclient import TestClient

KAWA = dict(origin_lat=35.4981, origin_lon=138.7690, origin_name="Kawaguchiko Station")
FUJISAN = dict(origin_lat=35.4839, origin_lon=138.7958, origin_name="Fujisan Station")
SHINJUKU = dict(origin_lat=35.6909, origin_lon=139.7003, origin_name="Tokyo Shinjuku")


def rec(client, **kw):
    r = client.get("/api/v1/discovery/recommend", params=kw)
    assert r.status_code == 200, r.text
    return r.json()


def ids(resp):
    return [i["place_id"] for i in resp["items"]]


def test_counts_match_database(client: TestClient):
    from backend.app.services.discovery import discovery_service as ds
    d = rec(client, **KAWA, mode="walk", max_km=5, view="catalogue", page_size=60)
    c = ds.catalogue_counts()
    assert d["counts"]["total"] == c["total"] >= 235
    assert d["counts"]["famous"] + d["counts"]["hidden_gems"] == c["total"]


def test_catalogue_never_narrowed_by_mode_or_distance(client: TestClient):
    walk = rec(client, **KAWA, mode="walk", max_km=1, view="catalogue", page_size=60)
    bus = rec(client, **KAWA, mode="fujikyu_bus", max_km=50, view="catalogue", page_size=60)
    assert walk["counts"]["showing"] == bus["counts"]["showing"] == walk["counts"]["total"]


def test_catalogue_pagination_covers_every_destination_once(client: TestClient):
    seen = []
    first = rec(client, **KAWA, view="catalogue", page_size=40, page=1)
    pages = first["total_pages"]
    for p in range(1, pages + 1):
        seen += ids(rec(client, **KAWA, view="catalogue", page_size=40, page=p))
    assert len(seen) == len(set(seen)) == first["counts"]["total"]


def test_catalogue_search_spans_all_records(client: TestClient):
    d = rec(client, **KAWA, view="catalogue", q="Oishi", page_size=60)
    assert any("oishi" in i["place_id"] for i in d["items"])
    gems = rec(client, **KAWA, view="catalogue", discovery_type="HIDDEN_GEM", page_size=60)
    assert gems["counts"]["matching_filters"] == gems["counts"]["hidden_gems"]


def test_station_change_changes_recommendations(client: TestClient):
    a = rec(client, **KAWA, mode="walk", max_km=5, page_size=60)
    b = rec(client, **FUJISAN, mode="walk", max_km=5, page_size=60)
    assert ids(a) != ids(b)
    assert len(a["items"]) > 2


def test_distance_change_changes_recommendations(client: TestClient):
    a = rec(client, **KAWA, mode="walk", max_km=1, page_size=60)
    b = rec(client, **KAWA, mode="walk", max_km=10, page_size=60)
    assert b["counts"]["recommended"] > a["counts"]["recommended"]
    assert set(ids(a)) <= set(ids(b))


def test_mode_change_changes_recommendations(client: TestClient):
    walk = rec(client, **KAWA, mode="walk", max_km=5, page_size=60)
    bike = rec(client, **KAWA, mode="bike", max_km=5, page_size=60)
    bus = rec(client, **KAWA, mode="fujikyu_bus", max_km=20, page_size=60)
    train = rec(client, **KAWA, mode="train", max_km=50, page_size=60)
    assert len({walk["counts"]["recommended"], bike["counts"]["recommended"], bus["counts"]["recommended"], train["counts"]["recommended"]}) >= 3
    assert "Fujikyu Bus" in bus["explanation"] and "Kawaguchiko Station" in bus["explanation"]
    assert all(i["reachable"] for i in bus["items"])


def test_walking_distance_is_estimate_labelled_and_above_direct(client: TestClient):
    d = rec(client, **KAWA, mode="walk", max_km=5, page_size=60)
    for i in d["items"]:
        assert i["travel_km"] >= i["direct_km"]
        assert i["distance_basis"].startswith("ESTIMATED")
        assert i["travel_km"] <= 5.0 + 1e-6


def test_bike_rental_not_claimed(client: TestClient):
    d = rec(client, **KAWA, mode="bike", max_km=10, page_size=5)
    assert d["items"][0]["bike_rental"]["status"] == "NO_VERIFIED_DATA"


def test_bus_recommendations_have_gtfs_details(client: TestClient):
    d = rec(client, **KAWA, mode="fujikyu_bus", max_km=20, page_size=12)
    with_service = [i for i in d["items"] if i["transit"].get("service_on_date")]
    assert with_service, "expected at least one place with a scheduled service"
    for i in with_service:
        assert i["transit"]["time_type"] == "SCHEDULED"
        assert i["travel_minutes"] and i["travel_minutes"] > 0


def test_train_mode_only_uses_rail(client: TestClient):
    d = rec(client, **KAWA, mode="train", max_km=50, page_size=60)
    r = client.get("/api/v1/discovery/route", params=dict(**{k: v for k, v in KAWA.items()}, place_id=d["items"][0]["place_id"], mode="train")) if d["items"] else None
    if r is not None and r.json().get("available"):
        kinds = {s["kind"] for s in r.json()["segments"]}
        assert kinds <= {"walk", "rail"}


def test_every_item_has_reason_in_recommended(client: TestClient):
    d = rec(client, **KAWA, mode="walk", max_km=10, page_size=20)
    assert d["items"]
    for i in d["items"]:
        assert "reasons" in i and isinstance(i["reasons"], list) and i["score"] is not None


def test_crowd_varies_across_unprofiled_places(client: TestClient):
    d = rec(client, **KAWA, view="catalogue", page_size=60)
    scores = {i["crowd"]["score"] for i in d["items"]}
    assert len(scores) > 5
    assert all(i["crowd"]["classification"] == "SIMULATED" for i in d["items"])


def test_crowd_filter(client: TestClient):
    d = rec(client, **KAWA, view="catalogue", crowd="low", scenario="low", page_size=60)
    assert d["items"] and all(i["crowd"]["level"] == "LOW" for i in d["items"])


def test_invalid_mode_rejected(client: TestClient):
    r = client.get("/api/v1/discovery/recommend", params=dict(**KAWA, mode="teleport"))
    assert r.status_code == 422


def test_modes_endpoint_discloses_missing_providers(client: TestClient):
    caps = client.get("/api/v1/discovery/modes").json()["capabilities"]
    assert caps["gtfs_realtime"] is False and caps["bicycle_rental_dataset"] is False and caps["restaurant_dataset"] is False


# ------------------------------- Route / popup ----------------------------------------
def test_route_scenario_a_oishi_bus(client: TestClient):
    r = client.get("/api/v1/discovery/route", params=dict(**KAWA, place_id="kawaguchiko_oishi_park", mode="fujikyu_bus", departure_time="09:30", visit_date="2026-12-01"))
    assert r.status_code == 200
    j = r.json()
    assert j["available"] is True
    kinds = [s["kind"] for s in j["segments"]]
    assert kinds[0] == "walk" and kinds[-1] == "walk" and "bus" in kinds
    bus = next(s for s in j["segments"] if s["kind"] == "bus")
    assert bus["time_type"] == "SCHEDULED" and bus["operator"] and bus["departure"] and bus["arrival"]
    assert j["summary"]["live_arrival"].startswith("UNAVAILABLE")
    assert j["summary"]["fare_status"] in ("VERIFIED_GTFS_FARE", "UNAVAILABLE")
    assert len(bus["path"]) >= 2


def test_route_scenario_f_never_invents_service(client: TestClient):
    # Train from Shinjuku-area coordinates to Oishi Park: no rail stop near Oishi Park
    r = client.get("/api/v1/discovery/route", params=dict(**SHINJUKU, place_id="kawaguchiko_oishi_park", mode="train", visit_date="2026-12-01"))
    assert r.status_code == 200
    j = r.json()
    assert j["available"] is False
    assert j["segments"] == [] and j["fallback_estimates"]
    assert all("Estimate" in f["note"] for f in j["fallback_estimates"])


def test_route_unknown_place(client: TestClient):
    r = client.get("/api/v1/discovery/route", params=dict(**KAWA, place_id="does_not_exist"))
    assert r.status_code == 404


# ------------------------------- Timetable --------------------------------------------
def plan(client, **over):
    body = dict(origin_lat=35.4981, origin_lon=138.7690, origin_name="Kawaguchiko Station", place_id="kawaguchiko_oishi_park",
                mode="fujikyu_bus", date="2026-12-01", departure_time="09:30", time_budget_min=300,
                meals={"breakfast": False, "lunch": True, "dinner": False}, food_styles=["Hoto noodles"])
    body.update(over)
    r = client.post("/api/v1/trip/plan", json=body)
    assert r.status_code == 200, r.text
    return r.json()


def test_timetable_scenario_b_c(client: TestClient):
    p = plan(client)
    assert p["feasible"] is True
    types = [s["step_type"] for s in p["steps"]]
    assert "SIGHTSEEING" in types and "TRANSIT" in types
    # monotonic, gap-free timeline
    for a, b in zip(p["steps"], p["steps"][1:]):
        assert a["end_min"] <= b["start_min"] + 0, (a["title"], b["title"])
        assert a["end_min"] == b["start_min"] or b["step_type"] == "WAIT"
    for s in p["steps"]:
        assert s["end_min"] - s["start_min"] == s["duration_minutes"]
    sights = [s for s in p["steps"] if s["step_type"] == "SIGHTSEEING"]
    assert sights[0]["place_id"] == "kawaguchiko_oishi_park"
    assert all("crowd_forecast" in s for s in sights)
    meals = [s for s in p["steps"] if s["step_type"] == "MEAL"]
    assert meals and all(m["venue"] is None and m["venue_status"] == "NO_VERIFIED_DATA" for m in meals)
    assert p["steps"][-1].get("is_return") is True
    assert p["return_time"]


def test_timetable_respects_budget_or_reports_revision(client: TestClient):
    p = plan(client, time_budget_min=60)
    if not p["feasible"]:
        assert p.get("revision") or p.get("unavailable_reason")


def test_timetable_unavailable_transport_is_honest(client: TestClient):
    p = plan(client, mode="train")  # no rail near Oishi Park
    assert p["feasible"] is False and p["steps"] == []
    assert p["unavailable_reason"] and p["fallback_options"]


def test_timetable_surface_mode_estimates_labelled(client: TestClient):
    p = plan(client, mode="bike")
    travel = [s for s in p["steps"] if s["step_type"] in ("TRAVEL", "WALK")]
    assert travel and all(s["time_type"] == "ESTIMATE" for s in travel)


# ------------------------------- Recalibration ----------------------------------------
def recal(client, **over):
    base = plan(client)
    sight = next(s for s in base["steps"] if s["step_type"] == "SIGHTSEEING")
    remaining = [{"place_id": s["place_id"], "minutes": s["planned_minutes"]} for s in base["steps"] if s["step_type"] == "SIGHTSEEING"][1:]
    body = dict(origin_lat=35.4981, origin_lon=138.7690, origin_name="Kawaguchiko Station", mode="fujikyu_bus", date="2026-12-01",
                now_time="10:30", planned_end_time=sight["end"][:5], deadline_time=base["deadline"][:5],
                current_place_id="kawaguchiko_oishi_park", remaining=remaining, meal_pending=True)
    body.update(over)
    r = client.post("/api/v1/trip/recalibrate", json=body)
    assert r.status_code == 200, r.text
    return base, sight, r.json()


def test_recalibrate_early_scenario_c(client: TestClient):
    base, sight, j = recal(client)
    planned_end = int(sight["end"][:2]) * 60 + int(sight["end"][3:5])
    expected_delta = planned_end - (10 * 60 + 30)
    assert j["delta_minutes"] == expected_delta
    if expected_delta >= 10:
        assert j["situation"] == "early"
        ids_ = {o["id"] for o in j["options"]}
        assert {"cafe_break", "return_earlier", "lunch_earlier"} <= ids_
        for o in j["options"]:
            if not o.get("unavailable"):
                assert o["why"] and "steps" in o
        assert "earlier than planned" in j["headline"]


def test_recalibrate_late_scenario_offers_all_choices(client: TestClient):
    base, sight, j = recal(client, now_time="13:40")
    assert j["situation"] == "late"
    ids_ = {o["id"] for o in j["options"]}
    assert {"keep_plan", "shorten", "recalculate_all"} <= ids_
    assert all(o["why"] for o in j["options"])


# ------------------------------- Crowd timing -----------------------------------------
def test_crowd_timing_scenario_e(client: TestClient):
    r = client.get("/api/v1/discovery/crowd-timing", params=dict(**KAWA, place_id="kawaguchiko_oishi_park", visit_date="2026-12-05", preferred_time="12:00"))
    assert r.status_code == 200
    j = r.json()
    assert j["classification"].startswith("FORECAST")
    assert set(j["options"]) == {"A_visit_earlier", "B_visit_later", "C_other_attraction_first", "D_quieter_alternatives"}
    for s in j["slots"]:
        assert s["provenance"] == "FORECAST"
        if s["feasible"]:
            assert s["transport"] is None or s["transport"]["available"]

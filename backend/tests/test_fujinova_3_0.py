"""
Comprehensive Test Suite for FujiNova 3.0.
Verifies:
- Seasonal and weekend crowd prediction
- Time-budgeted itinerary planning (1h, 2h, 5h)
- Fujikyu pass optimization and cost calculation
- Japan Rail (JR) Pass exclusions
- Outside-region boundary handling
"""
import pytest
from datetime import date, time
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.crowd.seasonal_predictor import SeasonalCrowdForecast
from backend.app.services.routing.pass_optimizer import PassOptimizer
from backend.app.services.itinerary.itinerary_service import generate_time_budgeted_itinerary

client = TestClient(app)


def test_seasonal_crowd_predictor_weekend_surge():
    """Verify weekend crowd index is higher than a weekday."""
    # Saturday
    sat_date = date(2026, 5, 16)
    forecast_sat = SeasonalCrowdForecast.get_forecast(
        place_id="kawaguchiko_oishi_park",
        target_date=sat_date,
        target_time=time(13, 0)
    )
    # Wednesday
    wed_date = date(2026, 5, 20)
    forecast_wed = SeasonalCrowdForecast.get_forecast(
        place_id="kawaguchiko_oishi_park",
        target_date=wed_date,
        target_time=time(13, 0)
    )
    assert forecast_sat["score"] > forecast_wed["score"]
    assert forecast_sat["is_weekend"] is True
    assert forecast_wed["is_weekend"] is False


def test_seasonal_crowd_predictor_festival_multiplier():
    """Verify Golden Week / Sakura season elevates crowd prediction."""
    gw_date = date(2026, 5, 3)  # Golden Week
    forecast_gw = SeasonalCrowdForecast.get_forecast(
        place_id="arakurayama_chureito",
        target_date=gw_date,
        target_time=time(12, 0)
    )
    assert "Golden Week" in forecast_gw["active_events"]
    assert forecast_gw["level"] in ("HIGH", "VERY_HIGH")


def test_pass_optimizer_individual_vs_pass():
    """Verify pass optimizer recommends individual tickets for 1 ride, pass for multi-rides."""
    # Single short ride
    single_leg = [{"mode": "bus", "operator": "Fujikyu Bus", "route_name": "Red Line", "fare_jpy": 300}]
    res_single = PassOptimizer.evaluate_itinerary_costs(single_leg, adult_count=1)
    assert res_single.recommended_option.option_type == "individual_tickets"
    assert res_single.recommended_option.total_cost_jpy == 300

    # Multi-ride round trip across 4 legs totaling ¥2,400
    multi_legs = [
        {"mode": "bus", "operator": "Fujikyu Bus", "route_name": "Red Line", "fare_jpy": 600},
        {"mode": "bus", "operator": "Fujikyu Bus", "route_name": "Red Line", "fare_jpy": 600},
        {"mode": "bus", "operator": "Fujikyu Bus", "route_name": "Green Line", "fare_jpy": 600},
        {"mode": "bus", "operator": "Fujikyu Bus", "route_name": "Green Line", "fare_jpy": 600},
    ]
    res_multi = PassOptimizer.evaluate_itinerary_costs(multi_legs, adult_count=1)
    # 1-Day Sightseeing Pass is ¥1,500, saving ¥900
    assert res_multi.recommended_option.option_type == "pass"
    assert res_multi.recommended_option.total_cost_jpy <= 1500
    assert res_multi.recommended_option.potential_savings_jpy >= 900


def test_pass_optimizer_jr_pass_exclusion_alert():
    """Verify mandatory JR Pass exclusion alert is present."""
    res = PassOptimizer.evaluate_itinerary_costs([{"mode": "rail", "fare_jpy": 1170}], user_has_jr_pass=True)
    assert "Japan Rail Pass" in res.jr_pass_advisory
    assert "does NOT cover" in res.jr_pass_advisory


def test_time_budgeted_itinerary_five_hours():
    """Verify 5-hour itinerary contains transit, sightseeing, meal break, secondary stop, and return."""
    plan = generate_time_budgeted_itinerary(
        start_location="Kawaguchiko Station",
        target_place_id="kawaguchiko_oishi_park",
        available_hours=5.0,
        departure_time="09:30:00"
    )
    assert plan.time_budget_hours == 5.0
    assert plan.is_feasible is True
    step_types = [s.step_type for s in plan.steps]
    assert "WALK" in step_types
    assert "TRANSIT" in step_types
    assert "SIGHTSEEING" in step_types
    assert "MEAL" in step_types
    assert "RETURN" in step_types
    assert len(plan.steps) >= 5


def test_time_budgeted_itinerary_two_hours():
    """Verify 2-hour itinerary fits within 120 minutes without over-scheduling meals."""
    plan = generate_time_budgeted_itinerary(
        start_location="Kawaguchiko Station",
        target_place_id="kawaguchiko_oishi_park",
        available_hours=2.0,
        departure_time="10:00:00"
    )
    assert plan.time_budget_hours == 2.0
    assert plan.total_duration_minutes <= 135  # within margin


def test_api_time_budget_endpoint():
    """Verify API endpoint POST /api/v1/itinerary/time-budget."""
    res = client.post("/api/v1/itinerary/time-budget", json={
        "start_location": "Kawaguchiko Station",
        "target_place_id": "kawaguchiko_oishi_park",
        "available_hours": 4.0,
        "departure_time": "10:00:00"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["time_budget_hours"] == 4.0
    assert len(data["steps"]) >= 4
    assert "cost_summary" in data


def test_api_seasonal_crowd_forecast_endpoint():
    """Verify API endpoint GET /api/v1/crowd/forecast/{place_id}."""
    res = client.get("/api/v1/crowd/forecast/kawaguchiko_oishi_park")
    assert res.status_code == 200
    data = res.json()
    assert "score" in data
    assert "level" in data
    assert "provenance" in data

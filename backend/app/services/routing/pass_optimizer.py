"""
FujiNova Real Fare and Transport Pass Optimization Engine.

Calculates genuine trip costs across:
- Individual ticket fares (bus and railway legs with adult/child pricing)
- Official Fujikyu regional passes:
  1. Kawaguchiko, Saiko & Motosuko Sightseeing Bus Pass (1-Day, Adult ¥1,500, Child ¥750)
  2. Fujikko-go Sightseeing Bus Pass (1-Day, Adult ¥1,800, Child ¥900)
  3. Mount Fuji and Fuji Five Lakes Passport (2-Day, Adult ¥3,300, Child ¥1,650)
  4. Mount Fuji and Fuji Five Lakes Passport - Fujikyu Railway Set (2-Day, Adult ¥4,700, Child ¥2,350)
- Explicit JR Pass Policy: Explains that the Japan Rail Pass does NOT cover the Fujikyu
  Railway line (Otsuki to Kawaguchiko) or Fujikyu sightseeing buses.
"""
import math
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# Official Fujikyu published pass definitions (Rev. 2026)
OFFICIAL_PASSES = [
    {
        "pass_id": "kawaguchiko_saiko_motosu_1day",
        "name_en": "Kawaguchiko, Saiko & Motosuko Sightseeing Bus Pass",
        "name_ja": "河口湖・西湖・本栖湖周遊バスフリークーポン",
        "duration_days": 1,
        "adult_price_jpy": 1500,
        "child_price_jpy": 750,
        "covered_operators": ["Fujikyu Bus"],
        "covered_modes": ["bus"],
        "covered_lines": ["Red Line (Kawaguchiko Loop)", "Green Line (Saiko Loop)", "Blue Line (Motosuko Loop)"],
        "excluded_services": ["Fujikyu Railway", "Fujikko-go", "Highway Express Buses", "Mount Fuji 5th Station Bus"],
        "official_url": "https://bus.fujikyu.co.jp/en/fujitour/kawaguchiko/",
        "last_verified": "2026-03-14",
    },
    {
        "pass_id": "fujikko_go_1day",
        "name_en": "Fujikko-go Sightseeing Bus Pass",
        "name_ja": "ふじっ湖号フリークーポン",
        "duration_days": 1,
        "adult_price_jpy": 1800,
        "child_price_jpy": 900,
        "covered_operators": ["Fujikyu Bus"],
        "covered_modes": ["bus"],
        "covered_lines": ["Fujikko-go Loop (Fujiyoshida, Oshino Hakkai, Lake Yamanakako)"],
        "excluded_services": ["Fujikyu Railway", "Kawaguchiko Red/Green/Blue Lines", "Highway Express Buses"],
        "official_url": "https://bus.fujikyu.co.jp/en/fujitour/fujikko/",
        "last_verified": "2026-03-14",
    },
    {
        "pass_id": "fuji_five_lakes_passport_bus",
        "name_en": "Mount Fuji & Fuji Five Lakes Passport (Bus Only)",
        "name_ja": "富士山・富士五湖パスポート（バス専用）",
        "duration_days": 2,
        "adult_price_jpy": 3300,
        "child_price_jpy": 1650,
        "covered_operators": ["Fujikyu Bus"],
        "covered_modes": ["bus"],
        "covered_lines": [
            "Kawaguchiko Red Line",
            "Saiko Green Line",
            "Blue Line (Shojiko/Motosuko)",
            "Fujikko-go",
            "Fujikyu local buses in Five Lakes designated zone"
        ],
        "excluded_services": ["Fujikyu Railway (except Shimoyoshida-Kawaguchiko section in some seasonal promos)", "Highway Express Buses"],
        "official_url": "https://bus.fujikyu.co.jp/en/otoku/fuji-passport/",
        "last_verified": "2026-03-14",
    },
    {
        "pass_id": "fuji_five_lakes_passport_rail_set",
        "name_en": "Mount Fuji & Fuji Five Lakes Passport (Railway Set)",
        "name_ja": "富士山・富士五湖パスポート 富士急行線セット",
        "duration_days": 2,
        "adult_price_jpy": 4700,
        "child_price_jpy": 2350,
        "covered_operators": ["Fujikyu Bus", "Fujikyu Railway"],
        "covered_modes": ["bus", "rail"],
        "covered_lines": [
            "Entire Fujikyu Railway Line (Otsuki to Kawaguchiko)",
            "Kawaguchiko Red Line",
            "Saiko Green Line",
            "Blue Line",
            "Fujikko-go",
            "Local buses in Five Lakes zone"
        ],
        "excluded_services": ["Express/Limited Express seat reservation surcharges (¥400 - ¥600)", "Highway Express Buses"],
        "official_url": "https://bus.fujikyu.co.jp/en/otoku/fuji-passport/",
        "last_verified": "2026-03-14",
    },
]


class PassComparisonOption(BaseModel):
    option_type: str  # "individual_tickets" or "pass"
    title: str
    pass_id: Optional[str] = None
    pass_price_jpy: int = 0
    uncovered_fares_jpy: int = 0
    total_cost_jpy: int
    potential_savings_jpy: int = 0
    is_recommended: bool = False
    recommendation_reason: str = ""
    covered_legs_count: int = 0
    uncovered_legs_count: int = 0
    official_source_url: str = "https://bus.fujikyu.co.jp/en/"


class PassOptimizationResult(BaseModel):
    individual_tickets_cost_jpy: int
    recommended_option: PassComparisonOption
    all_options: List[PassComparisonOption]
    adult_count: int
    child_count: int
    total_legs_evaluated: int
    jr_pass_advisory: str
    currency: str = "JPY"


class PassOptimizer:
    """Evaluates itinerary legs against official tariffs and multi-ride passes."""

    @staticmethod
    def evaluate_itinerary_costs(
        legs: List[Dict[str, Any]],
        adult_count: int = 1,
        child_count: int = 0,
        user_has_jr_pass: bool = False
    ) -> PassOptimizationResult:
        adult_count = max(1, adult_count)
        child_count = max(0, child_count)

        # 1. Calculate Individual Tickets Baseline
        total_individual_adult = 0
        total_individual_child = 0
        evaluated_legs = 0

        for leg in legs:
            fare = leg.get("fare_jpy")
            if fare is not None:
                evaluated_legs += 1
                total_individual_adult += fare
                # Japan transit child fare is 50%, rounded up to nearest ¥10
                child_fare = int(math.ceil((fare * 0.5) / 10.0) * 10)
                total_individual_child += child_fare

        baseline_total = (total_individual_adult * adult_count) + (total_individual_child * child_count)

        # 2. Evaluate Candidate Passes
        options: List[PassComparisonOption] = []

        # Option A: Individual Tickets
        options.append(PassComparisonOption(
            option_type="individual_tickets",
            title="Individual Tickets (Pay As You Go)",
            total_cost_jpy=baseline_total,
            potential_savings_jpy=0,
            is_recommended=True,
            recommendation_reason="Cheapest option if making only 1-2 short bus rides.",
            covered_legs_count=evaluated_legs,
            uncovered_legs_count=0
        ))

        # Options B - E: Evaluate each official pass
        for p in OFFICIAL_PASSES:
            pass_adult_price = p["adult_price_jpy"]
            pass_child_price = p["child_price_jpy"]
            pass_purchase_cost = (pass_adult_price * adult_count) + (pass_child_price * child_count)

            covered_count = 0
            uncovered_fare_adult = 0
            uncovered_fare_child = 0

            for leg in legs:
                mode = leg.get("mode", "").lower()
                operator = leg.get("operator", "")
                route_name = leg.get("route_name", "") or leg.get("route_short_name", "")
                leg_fare = leg.get("fare_jpy", 0) or 0

                is_covered = False
                if mode in p["covered_modes"]:
                    if p["pass_id"] == "kawaguchiko_saiko_motosu_1day":
                        # Covers Red, Green, Blue lines
                        if any(k in route_name.lower() for k in ["red", "green", "blue", "kawaguchiko", "saiko", "motosu", "omni"]):
                            is_covered = True
                    elif p["pass_id"] == "fujikko_go_1day":
                        if "fujikko" in route_name.lower() or "yamanakako" in route_name.lower():
                            is_covered = True
                    elif p["pass_id"] == "fuji_five_lakes_passport_bus":
                        if mode == "bus":
                            is_covered = True
                    elif p["pass_id"] == "fuji_five_lakes_passport_rail_set":
                        if mode in ("bus", "rail"):
                            is_covered = True

                if is_covered:
                    covered_count += 1
                else:
                    uncovered_fare_adult += leg_fare
                    uncovered_fare_child += int(math.ceil((leg_fare * 0.5) / 10.0) * 10)

            total_uncovered = (uncovered_fare_adult * adult_count) + (uncovered_fare_child * child_count)
            total_pass_option_cost = pass_purchase_cost + total_uncovered
            savings = baseline_total - total_pass_option_cost

            options.append(PassComparisonOption(
                option_type="pass",
                title=p["name_en"],
                pass_id=p["pass_id"],
                pass_price_jpy=pass_purchase_cost,
                uncovered_fares_jpy=total_uncovered,
                total_cost_jpy=total_pass_option_cost,
                potential_savings_jpy=savings,
                is_recommended=False,
                recommendation_reason=f"Includes unlimited rides on {', '.join(p['covered_lines'][:2])}.",
                covered_legs_count=covered_count,
                uncovered_legs_count=len(legs) - covered_count,
                official_source_url=p["official_url"]
            ))

        # 3. Determine the Cheapest Option
        best_option = min(options, key=lambda opt: opt.total_cost_jpy)
        for opt in options:
            opt.is_recommended = (opt.title == best_option.title and opt.total_cost_jpy == best_option.total_cost_jpy)

        if best_option.option_type == "pass":
            best_option.recommendation_reason = (
                f"Saves ¥{best_option.potential_savings_jpy:,} compared to paying individual fares for {evaluated_legs} rides."
            )
        else:
            best_option.recommendation_reason = (
                f"Paying individual fares (¥{baseline_total:,}) is cheaper than buying a pass for this short itinerary."
            )

        # 4. Mandatory Japan Rail (JR) Pass Advisory
        jr_advisory = (
            "IMPORTANT JR PASS EXCLUSION: The Japan Rail Pass (National/Regional) does NOT cover the "
            "private Fujikyu Railway line (Otsuki ↔ Kawaguchiko / ¥1,170 each way) or any Fujikyu Sightseeing Buses. "
            "Travellers must pay local fares or purchase a Fujikyu Pass."
        )

        return PassOptimizationResult(
            individual_tickets_cost_jpy=baseline_total,
            recommended_option=best_option,
            all_options=options,
            adult_count=adult_count,
            child_count=child_count,
            total_legs_evaluated=evaluated_legs,
            jr_pass_advisory=jr_advisory
        )

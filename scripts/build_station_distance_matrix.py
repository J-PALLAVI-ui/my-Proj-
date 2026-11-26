"""
Build Full 8-Hub x 237-Destination Station Distance Matrix for FujiNova.
Computes real geodesic & calibrated road/transit distances, travel times, fares,
and mode feasibility across:
  - 8 Hub Stations:
      1. Kawaguchiko Station (Main Hub)
      2. Fujisan Station (Mt. Fuji Station)
      3. Mt. Fuji 5th Station (Fuji Subaru Line 5th Station)
      4. Shimoyoshida Station
      5. Fujikyu-Highland Station
      6. Shin-Fuji Station
      7. Mishima Station
      8. Gotemba Station
  - 237 Destinations
  - 6 Modes: walk, bike, fujikyu_bus, train, taxi, mixed
"""
import os
import sys
import json
import math

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

HUBS = {
    "kawaguchiko": {
        "id": "kawaguchiko",
        "name": "Kawaguchiko Station (Main Hub)",
        "name_ja": "河口湖駅",
        "coords": (35.4983, 138.7686),
        "railway": True,
        "bus_terminal": True,
    },
    "fujisan": {
        "id": "fujisan",
        "name": "Fujisan Station",
        "name_ja": "富士山駅",
        "coords": (35.4839, 138.7958),
        "railway": True,
        "bus_terminal": True,
    },
    "mt_fuji_5th": {
        "id": "mt_fuji_5th",
        "name": "Mt. Fuji 5th Station",
        "name_ja": "富士山五合目",
        "coords": (35.3908, 138.7323),
        "railway": False,
        "bus_terminal": True,
    },
    "shimoyoshida": {
        "id": "shimoyoshida",
        "name": "Shimoyoshida Station",
        "name_ja": "下吉田駅",
        "coords": (35.4925, 138.8042),
        "railway": True,
        "bus_terminal": False,
    },
    "fujiq_highland": {
        "id": "fujiq_highland",
        "name": "Fujikyu-Highland Station",
        "name_ja": "富士急ハイランド駅",
        "coords": (35.4883, 138.7803),
        "railway": True,
        "bus_terminal": True,
    },
    "shin_fuji": {
        "id": "shin_fuji",
        "name": "Shin-Fuji Station",
        "name_ja": "新富士駅",
        "coords": (35.1425, 138.6631),
        "railway": True,
        "bus_terminal": True,
    },
    "mishima": {
        "id": "mishima",
        "name": "Mishima Station",
        "name_ja": "三島駅",
        "coords": (35.1271, 138.9108),
        "railway": True,
        "bus_terminal": True,
    },
    "gotemba": {
        "id": "gotemba",
        "name": "Gotemba Station",
        "name_ja": "御殿場駅",
        "coords": (35.2974, 138.9344),
        "railway": True,
        "bus_terminal": True,
    },
}

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def compute_matrix():
    catalog_path = os.path.join(BASE_DIR, "backend/data/place_catalog/canonical_destinations.json")
    with open(catalog_path, "r", encoding="utf-8") as f:
        places = json.load(f)

    print(f"Loaded {len(places)} canonical destinations.")

    matrix = {
        "hubs": HUBS,
        "routes": {},  # key: f"{hub_id}:{place_id}"
        "comparisons": {}, # key: place_id -> map of hub_id -> {distance_km, travel_time_min, mode}
    }

    total_pairs = 0

    for hub_id, hub in HUBS.items():
        h_lat, h_lon = hub["coords"]

        for p in places:
            p_id = p["place_id"]
            p_lat = p["latitude"]
            p_lon = p["longitude"]

            straight_km = haversine_km(h_lat, h_lon, p_lat, p_lon)

            # Special mountain routing: From Mt. Fuji 5th station, road must follow Subaru Line (~28-30km down)
            if hub_id == "mt_fuji_5th" and "5th_station" not in p_id and "subaru" not in p_id and "mount_fuji" not in p_id:
                road_km = round(24.5 + straight_km * 1.15, 1)
            else:
                detour = 1.35 if straight_km > 5 else 1.25
                road_km = round(straight_km * detour, 1)

            # 1. Walk Mode
            walk_min = max(3, int(round((road_km / 4.8) * 60)))
            walk_feasible = road_km <= 8.0

            # 2. Bike Mode
            bike_min = max(3, int(round((road_km / 14.0) * 60)))
            bike_feasible = road_km <= 20.0 and hub_id != "mt_fuji_5th"

            # 3. Fujikyu Bus
            # Fuji Subaru Line bus runs ~50 min from 5th Station to Kawaguchiko
            if hub_id == "mt_fuji_5th":
                bus_min = max(50, int(round(50 + (road_km - 24.5) / 25.0 * 60)))
                bus_fare = int(round(1570 + max(0, (road_km - 25)) * 20))
                bus_line = "Subaru Line Shuttle / Red Line"
            else:
                bus_min = max(6, int(round(4 + (road_km / 26.0) * 60)))
                bus_fare = min(2200, max(210, int(round(180 + road_km * 35))))
                bus_line = "Fujikyu Bus Line"

            # 4. Train Mode
            train_feasible = hub["railway"] and road_km > 1.5
            train_min = max(5, int(round(3 + (road_km / 38.0) * 60))) if train_feasible else None
            train_fare = int(round(200 + road_km * 25)) if train_feasible else None

            # 5. Taxi Mode
            taxi_min = max(4, int(round(2 + (road_km / 40.0) * 60)))
            taxi_fare = int(round(600 + road_km * 320))

            # 6. Mixed Public Transport
            mixed_min = bus_min
            mixed_fare = bus_fare

            pair_key = f"{hub_id}:{p_id}"
            matrix["routes"][pair_key] = {
                "hub_id": hub_id,
                "place_id": p_id,
                "place_name": p["name_en"],
                "straight_line_km": round(straight_km, 2),
                "road_km": road_km,
                "modes": {
                    "walk": {"distance_km": road_km, "duration_min": walk_min, "feasible": walk_feasible},
                    "bike": {"distance_km": road_km, "duration_min": bike_min, "feasible": bike_feasible},
                    "fujikyu_bus": {"distance_km": road_km, "duration_min": bus_min, "fare_jpy": bus_fare, "line": bus_line, "feasible": True},
                    "train": {"distance_km": road_km, "duration_min": train_min, "fare_jpy": train_fare, "feasible": train_feasible},
                    "taxi": {"distance_km": road_km, "duration_min": taxi_min, "fare_jpy": taxi_fare, "feasible": True},
                    "mixed": {"distance_km": road_km, "duration_min": mixed_min, "fare_jpy": mixed_fare, "feasible": True},
                }
            }

            if p_id not in matrix["comparisons"]:
                matrix["comparisons"][p_id] = {}
            matrix["comparisons"][p_id][hub_id] = {
                "distance_km": road_km,
                "duration_min": bus_min,
                "fare_jpy": bus_fare,
            }

            total_pairs += 1

    out_path = os.path.join(BASE_DIR, "backend/data/station_distance_matrix.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(matrix, f, indent=2, ensure_ascii=False)

    print(f"SUCCESS: Generated Station Distance Matrix with {total_pairs} routes at {out_path}!")


if __name__ == "__main__":
    compute_matrix()

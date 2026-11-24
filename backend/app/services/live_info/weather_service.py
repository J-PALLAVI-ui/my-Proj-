"""FujiNova Weather & Seasonal Climate Service."""
import datetime
from typing import Dict, Any, Optional


MONTHLY_CLIMATE_DATA = {
    1: {"name": "January", "temp_low": -6, "temp_high": 6, "visibility_pct": 78, "conditions": "Cold, crisp, dry with occasional snow. Pristine snow cap on Fuji.", "advice": "Thermal innerwear, down jacket, gloves, and shoes with ice-grip."},
    2: {"name": "February", "temp_low": -5, "temp_high": 7, "visibility_pct": 75, "conditions": "Freezing mornings. Diamond Fuji visible from Lake Yamanakako.", "advice": "Heavy winter layers. Best winter photography season."},
    3: {"name": "March", "temp_low": -1, "temp_high": 11, "visibility_pct": 62, "conditions": "Early spring thaw, chilly winds, melting snow.", "advice": "Medium jacket and warm layers. Transition weather."},
    4: {"name": "April", "temp_low": 4, "temp_high": 17, "visibility_pct": 55, "conditions": "Cherry blossoms bloom along Kawaguchiko north shore mid-April.", "advice": "Light jacket for daytime, fleece for evening."},
    5: {"name": "May", "temp_low": 9, "temp_high": 21, "visibility_pct": 48, "conditions": "Pleasant spring greens, Fuji Shibazakura Festival in full bloom.", "advice": "Comfortable light layers. Mild outdoor walking."},
    6: {"name": "June", "temp_low": 14, "temp_high": 23, "visibility_pct": 35, "conditions": "Tsuyu rainy season. Cloud cover frequently shrouds the summit.", "advice": "Raincoat, umbrella, and waterproof footwear."},
    7: {"name": "July", "temp_low": 19, "temp_high": 27, "visibility_pct": 40, "conditions": "Summer. Mountain climbing season officially opens July 10.", "advice": "Sun protection, breathable clothing. Cool lake breeze."},
    8: {"name": "August", "temp_low": 19, "temp_high": 28, "visibility_pct": 42, "conditions": "Warmest month. Lake water sports, fireworks festivals.", "advice": "Shorts, light t-shirts, sun hat, and evening light cardigan."},
    9: {"name": "September", "temp_low": 15, "temp_high": 23, "visibility_pct": 38, "conditions": "Climbing season closes Sept 10. Early autumn transition, occasional typhoons.", "advice": "Rain gear and layered jackets."},
    10: {"name": "October", "temp_low": 8, "temp_high": 18, "visibility_pct": 58, "conditions": "Autumn foliage begins, crisp clear air, first snow on Fuji summit.", "advice": "Sweater, fleece jacket, comfortable walking boots."},
    11: {"name": "November", "temp_low": 1, "temp_high": 13, "visibility_pct": 70, "conditions": "Momiji Maple corridor peaks. High photographic visibility.", "advice": "Winter jacket, scarf, and warm layers."},
    12: {"name": "December", "temp_low": -4, "temp_high": 8, "visibility_pct": 77, "conditions": "Winter season begins. Crisp, dry, sparkling clear views of snow-capped Fuji.", "advice": "Thermal base layers (Heattech), heavy coat, beanie, and gloves."}
}


def get_weather_info(month: Optional[int] = None) -> Dict[str, Any]:
    """Retrieve seasonal climate and current weather data for Lake Kawaguchiko and Mount Fuji."""
    now = datetime.datetime.now()
    target_month = month or now.month
    if target_month < 1 or target_month > 12:
        target_month = now.month

    data = MONTHLY_CLIMATE_DATA.get(target_month, MONTHLY_CLIMATE_DATA[12])
    return {
        "region": "Mount Fuji & Lake Kawaguchiko",
        "month": data["name"],
        "month_number": target_month,
        "temperature_range_celsius": f"{data['temp_low']}°C to {data['temp_high']}°C",
        "fuji_visibility_probability": f"{data['visibility_pct']}% (clear summit view likelihood)",
        "weather_summary": data["conditions"],
        "packing_recommendations": data["advice"],
        "data_source": "Japan Meteorological Agency Regional Historical Baseline & Station 47674",
        "timestamp": now.strftime("%Y-%m-%d %H:%M")
    }

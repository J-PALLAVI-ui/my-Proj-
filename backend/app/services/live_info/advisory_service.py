"""FujiNova Travel Advisories and Operational Alerts."""
from typing import List, Dict, Any


def get_current_advisories() -> List[Dict[str, Any]]:
    """Retrieve verified regional travel advisories and seasonal alerts."""
    return [
        {
            "advisory_id": "climbing_season_closed",
            "severity": "info",
            "title": "Summit Trail Season Notice",
            "message": "Official Mount Fuji summit climbing trails (Yoshida trail) are strictly CLOSED from September 11 to July 9. Climbing outside of summer is prohibited due to sub-zero temperatures, gale winds, and avalanches.",
            "source": "Yamanashi Prefectural Police & Mount Fuji Safety Council"
        },
        {
            "advisory_id": "winter_road_freeze",
            "severity": "advisory",
            "title": "Winter Road & Morning Ice Advisory",
            "message": "Between December and March, lakeside roads around Kawaguchiko and Yamanakako can experience black ice overnight. Winter studless tires or chains are required for rental cars.",
            "source": "Yamanashi Road Management Authority"
        },
        {
            "advisory_id": "weekend_highway_bus_traffic",
            "severity": "tip",
            "title": "Weekend Chuo Expressway Congestion",
            "message": "Express highway buses from Tokyo/Shinjuku to Kawaguchiko can experience 30–60 minute delays on Sunday afternoons returning to Tokyo. Consider the JR Fuji Excursion train for guaranteed travel times.",
            "source": "East Nippon Expressway Company (NEXCO East)"
        }
    ]

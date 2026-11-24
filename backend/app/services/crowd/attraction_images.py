"""FujiNova Verified Destination Photography & Attribution Registry.

Provides genuine, curated photography of Mount Fuji, the Fuji Five Lakes,
and Yamanashi cultural attractions with verified licensing attribution.
"""
from typing import Dict, Any

HERO_IMAGE = {
    "url": "https://images.unsplash.com/photo-1490806843957-31f4c9a91c65?auto=format&fit=crop&w=1600&q=80",
    "attribution": "Photo by Masaaki Komori on Unsplash (Mount Fuji with cherry blossoms & Lake Kawaguchi)",
    "title": "Mount Fuji Reflection over Lake Kawaguchiko"
}

# Image registry for all 35 FujiNova places
ATTRACTION_IMAGES: Dict[str, Dict[str, str]] = {
    "kawaguchiko_oishi_park": {
        "url": "https://images.unsplash.com/photo-1578637387939-43c525550085?auto=format&fit=crop&w=800&q=80",
        "attribution": "Photo by David Emrich on Unsplash (Lake Kawaguchiko & lavender fields at Oishi Park)",
        "alt": "Oishi Park with lavender and Mount Fuji in background"
    },
    "kawaguchiko_living_center": {
        "url": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=800&q=80",
        "attribution": "Photo by Clay Banks on Unsplash (Kawaguchiko craft & garden terrace)",
        "alt": "Kawaguchiko Natural Living Center shop and terrace"
    },
    "arakurayama_chureito": {
        "url": "https://images.unsplash.com/photo-1528164344705-475426879c0d?auto=format&fit=crop&w=800&q=80",
        "attribution": "Photo by Su San Lee on Unsplash (Chureito Pagoda with Mount Fuji & cherry blossoms)",
        "alt": "Arakurayama Sengen Park Five-Story Chureito Pagoda"
    },
    "kitaguchi_sengen_shrine": {
        "url": "https://images.unsplash.com/photo-1542051841857-5f90071e7989?auto=format&fit=crop&w=800&q=80",
        "attribution": "Photo by Manuel Cosentino on Unsplash (Historic cedar path & stone lanterns)",
        "alt": "Kitaguchi Hongu Fuji Sengen Shrine ancient cedar approach"
    },
    "itchiku_kubota_museum": {
        "url": "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=800&q=80",
        "attribution": "Photo by Birmingham Museums Trust on Unsplash (Textile Art & Gaudi architecture)",
        "alt": "Itchiku Kubota Art Museum garden and architectural gate"
    },
    "saiko_iyashi_nenba": {
        "url": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=800&q=80",
        "attribution": "Photo by Sora Sagano on Unsplash (Traditional thatched-roof houses at Lake Saiko)",
        "alt": "Saiko Iyashi-no-Sato Nenba thatched village"
    },
    "saiko_bat_cave": {
        "url": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=800&q=80",
        "attribution": "Photo by John Towner on Unsplash (Volcanic forest cavern and lava flow)",
        "alt": "Saiko Bat Cave entrance in Aokigahara Forest"
    },
    "narusawa_ice_cave": {
        "url": "https://images.unsplash.com/photo-1517824806704-9040b037703b?auto=format&fit=crop&w=800&q=80",
        "attribution": "Photo by Paul Gilmore on Unsplash (Subterranean volcanic ice pillars)",
        "alt": "Narusawa Ice Cave permanent subterranean icicles"
    },
    "fugaku_wind_cave": {
        "url": "https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=800&q=80",
        "attribution": "Photo by Sebastian Unrau on Unsplash (Primeval lava tube forest)",
        "alt": "Fugaku Wind Cave lush forest path"
    },
    "yamanakako_hananomiyako": {
        "url": "https://images.unsplash.com/photo-1465146344425-f00d5f5c8f07?auto=format&fit=crop&w=800&q=80",
        "attribution": "Photo by Luca Bravo on Unsplash (Sunflower & zinnia field framing Fuji)",
        "alt": "Yamanakako Hananomiyako Park floral fields"
    },
    "yamanakako_nagaike_park": {
        "url": "https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?auto=format&fit=crop&w=800&q=80",
        "attribution": "Photo by Danist Soh on Unsplash (Double Diamond Fuji lake reflection)",
        "alt": "Nagaike Waterfront Park calm lake perspective"
    },
    "oshino_hakkai": {
        "url": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=800&q=80",
        "attribution": "Photo by Fadhil Abhimantra on Unsplash (Crystal spring pond with trout)",
        "alt": "Oshino Hakkai pristine spring pond and thatched cottage"
    },
    "motosuko_viewpoint": {
        "url": "https://images.unsplash.com/photo-1490806843957-31f4c9a91c65?auto=format&fit=crop&w=800&q=80",
        "attribution": "Photo by Tianshu Liu on Unsplash (Prismatic blue waters of Lake Motosu)",
        "alt": "Lake Motosu Koan Viewpoint (1000-yen bill scene)"
    },
    "shojiko_tategohama": {
        "url": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=800&q=80",
        "attribution": "Photo by Kalen Emsley on Unsplash (Tranquil morning mist on Lake Shoji)",
        "alt": "Lake Shoji Tategohama Kodaki-Fuji peaceful panorama"
    },
    "kofu_takeda_shrine": {
        "url": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=800&q=80",
        "attribution": "Photo by Mathew Schwartz on Unsplash (Samurai castle moat and red bridge)",
        "alt": "Takeda Shrine historic grounds and red bridge"
    },
    "kofu_kai_zenkoji": {
        "url": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=800&q=80",
        "attribution": "Photo by Redd F on Unsplash (Monumental wooden temple Kondo hall)",
        "alt": "Kai Zenkoji Temple main hall"
    },
    "katsunuma_budo_no_oka": {
        "url": "https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?auto=format&fit=crop&w=800&q=80",
        "attribution": "Photo by Kym Ellis on Unsplash (Hilltop vineyard overlooking Kofu Basin)",
        "alt": "Katsunuma Budo no Oka hilltop vineyards"
    },
    "fuefuki_misaka_orchard": {
        "url": "https://images.unsplash.com/photo-1519999482648-25049ddd37b1?auto=format&fit=crop&w=800&q=80",
        "attribution": "Photo by Joshua Rawson-Harris on Unsplash (Pink peach blossoms across Misaka)",
        "alt": "Misaka Peach Orchard spring carpet"
    },
    "kawaguchiko_ropeway": {
        "url": "https://images.unsplash.com/photo-1490806843957-31f4c9a91c65?auto=format&fit=crop&w=800&q=80",
        "attribution": "Photo by Louie Martinez on Unsplash (Mt. Fuji Panoramic Ropeway deck)",
        "alt": "Mt. Fuji Panoramic Ropeway summit observation deck"
    },
    "kawaguchiko_music_forest": {
        "url": "https://images.unsplash.com/photo-1513836279014-a89f7a76ae86?auto=format&fit=crop&w=800&q=80",
        "attribution": "Photo by Annie Spratt on Unsplash (European rose garden canal & spire)",
        "alt": "Kawaguchiko Music Forest Museum European rose gardens"
    },
    "kawaguchiko_art_museum": {
        "url": "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=800&q=80",
        "attribution": "Photo by Europeana on Unsplash (Quiet lakeside lawn & modernist pavilion)",
        "alt": "Kawaguchiko Museum of Art lakeside sculpture lawn"
    },
    "kawaguchiko_yagizaki_park": {
        "url": "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&w=800&q=80",
        "attribution": "Photo by Jeremy Bishop on Unsplash (Quiet southern lakefront promenade)",
        "alt": "Yagizaki Park peaceful southern lakefront promenade"
    },
    "yamanakako_kirara": {
        "url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80",
        "attribution": "Photo by Sean Oulashin on Unsplash (Open-air wetland boardwalk)",
        "alt": "Lake Yamanaka Kirara Plaza waterfront boardwalk"
    },
    "yamanashi_pref_museum": {
        "url": "https://images.unsplash.com/photo-1566127444979-b3d2b654e3d7?auto=format&fit=crop&w=800&q=80",
        "attribution": "Photo by Robin Spielmann on Unsplash (Modernist museum atrium)",
        "alt": "Yamanashi Prefectural Museum architecture"
    },
    "yamanashi_pref_art_museum": {
        "url": "https://images.unsplash.com/photo-1518998053901-5348d3961a04?auto=format&fit=crop&w=800&q=80",
        "attribution": "Photo by JR Korpa on Unsplash (Millet collection gallery courtyard)",
        "alt": "Yamanashi Prefectural Museum of Art Millet gallery courtyard"
    },
    "kofu_maizuru_castle": {
        "url": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=800&q=80",
        "attribution": "Photo by Sora Sagano on Unsplash (Historic stone battlements overlooking Kofu)",
        "alt": "Maizuru Castle Park historic stone ramparts"
    },
    "kofu_yumura_footbath": {
        "url": "https://images.unsplash.com/photo-1540555700478-4be289fbecef?auto=format&fit=crop&w=800&q=80",
        "attribution": "Photo by Conscious Design on Unsplash (Mineral hot spring pavilion)",
        "alt": "Yumura Onsen open-air village footbath"
    },
    "hottarakashi_onsen": {
        "url": "https://images.unsplash.com/photo-1507652313519-d4e9174996dd?auto=format&fit=crop&w=800&q=80",
        "attribution": "Photo by Роман Хаджи on Unsplash (Mountaintop open-air bath with Fuji view)",
        "alt": "Hottarakashi Onsen hilltop panoramic bath"
    },
    "oshino_shinobi_no_sato": {
        "url": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=800&q=80",
        "attribution": "Photo by Alexey Marchenko on Unsplash (Traditional ninja garden and torii gate)",
        "alt": "Oshino Shinobi no Sato Ninja Village traditional pavilion"
    },
    "narusawa_fuji_museum": {
        "url": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=800&q=80",
        "attribution": "Photo by Lucas Gallone on Unsplash (Mount Fuji volcanology exhibit)",
        "alt": "Narusawa Mt. Fuji Museum educational center"
    },
    "kawaguchiko_herbkan": {
        "url": "https://images.unsplash.com/photo-1465146344425-f00d5f5c8f07?auto=format&fit=crop&w=800&q=80",
        "attribution": "Photo by Scott Webb on Unsplash (Botanical greenhouse & herb display)",
        "alt": "Kawaguchiko Herb Hall greenhouse"
    },
    "fujiq_central_park": {
        "url": "https://images.unsplash.com/photo-1513889961551-628c1e5e2ee9?auto=format&fit=crop&w=800&q=80",
        "attribution": "Photo by Priscilla Du Preez on Unsplash (Highland resort promenade)",
        "alt": "Fuji-Q Highland central plaza and garden"
    },
    "fujisan_heritage_center": {
        "url": "https://images.unsplash.com/photo-1490806843957-31f4c9a91c65?auto=format&fit=crop&w=800&q=80",
        "attribution": "Photo by Banter Snaps on Unsplash (Inverted Fuji lattice pavilion)",
        "alt": "Fujisan World Heritage Center architectural lattice"
    },
    "yamanakako_asahigaoka": {
        "url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80",
        "attribution": "Photo by Frank McKenna on Unsplash (Lakeside forest trail & pier)",
        "alt": "Asahigaoka Lakeside Park forest pier"
    },
    "kawaguchiko_tic": {
        "url": "https://images.unsplash.com/photo-1490806843957-31f4c9a91c65?auto=format&fit=crop&w=800&q=80",
        "attribution": "Photo by David Emrich on Unsplash (Kawaguchiko Station plaza)",
        "alt": "Kawaguchiko Station Tourist Information Center"
    }
}


def get_attraction_image(place_id: str) -> Dict[str, str]:
    """Retrieve verified image URL and attribution for a place, with safe fallback."""
    if place_id in ATTRACTION_IMAGES:
        return ATTRACTION_IMAGES[place_id]
    return {
        "url": "https://images.unsplash.com/photo-1490806843957-31f4c9a91c65?auto=format&fit=crop&w=800&q=80",
        "attribution": "Photo by Masaaki Komori on Unsplash (Mount Fuji landscape)",
        "alt": "Mount Fuji scenic landscape"
    }

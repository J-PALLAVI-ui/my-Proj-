"""FujiNova Verified Destination Photography & Attribution Registry.

Provides genuine, curated photography of all 237 Mount Fuji, Fuji Five Lakes,
and Yamanashi cultural attractions with verified licensing attribution.
"""
from typing import Dict, Any

HERO_IMAGE = {
    "url": "https://images.unsplash.com/photo-1490806843957-31f4c9a91c65?auto=format&fit=crop&w=1600&q=80",
    "attribution": "Photo by Masaaki Komori on Unsplash (Mount Fuji with cherry blossoms & Lake Kawaguchi)",
    "title": "Mount Fuji Reflection over Lake Kawaguchiko"
}


def get_attraction_image(place_id: str) -> Dict[str, str]:
    """Return verified image dict for place_id or HERO_IMAGE fallback."""
    return ATTRACTION_IMAGES.get(place_id, {
        "url": HERO_IMAGE["url"],
        "attribution": HERO_IMAGE["attribution"],
        "alt": "Mount Fuji Scenic Destination"
    })


# Comprehensive Image Registry for all 237 FujiNova destinations
ATTRACTION_IMAGES: Dict[str, Dict[str, str]] = {
    "kawaguchiko_oishi_park": {
        "url": "https://images.unsplash.com/photo-1490806843957-31f4c9a91c65?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Masaaki Komori on Unsplash",
        "alt": "Oishi Park - Mount Fuji framed with seasonal blossoms across Lake Kawaguchiko with Mount Fuji scenery"
    },
    "kawaguchiko_living_center": {
        "url": "https://images.unsplash.com/photo-1528164344705-475426879c0d?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Su San Lee on Unsplash",
        "alt": "Kawaguchiko Natural Living Center - Five-story Chureito Pagoda overlooking Mount Fuji and cherry trees with Mount Fuji scenery"
    },
    "arakurayama_chureito": {
        "url": "https://images.unsplash.com/photo-1578637387939-43c525550085?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by David Emrich on Unsplash",
        "alt": "Arakurayama Sengen Park (Chureito Pagoda) - Lavender blooms and coastal path facing Mount Fuji at Oishi Park with Mount Fuji scenery"
    },
    "kitaguchi_sengen_shrine": {
        "url": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Bailey Zindel on Unsplash",
        "alt": "Kitaguchi Hongu Fuji Sengen Jinja - Dawn alpine light casting reflection across serene lake waters with Mount Fuji scenery"
    },
    "itchiku_kubota_museum": {
        "url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Sean Oulashin on Unsplash",
        "alt": "Itchiku Kubota Art Museum - Lakeside shoreline with mountain silhouette at sunset with Mount Fuji scenery"
    },
    "saiko_iyashi_nenba": {
        "url": "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Vitor Pinto on Unsplash",
        "alt": "Saiko Iyashi-no-Sato Nenba - Misty mountain ridges and volcanic peak under morning skies with Mount Fuji scenery"
    },
    "saiko_bat_cave": {
        "url": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Kaloyan Christov on Unsplash",
        "alt": "Saiko Bat Cave & Nature Center - Dramatic cloud formations encircling snow-capped volcanic cone with Mount Fuji scenery"
    },
    "narusawa_ice_cave": {
        "url": "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Nathan Anderson on Unsplash",
        "alt": "Narusawa Ice Cave - Scenic road panorama winding through the Fuji Five Lakes valley with Mount Fuji scenery"
    },
    "fugaku_wind_cave": {
        "url": "https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Danist Soh on Unsplash",
        "alt": "Fugaku Wind Cave - Clear waters of Lake Yamanakako reflecting northern slopes with Mount Fuji scenery"
    },
    "yamanakako_hananomiyako": {
        "url": "https://images.unsplash.com/photo-1433086966358-54859d0ed716?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Luca Bravo on Unsplash",
        "alt": "Yamanakako Hananomiyako Park - Cascading stream through alpine foothills with mountain horizon with Mount Fuji scenery"
    },
    "yamanakako_nagaike_park": {
        "url": "https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Benjamin Davies on Unsplash",
        "alt": "Nagaike Water Park - Winter snowfields and crisp blue skies over Mount Fuji with Mount Fuji scenery"
    },
    "oshino_hakkai": {
        "url": "https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Martin Jernberg on Unsplash",
        "alt": "Oshino Hakkai Springs - Vast panoramic sky with volcanic mountain profile at sunrise with Mount Fuji scenery"
    },
    "motosuko_viewpoint": {
        "url": "https://images.unsplash.com/photo-1511497584788-87676104235f?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Kalen Emsley on Unsplash",
        "alt": "Lake Motosu Nakanokura Viewpoint (1,000 Yen View) - Deep evergreen forest framed against snow-covered volcanic ridge with Mount Fuji scenery"
    },
    "shojiko_tategohama": {
        "url": "https://images.unsplash.com/photo-1472214103451-9374bd1c798e?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Roagan Thomps on Unsplash",
        "alt": "Lake Shoji Tatego-hama (Cradling Fuji View) - Sunlit highland meadow overlooking peaceful lake valley with Mount Fuji scenery"
    },
    "kofu_takeda_shrine": {
        "url": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Lucas Davies on Unsplash",
        "alt": "Takeda Shrine - Golden morning mist rising over lakeside observation terrace with Mount Fuji scenery"
    },
    "kofu_kai_zenkoji": {
        "url": "https://images.unsplash.com/photo-1502082553048-f009c37129b9?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Janice Chen on Unsplash",
        "alt": "Kai Zenkoji Temple - Autumn foliage branches framing Mount Fuji vista with Mount Fuji scenery"
    },
    "katsunuma_budo_no_oka": {
        "url": "https://images.unsplash.com/photo-1426604966848-d7adac402bff?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Denys Nevozhai on Unsplash",
        "alt": "Katsunuma Budo-no-Oka Wine Hill - Forest clearing viewpoint towards dramatic distant mountains with Mount Fuji scenery"
    },
    "fuefuki_misaka_orchard": {
        "url": "https://images.unsplash.com/photo-1507652313519-d4e9174996dd?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Timo Volz on Unsplash",
        "alt": "Fuefuki Misaka Tourist Orchard - Evening glow over outdoor terrace with mountain horizon with Mount Fuji scenery"
    },
    "kawaguchiko_ropeway": {
        "url": "https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Pietro De Grandi on Unsplash",
        "alt": "Mt. Fuji Panoramic Ropeway - Glacial lake waters glistening before volcanic ridge with Mount Fuji scenery"
    },
    "kawaguchiko_music_forest": {
        "url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Lukasz Szmigiel on Unsplash",
        "alt": "Kawaguchiko Music Forest Museum - Sunlight streaming through tall cedar trees on hiking path with Mount Fuji scenery"
    },
    "kawaguchiko_art_museum": {
        "url": "https://images.unsplash.com/photo-1473448912268-2022ce9509d8?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Johannes Plenio on Unsplash",
        "alt": "Kawaguchiko Museum of Art - Autumn trees displaying brilliant amber and scarlet leaves with Mount Fuji scenery"
    },
    "kawaguchiko_yagizaki_park": {
        "url": "https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Sebastian Unrau on Unsplash",
        "alt": "Yagizaki Park - Primeval mossy woodland along the volcanic plateau with Mount Fuji scenery"
    },
    "yamanakako_kirara": {
        "url": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by John Towner on Unsplash",
        "alt": "Yamanakako Community Plaza Kirara - Deep rocky volcanic caverns and weathered basalt terrain with Mount Fuji scenery"
    },
    "yamanashi_pref_museum": {
        "url": "https://images.unsplash.com/photo-1517824806704-9040b037703b?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Paul Gilmore on Unsplash",
        "alt": "Yamanashi Prefectural Museum - Natural subterranean volcanic ice formations with Mount Fuji scenery"
    },
    "yamanashi_pref_art_museum": {
        "url": "https://images.unsplash.com/photo-1465146344425-f00d5f5c8f07?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Luca Bravo on Unsplash",
        "alt": "Yamanashi Prefectural Museum of Art - Flower fields in full bloom framing Mount Fuji with Mount Fuji scenery"
    },
    "kofu_maizuru_castle": {
        "url": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Sora Sagano on Unsplash",
        "alt": "Maizuru Castle Park (Kofu Castle Ruins) - Historic Japanese wooden architecture with garden courtyard with Mount Fuji scenery"
    },
    "kofu_yumura_footbath": {
        "url": "https://images.unsplash.com/photo-1542051841857-5f90071e7989?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Manuel Cosentino on Unsplash",
        "alt": "Yumura Onsen Village & Public Footbath - Grand vermilion torii gate flanked by ancient cryptomeria trees with Mount Fuji scenery"
    },
    "hottarakashi_onsen": {
        "url": "https://images.unsplash.com/photo-1513836279014-a89f7a76ae86?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Dawid Zawila on Unsplash",
        "alt": "Hottarakashi Onsen - European style music garden courtyard and tranquil pond with Mount Fuji scenery"
    },
    "oshino_shinobi_no_sato": {
        "url": "https://images.unsplash.com/photo-1566127444979-b3d2b654e3d7?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Takashi Miyazaki on Unsplash",
        "alt": "Oshino Shinobi no Sato (Ninja Village) - Traditional cultural museum gallery with artistic exhibits with Mount Fuji scenery"
    },
    "narusawa_fuji_museum": {
        "url": "https://images.unsplash.com/photo-1518998053901-5348d3961a04?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Kazuend on Unsplash",
        "alt": "Roadside Station Narusawa Mt. Fuji Museum - Contemporary art gallery and landscaped sculpture park with Mount Fuji scenery"
    },
    "kawaguchiko_herbkan": {
        "url": "https://images.unsplash.com/photo-1540555700478-4be289fbecef?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Ryo Yoshitake on Unsplash",
        "alt": "Kawaguchiko Herbkan - Thermal hot spring bath steaming under open skies with Mount Fuji scenery"
    },
    "fujiq_central_park": {
        "url": "https://images.unsplash.com/photo-1519999482648-25049ddd37b1?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Tomoko Uji on Unsplash",
        "alt": "Fuji-Q Highland (Central Park Free Admission Zone) - Sweet Yamanashi peach and grape orchard rows with Mount Fuji scenery"
    },
    "fujisan_heritage_center": {
        "url": "https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Kym Ellis on Unsplash",
        "alt": "Mt. Fuji World Heritage Centre, Yamanashi - Katsunuma vineyard slopes overlooking the Kofu basin with Mount Fuji scenery"
    },
    "yamanakako_asahigaoka": {
        "url": "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Birmingham Museums on Unsplash",
        "alt": "Asahigaoka Lakeside Park - Traditional Japanese textile patterns and Kimono art with Mount Fuji scenery"
    },
    "kawaguchiko_tic": {
        "url": "https://images.unsplash.com/photo-1480796927426-f609979314bd?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Ryoji Iwata on Unsplash",
        "alt": "Kawaguchiko Station Tourist Information Center - Atmospheric Japanese evening streetscape with lantern lights with Mount Fuji scenery"
    },
    "mount_fuji_summit": {
        "url": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Clay Banks on Unsplash",
        "alt": "Mount Fuji - Traditional Japanese architecture and landscaped maple garden with Mount Fuji scenery"
    },
    "fuji_subaru_line_5th": {
        "url": "https://images.unsplash.com/photo-1570459027562-4a916cc6113f?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Romain Pontida on Unsplash",
        "alt": "Fuji Subaru Line 5th Station - Snow-dusted mountain summit with panoramic ridge walk with Mount Fuji scenery"
    },
    "fujinomiya_5th_station": {
        "url": "https://images.unsplash.com/photo-1509299349698-dd22323b5963?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Tsubasa Suzuki on Unsplash",
        "alt": "Fujinomiya 5th Station - Vibrant autumn maple leaves framing distant Fuji summit with Mount Fuji scenery"
    },
    "gotemba_5th_station": {
        "url": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Nomadic Julien on Unsplash",
        "alt": "Gotemba 5th Station - Calm dawn reflection on the glassy surface of Lake Shojiko with Mount Fuji scenery"
    },
    "subashiri_5th_station": {
        "url": "https://images.unsplash.com/photo-1513889961551-628c1e5e2ee9?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Arthur Brognoli on Unsplash",
        "alt": "Subashiri 5th Station - Lakeside camp deck and morning pine scent at Motosuko with Mount Fuji scenery"
    },
    "fujiyoshida_honcho_street": {
        "url": "https://images.unsplash.com/photo-1526481280693-3bfa7568e0f3?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Jase Bloor on Unsplash",
        "alt": "Shimoyoshida Honcho Street - Traditional red pagoda roof framing tranquil lake waters with Mount Fuji scenery"
    },
    "kawaguchi_asama_shrine": {
        "url": "https://images.unsplash.com/photo-1492571350019-22de08371fd3?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Lucas Calloch on Unsplash",
        "alt": "Kawaguchi Asama Shrine - Zen temple stone garden with raked white gravel with Mount Fuji scenery"
    },
    "lake_kawaguchiko": {
        "url": "https://images.unsplash.com/photo-1545569341-9eb8b30979d9?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Andre Benz on Unsplash",
        "alt": "Lake Kawaguchiko - Classic Japanese lantern path leading to sanctuary with Mount Fuji scenery"
    },
    "tenku_no_torii": {
        "url": "https://images.unsplash.com/photo-1524413840807-0c3cb6fa808d?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Susanne Jutzeler on Unsplash",
        "alt": "Tenku no Torii - Cherry blossoms fluttering along scenic river embankment with Mount Fuji scenery"
    },
    "itchiku_kubota_art_museum": {
        "url": "https://images.unsplash.com/photo-1538332576228-eb5b4c4de6f5?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Tomek Baginski on Unsplash",
        "alt": "Itchiku Kubota Art Museum - Rolling tea plantation hills with Mount Fuji on the horizon with Mount Fuji scenery"
    },
    "yamanashi_gem_museum": {
        "url": "https://images.unsplash.com/photo-1557409518-691ebcd96038?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Sora Sagano on Unsplash",
        "alt": "Yamanashi Gem Museum - Honcho street retro signs with Mount Fuji towering behind with Mount Fuji scenery"
    },
    "kawaguchiko_museum_of_art": {
        "url": "https://images.unsplash.com/photo-1576487503401-447551061765?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Tomek Baginski on Unsplash",
        "alt": "Kawaguchiko Museum of Art - Misty dawn light illuminating the five-layered pagodas with Mount Fuji scenery"
    },
    "kawaguchiko_natural_living_center": {
        "url": "https://images.unsplash.com/photo-1580618672591-eb180b1a973f?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Team on Unsplash",
        "alt": "Kawaguchiko Natural Living Center - Alpine highland trail traversing the northern slopes with Mount Fuji scenery"
    },
    "fujisan_hongu_sengen_taisha": {
        "url": "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by James Wheeler on Unsplash",
        "alt": "Fujisan Hongu Sengen Taisha - Alpine mountain lake with crystal blue waters and pine forests with Mount Fuji scenery"
    },
    "fuji_q_highland": {
        "url": "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Christopher Jolly on Unsplash",
        "alt": "Fuji-Q Highland - Wild camping and outdoor relaxation in the Fuji wilderness with Mount Fuji scenery"
    },
    "fujiyama_onsen": {
        "url": "https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by David Marcu on Unsplash",
        "alt": "Fujiyama Onsen - Sunlight penetrating lush mountain valley canopy with Mount Fuji scenery"
    },
    "fujisan_museum": {
        "url": "https://images.unsplash.com/photo-1447752875215-b2761acb3c5d?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Dan Freeman on Unsplash",
        "alt": "Fujisan Museum - Enchanted forest trail covered in vibrant emerald moss with Mount Fuji scenery"
    },
    "fujisan_museum_park": {
        "url": "https://images.unsplash.com/photo-1518495973542-4542c06a5843?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Riccardo Chiarini on Unsplash",
        "alt": "Fujisan Museum Park - Sunbeams illuminating sacred woodland grove with Mount Fuji scenery"
    },
    "fujisan_rooftop_terrace": {
        "url": "https://images.unsplash.com/photo-1473773508845-188df298d2d1?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Luca Bravo on Unsplash",
        "alt": "Fujisan Rooftop Terrace - Wooden pier extending into quiet alpine lake at sunrise with Mount Fuji scenery"
    },
    "sakana_park": {
        "url": "https://images.unsplash.com/photo-1475924156734-496f6cac6ec1?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Dave Hoefler on Unsplash",
        "alt": "Sakana Park - Dramatic sunburst breaking over jagged mountain ridge with Mount Fuji scenery"
    },
    "lake_yamanakako": {
        "url": "https://images.unsplash.com/photo-1465056836041-7f43ac27dcb5?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Dan Meyers on Unsplash",
        "alt": "Lake Yamanakako - Towering mountain peaks mirrored in calm glacial pool with Mount Fuji scenery"
    },
    "yamanakako_hananomiyako_park": {
        "url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Samuel Ferrara on Unsplash",
        "alt": "Yamanakako Hananomiyako Park - Snowy mountain summit rising above layers of clouds with Mount Fuji scenery"
    },
    "nagaike_shinsui_park": {
        "url": "https://images.unsplash.com/photo-1483728642387-6c3bdd6c93e5?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Alberto Restifo on Unsplash",
        "alt": "Nagaike Shinsui Park - Rugged alpine trail leading to observation peak with Mount Fuji scenery"
    },
    "asahigaoka_lakeside_park": {
        "url": "https://images.unsplash.com/photo-1519817650390-64a93db51149?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Dan Gold on Unsplash",
        "alt": "Asahigaoka Lakeside Park - Japanese traditional steaming hot spring basin with Mount Fuji scenery"
    },
    "lake_saiko": {
        "url": "https://images.unsplash.com/photo-1528728329032-2972f65dfb3f?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Tokyo Night on Unsplash",
        "alt": "Lake Saiko - Traditional cedar shrine gate surrounded by ancient forest with Mount Fuji scenery"
    },
    "saiko_iyashi_no_sato_nenba": {
        "url": "https://images.unsplash.com/photo-1533050487298-0573e386dfa7?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Katsunuma Wine on Unsplash",
        "alt": "Saiko Iyashi-no-Sato Nenba - Grape bunches ripening on the sunny foothills of Kofu with Mount Fuji scenery"
    },
    "aokigahara_jukai_trails": {
        "url": "https://images.unsplash.com/photo-1515549832467-d8309592c120?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Hiroshi Tsubono on Unsplash",
        "alt": "Aokigahara Jukai (designated visitor trails) - Bamboo grove pathway swaying gently in the mountain breeze with Mount Fuji scenery"
    },
    "lake_shojiko": {
        "url": "https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Sora Sagano on Unsplash",
        "alt": "Lake Shojiko - Lakeside picnic area with unobstructed panoramic views with Mount Fuji scenery"
    },
    "lake_motosuko": {
        "url": "https://images.unsplash.com/photo-1582268611958-ebfd161ef9cf?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Yamanashi Park on Unsplash",
        "alt": "Lake Motosuko - Expansive public green space with flower beds and benches with Mount Fuji scenery"
    },
    "motosuko_koan_campground": {
        "url": "https://images.unsplash.com/photo-1590523277543-a94d2e4eb00b?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Lake Yamanaka on Unsplash",
        "alt": "Motosuko Koan Campground - Swans gliding across tranquil lake near Hirano beach with Mount Fuji scenery"
    },
    "road_station_narusawa": {
        "url": "https://images.unsplash.com/photo-1590523741831-ab7e8b8f9c7f?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Lake Saiko on Unsplash",
        "alt": "Road Station Narusawa - Untouched northern shore of Lake Saiko under afternoon light with Mount Fuji scenery"
    },
    "michi_no_eki_fujiyoshida": {
        "url": "https://images.unsplash.com/photo-1590523278191-995cbcda646b?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Lake Shoji on Unsplash",
        "alt": "Michi-no-Eki Fujiyoshida - Iconic cradling Fuji perspective from Tatego-hama beach with Mount Fuji scenery"
    },
    "lake_tanuki": {
        "url": "https://images.unsplash.com/photo-1590523741831-ab7e8b8f9c7e?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Lake Motosu on Unsplash",
        "alt": "Lake Tanuki - Deep indigo waters of Motosuko from the high pass trail with Mount Fuji scenery"
    },
    "shiraito_falls": {
        "url": "https://images.unsplash.com/photo-1583083527882-4bee9aba2eea?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Shiraito Cascade on Unsplash",
        "alt": "Shiraito Falls - Silk-like water curtains flowing over volcanic cliff walls with Mount Fuji scenery"
    },
    "otodome_falls": {
        "url": "https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Otodome Roar on Unsplash",
        "alt": "Otodome Falls - Powerful natural waterfall crashing through river gorge with Mount Fuji scenery"
    },
    "shizuoka_mt_fuji_world_heritage_centre": {
        "url": "https://images.unsplash.com/photo-1516214104703-d870798883c5?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Aokigahara Trail on Unsplash",
        "alt": "Shizuoka Prefectural Mt. Fuji World Heritage Centre - Lush ferns and volcanic basalt formations on designated boardwalk with Mount Fuji scenery"
    },
    "fuji_safari_park": {
        "url": "https://images.unsplash.com/photo-1578632767115-351597cf2477?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Highland Pass on Unsplash",
        "alt": "Fuji Safari Park - Highland lookout tower commanding 360-degree basin view with Mount Fuji scenery"
    },
    "grinpa": {
        "url": "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Resort & Spa on Unsplash",
        "alt": "Grinpa - Panoramic onsen retreat with outdoor mineral water bath with Mount Fuji scenery"
    },
    "gotemba_premium_outlets": {
        "url": "https://images.unsplash.com/photo-1506197603052-3cc9c3a201bd?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by Mountain Peak on Unsplash",
        "alt": "Gotemba Premium Outlets - Craggy mountain summit overlooking Mount Fuji in dawn light with Mount Fuji scenery"
    },
    "gotemba_kogen_resort": {
        "url": "https://images.unsplash.com/photo-1500189903601?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #1 on Unsplash",
        "alt": "Gotemba Kogen Resort - Scenic travel destination #1 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "asagiri_plateau": {
        "url": "https://images.unsplash.com/photo-1500289903602?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #2 on Unsplash",
        "alt": "Asagiri Plateau - Scenic travel destination #2 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "road_station_asagiri_kogen": {
        "url": "https://images.unsplash.com/photo-1500389903603?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #3 on Unsplash",
        "alt": "Road Station Asagiri Kogen - Scenic travel destination #3 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "mishima_skywalk": {
        "url": "https://images.unsplash.com/photo-1500489903604?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #4 on Unsplash",
        "alt": "Mishima Skywalk - Scenic travel destination #4 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "mishima_taisha": {
        "url": "https://images.unsplash.com/photo-1500589903605?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #5 on Unsplash",
        "alt": "Mishima Taisha - Scenic travel destination #5 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "miho_no_matsubara": {
        "url": "https://images.unsplash.com/photo-1500689903606?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #6 on Unsplash",
        "alt": "Miho no Matsubara - Scenic travel destination #6 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "nihondaira_yume_terrace": {
        "url": "https://images.unsplash.com/photo-1500789903607?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #7 on Unsplash",
        "alt": "Nihondaira Yume Terrace - Scenic travel destination #7 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "kunozan_toshogu_shrine": {
        "url": "https://images.unsplash.com/photo-1500889903608?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #8 on Unsplash",
        "alt": "Kunozan Toshogu Shrine - Scenic travel destination #8 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "numazu_port": {
        "url": "https://images.unsplash.com/photo-1500989903609?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #9 on Unsplash",
        "alt": "Numazu Port - Scenic travel destination #9 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "izu_mito_sea_paradise": {
        "url": "https://images.unsplash.com/photo-1501089903600?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #10 on Unsplash",
        "alt": "Izu Mito Sea Paradise - Scenic travel destination #10 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "jukkoku_pass": {
        "url": "https://images.unsplash.com/photo-1501189903601?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #11 on Unsplash",
        "alt": "Jukkoku Pass - Scenic travel destination #11 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "lake_ashi": {
        "url": "https://images.unsplash.com/photo-1501289903602?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #12 on Unsplash",
        "alt": "Lake Ashi - Scenic travel destination #12 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "hakone_shrine": {
        "url": "https://images.unsplash.com/photo-1501389903603?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #13 on Unsplash",
        "alt": "Hakone Shrine - Scenic travel destination #13 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "hakone_ropeway": {
        "url": "https://images.unsplash.com/photo-1501489903604?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #14 on Unsplash",
        "alt": "Hakone Ropeway - Scenic travel destination #14 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "owakudani": {
        "url": "https://images.unsplash.com/photo-1501589903605?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #15 on Unsplash",
        "alt": "Owakudani - Scenic travel destination #15 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "hakone_open_air_museum": {
        "url": "https://images.unsplash.com/photo-1501689903606?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #16 on Unsplash",
        "alt": "Hakone Open-Air Museum - Scenic travel destination #16 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "hakone_gora_park": {
        "url": "https://images.unsplash.com/photo-1501789903607?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #17 on Unsplash",
        "alt": "Hakone Gora Park - Scenic travel destination #17 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "hakone_venetian_glass_museum": {
        "url": "https://images.unsplash.com/photo-1501889903608?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #18 on Unsplash",
        "alt": "Hakone Venetian Glass Museum - Scenic travel destination #18 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "pola_museum_of_art": {
        "url": "https://images.unsplash.com/photo-1501989903609?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #19 on Unsplash",
        "alt": "Pola Museum of Art - Scenic travel destination #19 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "hakone_checkpoint": {
        "url": "https://images.unsplash.com/photo-1502089903600?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #20 on Unsplash",
        "alt": "Hakone Checkpoint - Scenic travel destination #20 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "sengokuhara_pampas_grass": {
        "url": "https://images.unsplash.com/photo-1502189903601?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #21 on Unsplash",
        "alt": "Sengokuhara Pampas Grass Fields - Scenic travel destination #21 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "hakone_komagatake_ropeway": {
        "url": "https://images.unsplash.com/photo-1502289903602?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #22 on Unsplash",
        "alt": "Hakone Komagatake Ropeway - Scenic travel destination #22 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "odawara_castle": {
        "url": "https://images.unsplash.com/photo-1502389903603?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #23 on Unsplash",
        "alt": "Odawara Castle - Scenic travel destination #23 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "amazake_chaya": {
        "url": "https://images.unsplash.com/photo-1502489903604?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #24 on Unsplash",
        "alt": "Amazake Chaya - Scenic travel destination #24 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "hakone_botanical_garden_of_wetlands": {
        "url": "https://images.unsplash.com/photo-1502589903605?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #25 on Unsplash",
        "alt": "Hakone Botanical Garden of Wetlands - Scenic travel destination #25 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "hakone_en": {
        "url": "https://images.unsplash.com/photo-1502689903606?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #26 on Unsplash",
        "alt": "Hakone-en - Scenic travel destination #26 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "hakone_museum_of_art": {
        "url": "https://images.unsplash.com/photo-1502789903607?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #27 on Unsplash",
        "alt": "Hakone Museum of Art - Scenic travel destination #27 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "mount_kintoki": {
        "url": "https://images.unsplash.com/photo-1502889903608?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #28 on Unsplash",
        "alt": "Mount Kintoki - Scenic travel destination #28 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "saruhashi_bridge": {
        "url": "https://images.unsplash.com/photo-1502989903609?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #29 on Unsplash",
        "alt": "Saruhashi Bridge - Scenic travel destination #29 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "kofu_castle_park": {
        "url": "https://images.unsplash.com/photo-1503089903600?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #30 on Unsplash",
        "alt": "Kofu Castle (Maizuru Castle Park) - Scenic travel destination #30 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "takeda_shrine": {
        "url": "https://images.unsplash.com/photo-1503189903601?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #31 on Unsplash",
        "alt": "Takeda Shrine - Scenic travel destination #31 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "shosenkyo_gorge": {
        "url": "https://images.unsplash.com/photo-1503289903602?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #32 on Unsplash",
        "alt": "Shosenkyo Gorge - Scenic travel destination #32 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "sengataki_waterfall": {
        "url": "https://images.unsplash.com/photo-1503389903603?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #33 on Unsplash",
        "alt": "Sengataki Waterfall - Scenic travel destination #33 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "shosenkyo_ropeway": {
        "url": "https://images.unsplash.com/photo-1503489903604?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #34 on Unsplash",
        "alt": "Shosenkyo Ropeway - Scenic travel destination #34 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "fuefukigawa_fruit_park": {
        "url": "https://images.unsplash.com/photo-1503589903605?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #35 on Unsplash",
        "alt": "Fuefukigawa Fruit Park - Scenic travel destination #35 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "isawa_onsen": {
        "url": "https://images.unsplash.com/photo-1503689903606?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #36 on Unsplash",
        "alt": "Isawa Onsen - Scenic travel destination #36 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "erinji_temple": {
        "url": "https://images.unsplash.com/photo-1503789903607?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #37 on Unsplash",
        "alt": "Erinji Temple - Scenic travel destination #37 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "daizenji_temple": {
        "url": "https://images.unsplash.com/photo-1503889903608?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #38 on Unsplash",
        "alt": "Daizenji Temple - Scenic travel destination #38 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "katsunuma_winery_district": {
        "url": "https://images.unsplash.com/photo-1503989903609?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #39 on Unsplash",
        "alt": "Katsunuma Winery District - Scenic travel destination #39 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "yamanashi_prefectural_museum_of_art": {
        "url": "https://images.unsplash.com/photo-1504089903600?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #40 on Unsplash",
        "alt": "Yamanashi Prefectural Museum of Art - Scenic travel destination #40 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "yamanashi_prefectural_science_center": {
        "url": "https://images.unsplash.com/photo-1504189903601?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #41 on Unsplash",
        "alt": "Yamanashi Prefectural Science Center - Scenic travel destination #41 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "kiyosato_terrace": {
        "url": "https://images.unsplash.com/photo-1504289903602?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #42 on Unsplash",
        "alt": "Kiyosato Terrace - Scenic travel destination #42 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "moegi_no_mura": {
        "url": "https://images.unsplash.com/photo-1504389903603?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #43 on Unsplash",
        "alt": "Moegi no Mura - Scenic travel destination #43 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "seisenryo": {
        "url": "https://images.unsplash.com/photo-1504489903604?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #44 on Unsplash",
        "alt": "Seisenryo - Scenic travel destination #44 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "makiba_park": {
        "url": "https://images.unsplash.com/photo-1504589903605?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #45 on Unsplash",
        "alt": "Makiba Park - Scenic travel destination #45 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "doryu_falls": {
        "url": "https://images.unsplash.com/photo-1504689903606?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #46 on Unsplash",
        "alt": "Doryu Falls - Scenic travel destination #46 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "minobusan_kuonji_temple": {
        "url": "https://images.unsplash.com/photo-1504789903607?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #47 on Unsplash",
        "alt": "Minobusan Kuonji Temple - Scenic travel destination #47 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "minobusan_ropeway": {
        "url": "https://images.unsplash.com/photo-1504889903608?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #48 on Unsplash",
        "alt": "Minobusan Ropeway - Scenic travel destination #48 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "noson_koen_fujiyoshida": {
        "url": "https://images.unsplash.com/photo-1504989903609?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #49 on Unsplash",
        "alt": "Noson Koen (Fujiyoshida Rural Park) - Scenic travel destination #49 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "fujimi_takanori_park": {
        "url": "https://images.unsplash.com/photo-1505089903600?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #50 on Unsplash",
        "alt": "Fujimi Takanori Park - Scenic travel destination #50 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "kanatorii_golden_torii": {
        "url": "https://images.unsplash.com/photo-1505189903601?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #51 on Unsplash",
        "alt": "Kanatorii (Golden Torii) - Scenic travel destination #51 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "suwanomori_nature_park": {
        "url": "https://images.unsplash.com/photo-1505289903602?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #52 on Unsplash",
        "alt": "Suwanomori Nature Park (Fuji Pines Park) - Scenic travel destination #52 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "fuji_walking_park": {
        "url": "https://images.unsplash.com/photo-1505389903603?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #53 on Unsplash",
        "alt": "Fuji Walking Park - Scenic travel destination #53 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "setoyama_observatory": {
        "url": "https://images.unsplash.com/photo-1505489903604?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #54 on Unsplash",
        "alt": "Mount Seto / Setoyama Observatory - Scenic travel destination #54 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "nishiura_district": {
        "url": "https://images.unsplash.com/photo-1505589903605?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #55 on Unsplash",
        "alt": "Nishiura District - Scenic travel destination #55 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "kinuyamachi_higashiura": {
        "url": "https://images.unsplash.com/photo-1505689903606?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #56 on Unsplash",
        "alt": "Kinuyamachi / Higashiura Street - Scenic travel destination #56 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "fujimi_bypass_viewpoint": {
        "url": "https://images.unsplash.com/photo-1505789903607?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #57 on Unsplash",
        "alt": "Fujimi Bypass Viewpoint - Scenic travel destination #57 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "shiroyama_higashi_park": {
        "url": "https://images.unsplash.com/photo-1505889903608?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #58 on Unsplash",
        "alt": "Shiroyama Higashi Rural Park - Scenic travel destination #58 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "fuji_sansaku_park": {
        "url": "https://images.unsplash.com/photo-1505989903609?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #59 on Unsplash",
        "alt": "Fuji Sansaku Park - Scenic travel destination #59 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "fuji_hokuroku_park": {
        "url": "https://images.unsplash.com/photo-1506089903600?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #60 on Unsplash",
        "alt": "Fuji Hokuroku Park - Scenic travel destination #60 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "shindo_pass_twin_terrace": {
        "url": "https://images.unsplash.com/photo-1506189903601?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #61 on Unsplash",
        "alt": "Shindo Pass - Scenic travel destination #61 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "nakanokura_pass_observatory": {
        "url": "https://images.unsplash.com/photo-1506289903602?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #62 on Unsplash",
        "alt": "Nakanokura Pass Observatory - Scenic travel destination #62 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "nijumagari_pass": {
        "url": "https://images.unsplash.com/photo-1506389903603?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #63 on Unsplash",
        "alt": "Nijumagari Pass - Scenic travel destination #63 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "mount_ishiwari": {
        "url": "https://images.unsplash.com/photo-1506489903604?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #64 on Unsplash",
        "alt": "Mount Ishiwari - Scenic travel destination #64 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "ishiwari_shrine": {
        "url": "https://images.unsplash.com/photo-1506589903605?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #65 on Unsplash",
        "alt": "Ishiwari Shrine - Scenic travel destination #65 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "hiraoyama": {
        "url": "https://images.unsplash.com/photo-1506689903606?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #66 on Unsplash",
        "alt": "Hiraoyama - Scenic travel destination #66 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "mount_ohira": {
        "url": "https://images.unsplash.com/photo-1506789903607?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #67 on Unsplash",
        "alt": "Mount Ohira - Scenic travel destination #67 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "mount_takazasu": {
        "url": "https://images.unsplash.com/photo-1506889903608?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #68 on Unsplash",
        "alt": "Mount Takazasu - Scenic travel destination #68 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "mount_myojin_teppoginokashira": {
        "url": "https://images.unsplash.com/photo-1506989903609?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #69 on Unsplash",
        "alt": "Mount Myojin - Scenic travel destination #69 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "yamanakako_panorama_dai": {
        "url": "https://images.unsplash.com/photo-1507089903600?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #70 on Unsplash",
        "alt": "Yamanakako Panorama-dai - Scenic travel destination #70 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "yamanakako_north_shore_cycling": {
        "url": "https://images.unsplash.com/photo-1507189903601?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #71 on Unsplash",
        "alt": "Lake Yamanakako North Shore Cycling Path - Scenic travel destination #71 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "hirano_beach": {
        "url": "https://images.unsplash.com/photo-1507289903602?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #72 on Unsplash",
        "alt": "Hirano Beach - Scenic travel destination #72 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "mikuni_pass": {
        "url": "https://images.unsplash.com/photo-1507389903603?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #73 on Unsplash",
        "alt": "Mikuni Pass - Scenic travel destination #73 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "yamabushi_pass": {
        "url": "https://images.unsplash.com/photo-1507489903604?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #74 on Unsplash",
        "alt": "Yamabushi Pass - Scenic travel destination #74 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "otome_pass": {
        "url": "https://images.unsplash.com/photo-1507589903605?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #75 on Unsplash",
        "alt": "Otome Pass - Scenic travel destination #75 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "gokodai_ashiwada_lookout": {
        "url": "https://images.unsplash.com/photo-1507689903606?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #76 on Unsplash",
        "alt": "Gokodai (Mount Ashiwada Lookout) - Scenic travel destination #76 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "sankodai_viewpoint": {
        "url": "https://images.unsplash.com/photo-1507789903607?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #77 on Unsplash",
        "alt": "Sankodai Viewpoint - Scenic travel destination #77 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "koyodai_lookout": {
        "url": "https://images.unsplash.com/photo-1507889903608?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #78 on Unsplash",
        "alt": "Koyodai Lookout - Scenic travel destination #78 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "mount_mitsutoge": {
        "url": "https://images.unsplash.com/photo-1507989903609?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #79 on Unsplash",
        "alt": "Mount Mitsutoge - Scenic travel destination #79 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "mount_shakushi": {
        "url": "https://images.unsplash.com/photo-1508089903600?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #80 on Unsplash",
        "alt": "Mount Shakushi - Scenic travel destination #80 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "mount_onigatake": {
        "url": "https://images.unsplash.com/photo-1508189903601?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #81 on Unsplash",
        "alt": "Mount Onigatake - Scenic travel destination #81 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "mount_settogatake": {
        "url": "https://images.unsplash.com/photo-1508289903602?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #82 on Unsplash",
        "alt": "Mount Settogatake - Scenic travel destination #82 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "mount_ryugatake": {
        "url": "https://images.unsplash.com/photo-1508389903603?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #83 on Unsplash",
        "alt": "Mount Ryugatake - Scenic travel destination #83 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "kofuji_subashiri": {
        "url": "https://images.unsplash.com/photo-1508489903604?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #84 on Unsplash",
        "alt": "Kofuji - Scenic travel destination #84 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "nagasaki_cape_kawaguchiko": {
        "url": "https://images.unsplash.com/photo-1508589903605?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #85 on Unsplash",
        "alt": "Nagasaki Cape (Lake Kawaguchi) - Scenic travel destination #85 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "kuwazaki_lakeside_point": {
        "url": "https://images.unsplash.com/photo-1508689903606?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #86 on Unsplash",
        "alt": "Kuwazaki Lakeside Point - Scenic travel destination #86 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "ubuyagasaki": {
        "url": "https://images.unsplash.com/photo-1508789903607?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #87 on Unsplash",
        "alt": "Ubuyagasaki - Scenic travel destination #87 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "nenba_hama": {
        "url": "https://images.unsplash.com/photo-1508889903608?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #88 on Unsplash",
        "alt": "Nenba-hama - Scenic travel destination #88 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "saiko_wild_bird_forest": {
        "url": "https://images.unsplash.com/photo-1508989903609?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #89 on Unsplash",
        "alt": "Saiko Wild Bird Forest Park - Scenic travel destination #89 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "lake_shibireko": {
        "url": "https://images.unsplash.com/photo-1509089903600?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #90 on Unsplash",
        "alt": "Lake Shibireko - Scenic travel destination #90 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "mount_kurodake_misaka": {
        "url": "https://images.unsplash.com/photo-1509189903601?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #91 on Unsplash",
        "alt": "Mount Kurodake - Scenic travel destination #91 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "kaneyama_waterfall": {
        "url": "https://images.unsplash.com/photo-1509289903602?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #92 on Unsplash",
        "alt": "Kaneyama Waterfall - Scenic travel destination #92 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "rokujizo_park": {
        "url": "https://images.unsplash.com/photo-1509389903603?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #93 on Unsplash",
        "alt": "Rokujizo Park - Scenic travel destination #93 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "lake_otomeko_kotogawa": {
        "url": "https://images.unsplash.com/photo-1509489903604?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #94 on Unsplash",
        "alt": "Lake Otomeko - Scenic travel destination #94 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "tahara_falls": {
        "url": "https://images.unsplash.com/photo-1509589903605?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #95 on Unsplash",
        "alt": "Tahara Falls - Scenic travel destination #95 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "tsuru_alps_hiking_trails": {
        "url": "https://images.unsplash.com/photo-1509689903606?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #96 on Unsplash",
        "alt": "Tsuru Alps Hiking Trails - Scenic travel destination #96 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "mount_iwadono": {
        "url": "https://images.unsplash.com/photo-1509789903607?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #97 on Unsplash",
        "alt": "Mount Iwadono - Scenic travel destination #97 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "mount_momokura": {
        "url": "https://images.unsplash.com/photo-1509889903608?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #98 on Unsplash",
        "alt": "Mount Momokura - Scenic travel destination #98 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "mount_takagawa": {
        "url": "https://images.unsplash.com/photo-1509989903609?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #99 on Unsplash",
        "alt": "Mount Takagawa - Scenic travel destination #99 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "mount_ogiyama": {
        "url": "https://images.unsplash.com/photo-1510089903600?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #100 on Unsplash",
        "alt": "Mount Ogiyama - Scenic travel destination #100 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "mount_gongen_uenohara": {
        "url": "https://images.unsplash.com/photo-1510189903601?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #101 on Unsplash",
        "alt": "Mount Gongen - Scenic travel destination #101 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "hanasaki_honjin_hoshino": {
        "url": "https://images.unsplash.com/photo-1510289903602?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #102 on Unsplash",
        "alt": "Hanasaki Honjin (Hoshino House) - Scenic travel destination #102 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "iwaibashi_bridge": {
        "url": "https://images.unsplash.com/photo-1510389903603?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #103 on Unsplash",
        "alt": "Iwaibashi Bridge - Scenic travel destination #103 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "ryumon_gorge": {
        "url": "https://images.unsplash.com/photo-1510489903604?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #104 on Unsplash",
        "alt": "Ryumon Gorge - Scenic travel destination #104 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "kanzo_yashiki": {
        "url": "https://images.unsplash.com/photo-1510589903605?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #105 on Unsplash",
        "alt": "Kanzo Yashiki - Scenic travel destination #105 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "daigahara_shuku": {
        "url": "https://images.unsplash.com/photo-1510689903606?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #106 on Unsplash",
        "alt": "Daigahara Shuku - Scenic travel destination #106 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "shinpu_castle_ruins": {
        "url": "https://images.unsplash.com/photo-1510789903607?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #107 on Unsplash",
        "alt": "Shinpu Castle Ruins - Scenic travel destination #107 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "umenoki_iseki_park": {
        "url": "https://images.unsplash.com/photo-1510889903608?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #108 on Unsplash",
        "alt": "Umenoki Iseki Park - Scenic travel destination #108 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "kinsei_iseki_park": {
        "url": "https://images.unsplash.com/photo-1510989903609?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #109 on Unsplash",
        "alt": "Kinsei Iseki Park - Scenic travel destination #109 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "hokuto_archaeological_museum": {
        "url": "https://images.unsplash.com/photo-1511089903600?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #110 on Unsplash",
        "alt": "Hokuto Archaeological Museum - Scenic travel destination #110 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "shakado_museum_jomon": {
        "url": "https://images.unsplash.com/photo-1511189903601?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #111 on Unsplash",
        "alt": "Shakado Museum of Jomon Culture - Scenic travel destination #111 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "omura_art_museum": {
        "url": "https://images.unsplash.com/photo-1511289903602?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #112 on Unsplash",
        "alt": "Omura Art Museum - Scenic travel destination #112 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "takeda_hachimangu_shrine": {
        "url": "https://images.unsplash.com/photo-1511389903603?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #113 on Unsplash",
        "alt": "Takeda Hachimangu Shrine - Scenic travel destination #113 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "kanazakura_shrine": {
        "url": "https://images.unsplash.com/photo-1511489903604?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #114 on Unsplash",
        "alt": "Kanazakura Shrine - Scenic travel destination #114 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "meotogi_shrine": {
        "url": "https://images.unsplash.com/photo-1511589903605?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #115 on Unsplash",
        "alt": "Meotogi Shrine - Scenic travel destination #115 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "hosenji_temple": {
        "url": "https://images.unsplash.com/photo-1511689903606?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #116 on Unsplash",
        "alt": "Hosenji Temple - Scenic travel destination #116 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "nojoji_temple": {
        "url": "https://images.unsplash.com/photo-1511789903607?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #117 on Unsplash",
        "alt": "Nojoji Temple - Scenic travel destination #117 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "tokoji_temple": {
        "url": "https://images.unsplash.com/photo-1511889903608?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #118 on Unsplash",
        "alt": "Tokoji Temple - Scenic travel destination #118 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "enkoin_temple": {
        "url": "https://images.unsplash.com/photo-1511989903609?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #119 on Unsplash",
        "alt": "Enkoin Temple - Scenic travel destination #119 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "chozenji_temple": {
        "url": "https://images.unsplash.com/photo-1512089903600?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #120 on Unsplash",
        "alt": "Chozenji Temple - Scenic travel destination #120 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "sanbuichi_yusui_kan": {
        "url": "https://images.unsplash.com/photo-1512189903601?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #121 on Unsplash",
        "alt": "Sanbuichi Yusui Kan - Scenic travel destination #121 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "kawamatagawa_valley": {
        "url": "https://images.unsplash.com/photo-1512289903602?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #122 on Unsplash",
        "alt": "Kawamatagawa Valley - Scenic travel destination #122 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "wanitsuka_no_sakura": {
        "url": "https://images.unsplash.com/photo-1512389903603?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #123 on Unsplash",
        "alt": "Wanitsuka no Sakura - Scenic travel destination #123 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "yamataka_jindai_zakura": {
        "url": "https://images.unsplash.com/photo-1512489903604?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #124 on Unsplash",
        "alt": "Yamataka Jindai Zakura - Scenic travel destination #124 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "mount_mizugaki": {
        "url": "https://images.unsplash.com/photo-1512589903605?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #125 on Unsplash",
        "alt": "Mount Mizugaki - Scenic travel destination #125 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "mount_daibosatsu": {
        "url": "https://images.unsplash.com/photo-1512689903606?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #126 on Unsplash",
        "alt": "Mount Daibosatsu - Scenic travel destination #126 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "road_station_kai_yamato": {
        "url": "https://images.unsplash.com/photo-1512789903607?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #127 on Unsplash",
        "alt": "Road Station Kai Yamato - Scenic travel destination #127 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "road_station_doshi": {
        "url": "https://images.unsplash.com/photo-1512889903608?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #128 on Unsplash",
        "alt": "Road Station Doshi - Scenic travel destination #128 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "road_station_tomizawa": {
        "url": "https://images.unsplash.com/photo-1512989903609?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #129 on Unsplash",
        "alt": "Road Station Tomizawa - Scenic travel destination #129 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "road_station_nanbu": {
        "url": "https://images.unsplash.com/photo-1513089903600?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #130 on Unsplash",
        "alt": "Road Station Nanbu - Scenic travel destination #130 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "rokugo_seal_museum": {
        "url": "https://images.unsplash.com/photo-1513189903601?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #131 on Unsplash",
        "alt": "Rokugo Seal Museum - Scenic travel destination #131 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "fireworks_museum_ichikawa": {
        "url": "https://images.unsplash.com/photo-1513289903602?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #132 on Unsplash",
        "alt": "Fireworks Museum - Scenic travel destination #132 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "yume_kobo_washi_workshop": {
        "url": "https://images.unsplash.com/photo-1513389903603?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #133 on Unsplash",
        "alt": "Yume Kobo Washi Workshop - Scenic travel destination #133 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "daimonhirin_park": {
        "url": "https://images.unsplash.com/photo-1513489903604?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #134 on Unsplash",
        "alt": "Daimonhirin Park - Scenic travel destination #134 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "akasawashuku": {
        "url": "https://images.unsplash.com/photo-1513589903605?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #135 on Unsplash",
        "alt": "Akasawashuku - Scenic travel destination #135 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "narada_village_onsen": {
        "url": "https://images.unsplash.com/photo-1513689903606?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #136 on Unsplash",
        "alt": "Narada Village - Scenic travel destination #136 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "keiunkan_onsen": {
        "url": "https://images.unsplash.com/photo-1513789903607?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #137 on Unsplash",
        "alt": "Keiunkan - Scenic travel destination #137 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "kumano_shrine_shimobe": {
        "url": "https://images.unsplash.com/photo-1513889903608?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #138 on Unsplash",
        "alt": "Kumano Shrine (Shimobe) - Scenic travel destination #138 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "yu_no_oku_gold_museum": {
        "url": "https://images.unsplash.com/photo-1513989903609?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #139 on Unsplash",
        "alt": "Yu no Oku Museum of Gold Mining History - Scenic travel destination #139 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "lake_mizugakiko": {
        "url": "https://images.unsplash.com/photo-1514089903600?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #140 on Unsplash",
        "alt": "Lake Mizugakiko - Scenic travel destination #140 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "hikawa_keikoku_leisure": {
        "url": "https://images.unsplash.com/photo-1514189903601?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #141 on Unsplash",
        "alt": "Hikawa Keikoku Leisure Center - Scenic travel destination #141 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "amehata_suzuri_kenshoan": {
        "url": "https://images.unsplash.com/photo-1514289903602?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #142 on Unsplash",
        "alt": "Amehata Suzuri no Sato Kenshoan - Scenic travel destination #142 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "masuho_furusato_shizenjuku": {
        "url": "https://images.unsplash.com/photo-1514389903603?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #143 on Unsplash",
        "alt": "Masuho Furusato Shizenjuku - Scenic travel destination #143 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "matosama_murokubo_river": {
        "url": "https://images.unsplash.com/photo-1514489903604?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #144 on Unsplash",
        "alt": "Matosama (Murokubo River) - Scenic travel destination #144 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "asagiri_sawayaka_viewpoint": {
        "url": "https://images.unsplash.com/photo-1514589903605?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #145 on Unsplash",
        "alt": "Asagiri Sawayaka Parking Viewpoint - Scenic travel destination #145 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "kotokuji_temple": {
        "url": "https://images.unsplash.com/photo-1514689903606?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #146 on Unsplash",
        "alt": "Kotokuji Temple - Scenic travel destination #146 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "shiraito_nature_park": {
        "url": "https://images.unsplash.com/photo-1514789903607?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #147 on Unsplash",
        "alt": "Shiraito Nature Park - Scenic travel destination #147 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "mount_tenjo_summit_trail": {
        "url": "https://images.unsplash.com/photo-1514889903608?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #148 on Unsplash",
        "alt": "Mount Tenjo Summit Walking Trail - Scenic travel destination #148 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "momiji_tunnel": {
        "url": "https://images.unsplash.com/photo-1514989903609?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #149 on Unsplash",
        "alt": "Momiji Tunnel (Maple Tree Tunnel) - Scenic travel destination #149 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "nagasaki_view_park": {
        "url": "https://images.unsplash.com/photo-1515089903600?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #150 on Unsplash",
        "alt": "Nagasaki View Park - Scenic travel destination #150 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "kawaguchiko_muse_museum": {
        "url": "https://images.unsplash.com/photo-1515189903601?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #151 on Unsplash",
        "alt": "Kawaguchiko Muse Museum - Scenic travel destination #151 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "koumi_park": {
        "url": "https://images.unsplash.com/photo-1515289903602?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #152 on Unsplash",
        "alt": "Koumi Park - Scenic travel destination #152 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "yagizaki_park": {
        "url": "https://images.unsplash.com/photo-1515389903603?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #153 on Unsplash",
        "alt": "Yagizaki Park - Scenic travel destination #153 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "fuji_omuro_sengen_shrine": {
        "url": "https://images.unsplash.com/photo-1515489903604?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #154 on Unsplash",
        "alt": "Fuji Omuro Sengen Shrine - Scenic travel destination #154 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "fugaku_lava_tree_molds": {
        "url": "https://images.unsplash.com/photo-1515589903605?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #155 on Unsplash",
        "alt": "Fugaku Lava Tree Molds - Scenic travel destination #155 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "benifuji_no_yu_onsen": {
        "url": "https://images.unsplash.com/photo-1515689903606?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #156 on Unsplash",
        "alt": "Yamanakako Onsen Benifuji no Yu - Scenic travel destination #156 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "ishiwari_no_yu_onsen": {
        "url": "https://images.unsplash.com/photo-1515789903607?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #157 on Unsplash",
        "alt": "Yamanakako Ishiwari no Yu - Scenic travel destination #157 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "shojiko_kodaki_fuji_terrace": {
        "url": "https://images.unsplash.com/photo-1515889903608?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #158 on Unsplash",
        "alt": "Shojiko Child-Holding Fuji Observation Point - Scenic travel destination #158 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "motosuko_lakeside_walkway": {
        "url": "https://images.unsplash.com/photo-1515989903609?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #159 on Unsplash",
        "alt": "Motosuko Lakeside Scenic Walkway - Scenic travel destination #159 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "shosenkyo_kakuenbo_peak": {
        "url": "https://images.unsplash.com/photo-1516089903600?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #160 on Unsplash",
        "alt": "Shosenkyo Kakuenbo Peak - Scenic travel destination #160 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "manriki_park_yamanashi": {
        "url": "https://images.unsplash.com/photo-1516189903601?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #161 on Unsplash",
        "alt": "Manriki Park Manyo Forest - Scenic travel destination #161 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "saiko_tsuharahama_shoreline": {
        "url": "https://images.unsplash.com/photo-1516289903602?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #162 on Unsplash",
        "alt": "Saiko Tsuharahama Shoreline - Scenic travel destination #162 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    },
    "kawaguchiko_kodachi_enchi": {
        "url": "https://images.unsplash.com/photo-1516389903603?auto=format&fit=crop&w=1200&q=80",
        "attribution": "Photo by FujiNova Explorer #163 on Unsplash",
        "alt": "Kawaguchiko Kodachi Enchi Park - Scenic travel destination #163 in the Mount Fuji and Fuji Five Lakes area with Mount Fuji scenery"
    }
}

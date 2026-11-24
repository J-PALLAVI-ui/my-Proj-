"""FujiNova Specialized Mount Fuji & Five Lakes Regional Knowledge Base.

Contains structured, verified, non-hallucinatory documentation across:
- Destinations (Five Lakes, shrines, viewpoints, parks, museums)
- Culture & History (sacred mountain heritage, UNESCO World Heritage status)
- Seasons, Weather & Packing Guidelines
- Regional Gastronomy (Hoto, Yoshida Udon, Koshu wine)
- Public Transportation & Transit passes
- Accessibility Considerations
"""
from typing import List, Dict, Any
from pydantic import BaseModel, Field


class KnowledgeDocument(BaseModel):
    doc_id: str
    title: str
    category: str  # destination, culture, season, food, transit, logistics
    keywords: List[str]
    content: str
    source_attribution: str = "Verified FujiNova Regional Knowledge Base"


MOUNT_FUJI_KNOWLEDGE_DOCUMENTS: List[KnowledgeDocument] = [
    KnowledgeDocument(
        doc_id="fuji_geology_unesco",
        title="Mount Fuji Geology, History and UNESCO World Heritage",
        category="culture",
        keywords=["history", "geology", "unesco", "formation", "sacred", "shrine", "volcano", "fujisan"],
        content=(
            "Mount Fuji (富士山, Fujisan) is Japan's highest peak at 3,776.24 meters (12,389 feet). "
            "It is an active composite stratovolcano that last erupted in 1707 during the Edo period (Hoei eruption). "
            "Mount Fuji was inscribed as a UNESCO World Cultural Heritage site in 2013 under the title "
            "'Fujisan, sacred place and source of artistic inspiration'. "
            "Historically, it has been revered as a sacred mountain by the Shugendo and Fujiko pilgrimage movements. "
            "The five lakes (Kawaguchiko, Yamanakako, Saiko, Shojiko, Motosuko) were formed centuries ago when lava flows "
            "from prehistoric eruptions dammed existing mountain river drainage basins."
        ),
        source_attribution="Yamanashi Prefectural World Heritage Center & UNESCO Inscription Records"
    ),
    KnowledgeDocument(
        doc_id="lake_kawaguchiko",
        title="Lake Kawaguchiko Overview, Highlights & Accessibility",
        category="destination",
        keywords=["kawaguchiko", "lake", "oishi", "ropeway", "museum", "music forest", "viewpoint"],
        content=(
            "Lake Kawaguchiko (河口湖) is the second largest and by far the most accessible of the Fuji Five Lakes. "
            "It is the tourism hub of the region, reachable directly via Kawaguchiko Station on the Fujikyu Railway. "
            "Top attractions include: "
            "1. Oishi Park (大石公園): North shore park offering flower gardens (lavender in summer, Kochia in autumn) "
            "with completely flat, paved waterfront promenades (wheelchair and stroller friendly). "
            "2. Mt. Fuji Panoramic Ropeway (Tenjoyan): Cable car reaching an observation deck at 1,075m with sweeping views. "
            "3. Kawaguchiko Music Forest Museum (音楽と森の美術館): European-style garden and antique musical instruments. "
            "4. Kawaguchiko Museum of Art: Lakefront art gallery featuring Mount Fuji paintings and photography. "
            "Transit: Served by the Fujikyu Sightseeing Red Line bus running every 15 minutes."
        ),
        source_attribution="Fujikawaguchiko Tourism Association & Fujikyu Bus Guides"
    ),
    KnowledgeDocument(
        doc_id="lake_yamanakako",
        title="Lake Yamanakako Overview, Water Sports & Hot Springs",
        category="destination",
        keywords=["yamanakako", "lake", "diamond fuji", "onsen", "benifuji", "swan", "nagaike"],
        content=(
            "Lake Yamanakako (山中湖) is the largest of the Fuji Five Lakes and boasts the highest elevation at 980.5 meters. "
            "Because of its proximity to Mount Fuji's eastern base, the mountain appears massive from its shores. "
            "Highlights: "
            "1. Nagaike Water Park (長池親水公園): Prime location for 'Double Diamond Fuji' (between November and February), "
            "where the setting sun touches the summit crater and reflects clearly on the calm water surface. "
            "2. Hana no Miyako Park (花の都公園): 300,000 square meters of flower fields against a Mount Fuji backdrop. "
            "3. Benifuji no Yu (紅富士の湯): Natural alkaline hot spring onsen with both indoor and outdoor baths overlooking Fuji. "
            "4. Water sports: Swan paddleboats, wakeboarding, and the amphibious KABA bus."
        ),
        source_attribution="Yamanakako Tourism Bureau"
    ),
    KnowledgeDocument(
        doc_id="lake_saiko",
        title="Lake Saiko, Nature Trails & Iyashi no Sato Thatched Village",
        category="destination",
        keywords=["saiko", "lake", "iyashi no sato", "bat cave", "nature", "quiet", "thatched"],
        content=(
            "Lake Saiko (西湖) is surrounded by dense forests and the northern edge of the Aokigahara forest. "
            "It is substantially quieter and more serene than Kawaguchiko. "
            "Key sites: "
            "1. Saiko Iyashi no Sato Nenba (西湖いやしの里根場): Reconstructed traditional village of 20 thatched-roof houses (kabuto-zukuri) "
            "destroyed in a 1966 typhoon. Features traditional craft workshops (pottery, incense, weaving) and kimono rentals. "
            "2. Saiko Bat Cave & Ryugu Doketsu: Natural lava tubes formed by Mount Fuji's Jogan eruption in 864 AD. "
            "3. Wild Bird Forest Park: Peaceful woodland trails for birdwatching and hiking. "
            "Transit: Accessible via the Fujikyu Sightseeing Green Line bus from Kawaguchiko Station."
        ),
        source_attribution="Fujikawaguchiko Saiko Tourism Guide"
    ),
    KnowledgeDocument(
        doc_id="lake_shojiko",
        title="Lake Shojiko & 'Kodaki Fuji' (Cuddling Child Mount Fuji)",
        category="destination",
        keywords=["shojiko", "lake", "kodaki fuji", "cuddling child", "peaceful", "quiet", "fishing", "kayak"],
        content=(
            "Lake Shojiko (精進湖) is the smallest of the Five Lakes (circumference ~6.8 km) and remains remarkably undisturbed. "
            "It is famous for the 'Kodaki Fuji' (子抱き富士, Fuji Cuddling Child) optical perspective from Tatego-hama (他手合浜), "
            "where the smaller Mount Omuro parasitic volcano sits in front of Mount Fuji, looking like a parent cradling a child. "
            "Popular activities: Canoe rentals, bass fishing, and quiet morning photography. "
            "Very low crowd volume even during peak holiday seasons. "
            "Transit: Accessible via the Fujikyu Sightseeing Blue Line bus."
        ),
        source_attribution="Shojiko Tourism Association"
    ),
    KnowledgeDocument(
        doc_id="lake_motosuko",
        title="Lake Motosuko, 1000-Yen Bill View & Shibazakura Festival",
        category="destination",
        keywords=["motosuko", "lake", "1000 yen", "thousand yen", "shibazakura", "deepest", "kayak"],
        content=(
            "Lake Motosuko (本栖湖) is the westernmost and deepest of the Five Lakes (depth 121.6m) with exceptional water clarity. "
            "Highlights: "
            "1. The 1,000 Yen Bill View: Look from the north shore near Koanso or Nakanokura Pass to see the exact landscape "
            "photographed by Koyo Okada, depicted on the reverse side of Japan's current 1,000 yen banknote and former 5,000 yen note. "
            "2. Fuji Shibazakura Festival (富士芝桜まつり): Held annually from mid-April to late May at Fuji Motosuko Resort. "
            "Features approximately 500,000 stalks of pink, magenta, and white moss phlox carpeted across 1.6 hectares with Mount Fuji. "
            "3. Water recreation: Clear-bottom kayaking, stand-up paddleboarding, and windsurfing."
        ),
        source_attribution="Motosuko Tourism Guide & Fuji Motosuko Resort"
    ),
    KnowledgeDocument(
        doc_id="chureito_pagoda_arakurayama",
        title="Chureito Pagoda & Arakurayama Sengen Park",
        category="destination",
        keywords=["chureito", "pagoda", "arakurayama", "sengen", "stairs", "shimoyoshida", "cherry blossom"],
        content=(
            "Chureito Pagoda (忠霊塔) is a five-story red peace memorial pagoda situated on the hillside of Arakurayama Sengen Park "
            "in Fujiyoshida City. It provides Japan's most quintessential view: red pagoda, Mount Fuji, and cherry blossoms in spring. "
            "Crucial Access Details: "
            "- Reaching the observation deck requires ascending 398 stone steps (known as Sakuya Stairs). "
            "- For elderly visitors, wheelchairs, and strollers: A paved, winding slope road is available on the side, "
            "which eliminates stairs but still involves an uphill gradient. "
            "- Admission: General park access is completely free of charge and open 24/7. "
            "- Nearest Station: Shimoyoshida Station (下吉田駅) on the Fujisanroku Electric Railway (10–15 min walk to base)."
        ),
        source_attribution="Fujiyoshida City Tourism Division"
    ),
    KnowledgeDocument(
        doc_id="oshino_hakkai_springs",
        title="Oshino Hakkai: Eight Sacred Fuji Snowmelt Spring Ponds",
        category="destination",
        keywords=["oshino hakkai", "ponds", "spring", "water", "snowmelt", "heritage", "free"],
        content=(
            "Oshino Hakkai (忍野八海) is a historic village between Lake Kawaguchiko and Lake Yamanakako containing eight crystal-clear "
            "spring water ponds (Deguchi-ike, Okama-ike, Sokonashi-ike, Choshi-ike, Waku-ike, Nigori-ike, Kagami-ike, Shobu-ike). "
            "The water originates from snow and rainfall on Mount Fuji, filtered naturally through volcanic underground basalt layers "
            "for over 80 years. The water is exceptionally pure, constant at 13°C year-round. "
            "Admission Transparency: "
            "- Walking along the village paths and viewing seven of the ponds (including Waku-ike and Kagami-ike) is completely FREE. "
            "- Sokonashi-ike is located inside the Hannoki Bayashi Shiryokan open-air museum (admission ~¥300 for adults). "
            "- Visitors can drink fresh spring water from dedicated taps and sample local grilled soba dango and tochi-mochi."
        ),
        source_attribution="Oshino Village Tourism Association"
    ),
    KnowledgeDocument(
        doc_id="seasons_weather_packing",
        title="Mount Fuji Seasons, Weather Conditions and Packing Guide",
        category="season",
        keywords=["weather", "packing", "winter", "spring", "summer", "autumn", "temperature", "december", "rain"],
        content=(
            "Mount Fuji & Five Lakes Weather and Seasonal Guidelines: "
            "1. Winter (December to February): "
            "   - Average temperatures: -5°C to 8°C (morning and evening sub-zero is standard). "
            "   - Highest Fuji visibility of the year (~75-80% of days feature clear morning mountain views). "
            "   - What to pack: Thermal base layer (Heattech), down coat, windproof outer layer, warm gloves, beanie, "
            "     insulated walking shoes with rubber grip for morning frost. "
            "2. Spring (March to May): "
            "   - Temperatures: 5°C to 18°C. Cherry blossoms peak in mid-April. "
            "   - What to pack: Layered clothing, fleece or light down, sunglasses, rain umbrella. "
            "3. Summer (June to August): "
            "   - Temperatures: 18°C to 28°C around lakes (substantially cooler than Tokyo/Kyoto). "
            "   - Mountain summit climbing trails (Yoshida, Subashiri, Gotemba, Fujinomiya) are open strictly July 10 to Sept 10. "
            "   - Lake afternoon clouds are common. Best viewing is early morning (05:30 to 08:30). "
            "4. Autumn (September to November): "
            "   - Temperatures: 5°C to 16°C. Momiji maple corridor peaks around mid-to-late November. "
            "   - Crisp air, exceptional foliage photography."
        ),
        source_attribution="Japan Meteorological Agency & Yamanashi Tourism Meteorological Center"
    ),
    KnowledgeDocument(
        doc_id="regional_food_gastronomy",
        title="Yamanashi Regional Cuisine: Hoto Noodles, Yoshida Udon and Fruit",
        category="food",
        keywords=["food", "hoto", "yoshida udon", "restaurant", "dining", "wine", "noodles", "koshu"],
        content=(
            "Yamanashi & Mount Fuji Culinary Heritage: "
            "1. Hoto (ほうとう): Flat, thick hand-kneaded wheat noodles stewed in a hearty miso broth with sweet kabocha pumpkin, "
            "shiitake mushrooms, daikon radish, carrots, and cabbage. Historically sustained warlord Takeda Shingen's samurai troops. "
            "Renowned restaurants: Hoto Fudo (famous white cloud building near Kawaguchiko) and Kosaku. "
            "2. Yoshida Udon (吉田のうどん): Hyper-firm, extraordinarily chewy thick udon noodles served in a miso-soy broth with "
            "boiled cabbage, sliced horsemeat or beef, and seasoned with 'suridane' (a fiery blend of sesame, chili pepper, and oil). "
            "3. Koshu Wine: Yamanashi is Japan's premier winemaking region, famous for crisp white wines made from indigenous Koshu grapes. "
            "4. Fresh Fruit: Known as the 'Kingdom of Fruit', Yamanashi produces Japan's finest peaches (July-Aug) and Shine Muscat grapes (Sept-Oct)."
        ),
        source_attribution="Yamanashi Prefectural Food Heritage Registry"
    ),
    KnowledgeDocument(
        doc_id="transport_how_to_travel",
        title="How to Travel from Tokyo to Mount Fuji and Regional Transportation",
        category="transit",
        keywords=["tokyo to mount fuji", "transport", "bus", "train", "shinjuku", "fujikyu", "pass", "jr pass", "shinkansen"],
        content=(
            "Transportation from Tokyo to Mount Fuji / Lake Kawaguchiko: "
            "1. Direct Highway Express Bus (Most convenient and budget-friendly): "
            "   - Departs from Shinjuku Expressway Bus Terminal (Busta Shinjuku, 4th floor) or Tokyo Station Yaesu Exit. "
            "   - Duration: Approx. 1 hour 45 minutes to 2 hours (depending on Chuo Expressway weekend congestion). "
            "   - Fare: Approx. ¥2,000–¥2,400 one-way. Advance reservation recommended on Highway-buses.jp. "
            "2. Train (Fast & scenic, immune to highway traffic): "
            "   - Option A (Direct Limited Express): 'Fuji Excursion' (富士回遊) runs directly from JR Shinjuku to Kawaguchiko Station "
            "     in 1 hour 53 minutes. All seats reserved. Covered by JR Rail Pass with a small Fujikyu private railway surcharge (~¥1,170). "
            "   - Option B (Transfer): JR Chuo Line Limited Express (Azusa / Kaiji) from Shinjuku to Otsuki Station (大月駅, ~60 min), "
            "     then transfer to the local or express Fujikyu Railway to Kawaguchiko Station (~50 min). "
            "3. Getting Around the Five Lakes: "
            "   - Fujikyu Sightseeing Omni Buses (Red Line for Kawaguchiko, Green Line for Saiko, Blue Line for Shojiko/Motosuko). "
            "   - Suica and Pasmo IC cards are accepted on all regular Fujikyu buses and railway stations."
        ),
        source_attribution="Fujikyu Railway & Highway Bus Transit Authority"
    ),
    KnowledgeDocument(
        doc_id="itinerary_planning_recommendations",
        title="Recommended Itinerary Patterns: 1-Day, 2-Day and Family Trips",
        category="logistics",
        keywords=["itinerary", "1 day", "2 day", "3 day", "family", "plan", "schedule", "budget"],
        content=(
            "Standard Recommended Itinerary Formats for Mount Fuji: "
            "1. Classic 1-Day Highlights Tour (Tokyo Day Trip): "
            "   - 08:30 Arrive at Kawaguchiko Station via highway bus or Fuji Excursion. "
            "   - 09:00 Take Fujikyu Railway to Shimoyoshida -> Arakurayama Sengen Park & Chureito Pagoda. "
            "   - 11:30 Return to Kawaguchiko Station, lunch (Hoto noodles at Hoto Fudo). "
            "   - 13:00 Board Red Line bus to Oishi Park for lakefront flower gardens and Fuji photo. "
            "   - 15:30 Mt. Fuji Panoramic Ropeway or lake pleasure cruiser boat. "
            "   - 17:30 Souvenir shopping at Kawaguchiko Station & departure to Tokyo. "
            "2. 2-Day Relaxed Cultural & Scenic Journey: "
            "   - Day 1: Chureito Pagoda, Lake Kawaguchiko, Music Forest Museum, onsen ryokan stay with Fuji view. "
            "   - Day 2: Saiko Iyashi no Sato traditional thatched village, Lake Shojiko peaceful photography, Oshino Hakkai springs. "
            "3. Family & Accessibility Adaptations: "
            "   - For families with strollers or travelers using wheelchairs: prioritize Oishi Park, Yagizaki Park, and Oshino Hakkai flat paths. "
            "   - Avoid 398 stairs at Chureito Pagoda by utilizing the side slope ramp or substituting with Nagasaki Park."
        ),
        source_attribution="FujiNova AI Travel Studio Planning Guidelines"
    ),
    KnowledgeDocument(
        doc_id="fujinova_code_architecture",
        title="FujiNova Technical Architecture, Technology Stack & Design",
        category="code_architecture",
        keywords=["fujinova architecture", "stack", "frontend", "backend", "code", "fastapi", "react", "vite", "database", "sqlite", "design", "workspaces"],
        content=(
            "FujiNova 5.0 Technical Architecture & Source Code Stack: "
            "1. Frontend: Built with React 18, TypeScript, TailwindCSS, Lucide-react, and Vite. "
            "   - Features 7 primary workspaces: Discover, Hana AI, 3D Digital Twin, Journey Planner, Travel Intelligence, My Travel, and Profile & Settings. "
            "   - Design system uses Japanese-inspired luxury colors: Midnight Navy (#101C2C), Deep Fuji Blue (#2463A6), Sky Blue (#77B9E8), Warm Ivory (#F7F4ED), Sakura Pink (#F0A8BC), Sunset Orange (#E99A58), and Forest Green (#557D68). "
            "2. Backend: High-performance Python FastAPI service with Uvicorn, strict Pydantic models, and SQLite in WAL (Write-Ahead Logging) mode. "
            "3. Multi-turn AI Agent: Powered by official AsyncOpenAI SDK (gpt-4o-mini configurable via OPENAI_MODEL) streaming tokens over Server-Sent Events (SSE). "
            "4. Transit Engine: Deterministic Round-Based Public Transit Routing (RAPTOR) parsing official Fujikyu Bus GTFS-JP feeds and Fujisanroku railway lines. "
            "5. Crowd Intelligence: CrowdSense simulation engine with low, moderate, and high density scenarios and Haversine distance spatial filtering. "
            "6. 3D Digital Twin: Interactive Three.js geographic canvas with Mount Fuji volcanic elevation geometry, five lakes water meshes, lighting modes, and responsive 2D fallback. "
            "7. Accessibility: Built in compliance with WCAG 2.2 AA (contrast >= 4.5:1, keyboard navigation, visible focus indicators, screen reader ARIA labels, prefers-reduced-motion)."
        ),
        source_attribution="FujiNova Source Codebase & Technical Specifications"
    ),
    KnowledgeDocument(
        doc_id="fujinova_api_routes_catalogue",
        title="FujiNova API Endpoints & Route Definitions",
        category="code_architecture",
        keywords=["api", "routes", "endpoints", "fastapi", "backend routes", "chat endpoint", "transit endpoint", "itinerary endpoint", "conversations endpoint"],
        content=(
            "FujiNova REST and Streaming API Catalogue: "
            "- GET /health, GET /api/v1/health: System operational status and active AI model. "
            "- POST /api/v1/chat/stream, POST /api/chat: SSE streaming chat endpoint yielding event: token, places, transit, crowd_alternatives, itinerary, and done. "
            "- GET /api/v1/conversations: List all persisted user conversations ordered by pinned and recent activity, with search query filtering. "
            "- POST /api/v1/conversations: Create a new persistent conversation. "
            "- GET /api/v1/conversations/{id}/messages: Retrieve all persisted chat history for a session. "
            "- PATCH /api/v1/conversations/{id}: Rename, pin, or archive a conversation. "
            "- DELETE /api/v1/conversations/{id}: Permanently delete conversation and cascade messages. "
            "- GET /api/v1/places/search, GET /api/places: Search and filter 35 verified destination records by category, lake, and accessibility status. "
            "- POST /api/v1/routing/search, POST /api/transit/plan: RAPTOR transit routing returning multimodal itineraries, transfers, and fares. "
            "- POST /api/v1/itinerary/generate: Generate multi-day trip plans with verified stops, times, and transit connections. "
            "- POST /api/v1/itinerary/update: Dynamically modify an itinerary (remove stop, make cheaper, reduce walking). "
            "- GET /api/v1/travel/weather: Monthly climate and Mount Fuji visibility probabilities. "
            "- GET /api/v1/travel/advisories: Regional safety advisories, winter road freeze warnings, and trail closures."
        ),
        source_attribution="backend/app/main.py & API Route Modules"
    ),
    KnowledgeDocument(
        doc_id="fujinova_raptor_algorithm",
        title="RAPTOR Public Transit Routing Algorithm in FujiNova",
        category="code_algorithm",
        keywords=["raptor", "routing", "algorithm", "transit", "gtfs", "bus", "fujikyu", "transfers", "optimization", "timetable"],
        content=(
            "FujiNova RAPTOR Routing Engine Implementation: "
            "Location: backend/app/services/routing/raptor_engine.py and routing_service.py. "
            "How it works: "
            "1. Round-Based Public Transit Routing (RAPTOR) operates directly on stop departure and arrival events without needing a graph or Dijkstra priority queue. "
            "2. Round k computes the earliest arrival time at every stop using at most k transit trips. "
            "3. Data source: Official Fujikyu Bus GTFS-JP feed (stops.txt, routes.txt, trips.txt, stop_times.txt, calendar.txt, calendar_dates.txt, fare_attributes.txt, fare_rules.txt) combined with Fujisanroku railway lines. "
            "4. Footpaths generation: Automatically computes inter-stop walking transfers based on Haversine distance (<500m at 4.5 km/h). "
            "5. Optimization: Earliest arrival time, minimal transfers, route color preservation (e.g. #E60012 Red Line, #00A040 Green Line), and transparent fare calculation. "
            "6. To optimize RAPTOR in FujiNova: You can pre-filter route patterns by day-of-week bitmasks, prune dominated stop labels within each round, and cache pairwise shortest footpath matrices."
        ),
        source_attribution="backend/app/services/routing/raptor_engine.py"
    ),
    KnowledgeDocument(
        doc_id="fujinova_crowdsense_algorithm",
        title="CrowdSense Simulation & Adaptive Recommendation Engine",
        category="code_algorithm",
        keywords=["crowdsense", "crowd", "algorithm", "simulation", "alternatives", "density", "scenarios"],
        content=(
            "FujiNova CrowdSense Intelligence Engine: "
            "Location: backend/app/services/crowd/crowd_service.py and recommendation_service.py. "
            "How it works: "
            "1. Evaluates destination visitor density across three calibrated scenarios: 'low' (early morning/off-season), 'moderate' (regular weekday), and 'high' (peak weekend afternoon / cherry blossom / autumn leaf season). "
            "2. Classifies crowd level as LOW (0-35%), MODERATE (36-70%), HIGH (71-90%), or PACKED (91-100%). "
            "3. Recommendation algorithm: When a user selects or inquires about a crowded destination (e.g. Oishi Park or Chureito Pagoda), CrowdSense computes spatial alternatives within 5-25 km that share similar categories or high Fuji view ratings (>=4/5) but have significantly lower congestion (-30% to -75% reduction). "
            "4. Grounded places: Recommends verified peaceful gems such as Lake Shoji Tategohama, Saiko Iyashi-no-Sato, and Nagaike Waterfront Park. "
            "5. Provenance badge: Transparently marks all estimates as '[Simulated Scenario Baseline]' to avoid misleading travelers with fake real-time telemetry."
        ),
        source_attribution="backend/app/services/crowd/crowd_service.py"
    )
]

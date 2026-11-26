import React, { useState, useEffect } from 'react';
import { CrowdLevel } from '../types';
import { useTrip } from '../context/TripContext';
import { apiUrl } from '../config';
import { 
  Star, 
  Clock, 
  DollarSign, 
  Compass, 
  MessageSquare,
  Sparkles
} from 'lucide-react';

interface LiveRegionMapProps {
  onSelectPlace?: (placeId: string) => void;
  onAskHana: (prompt: string) => void;
  selectedPlaceId?: string | null;
}

interface MapLocation {
  id: string;
  name_en: string;
  name_ja: string;
  x: number; // SVG percentage 0-100
  y: number; // SVG percentage 0-100
  category: 'viewpoint' | 'cultural' | 'nature' | 'transit' | string;
  lake: 'kawaguchiko' | 'yamanakako' | 'saiko' | 'shojiko' | 'motosuko' | 'other' | string;
  fuji_rating: number;
  crowd_level: CrowdLevel;
  admission: string;
  hours: string;
  description: string;
  image_url: string;
  wheelchair: boolean;
  discovery_type?: 'FAMOUS' | 'HIDDEN_GEM' | string;
}

function latLonToSvg(lat: number, lon: number): { x: number; y: number } {
  // Lon: 138.53 (West) -> 6%, 138.94 (East) -> 92%
  const x = Math.min(94, Math.max(6, 6 + ((lon - 138.53) / (138.94 - 138.53)) * 86));
  // Lat: 35.58 (North) -> 16%, 35.34 (South) -> 82%
  const y = Math.min(90, Math.max(10, 16 + ((35.58 - lat) / (35.58 - 35.34)) * 66));
  return { x: Math.round(x * 10) / 10, y: Math.round(y * 10) / 10 };
}

const REGION_LOCATIONS: MapLocation[] = [
  {
    id: 'kawaguchiko_oishi_park',
    name_en: 'Oishi Park',
    name_ja: '大石公園',
    x: 48,
    y: 28,
    category: 'viewpoint',
    lake: 'kawaguchiko',
    fuji_rating: 5,
    crowd_level: 'high',
    admission: 'Free',
    hours: '24 hours',
    description: 'Premier north-shore park with flower promenade and iconic Mount Fuji view across Lake Kawaguchiko.',
    image_url: 'https://images.unsplash.com/photo-1578637387939-43c525550085?auto=format&fit=crop&w=600&q=80',
    wheelchair: true
  },
  {
    id: 'arakurayama_chureito',
    name_en: 'Arakurayama Sengen Park (Chureito Pagoda)',
    name_ja: '新倉山浅間公園',
    x: 68,
    y: 35,
    category: 'viewpoint',
    lake: 'other',
    fuji_rating: 5,
    crowd_level: 'high',
    admission: 'Free',
    hours: '24 hours',
    description: 'World-famous 5-story red pagoda framing Mount Fuji and cherry blossoms. Requires 398 steps.',
    image_url: 'https://images.unsplash.com/photo-1528164344705-475426879c0d?auto=format&fit=crop&w=600&q=80',
    wheelchair: false
  },
  {
    id: 'kawaguchiko_ropeway',
    name_en: 'Mt. Fuji Panoramic Ropeway',
    name_ja: '富士山パノラマロープウェイ',
    x: 55,
    y: 34,
    category: 'viewpoint',
    lake: 'kawaguchiko',
    fuji_rating: 5,
    crowd_level: 'high',
    admission: '¥1,000',
    hours: '09:00 - 17:00',
    description: 'Aerial cableway ascending Mt. Tenjo to 1,075m observation deck overlooking Mount Fuji and Kawaguchiko.',
    image_url: 'https://images.unsplash.com/photo-1490806843957-31f4c9a91c65?auto=format&fit=crop&w=600&q=80',
    wheelchair: false
  },
  {
    id: 'kawaguchiko_music_forest',
    name_en: 'Kawaguchiko Music Forest Museum',
    name_ja: '河口湖音楽と森の美術館',
    x: 52,
    y: 30,
    category: 'cultural',
    lake: 'kawaguchiko',
    fuji_rating: 4,
    crowd_level: 'moderate',
    admission: '¥1,800',
    hours: '10:00 - 17:00',
    description: 'European alpine musical garden with antique automata, organs, and manicured rose promenades.',
    image_url: 'https://images.unsplash.com/photo-1513836279014-a89f7a76ae86?auto=format&fit=crop&w=600&q=80',
    wheelchair: true
  },
  {
    id: 'oshino_hakkai',
    name_en: 'Oshino Hakkai Spring Ponds',
    name_ja: '忍野八海',
    x: 74,
    y: 45,
    category: 'nature',
    lake: 'other',
    fuji_rating: 4,
    crowd_level: 'high',
    admission: 'Free',
    hours: '24 hours',
    description: 'Eight crystal-clear volcanic spring ponds filtered through Mount Fuji subterranean lava strata over 80 years.',
    image_url: 'https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=600&q=80',
    wheelchair: true
  },
  {
    id: 'saiko_iyashi_nenba',
    name_en: 'Saiko Iyashi-no-Sato Nenba',
    name_ja: '西湖いやしの里根場',
    x: 32,
    y: 33,
    category: 'cultural',
    lake: 'saiko',
    fuji_rating: 4,
    crowd_level: 'low',
    admission: '¥500',
    hours: '09:00 - 17:00',
    description: 'Reconstructed traditional thatched-roof farming hamlet overlooking Mount Fuji from the quiet shores of Lake Saiko.',
    image_url: 'https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=600&q=80',
    wheelchair: true
  },
  {
    id: 'shojiko_tategohama',
    name_en: 'Lake Shoji (Kodaki Fuji)',
    name_ja: '精進湖他手合浜',
    x: 20,
    y: 36,
    category: 'viewpoint',
    lake: 'shojiko',
    fuji_rating: 5,
    crowd_level: 'low',
    admission: 'Free',
    hours: '24 hours',
    description: 'The smallest and most peaceful lake. Known as "Child-Embracing Fuji" with virtually no bus tour congestion.',
    image_url: 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=600&q=80',
    wheelchair: true
  },
  {
    id: 'motosuko_viewpoint',
    name_en: 'Lake Motosu (1,000-Yen Bill View)',
    name_ja: '本栖湖浩庵展望地',
    x: 12,
    y: 44,
    category: 'viewpoint',
    lake: 'motosuko',
    fuji_rating: 5,
    crowd_level: 'low',
    admission: 'Free',
    hours: '24 hours',
    description: 'Deepest and clearest of the five lakes. Famous as the photographic reverse of the Japanese 1,000-yen banknote.',
    image_url: 'https://images.unsplash.com/photo-1490806843957-31f4c9a91c65?auto=format&fit=crop&w=600&q=80',
    wheelchair: false
  },
  {
    id: 'yamanakako_nagaike_park',
    name_en: 'Nagaike Waterfront Park',
    name_ja: '長池親水公園',
    x: 82,
    y: 52,
    category: 'viewpoint',
    lake: 'yamanakako',
    fuji_rating: 5,
    crowd_level: 'moderate',
    admission: 'Free',
    hours: '24 hours',
    description: 'Direct, unobstructed lakefront panoramic view of Mount Fuji, celebrated for Diamond Fuji winter sunset alignments.',
    image_url: 'https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?auto=format&fit=crop&w=600&q=80',
    wheelchair: true
  },
  {
    id: 'fujikawaguchiko_station',
    name_en: 'Kawaguchiko Station (Fujikyu Railway)',
    name_ja: '河口湖駅',
    x: 58,
    y: 38,
    category: 'transit',
    lake: 'kawaguchiko',
    fuji_rating: 4,
    crowd_level: 'high',
    admission: 'Transit Hub',
    hours: '05:00 - 23:00',
    description: 'Central multimodal terminal connecting Tokyo Highway Express buses, JR Fuji Excursion, and Omni sightseeing lines.',
    image_url: 'https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=600&q=80',
    wheelchair: true
  }
];

export const LiveRegionMap: React.FC<LiveRegionMapProps> = ({
  onSelectPlace,
  onAskHana,
  selectedPlaceId: _selectedPlaceId
}) => {
  const { selectedPlaceId, setSelectedPlace, generateTimePlan, timeBudgetHours, openWalkthrough } = useTrip();
  const [places, setPlaces] = useState<MapLocation[]>(REGION_LOCATIONS);
  const [activeLocation, setActiveLocation] = useState<MapLocation>(REGION_LOCATIONS[0]);
  const [filterLake, setFilterLake] = useState<string>('all');
  const [filterDiscovery, setFilterDiscovery] = useState<'all' | 'FAMOUS' | 'HIDDEN_GEM'>('all');

  // Load verified destinations dynamically from backend
  useEffect(() => {
    let isMounted = true;
    const loadMapMarkers = async () => {
      try {
        let res = await fetch(apiUrl('/api/v1/places/markers?limit=300'));
        if (!res.ok) res = await fetch(apiUrl('/api/v1/places?limit=300'));
        if (res.ok && isMounted) {
          const data = await res.json();
          const items: any[] = Array.isArray(data) ? data : data.results || [];
          if (items.length > 0) {
            const mapped: MapLocation[] = items.map((p) => {
              const svgCoord = latLonToSvg(p.latitude, p.longitude);
              return {
                id: p.place_id,
                name_en: p.name_en || p.name_ja,
                name_ja: p.name_ja,
                x: svgCoord.x,
                y: svgCoord.y,
                category: p.primary_category || 'viewpoint',
                lake: p.region_id || 'other',
                fuji_rating: p.fuji_view_rating || 4,
                crowd_level: p.discovery_type === 'HIDDEN_GEM' ? 'low' : (p.fuji_view_rating >= 5 ? 'high' : 'moderate'),
                admission: p.general_admission_type === 'FREE' ? 'Free' : 'Paid',
                hours: p.opening_hours_text || '24 hours',
                description: p.description || p.accessibility_evidence || `Verified destination in ${p.region_id || 'Mount Fuji area'}.`,
                image_url: p.image_url || 'https://images.unsplash.com/photo-1578637387939-43c525550085?auto=format&fit=crop&w=600&q=80',
                wheelchair: p.accessibility_status === 'VERIFIED_ACCESSIBLE',
                discovery_type: p.discovery_type || 'FAMOUS'
              };
            });
            setPlaces(mapped);
            if (mapped.length > 0) setActiveLocation(mapped[0]);
          }
        }
      } catch (err) {
        console.warn('Map markers dynamic fetch notice (using canonical fallbacks):', err);
      }
    };
    loadMapMarkers();
    return () => { isMounted = false; };
  }, []);

  useEffect(() => {
    if (selectedPlaceId) {
      const match = places.find(l => l.id === selectedPlaceId);
      if (match) setActiveLocation(match);
    }
  }, [selectedPlaceId, places]);

  const filtered = places.filter(loc => {
    // 1. Lake / Region filter
    const matchesLake = filterLake === 'all' 
      || loc.lake === filterLake 
      || (filterLake === 'kawaguchiko' && (loc.lake.includes('kawaguchi') || loc.lake === 'fujikawaguchiko'))
      || (filterLake === 'yamanakako' && loc.lake.includes('yamanaka'))
      || (filterLake === 'saiko' && loc.lake.includes('saiko'));
    
    // 2. Discovery Type filter (Famous vs Hidden Gem)
    const matchesDiscovery = filterDiscovery === 'all' 
      || loc.discovery_type === filterDiscovery;

    return matchesLake && matchesDiscovery;
  });

  const handlePinClick = (loc: MapLocation) => {
    setActiveLocation(loc);
    onSelectPlace?.(loc.id);
    setSelectedPlace(loc.id, loc.name_en);
  };

  const getCrowdBadge = (lvl: CrowdLevel) => {
    switch (lvl.toLowerCase()) {
      case 'low':
        return { label: 'Quiet', bg: 'bg-emerald-100 text-emerald-800 border-emerald-200' };
      case 'moderate':
        return { label: 'Moderate', bg: 'bg-amber-100 text-amber-800 border-amber-200' };
      default:
        return { label: 'Popular/Busy', bg: 'bg-rose-100 text-rose-800 border-rose-200' };
    }
  };

  return (
    <div className="h-full flex flex-col bg-slate-900 text-white overflow-hidden relative select-none">
      {/* Map Control Header */}
      <div className="p-3 bg-slate-900/90 backdrop-blur-md border-b border-slate-800 flex flex-wrap items-center justify-between gap-2 z-10">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-sky-500/20 text-sky-400 border border-sky-500/30 flex items-center justify-center">
            <Compass className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-xs font-bold text-white tracking-wide flex items-center gap-2">
              <span>Live Region Map & Five Lakes</span>
              <span className="text-[10px] bg-sky-500/20 text-sky-300 border border-sky-400/30 px-1.5 py-0.2 rounded font-mono">
                {filtered.length} / {places.length} Mapped
              </span>
            </h2>
            <p className="text-[10px] text-slate-400">Interactive Spatial Navigator • Mount Fuji (3,776m)</p>
          </div>
        </div>

        {/* Discovery & Lake Filter Pills */}
        <div className="flex flex-wrap items-center gap-1.5 text-[10px]">
          {/* Discovery Filter */}
          <div className="flex items-center bg-slate-800/80 p-0.5 rounded-lg border border-slate-700">
            <button
              onClick={() => setFilterDiscovery('all')}
              className={`px-2 py-0.5 rounded-md font-semibold transition-colors ${
                filterDiscovery === 'all' ? 'bg-sky-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              All Types
            </button>
            <button
              onClick={() => setFilterDiscovery('FAMOUS')}
              className={`px-2 py-0.5 rounded-md font-semibold transition-colors ${
                filterDiscovery === 'FAMOUS' ? 'bg-amber-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              Famous
            </button>
            <button
              onClick={() => setFilterDiscovery('HIDDEN_GEM')}
              className={`px-2 py-0.5 rounded-md font-semibold transition-colors ${
                filterDiscovery === 'HIDDEN_GEM' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              Hidden Gems
            </button>
          </div>

          <div className="h-4 w-px bg-slate-700" />

          {/* Lake Filters */}
          <button
            onClick={() => setFilterLake('all')}
            className={`px-2 py-1 rounded-md font-medium transition-colors ${
              filterLake === 'all' ? 'bg-sky-600 text-white' : 'bg-slate-800 text-slate-400 hover:text-white'
            }`}
          >
            All Lakes
          </button>
          <button
            onClick={() => setFilterLake('kawaguchiko')}
            className={`px-2 py-1 rounded-md font-medium transition-colors ${
              filterLake === 'kawaguchiko' ? 'bg-sky-600 text-white' : 'bg-slate-800 text-slate-400 hover:text-white'
            }`}
          >
            Kawaguchi
          </button>
          <button
            onClick={() => setFilterLake('saiko')}
            className={`px-2 py-1 rounded-md font-medium transition-colors ${
              filterLake === 'saiko' ? 'bg-sky-600 text-white' : 'bg-slate-800 text-slate-400 hover:text-white'
            }`}
          >
            Saiko
          </button>
          <button
            onClick={() => setFilterLake('yamanakako')}
            className={`px-2 py-1 rounded-md font-medium transition-colors ${
              filterLake === 'yamanakako' ? 'bg-sky-600 text-white' : 'bg-slate-800 text-slate-400 hover:text-white'
            }`}
          >
            Yamanaka
          </button>
        </div>
      </div>

      {/* SVG Canvas Map Area */}
      <div className="flex-1 relative overflow-hidden bg-radial from-slate-800 via-slate-900 to-slate-950 flex items-center justify-center">
        <svg
          viewBox="0 0 1000 700"
          className="w-full h-full object-contain pointer-events-auto"
        >
          <defs>
            <linearGradient id="lakeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#0284c7" stopOpacity="0.4" />
              <stop offset="100%" stopColor="#0369a1" stopOpacity="0.7" />
            </linearGradient>
            <linearGradient id="fujiGrad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#f8fafc" />
              <stop offset="30%" stopColor="#cbd5e1" />
              <stop offset="100%" stopColor="#334155" />
            </linearGradient>
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="4" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Grid lines */}
          <pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse">
            <path d="M 50 0 L 0 0 0 50" fill="none" stroke="#1e293b" strokeWidth="0.5" />
          </pattern>
          <rect width="1000" height="700" fill="url(#grid)" />

          {/* Mountain Fuji Base & Silhouette in South */}
          <g transform="translate(500, 560)">
            {/* Fuji mountain contour */}
            <polygon
              points="0,-220 280,120 -280,120"
              fill="url(#fujiGrad)"
              opacity="0.85"
            />
            {/* Snow Cap */}
            <polygon
              points="0,-220 70,-135 -70,-135"
              fill="#ffffff"
              opacity="0.95"
            />
            {/* Fuji Elevation Label */}
            <text
              x="0"
              y="-235"
              textAnchor="middle"
              fill="#38bdf8"
              fontSize="16"
              fontWeight="bold"
              letterSpacing="1"
            >
              ▲ Mt. Fuji (富士山 3,776m)
            </text>
            <text
              x="0"
              y="100"
              textAnchor="middle"
              fill="#94a3b8"
              fontSize="12"
            >
              UNESCO World Cultural Heritage
            </text>
          </g>

          {/* Five Lakes Shapes */}
          {/* Lake Motosu */}
          <g>
            <path
              d="M 100,300 C 130,280 150,320 135,350 C 110,360 80,340 100,300 Z"
              fill="url(#lakeGrad)"
              stroke="#38bdf8"
              strokeWidth="1.5"
            />
            <text x="120" y="325" fill="#bae6fd" fontSize="11" fontWeight="600" textAnchor="middle">
              Lake Motosu
            </text>
          </g>

          {/* Lake Shoji */}
          <g>
            <path
              d="M 180,250 C 210,230 230,260 215,280 C 195,290 170,275 180,250 Z"
              fill="url(#lakeGrad)"
              stroke="#38bdf8"
              strokeWidth="1.5"
            />
            <text x="200" y="265" fill="#bae6fd" fontSize="10" fontWeight="600" textAnchor="middle">
              Lake Shoji
            </text>
          </g>

          {/* Lake Saiko */}
          <g>
            <path
              d="M 280,220 C 360,200 400,240 370,260 C 320,270 260,250 280,220 Z"
              fill="url(#lakeGrad)"
              stroke="#38bdf8"
              strokeWidth="1.5"
            />
            <text x="330" y="242" fill="#bae6fd" fontSize="12" fontWeight="600" textAnchor="middle">
              Lake Saiko
            </text>
          </g>

          {/* Lake Kawaguchiko */}
          <g>
            <path
              d="M 440,180 C 520,150 620,190 580,240 C 530,270 450,220 440,180 Z"
              fill="url(#lakeGrad)"
              stroke="#38bdf8"
              strokeWidth="2"
            />
            <text x="520" y="210" fill="#e0f2fe" fontSize="14" fontWeight="bold" textAnchor="middle">
              Lake Kawaguchiko
            </text>
          </g>

          {/* Lake Yamanakako */}
          <g>
            <path
              d="M 760,320 C 850,280 910,370 860,420 C 800,430 730,370 760,320 Z"
              fill="url(#lakeGrad)"
              stroke="#38bdf8"
              strokeWidth="2"
            />
            <text x="820" y="370" fill="#e0f2fe" fontSize="13" fontWeight="bold" textAnchor="middle">
              Lake Yamanakako
            </text>
          </g>

          {/* Connecting Scenic Highway Lines */}
          <path
            d="M 120,330 Q 200,270 330,245 T 520,220 Q 640,240 700,280 T 820,370"
            fill="none"
            stroke="#475569"
            strokeWidth="2"
            strokeDasharray="4 4"
          />

          {/* Attraction Markers */}
          {filtered.map((loc) => {
            const isSelected = activeLocation.id === loc.id;
            const px = loc.x * 10;
            const py = loc.y * 7;

            return (
              <g
                key={loc.id}
                transform={`translate(${px}, ${py})`}
                onClick={() => handlePinClick(loc)}
                className="cursor-pointer transition-transform hover:scale-125"
              >
                {/* Pin shadow and ripple */}
                {isSelected && (
                  <circle
                    r="20"
                    fill="#38bdf8"
                    opacity="0.3"
                    className="animate-ping"
                  />
                )}
                <circle
                  r={isSelected ? "14" : "10"}
                  fill={isSelected ? "#0284c7" : "#0f172a"}
                  stroke={isSelected ? "#ffffff" : (loc.crowd_level === 'low' ? '#10b981' : (loc.crowd_level === 'moderate' ? '#f59e0b' : '#f43f5e'))}
                  strokeWidth="2.5"
                  filter={isSelected ? "url(#glow)" : undefined}
                />
                <circle
                  r="4"
                  fill="#ffffff"
                />
                {/* Label text */}
                <text
                  y="-14"
                  textAnchor="middle"
                  fill={isSelected ? "#ffffff" : "#cbd5e1"}
                  fontSize={isSelected ? "11" : "9"}
                  fontWeight={isSelected ? "bold" : "600"}
                  className="pointer-events-none drop-shadow-md"
                >
                  {loc.name_en.split(' ')[0]}
                </text>
              </g>
            );
          })}
        </svg>

        {/* Selected Place Overlay Card (Bottom of Map) */}
        {activeLocation && (
          <div className="absolute bottom-3 left-3 right-3 bg-slate-900/95 backdrop-blur-md border border-slate-700/80 rounded-xl p-3 shadow-xl z-20 transition-all">
            <div className="flex gap-3">
              <img
                src={activeLocation.image_url}
                alt={activeLocation.name_en}
                className="w-20 h-20 rounded-lg object-cover bg-slate-800 shrink-0 border border-slate-700"
              />
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h3 className="text-xs font-bold text-white truncate">
                      {activeLocation.name_en}
                    </h3>
                    <p className="text-[10px] text-slate-400 truncate">
                      {activeLocation.name_ja} • {activeLocation.lake.toUpperCase()}
                    </p>
                  </div>
                  <div className="flex items-center gap-1.5">
                    {activeLocation.discovery_type === 'HIDDEN_GEM' ? (
                      <span className="px-2 py-0.5 rounded-full text-[9px] font-bold border bg-emerald-950/80 text-emerald-300 border-emerald-500/40">
                        Hidden Gem
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded-full text-[9px] font-bold border bg-sky-950/80 text-sky-300 border-sky-500/40">
                        Famous
                      </span>
                    )}
                    <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold border ${getCrowdBadge(activeLocation.crowd_level).bg}`}>
                      {getCrowdBadge(activeLocation.crowd_level).label}
                    </span>
                  </div>
                </div>

                <p className="text-[11px] text-slate-300 mt-1 line-clamp-2 leading-relaxed">
                  {activeLocation.description}
                </p>

                <div className="flex items-center justify-between mt-2 pt-2 border-t border-slate-800 text-[10px]">
                  <div className="flex items-center gap-3 text-slate-400">
                    <span className="flex items-center gap-0.5 text-amber-400 font-bold">
                      <Star className="w-3 h-3 fill-amber-400" />
                      <span>{activeLocation.fuji_rating}/5</span>
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3 text-slate-400" />
                      <span>{activeLocation.hours}</span>
                    </span>
                    <span className="flex items-center gap-1 text-emerald-400 font-semibold">
                      <DollarSign className="w-3 h-3" />
                      <span>{activeLocation.admission}</span>
                    </span>
                  </div>

                  <div className="flex items-center gap-1.5">
                    <button
                      onClick={() => {
                        setSelectedPlace(activeLocation.id, activeLocation.name_en);
                        generateTimePlan(timeBudgetHours, activeLocation.id).then(() => openWalkthrough());
                      }}
                      className="flex items-center gap-1 px-2.5 py-1 rounded-md bg-indigo-600 hover:bg-indigo-500 text-white font-semibold shadow-xs transition-colors"
                    >
                      <Sparkles className="w-3 h-3" />
                      <span>Plan {timeBudgetHours}h Trip</span>
                    </button>
                    <button
                      onClick={() => onAskHana(`Tell me more about ${activeLocation.name_en} and how to reach it from Kawaguchiko Station.`)}
                      className="flex items-center gap-1 px-2.5 py-1 rounded-md bg-sky-600 hover:bg-sky-500 text-white font-semibold shadow-xs transition-colors"
                    >
                      <MessageSquare className="w-3 h-3" />
                      <span>Ask Hana</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

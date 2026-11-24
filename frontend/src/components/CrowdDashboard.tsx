import React, { useState, useEffect } from 'react';
import {
  PlaceCrowdStatus,
  CrowdAlternativeCard,
  CrowdScenario,
  CrowdPreference,
  CrowdRecommendationResponse,
  CrowdSystemStatusResponse,
} from '../types';
import { apiUrl } from '../config';
import { DestinationComparisonModal } from './DestinationComparisonModal';
import { AdaptiveItinerary } from './AdaptiveItinerary';
import {
  Compass,
  Mountain,
  ShieldAlert,
  Info,
  Sparkles,
  SlidersHorizontal,
  Search,
} from 'lucide-react';

interface CrowdDashboardProps {
  onAskHana?: (prompt: string) => void;
}

export const CrowdDashboard: React.FC<CrowdDashboardProps> = ({ onAskHana }) => {
  // State
  const [scenario, setScenario] = useState<CrowdScenario>('high');
  const [preference, setPreference] = useState<CrowdPreference>('quiet');
  const [currentPlaceId, setCurrentPlaceId] = useState<string>('kawaguchiko_oishi_park');
  const [originalPlaceId] = useState<string>('kawaguchiko_oishi_park');

  const [systemStatus, setSystemStatus] = useState<CrowdSystemStatusResponse | null>(null);
  const [fallbackPlaces, setFallbackPlaces] = useState<PlaceCrowdStatus[]>([]);
  const [recommendations, setRecommendations] = useState<CrowdRecommendationResponse | null>(null);
  const [isLoadingRecs, setIsLoadingRecs] = useState<boolean>(false);
  const [recError, setRecError] = useState<string | null>(null);

  const [selectedAlternative, setSelectedAlternative] = useState<CrowdAlternativeCard | null>(null);
  const [activeAdaptedAlternative, setActiveAdaptedAlternative] = useState<CrowdAlternativeCard | null>(null);

  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [showTelemetryNotice, setShowTelemetryNotice] = useState<boolean>(false);

  // Fetch system status when scenario changes
  useEffect(() => {
    let isMounted = true;
    const fetchStatus = async () => {
      try {
        let res = await fetch(apiUrl(`/api/crowd/status?scenario=${scenario}`));
        if (!res.ok) {
          res = await fetch(apiUrl(`/api/v1/crowd/status?scenario=${scenario}`));
        }
        if (res.ok && isMounted) {
          const data: CrowdSystemStatusResponse = await res.json();
          setSystemStatus(data);
          if (Array.isArray(data.places) && data.places.length > 0) {
            setFallbackPlaces(data.places);
            return;
          }
        }
      } catch (err) {
        console.error('Failed to fetch crowd system status', err);
      }

      // Secondary fallback: query /api/attractions if places list was not bundled
      try {
        const placesRes = await fetch(apiUrl('/api/attractions'));
        if (placesRes.ok && isMounted) {
          const placesData = await placesRes.json();
          const items: any[] = Array.isArray(placesData) ? placesData : (placesData.items || []);
          const mapped: PlaceCrowdStatus[] = items.map((p) => ({
            place_id: p.place_id,
            name_en: p.name_en || p.name_ja,
            name_ja: p.name_ja,
            primary_category: p.primary_category || 'viewpoint',
            fuji_view_rating: p.fuji_view_rating || 3,
            accessibility_status: p.accessibility_status || 'UNKNOWN',
            crowd_level: 'moderate',
            crowd_index: 50,
            congestion_advisory: 'Standard visitor presence.',
            image_url: 'https://images.unsplash.com/photo-1578637387939-43c525550085?auto=format&fit=crop&w=800&q=80',
            image_attribution: 'Curated Photo',
          }));
          setFallbackPlaces(mapped);
        }
      } catch (err) {
        console.warn('Fallback attractions fetch error:', err);
      }
    };
    fetchStatus();
    return () => { isMounted = false; };
  }, [scenario]);

  // Fetch recommendations when place, preference, or scenario changes
  useEffect(() => {
    let isMounted = true;
    const fetchRecommendations = async () => {
      setIsLoadingRecs(true);
      setRecError(null);
      try {
        const res = await fetch(apiUrl('/api/crowd/recommendations'), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            place_id: currentPlaceId,
            current_place_id: currentPlaceId,
            preference,
            scenario,
            limit: 3,
          }),
        });
        if (!isMounted) return;
        if (res.ok) {
          const data: CrowdRecommendationResponse = await res.json();
          setRecommendations(data);
        } else {
          const errData = await res.json().catch(() => null);
          console.warn('Failed to fetch recommendations:', res.status, errData);
          setRecError(`Recommendation service responded with status ${res.status}`);
        }
      } catch (err) {
        if (!isMounted) return;
        console.error('Failed to fetch recommendations', err);
        setRecError('Network error connecting to CrowdSense recommendations.');
      } finally {
        if (isMounted) setIsLoadingRecs(false);
      }
    };
    fetchRecommendations();
    return () => { isMounted = false; };
  }, [currentPlaceId, preference, scenario]);

  // Safely resolve places list (always an array)
  const placesList: PlaceCrowdStatus[] =
    Array.isArray(systemStatus?.places) && systemStatus.places.length > 0
      ? systemStatus.places
      : fallbackPlaces;

  // Find active place status in the current status list
  const activePlaceStatus: PlaceCrowdStatus | null =
    placesList.find((p) => p.place_id === currentPlaceId) ||
    (placesList.length > 0 ? placesList[0] : null);

  // Original place status (for comparison modal)
  const originalPlaceStatus: PlaceCrowdStatus | null =
    placesList.find((p) => p.place_id === originalPlaceId) ||
    activePlaceStatus;

  const handleSelectAlternative = (alt: CrowdAlternativeCard) => {
    setActiveAdaptedAlternative(alt);
    const pid = alt.place_id || alt.place?.place_id;
    if (pid) setCurrentPlaceId(pid);
  };

  const handleOpenComparison = (alt: CrowdAlternativeCard) => {
    setSelectedAlternative(alt);
    setIsModalOpen(true);
  };

  const getCrowdBadgeStyle = (level?: string) => {
    const lvl = (level || 'moderate').toLowerCase();
    switch (lvl) {
      case 'low':
        return 'bg-emerald-100 text-emerald-800 border-emerald-300';
      case 'moderate':
        return 'bg-amber-100 text-amber-800 border-amber-300';
      case 'high':
        return 'bg-rose-100 text-rose-800 border-rose-300';
      case 'packed':
        return 'bg-purple-100 text-purple-800 border-purple-300';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-300';
    }
  };

  // Filter places for catalogue
  const filteredPlaces = placesList.filter((p) => {
    const nameEn = (p.name_en || '').toLowerCase();
    const nameJa = (p.name_ja || '').toLowerCase();
    const q = searchQuery.toLowerCase();
    const matchesSearch = nameEn.includes(q) || nameJa.includes(q);
    const primaryCat = (p.primary_category || '').toLowerCase();
    const matchesCategory =
      selectedCategory === 'all' || primaryCat === selectedCategory.toLowerCase();
    return matchesSearch && matchesCategory;
  });

  const alternativesList: CrowdAlternativeCard[] =
    Array.isArray(recommendations?.alternatives) ? recommendations.alternatives : [];

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 space-y-8">
      {/* 1. Mount Fuji Hero Section */}
      <div className="relative rounded-3xl overflow-hidden shadow-xl border border-slate-200">
        <div className="h-64 sm:h-72 w-full relative">
          <img
            src={
              systemStatus?.hero_image_url ||
              'https://images.unsplash.com/photo-1490806843957-31f4c9a91c65?auto=format&fit=crop&w=1600&q=85'
            }
            alt="Mount Fuji over Lake Kawaguchiko"
            className="w-full h-full object-cover object-center"
            onError={(e) => {
              (e.currentTarget as HTMLImageElement).src =
                'https://images.unsplash.com/photo-1490806843957-31f4c9a91c65?auto=format&fit=crop&w=1600&q=85';
            }}
          />
          <div className="absolute inset-0 bg-gradient-to-t from-slate-950/90 via-slate-900/40 to-transparent" />
        </div>

        <div className="absolute bottom-0 inset-x-0 p-6 sm:p-8 text-white flex flex-col sm:flex-row sm:items-end justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="bg-sky-500/90 backdrop-blur-xs text-white text-xs font-bold px-2.5 py-0.5 rounded-full flex items-center gap-1">
                <Mountain className="w-3.5 h-3.5" />
                Stage 3 Engine
              </span>
              <span className="bg-amber-500/90 backdrop-blur-xs text-white text-xs font-bold px-2.5 py-0.5 rounded-full">
                SIMULATED DATA
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-white">
              CrowdSense Adaptive Intelligence
            </h1>
            <p className="text-slate-200 text-xs sm:text-sm max-w-2xl mt-1.5 leading-relaxed">
              Real-time crowd simulation and autonomous journey adaptation. Discover serene, high-rating
              alternatives when peak attractions reach capacity.
            </p>
          </div>

          <div className="text-[10px] text-slate-300 font-mono bg-slate-900/60 backdrop-blur-xs px-2.5 py-1.5 rounded-lg border border-slate-700/50 self-start sm:self-auto">
            {systemStatus?.hero_image_attribution || 'Photo: Mount Fuji / Unsplash'}
          </div>
        </div>
      </div>

      {/* 2. System Controls Bar: Scenario + Preference + Telemetry Notice */}
      <div className="bg-white rounded-2xl border border-slate-200 p-4 sm:p-6 shadow-sm space-y-4">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          {/* Scenario Segmented Control */}
          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
                <SlidersHorizontal className="w-3.5 h-3.5 text-sky-600" />
                Crowd Scenario Simulation:
              </span>
              <span className="text-[10px] bg-amber-50 text-amber-700 border border-amber-200 font-semibold px-2 py-0.5 rounded-full">
                SIMULATED
              </span>
            </div>
            <div className="inline-flex rounded-xl bg-slate-100 p-1 border border-slate-200">
              {(['low', 'moderate', 'high'] as CrowdScenario[]).map((sc) => (
                <button
                  key={sc}
                  onClick={() => setScenario(sc)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold capitalize transition-all ${
                    scenario === sc
                      ? 'bg-white text-slate-900 shadow-xs'
                      : 'text-slate-500 hover:text-slate-900'
                  }`}
                >
                  {sc === 'low' && '🟢 Low Crowd'}
                  {sc === 'moderate' && '🟡 Moderate Crowd'}
                  {sc === 'high' && '🔴 High Crowd'}
                </button>
              ))}
            </div>
          </div>

          {/* Preference Segmented Control */}
          <div className="space-y-1.5">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
              <Compass className="w-3.5 h-3.5 text-emerald-600" />
              Crowd Preference:
            </span>
            <div className="inline-flex rounded-xl bg-slate-100 p-1 border border-slate-200">
              <button
                onClick={() => setPreference('quiet')}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  preference === 'quiet'
                    ? 'bg-emerald-600 text-white shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                🌿 Prefer Quiet
              </button>
              <button
                onClick={() => setPreference('balanced')}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  preference === 'balanced'
                    ? 'bg-sky-600 text-white shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                ⚖️ Balanced
              </button>
              <button
                onClick={() => setPreference('popular')}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  preference === 'popular'
                    ? 'bg-indigo-600 text-white shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                🌟 Popular Fine
              </button>
            </div>
          </div>

          {/* Telemetry Status Popover Trigger */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowTelemetryNotice(!showTelemetryNotice)}
              className="flex items-center gap-1.5 text-xs text-amber-800 bg-amber-50 hover:bg-amber-100 border border-amber-300 px-3 py-2 rounded-xl transition-colors font-medium"
            >
              <ShieldAlert className="w-4 h-4 text-amber-600" />
              <span>Real-time Telemetry: UNAVAILABLE</span>
              <Info className="w-3.5 h-3.5 ml-1 text-amber-600" />
            </button>
          </div>
        </div>

        {/* Telemetry Disclosure Notice */}
        {showTelemetryNotice && (
          <div className="p-3.5 bg-amber-50/70 border border-amber-200 rounded-xl text-xs text-amber-900 space-y-1 animate-in fade-in duration-200">
            <div className="font-bold flex items-center gap-1.5">
              <span>Data Classification: SIMULATED_BASELINE</span>
            </div>
            <p className="leading-relaxed">
              Live cellular/IoT sensor feeds in the Yamanashi Five Lakes region are currently{' '}
              <strong>UNAVAILABLE</strong>. To maintain 100% transparency, CrowdSense uses calibrated
              deterministic baseline visitor distributions across Low, Moderate, and High peak scenarios.
            </p>
          </div>
        )}
      </div>

      {/* 3. Congestion Alert & Active Destination */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Active Destination Card */}
        <div className="lg:col-span-1 bg-white rounded-2xl border border-slate-200 p-5 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                Target Destination
              </span>
              <span
                className={`text-xs font-bold uppercase px-2.5 py-0.5 rounded-full border ${getCrowdBadgeStyle(
                  activePlaceStatus?.crowd_level || 'high'
                )}`}
              >
                {activePlaceStatus?.crowd_level || 'High'} Crowd
              </span>
            </div>

            <div className="mt-3 relative h-40 rounded-xl overflow-hidden bg-slate-100">
              <img
                src={
                  activePlaceStatus?.image_url ||
                  'https://images.unsplash.com/photo-1578637387939-43c525550085?auto=format&fit=crop&w=800&q=80'
                }
                alt={activePlaceStatus?.name_en || 'Active Destination'}
                className="w-full h-full object-cover"
                onError={(e) => {
                  (e.currentTarget as HTMLImageElement).src =
                    'https://images.unsplash.com/photo-1578637387939-43c525550085?auto=format&fit=crop&w=800&q=80';
                }}
              />
              <div className="absolute bottom-2 left-2 bg-slate-900/80 backdrop-blur-xs text-white text-[10px] font-mono px-2 py-0.5 rounded">
                {activePlaceStatus?.image_attribution || 'Curated Photo'}
              </div>
            </div>

            <div className="mt-3">
              <h3 className="text-base font-bold text-slate-900">
                {activePlaceStatus?.name_en || 'Oishi Park'}
              </h3>
              <p className="text-xs text-slate-500">{activePlaceStatus?.name_ja || '大石公園'}</p>

              <div className="mt-3 p-3 bg-rose-50 border border-rose-200 rounded-lg text-xs text-rose-800">
                <span className="font-bold block mb-0.5">Congestion Advisory:</span>
                {activePlaceStatus?.congestion_advisory ||
                  'Heavy tourist volume. Expect dense crowds at viewpoints and parking delays.'}
              </div>
            </div>
          </div>

          {activeAdaptedAlternative && (
            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
              <span className="text-xs text-emerald-700 font-semibold">
                ✓ Adapted to {activeAdaptedAlternative.name_en}
              </span>
              <button
                onClick={() => {
                  setActiveAdaptedAlternative(null);
                  setCurrentPlaceId(originalPlaceId);
                }}
                className="text-xs text-slate-500 hover:text-slate-800 underline"
              >
                Reset to Oishi Park
              </button>
            </div>
          )}
        </div>

        {/* Recommended Alternatives Grid */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-emerald-600" />
                CrowdSense Recommended Alternatives
              </h2>
              <p className="text-xs text-slate-500">
                Deterministic multi-factor ranking based on crowd reduction, Fuji view quality, distance, and
                accessibility.
              </p>
            </div>
            {onAskHana && (
              <button
                onClick={() =>
                  onAskHana(
                    `I want to visit ${activePlaceStatus?.name_en || 'Oishi Park'} with quiet alternatives.`
                  )
                }
                className="hidden sm:flex items-center gap-1.5 text-xs font-semibold text-sky-700 hover:text-sky-900 bg-sky-50 border border-sky-200 px-3 py-1.5 rounded-lg"
              >
                <Sparkles className="w-3.5 h-3.5 text-sky-600" />
                Ask Hana to Compare
              </button>
            )}
          </div>

          {isLoadingRecs ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="bg-white rounded-xl border border-slate-200 p-4 space-y-3 animate-pulse">
                  <div className="h-32 bg-slate-200 rounded-lg" />
                  <div className="h-4 bg-slate-200 rounded w-3/4" />
                  <div className="h-3 bg-slate-200 rounded w-1/2" />
                  <div className="h-8 bg-slate-200 rounded" />
                </div>
              ))}
            </div>
          ) : recError ? (
            <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl text-amber-800 text-xs">
              <span className="font-semibold block mb-1">Recommendation Notice:</span>
              {recError}
            </div>
          ) : alternativesList.length === 0 ? (
            <div className="p-8 text-center bg-slate-50 border border-dashed border-slate-200 rounded-xl text-slate-500 text-xs">
              No alternative destinations found for this filter combination.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {alternativesList.map((alt) => {
                const altId = alt.place_id || 'unknown';
                const altNameEn = alt.name_en || 'Alternative';
                const altNameJa = alt.name_ja || '';
                const altImg =
                  alt.image_url ||
                  'https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=800&q=80';
                const altReduction =
                  alt.crowd_reduction_percent ??
                  alt.crowd_reduction_pct ??
                  (typeof (alt as any).crowd_reduction === 'number' ? Math.round((alt as any).crowd_reduction * 100) : 0);
                const altCrowdLevel = alt.crowd_level || 'low';
                const altFuji = alt.fuji_view_rating ?? 4;
                const altDist = alt.distance_km ?? 0;
                const altCat = alt.primary_category || 'viewpoint';
                const altReason =
                  alt.recommendation_reason ||
                  (alt as any).adaptation_reason ||
                  'Verified alternative with reduced crowd density.';

                return (
                  <div
                    key={altId}
                    className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs hover:shadow-md transition-shadow flex flex-col justify-between"
                  >
                    <div>
                      <div className="relative h-32 bg-slate-100 overflow-hidden">
                        <img
                          src={altImg}
                          alt={altNameEn}
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            (e.currentTarget as HTMLImageElement).src =
                              'https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=800&q=80';
                          }}
                        />
                        <div className="absolute top-2 left-2">
                          <span className="bg-emerald-600 text-white font-bold text-[10px] px-2 py-0.5 rounded shadow-xs">
                            -{altReduction}% Crowd
                          </span>
                        </div>
                        <div className="absolute bottom-1.5 right-1.5">
                          <span
                            className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full border shadow-xs ${getCrowdBadgeStyle(
                              altCrowdLevel
                            )}`}
                          >
                            {altCrowdLevel}
                          </span>
                        </div>
                      </div>

                      <div className="p-3.5">
                        <h3 className="text-sm font-bold text-slate-900 line-clamp-1">{altNameEn}</h3>
                        <p className="text-[11px] text-slate-500 mb-2">{altNameJa}</p>

                        <div className="flex items-center gap-2 text-[11px] text-slate-600 mb-2 flex-wrap">
                          <span className="text-amber-500 font-semibold">★ {altFuji}/5</span>
                          <span>•</span>
                          <span>{altDist} km</span>
                          <span>•</span>
                          <span className="capitalize">{altCat}</span>
                        </div>

                        <p className="text-[11px] text-slate-600 line-clamp-2 leading-relaxed bg-slate-50 p-2 rounded border border-slate-100">
                          {altReason}
                        </p>
                      </div>
                    </div>

                    <div className="p-3.5 pt-0 space-y-2">
                      <div className="grid grid-cols-2 gap-2">
                        <button
                          onClick={() => handleOpenComparison(alt)}
                          className="w-full py-1.5 px-2 text-[11px] font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors text-center"
                        >
                          Compare
                        </button>
                        <button
                          onClick={() => handleSelectAlternative(alt)}
                          className="w-full py-1.5 px-2 text-[11px] font-bold text-white bg-emerald-600 hover:bg-emerald-700 rounded-lg transition-colors text-center shadow-xs"
                        >
                          Select
                        </button>
                      </div>

                      {onAskHana && (
                        <button
                          onClick={() =>
                            onAskHana(`Tell me about visiting ${altNameEn} as an alternative to Oishi Park.`)
                          }
                          className="w-full text-[10px] text-sky-700 hover:text-sky-900 text-center font-medium block"
                        >
                          Ask Hana about {altNameEn} →
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* 4. Adaptive Transit Itinerary Section */}
      <AdaptiveItinerary
        originName="Kawaguchiko Station"
        activeDestinationName={activeAdaptedAlternative ? activeAdaptedAlternative.name_en : 'Oishi Park'}
        activeDestinationJa={activeAdaptedAlternative ? activeAdaptedAlternative.name_ja : '大石公園'}
        originalDestinationName={originalPlaceStatus?.name_en || 'Oishi Park'}
        isAdapted={!!activeAdaptedAlternative}
        crowdReductionPercent={activeAdaptedAlternative?.crowd_reduction_percent}
        onAskHana={onAskHana}
      />

      {/* 5. All Verified Destinations Crowd Grid */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 className="text-base font-bold text-slate-900">
              All 35 Verified Destinations (Current Scenario: {scenario.toUpperCase()})
            </h2>
            <p className="text-xs text-slate-500">
              Browse crowd levels across all official Mount Fuji & Yamanashi destinations.
            </p>
          </div>

          {/* Search bar */}
          <div className="relative w-full sm:w-64">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search destination..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 text-xs border border-slate-200 rounded-lg outline-none focus:border-sky-500"
            />
          </div>
        </div>

        {/* Category Filter Chips */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs">
          {['all', 'viewpoint', 'shrine', 'park', 'museum', 'lakeside'].map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1 rounded-full capitalize font-medium transition-colors ${
                selectedCategory === cat
                  ? 'bg-slate-900 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Place cards grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 pt-2">
          {filteredPlaces.map((p) => (
            <div
              key={p.place_id}
              onClick={() => setCurrentPlaceId(p.place_id)}
              className={`rounded-xl border p-3 cursor-pointer transition-all ${
                currentPlaceId === p.place_id
                  ? 'border-sky-500 ring-2 ring-sky-100 bg-sky-50/20'
                  : 'border-slate-200 hover:border-slate-300 bg-white'
              }`}
            >
              <div className="relative h-28 rounded-lg overflow-hidden bg-slate-100 mb-2">
                <img
                  src={p.image_url}
                  alt={p.name_en}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    (e.currentTarget as HTMLImageElement).src =
                      'https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=800&q=80';
                  }}
                />
                <div className="absolute top-1.5 right-1.5">
                  <span
                    className={`text-[9px] font-bold uppercase px-2 py-0.5 rounded-full border shadow-xs ${getCrowdBadgeStyle(
                      p.crowd_level
                    )}`}
                  >
                    {p.crowd_level}
                  </span>
                </div>
              </div>

              <div className="space-y-1">
                <h4 className="text-xs font-bold text-slate-900 line-clamp-1">{p.name_en}</h4>
                <p className="text-[10px] text-slate-500 line-clamp-1">{p.name_ja}</p>
                <div className="flex items-center justify-between text-[10px] text-slate-500 pt-1">
                  <span>★ {p.fuji_view_rating}/5</span>
                  <span className="capitalize">{p.primary_category}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Comparison Modal */}
      <DestinationComparisonModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        originalPlace={originalPlaceStatus}
        alternative={selectedAlternative}
        onSelectAlternative={handleSelectAlternative}
      />
    </div>
  );
};

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
import {
  Mountain,
  Compass,
  SlidersHorizontal,
  Sparkles,
  Info,
  ShieldAlert,
} from 'lucide-react';

interface CrowdSenseDashboardProps {
  onAskHana?: (prompt: string) => void;
}

export const CrowdSenseDashboard: React.FC<CrowdSenseDashboardProps> = ({ onAskHana }) => {
  const [scenario, setScenario] = useState<CrowdScenario>('high');
  const [preference, setPreference] = useState<CrowdPreference>('quiet');
  const [currentPlaceId, setCurrentPlaceId] = useState<string>('kawaguchiko_oishi_park');
  const [originalPlaceId] = useState<string>('kawaguchiko_oishi_park');

  const [systemStatus, setSystemStatus] = useState<CrowdSystemStatusResponse | null>(null);
  const [recommendations, setRecommendations] = useState<CrowdRecommendationResponse | null>(null);
  const [isLoadingRecs, setIsLoadingRecs] = useState<boolean>(false);
  const [recError, setRecError] = useState<string | null>(null);

  const [selectedAlternative, setSelectedAlternative] = useState<CrowdAlternativeCard | null>(null);
  const [activeAdaptedAlternative, setActiveAdaptedAlternative] = useState<CrowdAlternativeCard | null>(null);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [showTelemetryNotice, setShowTelemetryNotice] = useState<boolean>(false);

  // 1. Fetch system status when scenario changes
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
        }
      } catch (err) {
        console.error('Failed to fetch crowd system status:', err);
      }
    };
    fetchStatus();
    return () => {
      isMounted = false;
    };
  }, [scenario]);

  // 2. Fetch recommendations whenever currentPlaceId, preference, or scenario changes
  useEffect(() => {
    let isMounted = true;
    const fetchRecommendations = async () => {
      setIsLoadingRecs(true);
      setRecError(null);
      try {
        const bodyPayload = {
          place_id: currentPlaceId,
          preference: preference,
          scenario: scenario,
          limit: 3,
        };

        let res = await fetch(apiUrl('/api/v1/crowd/recommendations'), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(bodyPayload),
        });

        if (!res.ok) {
          res = await fetch(apiUrl('/api/crowd/recommendations'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(bodyPayload),
          });
        }

        if (res.ok && isMounted) {
          const data: CrowdRecommendationResponse = await res.json();
          setRecommendations(data);
          setRecError(null);
        } else {
          const errText = await res.text().catch(() => '');
          console.error('Crowd recommendations error:', res.status, errText);
          setRecError('Failed to fetch crowd recommendations from backend.');
        }
      } catch (err) {
        if (!isMounted) return;
        setRecError('Network error connecting to CrowdSense recommendations.');
      } finally {
        if (isMounted) setIsLoadingRecs(false);
      }
    };
    fetchRecommendations();
    return () => {
      isMounted = false;
    };
  }, [currentPlaceId, preference, scenario]);

  const placesList: PlaceCrowdStatus[] = Array.isArray(systemStatus?.places)
    ? systemStatus.places
    : [];

  const activePlaceStatus: PlaceCrowdStatus | null =
    placesList.find((p) => p.place_id === currentPlaceId) ||
    (placesList.length > 0 ? placesList[0] : null);

  const originalPlaceStatus: PlaceCrowdStatus | null =
    placesList.find((p) => p.place_id === originalPlaceId) || activePlaceStatus;

  const handleOpenComparison = (alt: CrowdAlternativeCard) => {
    setSelectedAlternative(alt);
    setIsModalOpen(true);
  };

  const handleSelectAlternative = (alt: CrowdAlternativeCard) => {
    setActiveAdaptedAlternative(alt);
    const pid = alt.place_id || (alt.place && (alt.place as any).place_id);
    if (pid) setCurrentPlaceId(pid);
  };

  const alternativesList: CrowdAlternativeCard[] = Array.isArray(
    recommendations?.alternatives
  )
    ? recommendations.alternatives
    : [];

  return (
    <div className="space-y-6 pb-12">
      {/* 1. Large Scenic Mount Fuji Hero Banner (Matches Image 1) */}
      <div className="relative rounded-2xl overflow-hidden shadow-sm border border-[#E1EAF1]">
        <div className="h-[280px] sm:h-[300px] w-full relative">
          <img
            src={
              systemStatus?.hero_image_url ||
              'https://images.unsplash.com/photo-1490806843957-31f4c9a91c65?auto=format&fit=crop&w=1600&q=85'
            }
            alt="Mount Fuji with cherry blossoms & Lake Kawaguchi"
            className="w-full h-full object-cover object-center"
            onError={(e) => {
              (e.currentTarget as HTMLImageElement).src =
                'https://images.unsplash.com/photo-1490806843957-31f4c9a91c65?auto=format&fit=crop&w=1600&q=85';
            }}
          />
          {/* Subtle Deep Blue Gradient Overlay for legible white typography */}
          <div className="absolute inset-0 bg-gradient-to-r from-[#0C2340]/85 via-[#0C2340]/50 to-transparent" />
        </div>

        {/* Hero Content Overlay */}
        <div className="absolute inset-0 p-6 sm:p-8 text-white flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <span className="bg-[#078ACB] text-white text-[11px] font-bold px-2.5 py-0.5 rounded-full flex items-center gap-1 shadow-2xs">
                <Mountain className="w-3.5 h-3.5" />
                Stage 3 Engine
              </span>
              <span className="bg-[#F59E0B] text-white text-[11px] font-bold px-2.5 py-0.5 rounded-full shadow-2xs">
                SIMULATED DATA
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white font-sans drop-shadow-xs">
              CrowdSense Adaptive Intelligence
            </h1>
            <p className="text-slate-100 text-xs sm:text-sm max-w-xl mt-2 leading-relaxed font-normal drop-shadow-2xs">
              Real-time crowd simulation and autonomous journey adaptation. Discover serene, high-rating
              alternatives when peak attractions reach capacity.
            </p>
          </div>

          <div className="text-[10px] text-slate-200/90 font-mono">
            {systemStatus?.hero_image_attribution ||
              'Photo by Masaaki Komori on Unsplash (Mount Fuji with cherry blossoms & Lake Kawaguchi)'}
          </div>
        </div>
      </div>

      {/* 2. Simulation & Preference Control Bar (Matches Image 1) */}
      <div className="bg-white rounded-2xl border border-[#E1EAF1] p-4 sm:p-5 shadow-xs">
        <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-4">
          <div className="flex flex-col md:flex-row md:items-center gap-6">
            {/* A. CROWD SCENARIO SIMULATION */}
            <div className="space-y-1.5">
              <div className="flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-[#14283F]">
                <SlidersHorizontal className="w-3.5 h-3.5 text-[#078ACB]" />
                <span>Crowd Scenario Simulation:</span>
                <span className="text-[10px] text-amber-700 bg-amber-50 border border-amber-200 px-1.5 py-0.5 rounded font-normal">
                  SIMULATED
                </span>
              </div>
              <div className="inline-flex rounded-xl bg-[#F5F8FB] p-1 border border-[#E1EAF1]">
                <button
                  onClick={() => setScenario('low')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    scenario === 'low'
                      ? 'bg-white text-[#14283F] shadow-xs'
                      : 'text-[#718198] hover:text-[#14283F]'
                  }`}
                >
                  <span className="w-2 h-2 rounded-full bg-emerald-500" />
                  <span>Low Crowd</span>
                </button>
                <button
                  onClick={() => setScenario('moderate')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    scenario === 'moderate'
                      ? 'bg-white text-[#14283F] shadow-xs'
                      : 'text-[#718198] hover:text-[#14283F]'
                  }`}
                >
                  <span className="w-2 h-2 rounded-full bg-amber-500" />
                  <span>Moderate Crowd</span>
                </button>
                <button
                  onClick={() => setScenario('high')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    scenario === 'high'
                      ? 'bg-white text-[#14283F] shadow-xs'
                      : 'text-[#718198] hover:text-[#14283F]'
                  }`}
                >
                  <span className="w-2 h-2 rounded-full bg-rose-500" />
                  <span>High Crowd</span>
                </button>
              </div>
            </div>

            {/* B. CROWD PREFERENCE */}
            <div className="space-y-1.5">
              <div className="flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-[#14283F]">
                <Compass className="w-3.5 h-3.5 text-[#078ACB]" />
                <span>Crowd Preference:</span>
              </div>
              <div className="inline-flex rounded-xl bg-[#F5F8FB] p-1 border border-[#E1EAF1]">
                <button
                  onClick={() => setPreference('quiet')}
                  className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    preference === 'quiet'
                      ? 'bg-[#00875A] text-white shadow-xs'
                      : 'text-[#718198] hover:text-[#14283F]'
                  }`}
                >
                  <span>🌿 Prefer Quiet</span>
                </button>
                <button
                  onClick={() => setPreference('balanced')}
                  className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    preference === 'balanced'
                      ? 'bg-[#078ACB] text-white shadow-xs'
                      : 'text-[#718198] hover:text-[#14283F]'
                  }`}
                >
                  <span>⚖️ Balanced</span>
                </button>
                <button
                  onClick={() => setPreference('popular')}
                  className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    preference === 'popular'
                      ? 'bg-[#5243AA] text-white shadow-xs'
                      : 'text-[#718198] hover:text-[#14283F]'
                  }`}
                >
                  <span>🌟 Popular Fine</span>
                </button>
              </div>
            </div>
          </div>

          {/* C. REAL-TIME TELEMETRY STATUS */}
          <div className="flex items-center gap-2 self-start xl:self-center">
            <button
              onClick={() => setShowTelemetryNotice(!showTelemetryNotice)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-xl border border-amber-200 bg-amber-50/80 hover:bg-amber-100 text-amber-900 text-xs font-medium transition-colors"
            >
              <ShieldAlert className="w-4 h-4 text-amber-600" />
              <span>Real-time Telemetry: UNAVAILABLE</span>
              <Info className="w-3.5 h-3.5 text-amber-600" />
            </button>
          </div>
        </div>

        {/* Telemetry Disclosure Notice */}
        {showTelemetryNotice && (
          <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-900 leading-relaxed">
            <span className="font-bold block mb-0.5">Telemetry Infrastructure Notice:</span>
            Live IoT/cellular sensors for Lake Kawaguchiko are currently unconfigured.
            CrowdSense calculates deterministic distributions based on verified historical seasonal flow.
          </div>
        )}
      </div>

      {/* 3. Target Destination & Recommended Alternatives (Matches Image 1) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* LEFT COLUMN: Target Destination Card (~30% / 4 cols) */}
        <div className="lg:col-span-4 bg-white rounded-2xl border border-[#E1EAF1] p-5 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-[#E1EAF1]">
              <span className="text-xs font-bold uppercase tracking-wider text-[#718198]">
                Target Destination
              </span>
              <span className="text-xs font-bold uppercase px-3 py-0.5 rounded-full bg-rose-50 text-rose-700 border border-rose-200">
                {activePlaceStatus?.crowd_level || 'HIGH'} CROWD
              </span>
            </div>

            {/* Target Destination Photo */}
            <div className="mt-3.5 relative h-44 rounded-xl overflow-hidden bg-slate-100 border border-[#E1EAF1]">
              <img
                src={
                  activePlaceStatus?.image_url ||
                  'https://images.unsplash.com/photo-1578637387939-43c525550085?auto=format&fit=crop&w=800&q=80'
                }
                alt={activePlaceStatus?.name_en || 'Oishi Park'}
                className="w-full h-full object-cover"
                onError={(e) => {
                  (e.currentTarget as HTMLImageElement).src =
                    'https://images.unsplash.com/photo-1578637387939-43c525550085?auto=format&fit=crop&w=800&q=80';
                }}
              />
              <div className="absolute bottom-2 left-2 bg-[#0C2340]/80 backdrop-blur-xs text-white text-[10px] font-mono px-2 py-0.5 rounded">
                {activePlaceStatus?.image_attribution || 'Photo: Unsplash'}
              </div>
            </div>

            <div className="mt-3.5">
              <h3 className="text-base font-bold text-[#14283F]">
                {activePlaceStatus?.name_en || 'Oishi Park'}
              </h3>
              <p className="text-xs text-[#718198]">{activePlaceStatus?.name_ja || '大石公園'}</p>

              <div className="mt-3 p-3 bg-rose-50/70 border border-rose-200 rounded-xl text-xs text-rose-800 leading-relaxed">
                <span className="font-bold block mb-0.5">Congestion Advisory:</span>
                {activePlaceStatus?.congestion_advisory ||
                  'High tour bus arrivals; lakefront promenade heavily congested.'}
              </div>
            </div>
          </div>

          {activeAdaptedAlternative && (
            <div className="mt-4 pt-3 border-t border-[#E1EAF1] flex items-center justify-between">
              <span className="text-xs text-emerald-700 font-semibold">
                ✓ Adapted to {activeAdaptedAlternative.name_en}
              </span>
              <button
                onClick={() => {
                  setActiveAdaptedAlternative(null);
                  setCurrentPlaceId(originalPlaceId);
                }}
                className="text-xs text-[#078ACB] hover:underline"
              >
                Reset to Oishi Park
              </button>
            </div>
          )}
        </div>

        {/* RIGHT COLUMN: Recommended Alternatives (~70% / 8 cols) */}
        <div className="lg:col-span-8 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-[#14283F] flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-[#078ACB]" />
                CrowdSense Recommended Alternatives
              </h2>
              <p className="text-xs text-[#718198]">
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
                className="hidden sm:flex items-center gap-1.5 text-xs font-semibold text-[#078ACB] bg-[#EBF5FB] hover:bg-[#DDF0FA] border border-[#BDE0F5] px-3.5 py-1.5 rounded-lg transition-colors shadow-2xs"
              >
                <Sparkles className="w-3.5 h-3.5 text-[#078ACB]" />
                <span>Ask Hana to Compare</span>
              </button>
            )}
          </div>

          {isLoadingRecs ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="bg-white rounded-2xl border border-[#E1EAF1] p-4 space-y-3 animate-pulse"
                >
                  <div className="h-28 bg-slate-100 rounded-xl" />
                  <div className="h-4 bg-slate-100 rounded w-3/4" />
                  <div className="h-3 bg-slate-100 rounded w-1/2" />
                </div>
              ))}
            </div>
          ) : recError ? (
            <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl text-amber-800 text-xs">
              {recError}
            </div>
          ) : alternativesList.length === 0 ? (
            <div className="p-8 text-center bg-white border border-dashed border-[#E1EAF1] rounded-2xl text-[#718198] text-xs">
              No alternative destinations found for this criteria.
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
                  (typeof (alt as any).crowd_reduction === 'number'
                    ? Math.round((alt as any).crowd_reduction * 100)
                    : 0);
                const altFuji = alt.fuji_view_rating ?? 4;
                const altDist = alt.distance_km ?? 0;
                const altReason =
                  alt.recommendation_reason ||
                  (alt as any).adaptation_reason ||
                  'Verified alternative with reduced crowd density.';

                return (
                  <div
                    key={altId}
                    className="bg-white rounded-2xl border border-[#E1EAF1] overflow-hidden shadow-2xs hover:shadow-xs transition-shadow flex flex-col justify-between"
                  >
                    <div>
                      {/* Destination Image with Badge */}
                      <div className="relative h-28 bg-slate-100 overflow-hidden">
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
                          <span className="bg-[#00875A] text-white font-bold text-[10px] px-2 py-0.5 rounded-full shadow-xs">
                            -{altReduction}% Crowd
                          </span>
                        </div>
                      </div>

                      {/* Content */}
                      <div className="p-3.5">
                        <h3 className="text-sm font-bold text-[#14283F] line-clamp-1">{altNameEn}</h3>
                        <p className="text-[11px] text-[#718198] mb-2">{altNameJa}</p>

                        <div className="flex items-center gap-2 text-[11px] text-[#718198] mb-2">
                          <span className="text-amber-500 font-semibold">★ {altFuji}/5</span>
                          <span>•</span>
                          <span>{altDist} km</span>
                        </div>

                        <p className="text-[11px] text-[#425466] line-clamp-2 leading-relaxed bg-[#F5F8FB] p-2 rounded-lg border border-[#E1EAF1]">
                          {altReason}
                        </p>
                      </div>
                    </div>

                    <div className="p-3.5 pt-0 space-y-2">
                      <div className="grid grid-cols-2 gap-2">
                        <button
                          onClick={() => handleOpenComparison(alt)}
                          className="w-full py-1.5 px-2 text-[11px] font-semibold text-[#14283F] bg-[#F5F8FB] hover:bg-[#E1EAF1] rounded-lg transition-colors text-center border border-[#E1EAF1]"
                        >
                          Compare
                        </button>
                        <button
                          onClick={() => handleSelectAlternative(alt)}
                          className="w-full py-1.5 px-2 text-[11px] font-bold text-white bg-[#00875A] hover:bg-[#006644] rounded-lg transition-colors text-center shadow-xs"
                        >
                          Select
                        </button>
                      </div>

                      {onAskHana && (
                        <button
                          onClick={() =>
                            onAskHana(`Tell me about visiting ${altNameEn} as an alternative to Oishi Park.`)
                          }
                          className="w-full text-[10px] text-[#078ACB] hover:underline text-center font-medium block"
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

      {/* Comparison Modal */}
      {isModalOpen && selectedAlternative && originalPlaceStatus && (
        <DestinationComparisonModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          originalPlace={originalPlaceStatus}
          alternative={selectedAlternative}
          onSelectAlternative={(alt) => {
            handleSelectAlternative(alt);
            setIsModalOpen(false);
          }}
        />
      )}
    </div>
  );
};

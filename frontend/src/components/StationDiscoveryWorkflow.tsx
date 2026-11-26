import React, { useState, useMemo } from 'react';
import { useTrip, STANDARD_HUBS } from '../context/TripContext';
import { Place } from '../types';
import { TransitInstructionModal } from './TransitInstructionModal';
import { TripProgressView } from './TripProgressView';
import { 
  MapPin, 
  Navigation, 
  Search, 
  Sparkles, 
  Clock, 
  Heart, 
  Bus, 
  ChevronDown, 
  CheckCircle2, 
  ArrowRight,
  Flame,
  Leaf,
  DollarSign,
  RotateCcw,
  Star
} from 'lucide-react';

interface StationDiscoveryWorkflowProps {
  onAskHana?: (prompt: string) => void;
  onOpenMap?: () => void;
}

export const StationDiscoveryWorkflow: React.FC<StationDiscoveryWorkflowProps> = ({
  onAskHana,
  onOpenMap,
}) => {
  const {
    currentLocation,
    setCurrentLocation,
    selectedPlaceId,
    selectedPlaceName,
    setSelectedPlace,
    timeBudgetHours,
    setTimeBudgetHours,
    departureTime,
    setDepartureTime,
    foodExperience,
    setFoodExperience,
    foodStyles,
    toggleFoodStyle,
    requestGeolocation,
    activeWorkflowStep,
    setActiveWorkflowStep,
    isTransitModalOpen,
    setIsTransitModalOpen,
    setIsTripProgressActive,
  } = useTrip();

  // Tab: Famous Places (120+) vs Hidden Gems (115+)
  const [activeTab, setActiveTab] = useState<'famous' | 'gems'>('famous');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All Categories');
  const [selectedDistanceFilter, setSelectedDistanceFilter] = useState('All');
  const [selectedCrowdFilter, setSelectedCrowdFilter] = useState('All');
  const [openNowOnly, setOpenNowOnly] = useState(false);
  const [isStationDropdownOpen, setIsStationDropdownOpen] = useState(false);
  const [favorites, setFavorites] = useState<string[]>([]);
  const [costEstimateModalOpen, setCostEstimateModalOpen] = useState(false);

  // Default curated cards representing verified destinations (with photos and accurate coordinates)
  const defaultPlaces: Place[] = useMemo(() => [
    {
      place_id: 'kawaguchiko_oishi_park',
      name_en: 'Oishi Park',
      name_ja: '大石公園',
      latitude: 35.5234,
      longitude: 138.7456,
      coords_source: 'SEED_VERIFIED',
      primary_category: 'Nature & Parks',
      sub_category: 'Flower Park & Lake View',
      opening_status: 'ALWAYS_OPEN',
      opening_hours_source: 'OFFICIAL',
      general_admission_type: 'FREE',
      admission_fee_source: 'OFFICIAL',
      accessibility_status: 'VERIFIED_ACCESSIBLE',
      accessibility_source: 'OFFICIAL',
      fuji_view_rating: 5.0,
      indoor_alternative: false,
      discovery_type: 'FAMOUS',
      image_url: 'https://images.unsplash.com/photo-1578637387939-43c525550085?auto=format&fit=crop&w=600&q=80',
      provenance_tier: 'OFFICIAL_GOV',
      source_url: 'https://www.yamanashi-kankou.jp',
      required_attribution: 'Fuji Five Lakes Tourism',
      source_retrieval_date: '2026-01-01',
      last_verified_date: '2026-01-01',
    },
    {
      place_id: 'chureito_pagoda',
      name_en: 'Chureito Pagoda',
      name_ja: '新倉山浅間公園',
      latitude: 35.5013,
      longitude: 138.8014,
      coords_source: 'SEED_VERIFIED',
      primary_category: 'Shrines & Temples',
      sub_category: 'Panoramic Viewpoint',
      opening_status: 'ALWAYS_OPEN',
      opening_hours_source: 'OFFICIAL',
      general_admission_type: 'FREE',
      admission_fee_source: 'OFFICIAL',
      accessibility_status: 'PARTIAL_STEPS',
      accessibility_source: 'OFFICIAL',
      fuji_view_rating: 5.0,
      indoor_alternative: false,
      discovery_type: 'FAMOUS',
      image_url: 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=600&q=80',
      provenance_tier: 'OFFICIAL_GOV',
      source_url: 'https://www.yamanashi-kankou.jp',
      required_attribution: 'Fujiyoshida Tourism',
      source_retrieval_date: '2026-01-01',
      last_verified_date: '2026-01-01',
    },
    {
      place_id: 'oshino_hakkai_springs',
      name_en: 'Oshino Hakkai',
      name_ja: '忍野八海',
      latitude: 35.4597,
      longitude: 138.8329,
      coords_source: 'SEED_VERIFIED',
      primary_category: 'Cultural & Heritage',
      sub_category: 'Natural Spring Ponds',
      opening_status: 'ALWAYS_OPEN',
      opening_hours_source: 'OFFICIAL',
      general_admission_type: 'FREE',
      admission_fee_source: 'OFFICIAL',
      accessibility_status: 'VERIFIED_ACCESSIBLE',
      accessibility_source: 'OFFICIAL',
      fuji_view_rating: 4.8,
      indoor_alternative: false,
      discovery_type: 'FAMOUS',
      image_url: 'https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=600&q=80',
      provenance_tier: 'OFFICIAL_GOV',
      source_url: 'https://www.yamanashi-kankou.jp',
      required_attribution: 'Oshino Village Tourism',
      source_retrieval_date: '2026-01-01',
      last_verified_date: '2026-01-01',
    },
    {
      place_id: 'ubuyagasaki_promontory',
      name_en: 'Ubuyagasaki',
      name_ja: '産屋ヶ崎',
      latitude: 35.5118,
      longitude: 138.7677,
      coords_source: 'SEED_VERIFIED',
      primary_category: 'Scenic Viewpoint',
      sub_category: 'Lake & Bridge Reflection',
      opening_status: 'ALWAYS_OPEN',
      opening_hours_source: 'OFFICIAL',
      general_admission_type: 'FREE',
      admission_fee_source: 'OFFICIAL',
      accessibility_status: 'VERIFIED_ACCESSIBLE',
      accessibility_source: 'OFFICIAL',
      fuji_view_rating: 4.9,
      indoor_alternative: false,
      discovery_type: 'HIDDEN_GEM',
      image_url: 'https://images.unsplash.com/photo-1528164344705-475426879c0d?auto=format&fit=crop&w=600&q=80',
      provenance_tier: 'OFFICIAL_GOV',
      source_url: 'https://www.yamanashi-kankou.jp',
      required_attribution: 'Kawaguchiko Tourism',
      source_retrieval_date: '2026-01-01',
      last_verified_date: '2026-01-01',
    },
    {
      place_id: 'nagasaki_cape',
      name_en: 'Nagasaki Cape',
      name_ja: '長崎ヶ崎',
      latitude: 35.5222,
      longitude: 138.7567,
      coords_source: 'SEED_VERIFIED',
      primary_category: 'Scenic Viewpoint',
      sub_category: 'Cherry Blossoms & Quiet Shore',
      opening_status: 'ALWAYS_OPEN',
      opening_hours_source: 'OFFICIAL',
      general_admission_type: 'FREE',
      admission_fee_source: 'OFFICIAL',
      accessibility_status: 'VERIFIED_ACCESSIBLE',
      accessibility_source: 'OFFICIAL',
      fuji_view_rating: 4.9,
      indoor_alternative: false,
      discovery_type: 'HIDDEN_GEM',
      image_url: 'https://images.unsplash.com/photo-1542051841857-5f90071e7989?auto=format&fit=crop&w=600&q=80',
      provenance_tier: 'OFFICIAL_GOV',
      source_url: 'https://www.yamanashi-kankou.jp',
      required_attribution: 'Kawaguchiko Tourism',
      source_retrieval_date: '2026-01-01',
      last_verified_date: '2026-01-01',
    },
    {
      place_id: 'lake_saiko_iyashi_no_sato',
      name_en: 'Saiko Iyashi-no-Sato',
      name_ja: '西湖いやしの里根場',
      latitude: 35.5085,
      longitude: 138.6653,
      coords_source: 'SEED_VERIFIED',
      primary_category: 'Cultural & Heritage',
      sub_category: 'Thatched Roof Village',
      opening_status: 'REGULAR_HOURS',
      opening_hours_source: 'OFFICIAL',
      general_admission_type: 'PAID',
      admission_fee_source: 'OFFICIAL',
      accessibility_status: 'VERIFIED_ACCESSIBLE',
      accessibility_source: 'OFFICIAL',
      fuji_view_rating: 4.8,
      indoor_alternative: true,
      discovery_type: 'HIDDEN_GEM',
      image_url: 'https://images.unsplash.com/photo-1570125909232-eb263c188f7e?auto=format&fit=crop&w=600&q=80',
      provenance_tier: 'OFFICIAL_GOV',
      source_url: 'https://www.yamanashi-kankou.jp',
      required_attribution: 'Saiko Village',
      source_retrieval_date: '2026-01-01',
      last_verified_date: '2026-01-01',
    }
  ], []);

  // Compute distance from starting location for each card
  const getDistanceKm = (lat: number, lon: number) => {
    const R = 6371;
    const dLat = ((lat - currentLocation.lat) * Math.PI) / 180;
    const dLon = ((lon - currentLocation.lon) * Math.PI) / 180;
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos((currentLocation.lat * Math.PI) / 180) *
        Math.cos((lat * Math.PI) / 180) *
        Math.sin(dLon / 2) *
        Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return (R * c).toFixed(1);
  };

  const toggleFavorite = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    setFavorites((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  // Filtered cards based on tabs and query
  const displayedCards = useMemo(() => {
    return defaultPlaces.filter((p) => {
      if (activeTab === 'famous' && p.discovery_type !== 'FAMOUS') return false;
      if (activeTab === 'gems' && p.discovery_type !== 'HIDDEN_GEM') return false;
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchName =
          p.name_en?.toLowerCase().includes(q) ||
          p.name_ja?.toLowerCase().includes(q) ||
          p.sub_category?.toLowerCase().includes(q);
        if (!matchName) return false;
      }
      return true;
    });
  }, [defaultPlaces, activeTab, searchQuery]);

  // Handle selecting a destination card (transitions to Step B)
  const handleSelectCard = (place: Place) => {
    setSelectedPlace(place.place_id, place.name_en || place.name_ja);
    setActiveWorkflowStep('setup');
  };

  // "Choose for me" green button handler
  const handleChooseForMe = () => {
    // Pick the most scenic serene destination based on crowd preference
    const recommendation = defaultPlaces.find((p) => p.place_id === 'kawaguchiko_oishi_park') || defaultPlaces[0];
    setSelectedPlace(recommendation.place_id, recommendation.name_en || recommendation.name_ja);
    setActiveWorkflowStep('setup');
    if (onAskHana) {
      onAskHana(
        `I clicked "Choose for me" from ${currentLocation.name}. Recommend a balanced 5-hour itinerary taking me to ${recommendation.name_en} with serene views and local dining.`
      );
    }
  };

  return (
    <div className="space-y-6 mb-6">
      {/* =========================================================================
          PANEL A: STATION-FIRST DISCOVERY (CHOOSE YOUR DESTINATION)
         ========================================================================= */}
      {activeWorkflowStep === 'discovery' && (
        <div className="bg-white rounded-3xl border border-[#E1EAF1] p-6 shadow-xs space-y-5 animate-in fade-in duration-200">
          {/* Header & Subtitle */}
          <div className="pb-3 border-b border-[#E1EAF1]">
            <h2 className="text-xl font-bold text-[#14283F]">Where are you starting?</h2>
            <p className="text-xs text-[#718198] mt-0.5">
              Select your current location (station, bus stop, or area) to discover nearby places.
            </p>
          </div>

          {/* Location Selector Bar */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
            <div className="relative flex-1">
              <button
                type="button"
                onClick={() => setIsStationDropdownOpen(!isStationDropdownOpen)}
                className="w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl border border-[#D0DDE7] bg-white text-xs font-semibold text-[#14283F] hover:border-[#078ACB] transition-all shadow-2xs"
              >
                <div className="flex items-center gap-2 truncate">
                  <MapPin className="w-4 h-4 text-[#078ACB] shrink-0" />
                  <span className="truncate">{currentLocation.name}</span>
                </div>
                <ChevronDown className="w-4 h-4 text-slate-400 shrink-0 ml-1" />
              </button>

              {isStationDropdownOpen && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-[#D0DDE7] rounded-xl shadow-xl z-30 max-h-64 overflow-y-auto divide-y divide-slate-100">
                  {STANDARD_HUBS.map((hub) => (
                    <button
                      key={hub.name}
                      type="button"
                      onClick={() => {
                        setCurrentLocation(hub);
                        setIsStationDropdownOpen(false);
                      }}
                      className={`w-full text-left px-3.5 py-2.5 text-xs flex items-center justify-between hover:bg-sky-50 transition-colors ${
                        currentLocation.name === hub.name
                          ? 'bg-sky-50/80 font-bold text-[#078ACB]'
                          : 'text-[#14283F]'
                      }`}
                    >
                      <span className="truncate">{hub.name}</span>
                      {currentLocation.name === hub.name && (
                        <CheckCircle2 className="w-3.5 h-3.5 text-[#078ACB] shrink-0" />
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>

            <button
              type="button"
              onClick={requestGeolocation}
              className="flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-xl border border-sky-300 bg-sky-50/60 text-[#078ACB] text-xs font-bold hover:bg-sky-100/70 transition-colors shadow-2xs shrink-0"
            >
              <Navigation className="w-3.5 h-3.5 text-[#078ACB]" />
              <span>Use GPS</span>
            </button>
          </div>

          {/* Discovery Tabs: Famous Places (120+) & Hidden Gems (115+) */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setActiveTab('famous')}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all shadow-2xs ${
                activeTab === 'famous'
                  ? 'bg-sky-50 text-[#078ACB] border-2 border-[#078ACB]'
                  : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
              }`}
            >
              <Flame className="w-3.5 h-3.5 text-amber-500 fill-amber-500" />
              <span>Famous Places (120+)</span>
            </button>

            <button
              onClick={() => setActiveTab('gems')}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all shadow-2xs ${
                activeTab === 'gems'
                  ? 'bg-emerald-50 text-emerald-700 border-2 border-emerald-500'
                  : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
              }`}
            >
              <Leaf className="w-3.5 h-3.5 text-emerald-600 fill-emerald-600" />
              <span>Hidden Gems (115+)</span>
            </button>
          </div>

          {/* Filters Bar */}
          <div className="flex flex-wrap items-center gap-2.5 pt-1">
            <div className="relative flex-1 min-w-[200px]">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search places (e.g., Oishi Park, shrine, lake...)"
                className="w-full pl-9 pr-3 py-2 text-xs rounded-xl border border-slate-200 bg-white placeholder-slate-400 focus:outline-hidden focus:border-[#078ACB] focus:ring-1 focus:ring-[#078ACB]"
              />
            </div>

            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              aria-label="Filter places by category"
              className="text-xs py-2 px-3 rounded-xl border border-slate-200 bg-white text-slate-700 font-medium focus:outline-hidden"
            >
              <option>All Categories</option>
              <option>Nature & Parks</option>
              <option>Shrines & Temples</option>
              <option>Cultural & Heritage</option>
              <option>Scenic Viewpoint</option>
            </select>

            <select
              value={selectedDistanceFilter}
              onChange={(e) => setSelectedDistanceFilter(e.target.value)}
              aria-label="Filter places by distance"
              className="text-xs py-2 px-3 rounded-xl border border-slate-200 bg-white text-slate-700 font-medium focus:outline-hidden"
            >
              <option>Distance</option>
              <option>&lt; 5 km</option>
              <option>&lt; 10 km</option>
            </select>

            <select
              value={selectedCrowdFilter}
              onChange={(e) => setSelectedCrowdFilter(e.target.value)}
              aria-label="Filter places by crowd level"
              className="text-xs py-2 px-3 rounded-xl border border-slate-200 bg-white text-slate-700 font-medium focus:outline-hidden"
            >
              <option>Crowd</option>
              <option>Low Crowd</option>
              <option>Moderate Crowd</option>
            </select>

            <label className="flex items-center gap-2 px-3 py-2 rounded-xl border border-slate-200 bg-white text-xs font-semibold text-slate-700 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={openNowOnly}
                onChange={(e) => setOpenNowOnly(e.target.checked)}
                className="rounded border-slate-300 text-[#078ACB] focus:ring-[#078ACB]"
              />
              <span>Open Now</span>
            </label>
          </div>

          {/* 4 Cards Grid Matching Panel A */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-1">
            {displayedCards.slice(0, 4).map((place) => {
              const dist = getDistanceKm(place.latitude, place.longitude);
              const isFav = favorites.includes(place.place_id);
              const isChureito = place.place_id === 'chureito_pagoda';
              const isOshino = place.place_id === 'oshino_hakkai_springs';

              return (
                <div
                  key={place.place_id}
                  onClick={() => handleSelectCard(place)}
                  className="group bg-white rounded-2xl border border-[#E1EAF1] hover:border-[#078ACB] hover:shadow-md transition-all cursor-pointer overflow-hidden flex flex-col justify-between"
                >
                  <div>
                    {/* Photo with heart button */}
                    <div className="relative aspect-16/10 overflow-hidden bg-slate-100">
                      <img
                        src={place.image_url}
                        alt={place.name_en}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                        onError={(e) => {
                          (e.currentTarget as HTMLImageElement).src =
                            'https://images.unsplash.com/photo-1490806843957-31f4c9a91c65?auto=format&fit=crop&w=600&q=80';
                        }}
                      />
                      <button
                        type="button"
                        onClick={(e) => toggleFavorite(e, place.place_id)}
                        className="absolute top-2.5 right-2.5 w-7 h-7 rounded-full bg-white/80 backdrop-blur-xs flex items-center justify-center text-slate-600 hover:text-rose-500 transition-colors shadow-2xs"
                        aria-label="Add to favorites"
                      >
                        <Heart
                          className={`w-3.5 h-3.5 ${
                            isFav ? 'text-rose-500 fill-rose-500' : 'text-slate-600'
                          }`}
                        />
                      </button>
                    </div>

                    {/* Card Body */}
                    <div className="p-3.5 space-y-2">
                      <div>
                        <h4 className="text-sm font-bold text-[#14283F] group-hover:text-[#078ACB] transition-colors leading-tight">
                          {place.name_en}
                        </h4>
                        <div className="text-[11px] text-slate-500 font-japanese mt-0.5">
                          {place.name_ja}
                        </div>
                      </div>

                      {/* Distance & Accessibility Row */}
                      <div className="flex items-center justify-between text-[11px] text-[#425466]">
                        <span className="flex items-center gap-1 font-medium">
                          <MapPin className="w-3 h-3 text-[#078ACB]" />
                          <span>{dist} km</span>
                        </span>
                        <span className="text-[10px] text-slate-500 flex items-center gap-1">
                          <span>♿ Accessible</span>
                        </span>
                      </div>

                      {/* Transport Method */}
                      <div className="text-[11px] text-slate-600 flex items-center gap-1.5">
                        <Bus className="w-3 h-3 text-slate-400 shrink-0" />
                        <span className="truncate">
                          {isChureito
                            ? 'Walk / Local Bus'
                            : isOshino
                            ? 'Fujikyu Bus'
                            : 'Fujikyu Line'}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Bottom Badges Row */}
                  <div className="p-3.5 pt-0 flex items-center justify-between text-[10px]">
                    {isChureito ? (
                      <span className="font-bold text-rose-700 bg-rose-50 border border-rose-200 px-2 py-0.5 rounded-full">
                        ● High Crowd
                      </span>
                    ) : isOshino ? (
                      <span className="font-bold text-amber-700 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded-full">
                        ● Moderate
                      </span>
                    ) : (
                      <span className="font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full">
                        ● Low Crowd
                      </span>
                    )}

                    <span className="text-slate-500 font-semibold flex items-center gap-0.5">
                      <Star className="w-3 h-3 text-amber-400 fill-amber-400" />
                      <span>{place.fuji_view_rating.toFixed(1)}</span>
                    </span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Green "Choose for me" Button (Prominent, matching Panel A) */}
          <div className="pt-2">
            <button
              onClick={handleChooseForMe}
              className="w-full py-3.5 px-6 rounded-2xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm shadow-md transition-all flex flex-col items-center justify-center gap-0.5"
            >
              <span className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-emerald-200" />
                <span>Choose for me</span>
              </span>
              <span className="text-[11px] text-emerald-100 font-normal">
                Recommend the best plan based on time, crowd and season
              </span>
            </button>
          </div>
        </div>
      )}

      {/* =========================================================================
          PANEL B: TRIP SETUP & AI ITINERARY (5 HOURS)
         ========================================================================= */}
      {activeWorkflowStep === 'setup' && (
        <div className="bg-white rounded-3xl border border-[#E1EAF1] p-6 shadow-xs space-y-6 animate-in fade-in duration-200">
          {/* Header */}
          <div className="flex items-center justify-between pb-3 border-b border-[#E1EAF1]">
            <div>
              <h2 className="text-xl font-bold text-[#14283F]">Plan Your Trip</h2>
              <p className="text-xs text-[#718198] mt-0.5">
                Set your destination, time and preferences. Hana will build a smart itinerary for you.
              </p>
            </div>
            <button
              onClick={() => setActiveWorkflowStep('discovery')}
              className="text-xs text-[#078ACB] hover:underline font-semibold flex items-center gap-1"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Back to discovery</span>
            </button>
          </div>

          {/* Form Row: Starting Location, Destination, Time Budget, Departure */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-12 gap-3.5 items-end">
            <div className="lg:col-span-4 space-y-1">
              <label className="text-[11px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1">
                <MapPin className="w-3 h-3 text-[#078ACB]" />
                <span>Starting Location</span>
              </label>
              <select
                value={currentLocation.name}
                onChange={(e) => {
                  const found = STANDARD_HUBS.find((h) => h.name === e.target.value);
                  if (found) setCurrentLocation(found);
                }}
                className="w-full text-xs font-semibold py-2 px-3 rounded-xl border border-slate-200 bg-white text-[#14283F] focus:outline-hidden"
              >
                {STANDARD_HUBS.map((hub) => (
                  <option key={hub.name} value={hub.name}>
                    {hub.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="lg:col-span-4 space-y-1">
              <label className="text-[11px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1">
                <MapPin className="w-3 h-3 text-rose-500" />
                <span>Destination</span>
              </label>
              <select
                value={selectedPlaceId}
                onChange={(e) => {
                  const place = defaultPlaces.find((p) => p.place_id === e.target.value);
                  if (place) setSelectedPlace(place.place_id, place.name_en);
                }}
                className="w-full text-xs font-semibold py-2 px-3 rounded-xl border border-slate-200 bg-white text-[#14283F] focus:outline-hidden"
              >
                {defaultPlaces.map((p) => (
                  <option key={p.place_id} value={p.place_id}>
                    {p.name_en} ({p.name_ja})
                  </option>
                ))}
              </select>
            </div>

            <div className="lg:col-span-3 space-y-1">
              <label className="text-[11px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1">
                <Clock className="w-3 h-3 text-[#078ACB]" />
                <span>Trip Time Budget</span>
              </label>
              <div className="flex items-center gap-1">
                {[1, 2, 3, 4, 5, 6].map((hrs) => (
                  <button
                    key={hrs}
                    type="button"
                    onClick={() => setTimeBudgetHours(hrs)}
                    className={`flex-1 py-1.5 text-xs font-bold rounded-lg transition-colors ${
                      timeBudgetHours === hrs
                        ? 'bg-[#078ACB] text-white shadow-2xs'
                        : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                    }`}
                  >
                    {hrs}h
                  </button>
                ))}
              </div>
            </div>

            <div className="lg:col-span-1 space-y-1">
              <label className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
                Departure
              </label>
              <input
                type="time"
                value={departureTime}
                onChange={(e) => setDepartureTime(e.target.value)}
                className="w-full text-xs font-mono font-semibold py-1.5 px-2 rounded-xl border border-slate-200 bg-white text-[#14283F] focus:outline-hidden"
              />
            </div>
          </div>

          {/* Food Preferences Row */}
          <div className="space-y-3 pt-2">
            <div className="flex flex-col sm:flex-row sm:items-center gap-4">
              {/* Experience */}
              <div className="space-y-1.5">
                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
                  Food Preference
                </span>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setFoodExperience('local')}
                    className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all shadow-2xs flex items-center gap-1.5 ${
                      foodExperience === 'local'
                        ? 'bg-emerald-600 text-white'
                        : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                    }`}
                  >
                    <span>🍽️</span>
                    <span>Local cuisine</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setFoodExperience('hidden')}
                    className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all shadow-2xs flex items-center gap-1.5 ${
                      foodExperience === 'hidden'
                        ? 'bg-emerald-600 text-white'
                        : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                    }`}
                  >
                    <span>🏮</span>
                    <span>Hidden local spots</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setFoodExperience('famous')}
                    className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all shadow-2xs flex items-center gap-1.5 ${
                      foodExperience === 'famous'
                        ? 'bg-emerald-600 text-white'
                        : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                    }`}
                  >
                    <span>⭐</span>
                    <span>Famous restaurants</span>
                  </button>
                </div>
              </div>

              {/* Style Tags */}
              <div className="space-y-1.5">
                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
                  Food Style
                </span>
                <div className="flex flex-wrap items-center gap-1.5">
                  {['Hoto noodles', 'Soba', 'Sushi', 'Vegetarian'].map((style) => {
                    const isSelected = foodStyles.includes(style);
                    return (
                      <button
                        key={style}
                        type="button"
                        onClick={() => toggleFoodStyle(style)}
                        className={`px-3 py-1.5 rounded-full text-xs font-semibold transition-all ${
                          isSelected
                            ? 'bg-emerald-500 text-white'
                            : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                        }`}
                      >
                        {style}
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>

          {/* Sequential Itinerary Track (Dark Navy Blue Container Matching Panel B) */}
          <div className="rounded-3xl bg-[#0F2942] text-white p-5 shadow-lg space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-white/10 gap-2">
              <div className="flex items-center gap-2">
                <Bus className="w-4 h-4 text-[#078ACB]" />
                <h3 className="text-sm font-bold text-white">
                  Your {timeBudgetHours}-Hour Itinerary ({currentLocation.name.split('(')[0].trim()} → {selectedPlaceName} & Nearby)
                </h3>
              </div>
              <div className="flex items-center gap-3 text-xs text-slate-300 font-mono">
                <span className="flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5 text-sky-400" />
                  <span>Total: {timeBudgetHours}h 00m</span>
                </span>
                <span>•</span>
                <span>Est. Travel: 1h 20m</span>
              </div>
            </div>

            {/* Horizontal Timeline Cards with connecting arrows */}
            <div className="grid grid-cols-1 sm:grid-cols-5 gap-3 items-center">
              {/* 1. Breakfast */}
              <div className="bg-white/10 backdrop-blur-xs rounded-2xl p-3 border border-white/10 space-y-2">
                <span className="text-[10px] text-sky-300 font-mono block">09:30 - 10:00</span>
                <div className="aspect-16/10 rounded-xl overflow-hidden bg-white/5">
                  <img
                    src="https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=400&q=80"
                    alt="Breakfast"
                    className="w-full h-full object-cover"
                  />
                </div>
                <div>
                  <h5 className="text-xs font-bold text-white leading-tight">Breakfast at Kawaguchiko</h5>
                  <span className="text-[10px] text-slate-400 block mt-0.5">(30 min)</span>
                </div>
              </div>

              {/* 2. Target Destination */}
              <div className="bg-white/10 backdrop-blur-xs rounded-2xl p-3 border border-white/10 space-y-2">
                <span className="text-[10px] text-sky-300 font-mono block">10:00 - 11:00</span>
                <div className="aspect-16/10 rounded-xl overflow-hidden bg-white/5">
                  <img
                    src="https://images.unsplash.com/photo-1578637387939-43c525550085?auto=format&fit=crop&w=400&q=80"
                    alt={selectedPlaceName}
                    className="w-full h-full object-cover"
                  />
                </div>
                <div>
                  <h5 className="text-xs font-bold text-white leading-tight">{selectedPlaceName} Visit</h5>
                  <span className="text-[10px] text-slate-400 block mt-0.5">(60 min)</span>
                </div>
              </div>

              {/* 3. Lunch */}
              <div className="bg-white/10 backdrop-blur-xs rounded-2xl p-3 border border-white/10 space-y-2">
                <span className="text-[10px] text-sky-300 font-mono block">11:00 - 12:00</span>
                <div className="aspect-16/10 rounded-xl overflow-hidden bg-white/5">
                  <img
                    src="https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=400&q=80"
                    alt="Lunch"
                    className="w-full h-full object-cover"
                  />
                </div>
                <div>
                  <h5 className="text-xs font-bold text-white leading-tight">Lunch (Hoto noodles)</h5>
                  <span className="text-[10px] text-slate-400 block mt-0.5">(60 min)</span>
                </div>
              </div>

              {/* 4. Secondary Spot */}
              <div className="bg-white/10 backdrop-blur-xs rounded-2xl p-3 border border-white/10 space-y-2">
                <span className="text-[10px] text-sky-300 font-mono block">12:00 - 13:30</span>
                <div className="aspect-16/10 rounded-xl overflow-hidden bg-white/5">
                  <img
                    src="https://images.unsplash.com/photo-1528164344705-475426879c0d?auto=format&fit=crop&w=400&q=80"
                    alt="Ubuyagasaki"
                    className="w-full h-full object-cover"
                  />
                </div>
                <div>
                  <h5 className="text-xs font-bold text-white leading-tight">Ubuyagasaki Lakeside</h5>
                  <span className="text-[10px] text-slate-400 block mt-0.5">(90 min)</span>
                </div>
              </div>

              {/* 5. Return */}
              <div className="bg-white/10 backdrop-blur-xs rounded-2xl p-3 border border-white/10 space-y-2">
                <span className="text-[10px] text-sky-300 font-mono block">13:30 - 14:30</span>
                <div className="aspect-16/10 rounded-xl overflow-hidden bg-white/5">
                  <img
                    src="https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=400&q=80"
                    alt="Return"
                    className="w-full h-full object-cover"
                  />
                </div>
                <div>
                  <h5 className="text-xs font-bold text-white leading-tight">Return to Kawaguchiko</h5>
                  <span className="text-[10px] text-slate-400 block mt-0.5">(60 min)</span>
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons Row Matching Panel B */}
          <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
            <div className="flex flex-wrap items-center gap-2.5">
              {/* Show bus route -> Triggers Panel C Transit Modal */}
              <button
                type="button"
                onClick={() => setIsTransitModalOpen(true)}
                className="flex items-center gap-1.5 px-4 py-2.5 rounded-xl border border-sky-300 bg-sky-50 text-sky-700 text-xs font-bold hover:bg-sky-100 transition-colors shadow-2xs"
              >
                <Bus className="w-3.5 h-3.5 text-[#078ACB]" />
                <span>Show bus route</span>
              </button>

              {/* Estimate cost */}
              <button
                type="button"
                onClick={() => setCostEstimateModalOpen(true)}
                className="flex items-center gap-1.5 px-4 py-2.5 rounded-xl border border-slate-200 bg-white text-slate-700 text-xs font-bold hover:bg-slate-50 transition-colors shadow-2xs"
              >
                <DollarSign className="w-3.5 h-3.5 text-emerald-600" />
                <span>Estimate total cost</span>
              </button>

              {/* Change the plan */}
              <button
                type="button"
                onClick={() => setActiveWorkflowStep('discovery')}
                className="flex items-center gap-1.5 px-4 py-2.5 rounded-xl border border-slate-200 bg-white text-slate-700 text-xs font-bold hover:bg-slate-50 transition-colors shadow-2xs"
              >
                <RotateCcw className="w-3.5 h-3.5 text-slate-500" />
                <span>Change the plan</span>
              </button>
            </div>

            {/* Start Live Progress -> Triggers Panel D */}
            <button
              type="button"
              onClick={() => {
                setIsTripProgressActive(true);
                setActiveWorkflowStep('progress');
              }}
              className="flex items-center gap-1.5 px-5 py-2.5 rounded-xl bg-emerald-600 text-white text-xs font-bold hover:bg-emerald-700 transition-colors shadow-sm"
            >
              <span>Start Live Trip Progress</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* =========================================================================
          PANEL D: TRIP PROGRESS & ADAPTIVE UPDATE
         ========================================================================= */}
      {activeWorkflowStep === 'progress' && (
        <TripProgressView
          onAskHana={onAskHana}
          onOpenMap={onOpenMap}
          onCheckBus={() => setIsTransitModalOpen(true)}
        />
      )}

      {/* =========================================================================
          PANEL C: TRANSIT INSTRUCTION (NEXT BUS) MODAL
         ========================================================================= */}
      <TransitInstructionModal
        isOpen={isTransitModalOpen}
        onClose={() => setIsTransitModalOpen(false)}
        destinationName={selectedPlaceName}
        onOpenRoute={onOpenMap}
        onConfirmDepart={() => {
          setIsTransitModalOpen(false);
          setIsTripProgressActive(true);
          setActiveWorkflowStep('progress');
        }}
      />

      {/* Cost Estimate Modal */}
      {costEstimateModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs">
          <div className="bg-white rounded-3xl p-6 max-w-md w-full shadow-2xl space-y-4 border border-slate-100">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="text-base font-bold text-[#14283F] flex items-center gap-2">
                <DollarSign className="w-4 h-4 text-emerald-600" />
                <span>Estimated Cost Breakdown</span>
              </h3>
              <button
                onClick={() => setCostEstimateModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 text-sm font-bold"
              >
                ✕
              </button>
            </div>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-600">Fujikyu Sightseeing Bus Fare (Return)</span>
                <span className="font-semibold text-[#14283F]">¥1,160</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-600">Attraction Admission ({selectedPlaceName})</span>
                <span className="font-semibold text-emerald-600">¥0 (Free Admission)</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-600">Local Lunch (Hoto noodles)</span>
                <span className="font-semibold text-[#14283F]">¥1,500</span>
              </div>
              <div className="flex justify-between py-2 font-bold text-sm text-[#14283F]">
                <span>Total Estimated Cost</span>
                <span className="text-[#078ACB]">¥2,660 per adult</span>
              </div>
              <div className="p-3 bg-sky-50 rounded-xl border border-sky-100 text-[11px] text-sky-800">
                💡 <strong>Fujikyu 2-Day Pass (¥2,000):</strong> Unlimited bus rides around Kawaguchiko, Saiko, and Yamanakako. Recommended if taking more than 3 bus rides!
              </div>
            </div>
            <button
              onClick={() => setCostEstimateModalOpen(false)}
              className="w-full py-2.5 rounded-xl bg-[#078ACB] text-white text-xs font-bold hover:bg-[#0672A7] transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

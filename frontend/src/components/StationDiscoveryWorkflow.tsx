import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useTrip, STANDARD_HUBS } from '../context/TripContext';
import { useI18n } from '../i18n/I18nContext';
import { TravelMode, DiscoveryPlaceItem, DiscoveryRecommendResponse, TransitRouteResponse, TripPlanResponse } from '../types';
import { apiUrl } from '../config';
import { TransitInstructionModal } from './TransitInstructionModal';
import { 
  MapPin, 
  Navigation, 
  Search, 
  Sparkles, 
  Clock, 
  Heart, 
  Bus, 
  ChevronDown, 
  ChevronLeft,
  ChevronRight,
  CheckCircle2, 
  ArrowRight,
  Flame,
  Leaf,
  RotateCcw,
  Star,
  Play,
  Pause,
  Volume2,
  VolumeX,
  AlertTriangle,
  Bike,
  Car,
  Train,
  Footprints,
  Shuffle,
  Calendar,
  Layers,
  Map as MapIcon,
  Check
} from 'lucide-react';

interface StationDiscoveryWorkflowProps {
  onAskHana?: (prompt: string) => void;
  onOpenMap?: () => void;
}

const TRAVEL_MODES_CONFIG: Array<{
  id: TravelMode;
  label: string;
  icon: any;
  defaultMaxKm: number;
  fareBasis: string;
}> = [
  { id: 'walk', label: 'Walking', icon: Footprints, defaultMaxKm: 5, fareBasis: 'Free' },
  { id: 'bike', label: 'Rent a Bicycle', icon: Bike, defaultMaxKm: 15, fareBasis: 'Rental ~¥1,500/day' },
  { id: 'fujikyu_bus', label: 'Fujikyu Bus', icon: Bus, defaultMaxKm: 30, fareBasis: '¥200 - ¥1,200' },
  { id: 'bus', label: 'Other Buses', icon: Bus, defaultMaxKm: 30, fareBasis: 'Standard fare' },
  { id: 'train', label: 'Train', icon: Train, defaultMaxKm: 45, fareBasis: 'Fujikyuko Line' },
  { id: 'taxi', label: 'Taxi', icon: Car, defaultMaxKm: 35, fareBasis: 'Metered' },
  { id: 'mixed', label: 'Mixed Transport', icon: Shuffle, defaultMaxKm: 30, fareBasis: 'Bus + Rail + Walk' },
  { id: 'car', label: 'Private Vehicle', icon: Car, defaultMaxKm: 50, fareBasis: 'Road' },
];

export const StationDiscoveryWorkflow: React.FC<StationDiscoveryWorkflowProps> = ({
  onAskHana,
  onOpenMap,
}) => {
  const { t } = useI18n();
  const {
    currentLocation,
    setCurrentLocation,
    selectedPlaceId,
    selectedPlaceName,
    setSelectedPlace,
    travelMode,
    setTravelMode,
    timeBudgetHours,
    setTimeBudgetHours,
    requestGeolocation,
    activeWorkflowStep,
    setActiveWorkflowStep,
    isTransitModalOpen,
    setIsTransitModalOpen,
    setIsTripProgressActive,
    fetchTransitRoute,
    fetchTripPlan,
    recalibrateTrip,
    isSoundEnabled,
    toggleSoundEnabled,
    playTimerChime,
  } = useTrip();

  // Screen A state
  const [activeTab, setActiveTab] = useState<'all' | 'famous' | 'gems'>('famous');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All Categories');
  const [selectedDistanceFilter, setSelectedDistanceFilter] = useState('All');
  const [selectedCrowdFilter, setSelectedCrowdFilter] = useState('All');
  const [openNowOnly, setOpenNowOnly] = useState(false);
  const [isStationDropdownOpen, setIsStationDropdownOpen] = useState(false);
  const [favorites, setFavorites] = useState<string[]>([]);
  const [showStationBanner, setShowStationBanner] = useState(false);
  const [lastStationName, setLastStationName] = useState(currentLocation.name);

  // Pagination state (Screen A)
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(12);

  // Screen B state
  const [selectedDistanceKm, setSelectedDistanceKm] = useState(20);
  const [selectedBudgetTier, setSelectedBudgetTier] = useState('≤ ¥3,000');
  const [selectedTravelStyle, setSelectedTravelStyle] = useState('Scenic & Relaxed');
  const [recommendedPlaces, setRecommendedPlaces] = useState<DiscoveryPlaceItem[]>([]);
  const [cataloguePlaces, setCataloguePlaces] = useState<DiscoveryPlaceItem[]>([]);
  const [isLoadingRecs, setIsLoadingRecs] = useState(false);
  const [isLoadingCatalogue, setIsLoadingCatalogue] = useState(false);

  // Screen C state (Transit Route)
  const [, setActiveRoute] = useState<TransitRouteResponse | null>(null);
  const [isLoadingRoute, setIsLoadingRoute] = useState(false);

  // Screen D state (Itinerary & Live Timers)
  const [, setActivePlan] = useState<TripPlanResponse | null>(null);
  const [isTimerRunning, setIsTimerRunning] = useState(true);
  const [timerSecondsRemaining, setTimerSecondsRemaining] = useState<number>(2292); // 00:38:12 remaining
  const [timerSecondsElapsed, setTimerSecondsElapsed] = useState<number>(4908); // 01:21:48 elapsed
  const [totalTimerSeconds] = useState<number>(18000); // 5 hours = 18000 sec
  const [isOverdueBannerVisible, setIsOverdueBannerVisible] = useState(false);
  const [isEarlyRecalibrationModalOpen, setIsEarlyRecalibrationModalOpen] = useState(false);
  const [recalibrationMinutes] = useState(40);
  const [activeStepIndex] = useState(2); // 0=Breakfast, 1=Travel, 2=Oishi Park (Main)

  useEffect(() => {
    if (!isTimerRunning) return;
    const interval = setInterval(() => {
      setTimerSecondsElapsed((prev) => Math.min(prev + 1, totalTimerSeconds));
    }, 1000);
    return () => clearInterval(interval);
  }, [isTimerRunning, totalTimerSeconds]);

  // Track map zoom in Panel A
  const [mapZoom, setMapZoom] = useState(1);

  // Detect station change to trigger blue banner
  useEffect(() => {
    if (currentLocation.name !== lastStationName) {
      setLastStationName(currentLocation.name);
      setShowStationBanner(true);
      setCurrentPage(1);
    }
  }, [currentLocation.name, lastStationName]);

  const isFujisan = currentLocation.name.toLowerCase().includes('fujisan') || currentLocation.name.includes('富士山');
  const isModeFiltered = travelMode === 'fujikyu_bus' && selectedCategory === 'Nature & Parks' && (selectedDistanceFilter === '< 20 km' || selectedDistanceKm === 20);
  const famousCount = isFujisan ? 98 : 124;
  const hiddenGemsCount = isFujisan ? 137 : 113;
  const totalCount = isModeFiltered ? 69 : 237;
  const totalPages = isModeFiltered ? 12 : isFujisan ? (activeTab === 'gems' ? 12 : 17) : 20;

  const getLocalizedHubName = (name: string) => {
    if (name.includes('Kawaguchiko')) return t('station.kawaguchiko', name);
    if (name.includes('Fujisan')) return t('station.fujisan', name);
    if (name.includes('5th')) return t('station.fuji5th', name);
    if (name.includes('Shin-Fuji')) return t('station.shinfuji', name);
    if (name.includes('Mishima')) return t('station.mishima', name);
    if (name.includes('Gotemba')) return t('station.gotemba', name);
    if (name.includes('Tokyo')) return t('station.tokyo', name);
    if (name.includes('Shinjuku')) return t('station.shinjuku', name);
    return name;
  };

  // Fetch Catalogue data for Screen A
  const fetchCatalogue = useCallback(async () => {
    setIsLoadingCatalogue(true);
    try {
      const distParam = selectedDistanceFilter === '< 5 km' ? '&max_km=5' : selectedDistanceFilter === '< 10 km' ? '&max_km=10' : '';
      const catParam = selectedCategory !== 'All Categories' ? `&category=${encodeURIComponent(selectedCategory)}` : '';
      const searchParam = searchQuery.trim() ? `&search=${encodeURIComponent(searchQuery.trim())}` : '';
      const res = await fetch(
        apiUrl(
          `/api/v1/discovery/recommend?origin_lat=${currentLocation.lat}&origin_lon=${currentLocation.lon}&origin_name=${encodeURIComponent(
            currentLocation.name
          )}&mode=${travelMode}&view=catalogue&page=${currentPage}&page_size=${pageSize}${distParam}${catParam}${searchParam}`
        )
      );
      if (res.ok) {
        const data: DiscoveryRecommendResponse = await res.json();
        setCataloguePlaces(data.places || (data as any).items || []);
      }
    } catch (err) {
      console.warn('Failed to load catalogue from discovery endpoint:', err);
    } finally {
      setIsLoadingCatalogue(false);
    }
  }, [currentLocation.lat, currentLocation.lon, currentLocation.name, travelMode, currentPage, pageSize, selectedDistanceFilter, selectedCategory, searchQuery]);

  // Fetch Recommended data for Screen B
  const fetchRecommendations = useCallback(async () => {
    setIsLoadingRecs(true);
    try {
      const res = await fetch(
        apiUrl(
          `/api/v1/discovery/recommend?start_hub=${encodeURIComponent(
            currentLocation.name
          )}&mode=${travelMode}&view=recommended&max_km=${selectedDistanceKm}&page=1&page_size=8`
        )
      );
      if (res.ok) {
        const data: DiscoveryRecommendResponse = await res.json();
        setRecommendedPlaces(data.places || []);
      }
    } catch (err) {
      console.warn('Failed to load mode recommendations:', err);
    } finally {
      setIsLoadingRecs(false);
    }
  }, [currentLocation.name, travelMode, selectedDistanceKm]);

  // Load catalogue on change
  useEffect(() => {
    fetchCatalogue();
  }, [fetchCatalogue]);

  // Load recommendations on mode or distance change
  useEffect(() => {
    fetchRecommendations();
  }, [fetchRecommendations]);

  // Timer countdown hook for Panel D
  useEffect(() => {
    if (!isTimerRunning || (activeWorkflowStep !== 'progress' && activeWorkflowStep !== 'itinerary')) return;
    const interval = setInterval(() => {
      setTimerSecondsRemaining((prev) => {
        if (prev <= 1) {
          playTimerChime();
          setIsOverdueBannerVisible(true);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [isTimerRunning, activeWorkflowStep, playTimerChime]);

  // Distance calculator helper
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

  // Fallback cards if backend is offline or for specific panel demonstrations
  const fallbackPlaces: DiscoveryPlaceItem[] = useMemo(() => [
    // Panel A: Kawaguchiko Famous
    {
      place_id: 'kawaguchiko_oishi_park',
      name_en: 'Oishi Park',
      name_ja: '大石公園',
      latitude: 35.5234,
      longitude: 138.7456,
      primary_category: 'Nature & Parks',
      sub_category: 'Flower Park & Lake View',
      image_url: 'https://images.unsplash.com/photo-1578637387939-43c525550085?auto=format&fit=crop&w=600&q=80',
      distance_km: 3.5,
      travel_time_min: 20,
      fare_yen: 340,
      mode: 'fujikyu_bus',
      route_label: 'Fujikyu Bus',
      crowd_level: 'LOW',
      crowd_score: 28,
      fuji_view_rating: 5.0,
      accessibility_status: 'VERIFIED_ACCESSIBLE',
      discovery_type: 'FAMOUS',
      honest_disclosure: 'SCHEDULED',
      admission_type: 'FREE',
    },
    {
      place_id: 'chureito_pagoda',
      name_en: 'Chureito Pagoda',
      name_ja: '新倉山浅間公園',
      latitude: 35.5013,
      longitude: 138.8014,
      primary_category: 'Shrines & Temples',
      sub_category: 'Panoramic Viewpoint',
      image_url: 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=600&q=80',
      distance_km: 4.7,
      travel_time_min: 25,
      fare_yen: 310,
      mode: 'bus',
      route_label: 'Walk / Local Bus',
      crowd_level: 'HIGH',
      crowd_score: 85,
      fuji_view_rating: 5.0,
      accessibility_status: 'PARTIAL_STEPS',
      discovery_type: 'FAMOUS',
      honest_disclosure: 'SCHEDULED',
      admission_type: 'FREE',
    },
    {
      place_id: 'lake_kawaguchiko_promenade',
      name_en: 'Lake Kawaguchiko',
      name_ja: '河口湖畔プロムナード',
      latitude: 35.5118,
      longitude: 138.7677,
      primary_category: 'Nature & Parks',
      sub_category: 'Lakeside Walking Promenade',
      image_url: 'https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=600&q=80',
      distance_km: 2.1,
      travel_time_min: 15,
      fare_yen: 200,
      mode: 'fujikyu_bus',
      route_label: 'Fujikyu Bus',
      crowd_level: 'MODERATE',
      crowd_score: 52,
      fuji_view_rating: 4.9,
      accessibility_status: 'VERIFIED_ACCESSIBLE',
      discovery_type: 'FAMOUS',
      honest_disclosure: 'SCHEDULED',
      admission_type: 'FREE',
    },
    {
      place_id: 'oshino_hakkai_springs',
      name_en: 'Oshino Hakkai',
      name_ja: '忍野八海',
      latitude: 35.4597,
      longitude: 138.8329,
      primary_category: 'Cultural & Heritage',
      sub_category: 'Natural Spring Ponds',
      image_url: 'https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=600&q=80',
      distance_km: 8.9,
      travel_time_min: 30,
      fare_yen: 560,
      mode: 'fujikyu_bus',
      route_label: 'Fujikyu Bus',
      crowd_level: 'MODERATE',
      crowd_score: 55,
      fuji_view_rating: 4.9,
      accessibility_status: 'VERIFIED_ACCESSIBLE',
      discovery_type: 'FAMOUS',
      honest_disclosure: 'SCHEDULED',
      admission_type: 'FREE',
    },
    {
      place_id: 'ubuyagasaki_promontory',
      name_en: 'Ubuyagasaki',
      name_ja: '産屋ヶ崎',
      latitude: 35.5118,
      longitude: 138.7677,
      primary_category: 'Scenic Viewpoint',
      sub_category: 'Lake & Bridge Reflection',
      image_url: 'https://images.unsplash.com/photo-1528164344705-475426879c0d?auto=format&fit=crop&w=600&q=80',
      distance_km: 2.1,
      travel_time_min: 15,
      fare_yen: 200,
      mode: 'fujikyu_bus',
      route_label: 'Fujikyu Bus',
      crowd_level: 'LOW',
      crowd_score: 22,
      fuji_view_rating: 4.9,
      accessibility_status: 'VERIFIED_ACCESSIBLE',
      discovery_type: 'HIDDEN_GEM',
      honest_disclosure: 'SCHEDULED',
      admission_type: 'FREE',
    },
    {
      place_id: 'nagasaki_cape',
      name_en: 'Nagasaki Cape',
      name_ja: '長崎ヶ崎',
      latitude: 35.5222,
      longitude: 138.7567,
      primary_category: 'Scenic Viewpoint',
      sub_category: 'Lakeside Viewpoint',
      image_url: 'https://images.unsplash.com/photo-1542051841857-5f90071e7989?auto=format&fit=crop&w=600&q=80',
      distance_km: 3.8,
      travel_time_min: 25,
      fare_yen: 340,
      mode: 'fujikyu_bus',
      route_label: 'Fujikyu Bus',
      crowd_level: 'LOW',
      crowd_score: 18,
      fuji_view_rating: 4.9,
      accessibility_status: 'VERIFIED_ACCESSIBLE',
      discovery_type: 'HIDDEN_GEM',
      honest_disclosure: 'SCHEDULED',
      admission_type: 'FREE',
    },

    // Panel B: Fujisan Station Famous Places
    {
      place_id: 'fujisan_kitaguchi_hongu_fuji_sengen_shrine',
      name_en: 'Kitaguchi Hongu Fuji Sengen Shrine',
      name_ja: '北口本宮冨士浅間神社',
      latitude: 35.4745,
      longitude: 138.7946,
      primary_category: 'Shrines & Temples',
      sub_category: 'Historic Sacred Shrine',
      image_url: 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=600&q=80',
      distance_km: 1.2,
      travel_time_min: 15,
      fare_yen: 0,
      mode: 'walk',
      route_label: 'Walk 15 min',
      crowd_level: 'LOW',
      crowd_score: 24,
      fuji_view_rating: 4.9,
      accessibility_status: 'VERIFIED_ACCESSIBLE',
      discovery_type: 'FAMOUS',
      honest_disclosure: 'SCHEDULED',
      admission_type: 'FREE',
    },
    {
      place_id: 'fujisan_fujiyoshida_honcho_street',
      name_en: 'Fujiyoshida Honcho Street',
      name_ja: '本町通り',
      latitude: 35.4882,
      longitude: 138.8043,
      primary_category: 'Cultural & Heritage',
      sub_category: 'Iconic Fuji Street View',
      image_url: 'https://images.unsplash.com/photo-1570125909232-eb263c188f7e?auto=format&fit=crop&w=600&q=80',
      distance_km: 1.4,
      travel_time_min: 18,
      fare_yen: 0,
      mode: 'walk',
      route_label: 'Walk 18 min',
      crowd_level: 'MODERATE',
      crowd_score: 54,
      fuji_view_rating: 4.8,
      accessibility_status: 'VERIFIED_ACCESSIBLE',
      discovery_type: 'FAMOUS',
      honest_disclosure: 'SCHEDULED',
      admission_type: 'FREE',
    },
    {
      place_id: 'fujisan_arakurayama_sengen_park',
      name_en: 'Arakurayama Sengen Park',
      name_ja: '新倉山浅間公園',
      latitude: 35.5013,
      longitude: 138.8014,
      primary_category: 'Shrines & Temples',
      sub_category: 'Iconic Pagoda & Viewpoint',
      image_url: 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=600&q=80',
      distance_km: 2.6,
      travel_time_min: 10,
      fare_yen: 220,
      mode: 'fujikyu_bus',
      route_label: 'Local Bus 10 min',
      crowd_level: 'MODERATE',
      crowd_score: 58,
      fuji_view_rating: 4.9,
      accessibility_status: 'PARTIAL_STEPS',
      discovery_type: 'FAMOUS',
      honest_disclosure: 'SCHEDULED',
      admission_type: 'FREE',
    },

    // Panel C: Fujisan Station Hidden Gems
    {
      place_id: 'fujisan_arakura_fuji_view_point',
      name_en: 'Arakura Fuji View Point',
      name_ja: '新倉富士見ビューポイント',
      latitude: 35.5042,
      longitude: 138.8048,
      primary_category: 'Scenic Viewpoint',
      sub_category: 'Quiet Upper Ridge Observation Deck',
      image_url: 'https://images.unsplash.com/photo-1542051841857-5f90071e7989?auto=format&fit=crop&w=600&q=80',
      distance_km: 2.1,
      travel_time_min: 25,
      fare_yen: 0,
      mode: 'walk',
      route_label: 'Walk 25 min',
      crowd_level: 'LOW',
      crowd_score: 19,
      fuji_view_rating: 4.7,
      accessibility_status: 'PARTIAL_STEPS',
      discovery_type: 'HIDDEN_GEM',
      honest_disclosure: 'SCHEDULED',
      admission_type: 'FREE',
    },
    {
      place_id: 'fujisan_shiraito_falls_yamanashi',
      name_en: 'Shiraito Falls (Yamanashi)',
      name_ja: '白糸の滝 (山梨)',
      latitude: 35.4385,
      longitude: 138.8315,
      primary_category: 'Nature & Parks',
      sub_category: 'Secluded Forest Waterfall',
      image_url: 'https://images.unsplash.com/photo-1528164344705-475426879c0d?auto=format&fit=crop&w=600&q=80',
      distance_km: 7.8,
      travel_time_min: 20,
      fare_yen: 440,
      mode: 'fujikyu_bus',
      route_label: 'Bus 20 min',
      crowd_level: 'LOW',
      crowd_score: 21,
      fuji_view_rating: 4.9,
      accessibility_status: 'VERIFIED_ACCESSIBLE',
      discovery_type: 'HIDDEN_GEM',
      honest_disclosure: 'SCHEDULED',
      admission_type: 'FREE',
    },
    {
      place_id: 'fujisan_takizawa_forest_trail',
      name_en: 'Takizawa Forest Trail Trailhead',
      name_ja: '滝沢の森遊歩道',
      latitude: 35.4412,
      longitude: 138.7612,
      primary_category: 'Nature & Parks',
      sub_category: 'Subalpine Forest Trailhead',
      image_url: 'https://images.unsplash.com/photo-1570125909232-eb263c188f7e?auto=format&fit=crop&w=600&q=80',
      distance_km: 6.4,
      travel_time_min: 18,
      fare_yen: 380,
      mode: 'fujikyu_bus',
      route_label: 'Bus 18 min',
      crowd_level: 'LOW',
      crowd_score: 16,
      fuji_view_rating: 4.8,
      accessibility_status: 'VERIFIED_ACCESSIBLE',
      discovery_type: 'HIDDEN_GEM',
      honest_disclosure: 'SCHEDULED',
      admission_type: 'FREE',
    },

    // Panel D: Bus Mode & Nature/Parks (< 20 km)
    {
      place_id: 'lake_saiko_iyashi_no_sato',
      name_en: 'Saiko Iyashi-no-Sato',
      name_ja: '西湖いやしの里根場',
      latitude: 35.5085,
      longitude: 138.6653,
      primary_category: 'Nature & Parks',
      sub_category: 'Traditional Village & Park',
      image_url: 'https://images.unsplash.com/photo-1570125909232-eb263c188f7e?auto=format&fit=crop&w=600&q=80',
      distance_km: 12.4,
      travel_time_min: 25,
      fare_yen: 710,
      mode: 'fujikyu_bus',
      route_label: 'Fujikyu Bus 25 min',
      crowd_level: 'MODERATE',
      crowd_score: 48,
      fuji_view_rating: 4.8,
      accessibility_status: 'VERIFIED_ACCESSIBLE',
      discovery_type: 'HIDDEN_GEM',
      honest_disclosure: 'SCHEDULED',
      admission_type: 'PAID',
    },
    {
      place_id: 'narusawa_ice_cave',
      name_en: 'Narusawa Ice Cave',
      name_ja: '鳴沢氷穴',
      latitude: 35.4751,
      longitude: 138.6538,
      primary_category: 'Nature & Parks',
      sub_category: 'Volcanic Lava Cave',
      image_url: 'https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=600&q=80',
      distance_km: 14.8,
      travel_time_min: 35,
      fare_yen: 780,
      mode: 'fujikyu_bus',
      route_label: 'Fujikyu Bus 35 min',
      crowd_level: 'LOW',
      crowd_score: 30,
      fuji_view_rating: 4.7,
      accessibility_status: 'PARTIAL_STEPS',
      discovery_type: 'HIDDEN_GEM',
      honest_disclosure: 'SCHEDULED',
      admission_type: 'PAID',
    },
    {
      place_id: 'aokigahara_forest',
      name_en: 'Aokigahara Forest',
      name_ja: '青木ヶ原樹海',
      latitude: 35.4735,
      longitude: 138.6432,
      primary_category: 'Nature & Parks',
      sub_category: 'Ancient Lava Bed Forest Trail',
      image_url: 'https://images.unsplash.com/photo-1542051841857-5f90071e7989?auto=format&fit=crop&w=600&q=80',
      distance_km: 17.1,
      travel_time_min: 38,
      fare_yen: 850,
      mode: 'fujikyu_bus',
      route_label: 'Fujikyu Bus 38 min',
      crowd_level: 'LOW',
      crowd_score: 22,
      fuji_view_rating: 4.6,
      accessibility_status: 'VERIFIED_ACCESSIBLE',
      discovery_type: 'HIDDEN_GEM',
      honest_disclosure: 'SCHEDULED',
      admission_type: 'FREE',
    }
  ], []);

  const isMetroSearch = searchQuery.toLowerCase().includes('metro') || searchQuery.toLowerCase().includes('subway');

  // Filtered catalogue places for Screen A
  const displayedCataloguePlaces = useMemo(() => {
    let list = cataloguePlaces.length > 0 ? cataloguePlaces : fallbackPlaces;

    if (isFujisan) {
      const fujiPlaces = fallbackPlaces.filter(p => p.place_id.startsWith('fujisan_'));
      const otherPlaces = list.filter(p => !p.place_id.startsWith('fujisan_'));
      list = [...fujiPlaces, ...otherPlaces];
    } else if (isModeFiltered) {
      const natureModePlaces = fallbackPlaces.filter(p => 
        p.place_id.includes('saiko') || p.place_id.includes('narusawa') || p.place_id.includes('aokigahara')
      );
      const otherPlaces = list.filter(p => 
        !p.place_id.includes('saiko') && !p.place_id.includes('narusawa') && !p.place_id.includes('aokigahara')
      );
      list = [...natureModePlaces, ...otherPlaces];
    }

    if (searchQuery.trim() && !isMetroSearch) {
      const q = searchQuery.toLowerCase().trim();
      list = list.filter(p =>
        p.name_en.toLowerCase().includes(q) ||
        p.name_ja.includes(q) ||
        p.primary_category.toLowerCase().includes(q) ||
        (p.sub_category && p.sub_category.toLowerCase().includes(q)) ||
        (p.route_label && p.route_label.toLowerCase().includes(q))
      );
    }

    if (selectedCategory !== 'All Categories') {
      list = list.filter(p => p.primary_category === selectedCategory);
    }

    return list.filter((p) => {
      if (activeTab === 'famous' && p.discovery_type !== 'FAMOUS') return false;
      if (activeTab === 'gems' && p.discovery_type !== 'HIDDEN_GEM') return false;
      return true;
    });
  }, [cataloguePlaces, fallbackPlaces, activeTab, isFujisan, isModeFiltered, searchQuery, isMetroSearch, selectedCategory]);

  // Recommended places for Screen B
  const displayedRecommended = useMemo(() => {
    return recommendedPlaces.length > 0 ? recommendedPlaces : fallbackPlaces.slice(0, 3);
  }, [recommendedPlaces, fallbackPlaces]);

  // Navigate to Route (Screen C)
  const handleSelectDestinationForRoute = async (placeId: string, placeName: string) => {
    setSelectedPlace(placeId, placeName);
    setIsLoadingRoute(true);
    setActiveWorkflowStep('route');
    try {
      const routeData = await fetchTransitRoute(placeId, travelMode);
      if (routeData) setActiveRoute(routeData);
    } catch (e) {
      console.warn('Error fetching transit route:', e);
    } finally {
      setIsLoadingRoute(false);
    }
    if (onAskHana) {
      onAskHana(
        `I selected ${placeName} from ${currentLocation.name} by ${travelMode}. Please show me the best route and scheduled bus times.`
      );
    }
  };

  // Navigate to Day Itinerary (Screen D)
  const handlePlanFullTrip = async () => {
    setActiveWorkflowStep('itinerary');
    setIsTripProgressActive(true);
    try {
      const plan = await fetchTripPlan(selectedPlaceId, timeBudgetHours, travelMode);
      if (plan) setActivePlan(plan);
    } catch (e) {
      console.warn('Error planning trip:', e);
    }
    if (onAskHana) {
      onAskHana(
        `Here is my ${timeBudgetHours}-hour day trip plan to ${selectedPlaceName}. Can you guide my schedule and monitor crowd levels?`
      );
    }
  };

  // Recalibrate handler
  const handleApplyRecalibration = async () => {
    setIsEarlyRecalibrationModalOpen(false);
    try {
      const newPlan = await recalibrateTrip(activeStepIndex, -recalibrationMinutes);
      if (newPlan) setActivePlan(newPlan);
    } catch (e) {
      console.warn('Failed recalibration:', e);
    }
    if (onAskHana) {
      onAskHana(
        `I finished ${selectedPlaceName} ${recalibrationMinutes} minutes early! Recalculate my plan to include a serene hidden gem or café.`
      );
    }
  };

  // Format timer string
  const formatTimeSeconds = (sec: number) => {
    const hrs = Math.floor(sec / 3600);
    const mins = Math.floor((sec % 3600) / 60);
    const s = sec % 60;
    return `${String(hrs).padStart(2, '0')}:${String(mins).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  };

  // Choose for me handler
  const handleChooseForMe = () => {
    const choice = fallbackPlaces[0];
    setSelectedPlace(choice.place_id, choice.name_en);
    setActiveWorkflowStep('modes');
    if (onAskHana) {
      onAskHana(
        `I clicked "Choose for me" at ${currentLocation.name}. Recommend the best plan based on time, crowd, and season.`
      );
    }
  };

  return (
    <div className="space-y-6 mb-6">
      {/* =========================================================================
          STEPPER TABS BAR (Navigating between Screens A, B, C, D)
         ========================================================================= */}
      <div className="bg-white rounded-2xl border border-[#E1EAF1] p-2 shadow-2xs flex items-center justify-between overflow-x-auto gap-2">
        <div className="flex items-center gap-1.5 min-w-max">
          <button
            onClick={() => setActiveWorkflowStep('discovery')}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
              activeWorkflowStep === 'discovery'
                ? 'bg-[#078ACB] text-white shadow-2xs'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <span>① Discovery (237 Places)</span>
          </button>

          <button
            onClick={() => setActiveWorkflowStep('modes')}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
              activeWorkflowStep === 'modes' || activeWorkflowStep === 'setup'
                ? 'bg-[#078ACB] text-white shadow-2xs'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <span>② Travel Modes & Recs</span>
          </button>

          <button
            onClick={() => handleSelectDestinationForRoute(selectedPlaceId, selectedPlaceName)}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
              activeWorkflowStep === 'route'
                ? 'bg-[#078ACB] text-white shadow-2xs'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <span>③ Route & Transit</span>
          </button>

          <button
            onClick={() => setActiveWorkflowStep('itinerary')}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
              activeWorkflowStep === 'itinerary' || activeWorkflowStep === 'progress'
                ? 'bg-[#078ACB] text-white shadow-2xs'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <span>④ Day Plan & Live Progress</span>
          </button>
        </div>

        {/* Global Sound Chime Toggle */}
        <button
          onClick={toggleSoundEnabled}
          title={isSoundEnabled ? 'Audio alerts enabled' : 'Audio alerts muted'}
          className={`px-2.5 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1 border transition-colors ${
            isSoundEnabled
              ? 'bg-emerald-50 text-emerald-800 border-emerald-200 hover:bg-emerald-100'
              : 'bg-slate-50 text-slate-500 border-slate-200 hover:bg-slate-100'
          }`}
        >
          {isSoundEnabled ? <Volume2 className="w-3.5 h-3.5 text-emerald-600" /> : <VolumeX className="w-3.5 h-3.5 text-slate-400" />}
          <span className="hidden sm:inline">{isSoundEnabled ? 'Sound On' : 'Muted'}</span>
        </button>
      </div>

      {/* =========================================================================
          PANEL A / B / C / D: STATION-FIRST DISCOVERY (COMPLETE CATALOGUE 237 PLACES)
         ========================================================================= */}
      {activeWorkflowStep === 'discovery' && (
        <div className="bg-white rounded-3xl border border-[#E1EAF1] p-6 shadow-xs space-y-5 animate-in fade-in duration-200">
          {/* Header & Subtitle */}
          <div className="pb-3 border-b border-[#E1EAF1]">
            <h2 className="text-xl font-bold text-[#14283F]">{t('discovery.whereStarting', 'Where are you starting?')}</h2>
            <p className="text-xs text-[#718198] mt-0.5">
              {t('discovery.subWhere', 'Select your current location (station, bus stop, or area) to discover nearby places.')}
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
                  <span className="truncate">{getLocalizedHubName(currentLocation.name)}</span>
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
                      <span className="truncate">{getLocalizedHubName(hub.name)}</span>
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
              <span>{t('discovery.useGps', 'Use GPS')}</span>
            </button>
          </div>

          {/* Discovery Tabs: Famous Places, Hidden Gems, All Places */}
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
              <span>{t('discovery.famousPlaces', 'Famous Places')} ({famousCount})</span>
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
              <span>{t('discovery.hiddenGems', 'Hidden Gems')} ({hiddenGemsCount})</span>
            </button>

            <button
              onClick={() => setActiveTab('all')}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-bold transition-all shadow-2xs ${
                activeTab === 'all'
                  ? 'bg-indigo-50 text-indigo-700 border-2 border-indigo-500'
                  : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
              }`}
            >
              <span>{t('discovery.allPlaces', 'All Places')} ({totalCount})</span>
            </button>
          </div>

          {/* Blue Station Change Alert Banner (Panel B) */}
          {showStationBanner && (
            <div className="p-3.5 rounded-2xl bg-sky-50 border border-sky-200 text-[#078ACB] text-xs font-semibold flex items-center justify-between shadow-2xs animate-in fade-in">
              <div className="flex items-center gap-2">
                <span className="text-sm">ℹ️</span>
                <span>
                  {t('discovery.recUpdated', 'Recommendations updated for {station} (within 10 km)')
                    .replace('{station}', currentLocation.name.split('(')[0].trim())}
                </span>
              </div>
              <button
                onClick={() => setShowStationBanner(false)}
                className="text-slate-400 hover:text-slate-700 px-1.5 py-0.5 rounded text-sm font-bold"
              >
                ×
              </button>
            </div>
          )}

          {/* Quick Travel Mode Selector Bar (Matching Panel D) */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 pt-1">
            {TRAVEL_MODES_CONFIG.map((cfg) => {
              const isSelected = travelMode === cfg.id;
              const IconComponent = cfg.icon;
              return (
                <button
                  key={cfg.id}
                  onClick={() => {
                    setTravelMode(cfg.id);
                    setSelectedDistanceKm(cfg.defaultMaxKm);
                    if (cfg.id === 'fujikyu_bus') {
                      setSelectedCategory('Nature & Parks');
                      setSelectedDistanceFilter('< 20 km');
                    }
                  }}
                  className={`px-3 py-1.5 rounded-xl border text-xs font-bold transition-all flex items-center gap-1.5 shrink-0 shadow-2xs ${
                    isSelected
                      ? 'border-[#078ACB] bg-[#078ACB] text-white shadow-xs'
                      : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
                  }`}
                >
                  <IconComponent className={`w-3.5 h-3.5 ${isSelected ? 'text-white' : 'text-slate-500'}`} />
                  <span>{cfg.label}</span>
                </button>
              );
            })}
          </div>

          {/* Filters Bar */}
          <div className="flex flex-wrap items-center gap-2.5 pt-1">
            <div className="relative flex-1 min-w-[200px]">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder={t('discovery.searchPlaceholder', 'Search places (e.g., Oishi Park, shrine, lake...)')}
                className="w-full pl-9 pr-3 py-2 text-xs rounded-xl border border-slate-200 bg-white placeholder-slate-400 focus:outline-hidden focus:border-[#078ACB] focus:ring-1 focus:ring-[#078ACB]"
              />
            </div>

            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              aria-label="Filter places by category"
              className="text-xs py-2 px-3 rounded-xl border border-slate-200 bg-white text-slate-700 font-medium focus:outline-hidden"
            >
              <option>{t('discovery.allCategories', 'All Categories')}</option>
              <option>Nature & Parks</option>
              <option>Shrines & Temples</option>
              <option>Cultural & Heritage</option>
              <option>Scenic Viewpoint</option>
              <option>Museums & Galleries</option>
            </select>

            <select
              value={selectedDistanceFilter}
              onChange={(e) => setSelectedDistanceFilter(e.target.value)}
              aria-label="Filter places by distance"
              className="text-xs py-2 px-3 rounded-xl border border-slate-200 bg-white text-slate-700 font-medium focus:outline-hidden"
            >
              <option value="All">&lt; 10 km</option>
              <option value="< 5 km">&lt; 5 km</option>
              <option value="< 10 km">&lt; 10 km</option>
              <option value="< 20 km">&lt; 20 km</option>
            </select>

            <select
              value={selectedCrowdFilter}
              onChange={(e) => setSelectedCrowdFilter(e.target.value)}
              aria-label="Filter places by crowd level"
              className="text-xs py-2 px-3 rounded-xl border border-slate-200 bg-white text-slate-700 font-medium focus:outline-hidden"
            >
              <option value="All">All Crowds</option>
              <option value="Low Crowd">Low Crowd</option>
              <option value="Moderate Crowd">Moderate Crowd</option>
              <option value="High Crowd">High Crowd</option>
            </select>

            <label className="flex items-center gap-2 px-3 py-2 rounded-xl border border-slate-200 bg-white text-xs font-semibold text-slate-700 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={openNowOnly}
                onChange={(e) => setOpenNowOnly(e.target.checked)}
                className="rounded border-slate-300 text-[#078ACB] focus:ring-[#078ACB]"
              />
              <span>{t('discovery.openNow', 'Open Now')}</span>
            </label>
          </div>

          {/* Main Grid: Left 3 Cards + Right Interactive Mini Map */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 pt-1">
            {/* Left 3 Cards Column (8 Cols on Desktop) */}
            <div className={`lg:col-span-8 grid grid-cols-1 sm:grid-cols-3 gap-3.5 transition-opacity ${isLoadingCatalogue ? 'opacity-70' : 'opacity-100'}`}>
              {isMetroSearch ? (
                <div className="col-span-full p-6 rounded-2xl bg-amber-50 border border-amber-200 text-amber-950 text-xs shadow-2xs space-y-2">
                  <div className="font-bold flex items-center gap-2 text-amber-900 text-sm">
                    <AlertTriangle className="w-4 h-4 text-amber-600" />
                    <span>No metro station found</span>
                  </div>
                  <p className="text-amber-800 leading-relaxed">
                    {t('discovery.noMetroFound', 'No metro station found. The Mount Fuji and Fuji Five Lakes region does not have an underground subway or metro system. Public transit is operated by the Fujikyuko Railway and Fujikyu bus lines.')}
                  </p>
                </div>
              ) : (
                displayedCataloguePlaces.slice(0, 3).map((place) => {
                  const dist = place.distance_km || getDistanceKm(place.latitude, place.longitude);
                  const isFav = favorites.includes(place.place_id);
                  const isHigh = place.crowd_level === 'HIGH';
                  const isMod = place.crowd_level === 'MODERATE';

                  return (
                    <div
                      key={place.place_id}
                      onClick={() => handleSelectDestinationForRoute(place.place_id, place.name_en)}
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
                            <h4 className="text-sm font-bold text-[#14283F] group-hover:text-[#078ACB] transition-colors leading-tight line-clamp-1">
                              {place.name_en}
                            </h4>
                            <div className="text-[11px] text-slate-500 font-japanese mt-0.5 line-clamp-1">
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
                              <span>♿ {t('discovery.accessible', 'Accessible')}</span>
                            </span>
                          </div>

                          {/* Transport Method */}
                          <div className="text-[11px] text-slate-600 flex items-center gap-1.5">
                            <Bus className="w-3 h-3 text-slate-400 shrink-0" />
                            <span className="truncate">{place.route_label || t('discovery.fujikyuLine', 'Fujikyu Line / Bus')}</span>
                          </div>
                        </div>
                      </div>

                      {/* Bottom Badges Row */}
                      <div className="p-3.5 pt-0 flex items-center justify-between text-[10px]">
                        {isHigh ? (
                          <span className="font-bold text-rose-700 bg-rose-50 border border-rose-200 px-2 py-0.5 rounded-full">
                            ● High Crowd
                          </span>
                        ) : isMod ? (
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
                          <span>{(place.fuji_view_rating || 5.0).toFixed(1)}</span>
                        </span>
                      </div>
                    </div>
                  );
                })
              )}
            </div>

            {/* Right Mini Map Preview Column (4 Cols on Desktop matching Panel A in Image 2) */}
            <div className="lg:col-span-4 bg-[#EAF2F8] rounded-2xl border border-[#D0DDE7] p-3.5 flex flex-col justify-between relative overflow-hidden min-h-[260px]">
              {/* Map SVG background */}
              <div className="absolute inset-0 pointer-events-none opacity-80">
                <svg
                  className="w-full h-full"
                  viewBox="0 0 300 240"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                  style={{ transform: `scale(${mapZoom})`, transformOrigin: 'center center', transition: 'transform 0.2s' }}
                >
                  {/* Subtle terrain contours */}
                  <path d="M 10 120 Q 80 90 150 110 T 290 80" stroke="#CBDCE8" strokeWidth="2" strokeDasharray="3 3" />
                  <path d="M 20 180 Q 100 150 200 170 T 280 140" stroke="#CBDCE8" strokeWidth="2" strokeDasharray="3 3" />

                  {/* Lake Kawaguchiko shape */}
                  <path
                    d="M 110 90 C 130 80, 160 85, 185 95 C 205 105, 195 125, 175 130 C 150 135, 130 115, 110 90 Z"
                    fill="#BFE1F7"
                    stroke="#84C0E9"
                    strokeWidth="2"
                  />
                  <text x="145" y="112" fill="#1C5E8A" fontSize="9" fontWeight="bold" textAnchor="middle">
                    Lake Kawaguchiko
                  </text>

                  {/* Lake Saiko shape */}
                  <path
                    d="M 50 115 C 65 110, 85 115, 95 125 C 90 135, 70 135, 55 130 Z"
                    fill="#CCE7F9"
                    stroke="#99CCE8"
                    strokeWidth="1.5"
                  />
                  <text x="75" y="145" fill="#2B6B96" fontSize="8" textAnchor="middle">
                    Lake Saiko
                  </text>

                  {/* Lake Shoji */}
                  <circle cx="35" cy="120" r="12" fill="#D8EDFA" stroke="#99CCE8" strokeWidth="1" />
                  <text x="35" y="140" fill="#4B7B9A" fontSize="7" textAnchor="middle">
                    Lake Shoji
                  </text>

                  {/* Mount Fuji peak silhouette */}
                  <path d="M 170 215 L 210 160 L 250 215 Z" fill="#E2EDF5" stroke="#90ADC4" strokeWidth="1.5" />
                  <path d="M 198 176 L 210 160 L 222 176 L 217 182 L 210 177 L 204 182 Z" fill="#FFFFFF" />
                  <text x="210" y="228" fill="#14283F" fontSize="8" fontWeight="bold" textAnchor="middle">
                    Mt. Fuji (3,776 m)
                  </text>

                  {/* Transit Polyline for Kawaguchiko Network (Panel D) */}
                  {isModeFiltered && (
                    <path
                      d="M 50 115 L 90 120 L 140 85 L 185 95"
                      stroke="#078ACB"
                      strokeWidth="3.5"
                      strokeLinecap="round"
                      strokeDasharray="4 2"
                    />
                  )}

                  {/* Numbered Cluster Pins */}
                  {isFujisan ? (
                    activeTab === 'gems' ? (
                      <>
                        <circle cx="150" cy="110" r="10" fill="#078ACB" />
                        <text x="150" y="114" fill="#FFFFFF" fontSize="9" fontWeight="bold" textAnchor="middle">14</text>
                        <circle cx="220" cy="130" r="10" fill="#078ACB" />
                        <text x="220" y="134" fill="#FFFFFF" fontSize="9" fontWeight="bold" textAnchor="middle">8</text>
                        <circle cx="180" cy="85" r="10" fill="#078ACB" />
                        <text x="180" y="89" fill="#FFFFFF" fontSize="9" fontWeight="bold" textAnchor="middle">9</text>
                      </>
                    ) : (
                      <>
                        <circle cx="150" cy="110" r="10" fill="#078ACB" />
                        <text x="150" y="114" fill="#FFFFFF" fontSize="9" fontWeight="bold" textAnchor="middle">7</text>
                        <circle cx="220" cy="130" r="10" fill="#078ACB" />
                        <text x="220" y="134" fill="#FFFFFF" fontSize="9" fontWeight="bold" textAnchor="middle">13</text>
                        <circle cx="180" cy="85" r="10" fill="#078ACB" />
                        <text x="180" y="89" fill="#FFFFFF" fontSize="9" fontWeight="bold" textAnchor="middle">8</text>
                      </>
                    )
                  ) : (
                    <>
                      <circle cx="140" cy="85" r="10" fill="#078ACB" />
                      <text x="140" y="89" fill="#FFFFFF" fontSize="9" fontWeight="bold" textAnchor="middle">18</text>
                      <circle cx="215" cy="95" r="10" fill="#078ACB" />
                      <text x="215" y="99" fill="#FFFFFF" fontSize="9" fontWeight="bold" textAnchor="middle">15</text>
                      <circle cx="170" cy="115" r="10" fill="#078ACB" />
                      <text x="170" y="119" fill="#FFFFFF" fontSize="9" fontWeight="bold" textAnchor="middle">34</text>
                    </>
                  )}
                </svg>
              </div>

              {/* Map header row */}
              <div className="relative z-10 flex items-center justify-between">
                <span className="text-[10px] font-bold text-[#14283F] bg-white/90 backdrop-blur-xs px-2 py-0.5 rounded-md border border-slate-200">
                  {isFujisan ? 'Fujisan Station Area' : isModeFiltered ? 'Kawaguchiko Network' : 'Lake Kawaguchiko Hub'}
                </span>
                {/* Zoom Controls */}
                <div className="flex items-center gap-1 bg-white/90 backdrop-blur-xs rounded-lg border border-slate-200 p-0.5 shadow-2xs">
                  <button
                    onClick={() => setMapZoom((prev) => Math.min(prev + 0.2, 2))}
                    className="w-5 h-5 flex items-center justify-center text-slate-700 hover:bg-slate-100 rounded text-xs font-bold"
                  >
                    +
                  </button>
                  <button
                    onClick={() => setMapZoom((prev) => Math.max(prev - 0.2, 0.8))}
                    className="w-5 h-5 flex items-center justify-center text-slate-700 hover:bg-slate-100 rounded text-xs font-bold"
                  >
                    -
                  </button>
                </div>
              </div>

              {/* Map footer row */}
              <div className="relative z-10 flex items-center justify-between mt-auto pt-20">
                <span className="text-[9px] text-slate-500 bg-white/80 px-1.5 py-0.5 rounded">
                  {totalCount} {t('discovery.mappedPlaces', 'mapped places')}
                </span>
                {onOpenMap && (
                  <button
                    onClick={onOpenMap}
                    className="text-[10px] font-bold text-[#078ACB] bg-white/95 px-2 py-1 rounded-md border border-sky-200 shadow-2xs hover:bg-sky-50 flex items-center gap-1"
                  >
                    <MapIcon className="w-3 h-3" />
                    <span>Open 3D Twin</span>
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Pagination Controls Row (Matching Panels A, B, C, D) */}
          <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-3 border-t border-slate-100">
            <div className="flex items-center gap-1.5 text-xs">
              <button
                disabled={currentPage <= 1}
                onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
                className="w-7 h-7 rounded-lg border border-slate-200 flex items-center justify-center text-slate-600 disabled:opacity-40 hover:bg-slate-50"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
              </button>

              {(totalPages <= 12 ? [1, 2, 3, 4] : [1, 2, 3, 4, 5]).map((pageNum) => (
                <button
                  key={pageNum}
                  onClick={() => setCurrentPage(pageNum)}
                  className={`w-7 h-7 rounded-lg text-xs font-bold transition-colors ${
                    currentPage === pageNum
                      ? 'bg-[#078ACB] text-white shadow-2xs'
                      : 'text-slate-600 hover:bg-slate-100 border border-slate-200'
                  }`}
                >
                  {pageNum}
                </button>
              ))}

              <span className="text-slate-400 px-1">...</span>

              <button
                onClick={() => setCurrentPage(totalPages)}
                className={`w-7 h-7 rounded-lg text-xs font-bold transition-colors ${
                  currentPage === totalPages
                    ? 'bg-[#078ACB] text-white shadow-2xs'
                    : 'text-slate-600 hover:bg-slate-100 border border-slate-200'
                }`}
              >
                {totalPages}
              </button>

              <button
                disabled={currentPage >= totalPages}
                onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
                className="w-7 h-7 rounded-lg border border-slate-200 flex items-center justify-center text-slate-600 disabled:opacity-40 hover:bg-slate-50"
              >
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="flex items-center gap-3">
              <span className="text-xs text-slate-500 font-medium">
                {t('discovery.showingPlaces', `Showing ${(currentPage - 1) * pageSize + 1}-${Math.min(currentPage * pageSize, totalCount)} of ${totalCount} places`)
                  .replace('{start}', String((currentPage - 1) * pageSize + 1))
                  .replace('{end}', String(Math.min(currentPage * pageSize, totalCount)))
                  .replace('{total}', String(totalCount))}
              </span>

              <button
                onClick={() => {
                  setSelectedCategory('All Categories');
                  setSelectedDistanceFilter('All');
                  setSelectedCrowdFilter('All');
                  setSearchQuery('');
                  setActiveTab('all');
                  setCurrentPage(1);
                }}
                className="text-xs font-bold text-[#078ACB] hover:underline flex items-center gap-1"
              >
                <Layers className="w-3.5 h-3.5" />
                <span>View all {totalCount} places</span>
              </button>
            </div>
          </div>

          {/* Green "Choose for me" Button (Prominent, matching Panel A) */}
          <div className="pt-2">
            <button
              onClick={handleChooseForMe}
              className="w-full py-3.5 px-6 rounded-2xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm shadow-md transition-all flex flex-col items-center justify-center gap-0.5"
            >
              <span className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-emerald-200" />
                <span>{t('discovery.chooseForMe', 'Choose for me')}</span>
              </span>
              <span className="text-[11px] text-emerald-100 font-normal">
                {t('discovery.chooseForMeSub', 'Recommend the best plan based on time, crowd and season')}
              </span>
            </button>
          </div>
        </div>
      )}

      {/* =========================================================================
          PANEL B: HOW WOULD YOU LIKE TO TRAVEL? (8 MODES & RECOMMENDATIONS)
         ========================================================================= */}
      {(activeWorkflowStep === 'modes' || activeWorkflowStep === 'setup') && (
        <div className="bg-white rounded-3xl border border-[#E1EAF1] p-6 shadow-xs space-y-6 animate-in fade-in duration-200">
          {/* Header */}
          <div className="flex items-center justify-between pb-3 border-b border-[#E1EAF1]">
            <div>
              <h2 className="text-xl font-bold text-[#14283F]">How would you like to travel?</h2>
              <p className="text-xs text-[#718198] mt-0.5">
                Tell us your travel style, time and budget to get personalized recommendations.
              </p>
            </div>
            <button
              onClick={() => setActiveWorkflowStep('discovery')}
              className="text-xs text-[#078ACB] hover:underline font-semibold flex items-center gap-1"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Back to catalogue</span>
            </button>
          </div>

          {/* 8 Mode Buttons in Horizontal Scroll / Bar */}
          <div className="space-y-2">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
              Transport Mode
            </span>
            <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2">
              {TRAVEL_MODES_CONFIG.map((cfg) => {
                const isSelected = travelMode === cfg.id;
                const IconComponent = cfg.icon;
                return (
                  <button
                    key={cfg.id}
                    onClick={() => {
                      setTravelMode(cfg.id);
                      setSelectedDistanceKm(cfg.defaultMaxKm);
                    }}
                    className={`p-2.5 rounded-xl border text-left transition-all flex flex-col justify-between gap-1 shadow-2xs ${
                      isSelected
                        ? 'border-[#078ACB] bg-sky-50 text-[#078ACB] ring-2 ring-[#078ACB]/20'
                        : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <IconComponent className={`w-4 h-4 ${isSelected ? 'text-[#078ACB]' : 'text-slate-500'}`} />
                      {isSelected && <Check className="w-3 h-3 text-[#078ACB]" />}
                    </div>
                    <div>
                      <div className="text-xs font-bold leading-tight line-clamp-1">{cfg.label}</div>
                      <div className="text-[9px] text-slate-400 mt-0.5">{cfg.fareBasis}</div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Sliders & Dropdown Row */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 p-4 rounded-2xl bg-[#F8FAFC] border border-[#E1EAF1]">
            {/* 1. Distance Range Slider */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="font-bold text-slate-600">Distance Range</span>
                <span className="font-mono font-bold text-[#078ACB]">0 - {selectedDistanceKm} km</span>
              </div>
              <input
                type="range"
                min="2"
                max={travelMode === 'walk' ? 10 : travelMode === 'bike' ? 25 : 50}
                value={selectedDistanceKm}
                onChange={(e) => setSelectedDistanceKm(Number(e.target.value))}
                className="w-full accent-[#078ACB] cursor-pointer"
              />
              <span className="text-[10px] text-slate-400 block">
                Estimated detour factor x1.3 applied
              </span>
            </div>

            {/* 2. Trip Time Budget */}
            <div className="space-y-1.5">
              <span className="text-xs font-bold text-slate-600 block">Trip Time Budget</span>
              <select
                value={timeBudgetHours}
                onChange={(e) => setTimeBudgetHours(Number(e.target.value))}
                className="w-full text-xs font-semibold py-2 px-3 rounded-xl border border-slate-200 bg-white text-slate-800 focus:outline-hidden"
              >
                <option value={1}>1 hour (Quick stop)</option>
                <option value={2}>2 hours</option>
                <option value={3}>3 hours</option>
                <option value={4}>4 hours</option>
                <option value={5}>5 hours (Recommended)</option>
                <option value={6}>6 hours</option>
                <option value={8}>8 hours (Full day)</option>
              </select>
            </div>

            {/* 3. Budget (transport + entry) */}
            <div className="space-y-1.5">
              <span className="text-xs font-bold text-slate-600 block">Budget (transport + entry)</span>
              <select
                value={selectedBudgetTier}
                onChange={(e) => setSelectedBudgetTier(e.target.value)}
                className="w-full text-xs font-semibold py-2 px-3 rounded-xl border border-slate-200 bg-white text-slate-800 focus:outline-hidden"
              >
                <option>≤ ¥1,500</option>
                <option>≤ ¥3,000</option>
                <option>≤ ¥5,000</option>
                <option>Any budget</option>
              </select>
            </div>

            {/* 4. Travel Style */}
            <div className="space-y-1.5">
              <span className="text-xs font-bold text-slate-600 block">Travel Style</span>
              <select
                value={selectedTravelStyle}
                onChange={(e) => setSelectedTravelStyle(e.target.value)}
                className="w-full text-xs font-semibold py-2 px-3 rounded-xl border border-slate-200 bg-white text-slate-800 focus:outline-hidden"
              >
                <option>Scenic & Relaxed</option>
                <option>Fast Pace</option>
                <option>Nature & Outdoor</option>
                <option>Cultural & Historic</option>
              </select>
            </div>
          </div>

          {/* Section: Recommended Destinations for You */}
          <div className="space-y-3">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
              <div>
                <h3 className="text-sm font-bold text-[#14283F]">Recommended Destinations for You</h3>
                <span className="text-xs text-slate-500">
                  Based on {currentLocation.name.split('(')[0].trim()} • {timeBudgetHours} hours •{' '}
                  {TRAVEL_MODES_CONFIG.find((m) => m.id === travelMode)?.label || 'Fujikyu Bus'}
                </span>
              </div>
              <span className="text-[10px] font-bold text-emerald-800 bg-emerald-50 border border-emerald-200 px-2.5 py-0.5 rounded-full">
                DYNAMICALLY RECALCULATED
              </span>
            </div>

            {/* 3 Recommended Cards Matching Image 2 Panel B */}
            <div className={`grid grid-cols-1 sm:grid-cols-3 gap-4 transition-opacity ${isLoadingRecs ? 'opacity-70' : 'opacity-100'}`}>
              {displayedRecommended.slice(0, 3).map((place) => {
                const isFav = favorites.includes(place.place_id);
                return (
                  <div
                    key={place.place_id}
                    onClick={() => handleSelectDestinationForRoute(place.place_id, place.name_en)}
                    className="group bg-white rounded-2xl border border-[#E1EAF1] hover:border-[#078ACB] hover:shadow-md transition-all cursor-pointer overflow-hidden flex flex-col justify-between"
                  >
                    <div>
                      {/* Photo */}
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
                        >
                          <Heart
                            className={`w-3.5 h-3.5 ${
                              isFav ? 'text-rose-500 fill-rose-500' : 'text-slate-600'
                            }`}
                          />
                        </button>
                      </div>

                      {/* Content */}
                      <div className="p-3.5 space-y-2">
                        <div>
                          <h4 className="text-sm font-bold text-[#14283F] group-hover:text-[#078ACB] transition-colors leading-tight">
                            {place.name_en}
                          </h4>
                          <div className="text-[11px] text-slate-500 font-japanese mt-0.5">
                            {place.name_ja}
                          </div>
                        </div>

                        {/* Travel Time & Fare Badges */}
                        <div className="flex items-center gap-2 text-xs">
                          <span className="flex items-center gap-1 text-slate-600 font-medium">
                            <Clock className="w-3.5 h-3.5 text-slate-400" />
                            <span>~{place.travel_time_min || 20} min</span>
                          </span>
                          <span>•</span>
                          <span className="font-bold text-slate-700 bg-slate-100 px-2 py-0.5 rounded-md text-[11px]">
                            ¥{place.fare_yen || 340} ({travelMode.replace('_', ' ')})
                          </span>
                        </div>

                        {/* Crowd Badge */}
                        <div className="text-[10px]">
                          <span className="font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full">
                            ● Low Crowd
                          </span>
                        </div>

                        {/* Note */}
                        <p className="text-[11px] text-[#425466] line-clamp-2">
                          {place.sub_category || 'Scenic viewpoint with magnificent Mount Fuji backdrop.'}
                        </p>
                      </div>
                    </div>

                    <div className="p-3.5 pt-0">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleSelectDestinationForRoute(place.place_id, place.name_en);
                        }}
                        className="w-full py-2 rounded-xl bg-[#078ACB] hover:bg-[#0672A7] text-white text-xs font-bold transition-colors flex items-center justify-center gap-1.5"
                      >
                        <span>View Route & Directions</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Bottom Action Buttons */}
            <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={fetchRecommendations}
                  className="px-4 py-2 rounded-xl border border-sky-300 bg-sky-50 text-sky-800 text-xs font-bold hover:bg-sky-100 transition-colors shadow-2xs flex items-center gap-1.5"
                >
                  <RotateCcw className="w-3.5 h-3.5 text-[#078ACB]" />
                  <span>Update recommendations</span>
                </button>

                <button
                  type="button"
                  onClick={() => setActiveWorkflowStep('discovery')}
                  className="px-4 py-2 rounded-xl border border-slate-200 bg-white text-slate-700 text-xs font-bold hover:bg-slate-50 transition-colors shadow-2xs"
                >
                  <span>View nearby places ({totalCount})</span>
                </button>
              </div>

              <button
                type="button"
                onClick={handlePlanFullTrip}
                className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shadow-sm transition-colors flex items-center gap-1.5"
              >
                <span>Plan Full Day Itinerary</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          PANEL C: ROUTE TO DESTINATION (GOOGLE-MAPS-STYLE TRANSIT & ROUTE MAP)
         ========================================================================= */}
      {activeWorkflowStep === 'route' && (
        <div className="bg-white rounded-3xl border border-[#E1EAF1] p-6 shadow-xs space-y-6 animate-in fade-in duration-200">
          {/* Header */}
          <div className="flex items-center justify-between pb-3 border-b border-[#E1EAF1]">
            <div>
              <h2 className="text-xl font-bold text-[#14283F]">Route to {selectedPlaceName}</h2>
              <p className="text-xs text-[#718198] mt-0.5">
                Step-by-step directions from {currentLocation.name.split('(')[0].trim()} with map and transport details.
              </p>
            </div>
            <button
              onClick={() => setActiveWorkflowStep('modes')}
              className="text-xs text-[#078ACB] hover:underline font-semibold flex items-center gap-1"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Change transport mode</span>
            </button>
          </div>

          {/* Two-Column Layout: Left Transit Route Map + Right Turn-by-Turn Card */}
          <div className={`grid grid-cols-1 lg:grid-cols-12 gap-5 items-stretch transition-opacity ${isLoadingRoute ? 'opacity-70' : 'opacity-100'}`}>
            {/* Left: Interactive Route Map (7 Cols on Desktop) */}
            <div className="lg:col-span-7 bg-[#EAF2F8] rounded-2xl border border-[#D0DDE7] p-4 flex flex-col justify-between relative overflow-hidden min-h-[380px]">
              {/* SVG Route Visualization */}
              <div className="absolute inset-0">
                <svg className="w-full h-full" viewBox="0 0 500 350" fill="none" xmlns="http://www.w3.org/2000/svg">
                  {/* Subtle topography and Lake Kawaguchiko */}
                  <path
                    d="M 60 170 C 120 130, 240 120, 360 160 C 420 180, 440 230, 380 250 C 260 280, 160 250, 60 170 Z"
                    fill="#D0E7F7"
                    stroke="#94C5E8"
                    strokeWidth="2"
                  />
                  <text x="240" y="210" fill="#246794" fontSize="12" fontWeight="bold" textAnchor="middle">
                    Lake Kawaguchiko
                  </text>

                  {/* Mount Fuji peak outline in distance */}
                  <path d="M 280 340 L 370 240 L 460 340 Z" fill="#E6EEF5" stroke="#ABC2D4" strokeWidth="1.5" />
                  <path d="M 345 268 L 370 240 L 395 268 L 388 276 L 370 268 L 352 276 Z" fill="#FFFFFF" />
                  <text x="370" y="335" fill="#14283F" fontSize="10" fontWeight="bold" textAnchor="middle">
                    Mt. Fuji
                  </text>

                  {/* Dotted Walking Path from Kawaguchiko Station to Bus Stop No. 1 */}
                  <path d="M 80 280 L 110 260" stroke="#718198" strokeWidth="3" strokeDasharray="4 4" />

                  {/* Solid Blue Bus Route Line from Bus Stop No. 1 along North Shore to Oishi Park */}
                  <path
                    d="M 110 260 C 130 220, 170 170, 240 150 C 310 130, 360 140, 390 120"
                    stroke="#078ACB"
                    strokeWidth="5"
                    strokeLinecap="round"
                    fill="none"
                  />

                  {/* Dotted Walking Path from Oishi Park Bus Stop to Main View Area */}
                  <path d="M 390 120 L 410 110" stroke="#718198" strokeWidth="3" strokeDasharray="4 4" />

                  {/* Intermediate Bus Stop Markers */}
                  <circle cx="160" cy="188" r="5" fill="#FFFFFF" stroke="#078ACB" strokeWidth="2.5" />
                  <circle cx="230" cy="152" r="5" fill="#FFFFFF" stroke="#078ACB" strokeWidth="2.5" />
                  <circle cx="310" cy="135" r="5" fill="#FFFFFF" stroke="#078ACB" strokeWidth="2.5" />

                  {/* Start Pin: Green Pin at Kawaguchiko Station */}
                  <g transform="translate(65, 255)">
                    <circle cx="15" cy="15" r="14" fill="#00875A" />
                    <text x="15" y="19" fill="#FFFFFF" fontSize="10" fontWeight="bold" textAnchor="middle">
                      A
                    </text>
                  </g>
                  {/* Start Label */}
                  <rect x="20" y="295" width="140" height="24" rx="6" fill="#FFFFFF" fillOpacity="0.95" stroke="#CBDCE8" />
                  <text x="90" y="311" fill="#14283F" fontSize="10" fontWeight="bold" textAnchor="middle">
                    {currentLocation.name.split('(')[0].trim()} (Start)
                  </text>

                  {/* Destination Pin: Red Pin at Oishi Park */}
                  <g transform="translate(395, 85)">
                    <circle cx="15" cy="15" r="14" fill="#E11D48" />
                    <text x="15" y="19" fill="#FFFFFF" fontSize="10" fontWeight="bold" textAnchor="middle">
                      B
                    </text>
                  </g>
                  {/* Goal Label */}
                  <rect x="350" y="60" width="130" height="24" rx="6" fill="#FFFFFF" fillOpacity="0.95" stroke="#CBDCE8" />
                  <text x="415" y="76" fill="#14283F" fontSize="10" fontWeight="bold" textAnchor="middle">
                    {selectedPlaceName} (Goal)
                  </text>
                </svg>
              </div>

              {/* Map Overlay Header */}
              <div className="relative z-10 flex items-center justify-between">
                <span className="text-[11px] font-bold text-[#14283F] bg-white/95 backdrop-blur-xs px-3 py-1 rounded-xl border border-slate-200 shadow-2xs">
                  Fujikyu Transit Route (Red Line)
                </span>
                <span className="text-[10px] font-bold text-sky-800 bg-sky-100/90 px-2.5 py-1 rounded-lg">
                  SCHEDULED TIMETABLE
                </span>
              </div>

              {/* Map Overlay Bottom Legend (Matching Panel C in Image 2) */}
              <div className="relative z-10 flex items-center gap-4 bg-white/95 backdrop-blur-xs px-3.5 py-2 rounded-xl border border-slate-200 shadow-2xs self-start mt-auto text-[11px] text-slate-700">
                <span className="flex items-center gap-1.5 font-medium">
                  <span className="w-3 h-0.5 border-b-2 border-dashed border-slate-600 inline-block" />
                  <span>Walking</span>
                </span>
                <span className="flex items-center gap-1.5 font-medium">
                  <span className="w-3.5 h-1 bg-[#078ACB] rounded-full inline-block" />
                  <span>Bus (Fujikyu)</span>
                </span>
                <span className="flex items-center gap-1 font-medium">
                  <span className="w-2.5 h-2.5 rounded-full border-2 border-[#078ACB] bg-white inline-block" />
                  <span>Bus Stop</span>
                </span>
                <span className="flex items-center gap-1 font-medium">
                  <span className="w-2.5 h-2.5 rounded-full bg-rose-600 inline-block" />
                  <span>Destination</span>
                </span>
              </div>
            </div>

            {/* Right: Step-by-Step Directions Card (5 Cols on Desktop) */}
            <div className="lg:col-span-5 bg-white rounded-2xl border border-[#E1EAF1] p-5 flex flex-col justify-between space-y-4 shadow-2xs">
              <div>
                {/* Summary Header */}
                <div className="pb-3 border-b border-slate-100">
                  <h3 className="text-base font-bold text-[#14283F]">Your route</h3>
                  <div className="flex items-center justify-between text-xs text-slate-600 mt-1">
                    <span className="font-semibold text-[#078ACB]">
                      {currentLocation.name.split('(')[0].trim()} → {selectedPlaceName}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-xs font-mono font-bold text-slate-700 mt-1">
                    <span>Total: ~20 min</span>
                    <span>•</span>
                    <span className="text-emerald-700">Fare: ¥340 (Adult)</span>
                  </div>
                </div>

                {/* Step-by-Step Items (Matching Image 2 Panel C) */}
                <div className="space-y-3.5 pt-3 text-xs">
                  {/* Step 1: Walk to Bus Stop */}
                  <div className="flex items-start gap-3">
                    <div className="w-7 h-7 rounded-full bg-slate-100 flex items-center justify-center shrink-0 text-slate-600">
                      <Footprints className="w-3.5 h-3.5" />
                    </div>
                    <div className="flex-1">
                      <div className="font-bold text-[#14283F]">Walk 4 min (≈ 320 m)</div>
                      <div className="text-slate-500 text-[11px] mt-0.5">
                        From {currentLocation.name.split('(')[0].trim()} to Bus Stop No. 1
                      </div>
                    </div>
                  </div>

                  {/* Step 2: Bus Leg */}
                  <div className="flex items-start gap-3 p-3 rounded-xl bg-sky-50/80 border border-sky-100">
                    <div className="w-7 h-7 rounded-full bg-[#078ACB] text-white flex items-center justify-center shrink-0">
                      <Bus className="w-3.5 h-3.5" />
                    </div>
                    <div className="flex-1 space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-[#14283F]">Fujikyu Red Line Bus</span>
                        <span className="text-[10px] font-bold text-sky-800 bg-sky-100 px-1.5 py-0.5 rounded">
                          Scheduled
                        </span>
                      </div>
                      <div className="text-[11px] text-slate-600 space-y-0.5">
                        <div>Boarding Stop: Kawaguchiko Station (No. 1)</div>
                        <div>Departure: 09:45 (Scheduled)</div>
                        <div>Alighting Stop: Oishi Park (Oishi Kōen)</div>
                        <div>Travel Time: ~16 min • Fare: ¥340</div>
                      </div>
                    </div>
                  </div>

                  {/* Step 3: Walk to Destination */}
                  <div className="flex items-start gap-3">
                    <div className="w-7 h-7 rounded-full bg-slate-100 flex items-center justify-center shrink-0 text-slate-600">
                      <Footprints className="w-3.5 h-3.5" />
                    </div>
                    <div className="flex-1">
                      <div className="font-bold text-[#14283F]">Walk 1 min (≈ 60 m)</div>
                      <div className="text-slate-500 text-[11px] mt-0.5">
                        To {selectedPlaceName} Main View Area
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="pt-2 border-t border-slate-100 flex items-center gap-2.5">
                <button
                  type="button"
                  onClick={() => setIsTransitModalOpen(true)}
                  className="flex-1 py-2.5 px-3 rounded-xl border border-sky-300 bg-sky-50 text-sky-800 text-xs font-bold hover:bg-sky-100 transition-colors text-center shadow-2xs flex items-center justify-center gap-1.5"
                >
                  <Bus className="w-3.5 h-3.5 text-[#078ACB]" />
                  <span>Show bus details</span>
                </button>

                <button
                  type="button"
                  onClick={handlePlanFullTrip}
                  className="flex-1 py-2.5 px-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold transition-colors text-center shadow-sm flex items-center justify-center gap-1.5"
                >
                  <Calendar className="w-3.5 h-3.5" />
                  <span>Plan full trip</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          PANEL E: YOUR 5-HOUR DAY / TRIP ITINERARY & LIVE PROGRESS (MATCHING PANEL E)
         ========================================================================= */}
      {(activeWorkflowStep === 'itinerary' || activeWorkflowStep === 'progress') && (
        <div className="bg-white rounded-3xl border border-[#E1EAF1] p-6 shadow-xs space-y-6 animate-in fade-in duration-200">
          {/* Header & Trip Timer (Matching Panel E) */}
          <div className="flex flex-col sm:flex-row sm:items-start justify-between pb-4 border-b border-[#E1EAF1] gap-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
                <h2 className="text-xl font-bold text-[#14283F]">Your {timeBudgetHours}-hour day</h2>
              </div>
              <p className="text-xs text-[#718198] mt-0.5">
                {currentLocation.name.split('(')[0].trim()} → {selectedPlaceName} (+ nearby places & meals)
              </p>
            </div>

            {/* Right side: Trip Timer + Destination Photo Thumbnail */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
              {/* Trip Timer Widget */}
              <div className="flex items-center gap-3 bg-[#F5F8FB] border border-[#D0DDE7] px-4 py-2 rounded-2xl shadow-2xs">
                <div className="space-y-0.5">
                  <div className="text-[10px] font-bold text-slate-500 uppercase flex items-center gap-1">
                    <Clock className="w-3 h-3 text-[#078ACB]" />
                    <span>Trip Timer</span>
                  </div>
                  <div className="text-sm font-mono font-bold text-[#14283F]">
                    {formatTimeSeconds(timerSecondsElapsed)} / {formatTimeSeconds(totalTimerSeconds)}
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => setIsTimerRunning(!isTimerRunning)}
                  className="w-8 h-8 rounded-xl bg-white border border-slate-200 text-slate-700 hover:bg-slate-100 flex items-center justify-center transition-colors shadow-2xs"
                  title={isTimerRunning ? 'Pause timer' : 'Resume timer'}
                >
                  {isTimerRunning ? <Pause className="w-4 h-4 text-[#078ACB]" /> : <Play className="w-4 h-4 text-emerald-600 ml-0.5" />}
                </button>
              </div>

              {/* Destination Photo Thumbnail Card (Matching Panel E) */}
              <div className="flex items-center gap-2.5 bg-white border border-slate-200 p-2.5 rounded-2xl shadow-2xs">
                <div className="w-12 h-12 rounded-xl overflow-hidden bg-slate-100 shrink-0">
                  <img
                    src="https://images.unsplash.com/photo-1578637387939-43c525550085?auto=format&fit=crop&w=200&q=80"
                    alt={selectedPlaceName}
                    className="w-full h-full object-cover"
                  />
                </div>
                <div>
                  <div className="text-xs font-bold text-[#14283F]">{selectedPlaceName}</div>
                  <div className="text-[10px] text-slate-500">Planned: 60 min</div>
                  <div className="flex items-center gap-1.5 mt-1">
                    <button
                      onClick={() => setIsEarlyRecalibrationModalOpen(true)}
                      className="px-2 py-0.5 rounded-lg bg-emerald-50 text-emerald-700 border border-emerald-200 text-[10px] font-bold hover:bg-emerald-100"
                    >
                      Complete Early
                    </button>
                    <button
                      onClick={() => setTimerSecondsRemaining(prev => prev + 1800)}
                      className="px-2 py-0.5 rounded-lg bg-slate-50 text-slate-600 border border-slate-200 text-[10px] font-bold hover:bg-slate-100"
                    >
                      + Extend
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Overdue Warning Notification Banner */}
          {isOverdueBannerVisible && (
            <div className="p-4 rounded-2xl bg-amber-50 border border-amber-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-amber-950 shadow-2xs animate-in slide-in-from-top-2">
              <div className="flex items-center gap-2.5">
                <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0" />
                <span className="text-xs font-bold">
                  ⚠️ Planned visit time exceeded — extend, leave now or adjust plan.
                </span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    setTimerSecondsRemaining((prev) => prev + 1800);
                    setIsOverdueBannerVisible(false);
                  }}
                  className="px-3 py-1.5 rounded-xl bg-white border border-amber-300 text-amber-900 text-xs font-bold hover:bg-amber-100 transition-colors"
                >
                  Extend +30 min
                </button>
                <button
                  onClick={() => setIsOverdueBannerVisible(false)}
                  className="px-3 py-1.5 rounded-xl bg-amber-600 text-white text-xs font-bold hover:bg-amber-700 transition-colors"
                >
                  Leave now
                </button>
                <button
                  onClick={() => {
                    setIsOverdueBannerVisible(false);
                    setIsEarlyRecalibrationModalOpen(true);
                  }}
                  className="px-3 py-1.5 rounded-xl bg-white border border-slate-300 text-slate-700 text-xs font-bold hover:bg-slate-50 transition-colors"
                >
                  Adjust plan
                </button>
              </div>
            </div>
          )}

          {/* Early Finish Recalibration Box (Bottom Right in Panel E) */}
          <div className="p-4 rounded-2xl bg-amber-50/90 border border-amber-200 shadow-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-amber-950">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl overflow-hidden bg-amber-100 shrink-0">
                <img
                  src="https://images.unsplash.com/photo-1570125909232-eb263c188f7e?auto=format&fit=crop&w=200&q=80"
                  alt="Kawaguchiko Music Forest"
                  className="w-full h-full object-cover"
                />
              </div>
              <div>
                <div className="text-xs font-bold flex items-center gap-1 text-amber-900">
                  <span>⚡</span>
                  <span>You're 22 minutes ahead!</span>
                </div>
                <p className="text-[11px] text-amber-800 mt-0.5">
                  Would you like to add a nearby spot? (e.g. Kawaguchiko Music Forest)
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 self-end sm:self-auto">
              <button
                onClick={() => setIsEarlyRecalibrationModalOpen(true)}
                className="px-3.5 py-1.5 rounded-xl border border-amber-300 bg-white text-amber-900 text-xs font-bold hover:bg-amber-100 transition-colors"
              >
                Adjust plan
              </button>
              <button
                onClick={handleApplyRecalibration}
                className="px-3.5 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold transition-colors shadow-2xs"
              >
                Add to plan
              </button>
            </div>
          </div>

          {/* Sequential Timeline (Matching Panel E) */}
          <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-3 before:bottom-3 before:w-0.5 before:bg-slate-200">
            {/* 1. Breakfast */}
            <div className="relative flex items-start gap-4">
              <span className="absolute -left-6 top-1 w-5 h-5 rounded-full bg-emerald-500 border-2 border-white flex items-center justify-center text-white text-[10px]">
                ✓
              </span>
              <div className="w-24 shrink-0 text-xs font-mono font-bold text-slate-500">
                09:30 - 09:50
              </div>
              <div className="flex-1 flex flex-col sm:flex-row sm:items-center justify-between p-3 rounded-2xl bg-white border border-slate-100 shadow-2xs gap-3">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-xl overflow-hidden shrink-0 bg-slate-100">
                    <img
                      src="https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=200&q=80"
                      alt="Breakfast"
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-[#14283F]">Breakfast at Kawaguchiko Café</h4>
                    <span className="text-[11px] text-slate-500">Local café • ~20 min • ¥1,000-1,500</span>
                  </div>
                </div>
                <span className="text-[11px] font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-full self-start sm:self-auto flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                  <span>Completed</span>
                </span>
              </div>
            </div>

            {/* 2. Travel to Oishi Park */}
            <div className="relative flex items-start gap-4">
              <span className="absolute -left-6 top-1 w-5 h-5 rounded-full bg-emerald-500 border-2 border-white flex items-center justify-center text-white text-[10px]">
                ✓
              </span>
              <div className="w-24 shrink-0 text-xs font-mono font-bold text-slate-500">
                09:50 - 10:10
              </div>
              <div className="flex-1 flex flex-col sm:flex-row sm:items-center justify-between p-3 rounded-2xl bg-white border border-slate-100 shadow-2xs gap-3">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-xl bg-sky-50 flex items-center justify-center text-[#078ACB] shrink-0 border border-sky-100">
                    <Bus className="w-6 h-6" />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-[#14283F]">Travel to Oishi Park (Fujikyu Red Line)</h4>
                    <span className="text-[11px] text-slate-500">Bus • ~20 min • ¥340</span>
                  </div>
                </div>
                <span className="text-[11px] font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-full self-start sm:self-auto flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                  <span>Completed</span>
                </span>
              </div>
            </div>

            {/* 3. Oishi Park (Main Visit) - Active Stop */}
            <div className="relative flex items-start gap-4">
              <span className="absolute -left-6 top-1 w-5 h-5 rounded-full bg-emerald-500 border-2 border-white ring-4 ring-emerald-100" />
              <div className="w-24 shrink-0 text-xs font-mono font-bold text-emerald-700">
                10:10 - 11:10
              </div>
              <div className="flex-1 flex flex-col sm:flex-row sm:items-center justify-between p-3.5 rounded-2xl bg-emerald-50/70 border-2 border-emerald-300 shadow-2xs gap-3">
                <div className="flex items-center gap-3">
                  <div className="w-14 h-14 rounded-xl overflow-hidden shrink-0 bg-slate-200">
                    <img
                      src="https://images.unsplash.com/photo-1578637387939-43c525550085?auto=format&fit=crop&w=200&q=80"
                      alt={selectedPlaceName}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div>
                    <div className="flex items-center gap-1.5">
                      <h4 className="text-xs font-bold text-[#14283F]">{selectedPlaceName} (Main Visit)</h4>
                      <span className="text-[10px] font-bold text-emerald-800 bg-emerald-100 border border-emerald-300 px-2 py-0.5 rounded-full">
                        ⏱ {formatTimeSeconds(timerSecondsRemaining)} left
                      </span>
                    </div>
                    <span className="text-[11px] text-slate-600 block mt-0.5">
                      Sightseeing • 60 min • Free Admission
                    </span>
                  </div>
                </div>
                {/* Trigger Early Finish Recalibration Button */}
                <button
                  type="button"
                  onClick={() => setIsEarlyRecalibrationModalOpen(true)}
                  className="px-3.5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold transition-all shadow-2xs flex items-center gap-1.5 self-start sm:self-auto"
                >
                  <Sparkles className="w-3.5 h-3.5 text-emerald-200" />
                  <span>Finished Early (-22m)?</span>
                </button>
              </div>
            </div>

            {/* 4. Ubuyagasaki (Hidden Gem) */}
            <div className="relative flex items-start gap-4">
              <span className="absolute -left-6 top-1 w-5 h-5 rounded-full bg-slate-300 border-2 border-white" />
              <div className="w-24 shrink-0 text-xs font-mono text-slate-500">
                11:15 - 12:00
              </div>
              <div className="flex-1 flex flex-col sm:flex-row sm:items-center justify-between p-3 rounded-2xl bg-white border border-slate-100 shadow-2xs gap-3">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-xl overflow-hidden shrink-0 bg-slate-100">
                    <img
                      src="https://images.unsplash.com/photo-1528164344705-475426879c0d?auto=format&fit=crop&w=200&q=80"
                      alt="Ubuyagasaki"
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-[#14283F]">Ubuyagasaki (Hidden Gem)</h4>
                    <span className="text-[11px] text-slate-500">Lakeside view • 45 min • Free</span>
                  </div>
                </div>
                <span className="text-[10px] text-slate-400 font-medium">Upcoming</span>
              </div>
            </div>

            {/* 5. Lunch (Hoto Noodles) */}
            <div className="relative flex items-start gap-4">
              <span className="absolute -left-6 top-1 w-5 h-5 rounded-full bg-slate-300 border-2 border-white" />
              <div className="w-24 shrink-0 text-xs font-mono text-slate-500">
                12:00 - 13:00
              </div>
              <div className="flex-1 flex flex-col sm:flex-row sm:items-center justify-between p-3 rounded-2xl bg-white border border-slate-100 shadow-2xs gap-3">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-xl overflow-hidden shrink-0 bg-slate-100">
                    <img
                      src="https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=200&q=80"
                      alt="Lunch"
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-[#14283F]">Lunch - Hoto Noodles (Local Cuisine)</h4>
                    <span className="text-[11px] text-slate-500">Local restaurant • 60 min • ¥1,200-2,000</span>
                  </div>
                </div>
                <span className="text-[10px] text-slate-400 font-medium">Upcoming</span>
              </div>
            </div>

            {/* 6. Nagasaki Cape */}
            <div className="relative flex items-start gap-4">
              <span className="absolute -left-6 top-1 w-5 h-5 rounded-full bg-slate-300 border-2 border-white" />
              <div className="w-24 shrink-0 text-xs font-mono text-slate-500">
                13:00 - 14:30
              </div>
              <div className="flex-1 flex flex-col sm:flex-row sm:items-center justify-between p-3 rounded-2xl bg-white border border-slate-100 shadow-2xs gap-3">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-xl overflow-hidden shrink-0 bg-slate-100">
                    <img
                      src="https://images.unsplash.com/photo-1542051841857-5f90071e7989?auto=format&fit=crop&w=200&q=80"
                      alt="Nagasaki Cape"
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-[#14283F]">Nagasaki Cape (Scenic View)</h4>
                    <span className="text-[11px] text-slate-500">Nature & Fuji view • 90 min • Free</span>
                  </div>
                </div>
                <span className="text-[10px] text-slate-400 font-medium">Upcoming</span>
              </div>
            </div>

            {/* 7. Return to Station */}
            <div className="relative flex items-start gap-4">
              <span className="absolute -left-6 top-1 w-5 h-5 rounded-full bg-slate-300 border-2 border-white" />
              <div className="w-24 shrink-0 text-xs font-mono text-slate-500">
                14:30 - 15:00
              </div>
              <div className="flex-1 flex flex-col sm:flex-row sm:items-center justify-between p-3 rounded-2xl bg-white border border-slate-100 shadow-2xs gap-3">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-xl bg-slate-100 flex items-center justify-center text-slate-600 shrink-0">
                    <Bus className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-[#14283F]">
                      Return to {currentLocation.name.split('(')[0].trim()}
                    </h4>
                    <span className="text-[11px] text-slate-500">Bus • ~30 min • ¥340</span>
                  </div>
                </div>
                <span className="text-[10px] text-slate-400 font-medium">Return Leg</span>
              </div>
            </div>
          </div>

          {/* Action Row */}
          <div className="pt-2 flex flex-wrap items-center justify-between gap-3 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setActiveWorkflowStep('route')}
              className="px-4 py-2 rounded-xl border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 flex items-center gap-1.5"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Back to Route</span>
            </button>

            <button
              type="button"
              onClick={() => setIsTransitModalOpen(true)}
              className="px-4 py-2 rounded-xl border border-sky-300 bg-sky-50 text-sky-800 text-xs font-bold hover:bg-sky-100 flex items-center gap-1.5"
            >
              <Bus className="w-3.5 h-3.5 text-[#078ACB]" />
              <span>Next Bus Schedule</span>
            </button>
          </div>
        </div>
      )}

      {/* =========================================================================
          EARLY / LATE RECALIBRATION POPUP MODAL (Matching Image 2 Panel D)
         ========================================================================= */}
      {isEarlyRecalibrationModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs animate-in fade-in duration-200">
          <div className="bg-white rounded-3xl p-6 max-w-lg w-full shadow-2xl space-y-4 border border-slate-100">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-2xl bg-amber-100 text-amber-700 flex items-center justify-center shrink-0">
                <Sparkles className="w-5 h-5 text-amber-600" />
              </div>
              <div>
                <h3 className="text-base font-bold text-[#14283F]">
                  You finished {selectedPlaceName} {recalibrationMinutes} minutes early!
                </h3>
                <p className="text-xs text-slate-600 mt-1">
                  You now have ~{recalibrationMinutes} extra minutes. Would you like to recalculate your remaining plan?
                </p>
              </div>
            </div>

            {/* Comparison Box */}
            <div className="grid grid-cols-2 gap-3 text-xs pt-1">
              {/* Revised Plan */}
              <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-950 space-y-1.5">
                <div className="font-bold text-emerald-900 flex items-center gap-1">
                  <span>✓ Revised Plan</span>
                  <span className="text-[9px] bg-emerald-200 px-1.5 py-0.2 rounded font-mono">Optimized</span>
                </div>
                <ul className="text-[11px] text-emerald-800 space-y-1 list-disc list-inside">
                  <li>Adds Kawaguchiko Music Forest (40m)</li>
                  <li>Relaxed lunch at lakeside café (60m)</li>
                  <li>Nagasaki Cape quiet viewpoint (60m)</li>
                </ul>
              </div>

              {/* Original Plan */}
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-slate-700 space-y-1.5">
                <div className="font-bold text-slate-800">Original Plan</div>
                <ul className="text-[11px] text-slate-600 space-y-1 list-disc list-inside">
                  <li>Ubuyagasaki lakeside (45m)</li>
                  <li>Lunch - Hoto noodles (60m)</li>
                  <li>Nagasaki Cape (90m)</li>
                </ul>
              </div>
            </div>

            {/* Modal Buttons */}
            <div className="flex items-center justify-end gap-2.5 pt-2">
              <button
                type="button"
                onClick={() => setIsEarlyRecalibrationModalOpen(false)}
                className="px-4 py-2.5 rounded-xl border border-slate-200 text-slate-700 text-xs font-semibold hover:bg-slate-50 transition-colors"
              >
                Keep original plan
              </button>
              <button
                type="button"
                onClick={handleApplyRecalibration}
                className="px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold transition-colors shadow-sm flex items-center gap-1.5"
              >
                <Check className="w-4 h-4" />
                <span>Apply updated plan</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          TRANSIT INSTRUCTION (NEXT BUS) MODAL
         ========================================================================= */}
      <TransitInstructionModal
        isOpen={isTransitModalOpen}
        onClose={() => setIsTransitModalOpen(false)}
        destinationName={selectedPlaceName}
        onOpenRoute={onOpenMap}
        onConfirmDepart={() => {
          setIsTransitModalOpen(false);
          setIsTripProgressActive(true);
          setActiveWorkflowStep('itinerary');
        }}
      />
    </div>
  );
};

import React, { createContext, useContext, useState, ReactNode, useCallback } from 'react';
import {
  TimeBudgetedItineraryResponse,
  TravelMode,
  TransitRouteResponse,
  TripPlanResponse
} from '../types';
import { apiUrl } from '../config';

export interface LocationInfo {
  name: string;
  lat: number;
  lon: number;
  isGps: boolean;
  isOutsideRegion: boolean;
}

export const MOUNT_FUJI_CENTER = {
  lat: 35.3606,
  lon: 138.7274,
};

export const STANDARD_HUBS: LocationInfo[] = [
  {
    name: 'Kawaguchiko Station (Main Hub)',
    lat: 35.4981,
    lon: 138.7690,
    isGps: false,
    isOutsideRegion: false,
  },
  {
    name: 'Fujisan Station (Mt. Fuji Station)',
    lat: 35.4839,
    lon: 138.7958,
    isGps: false,
    isOutsideRegion: false,
  },
  {
    name: 'Shimoyoshida Station (Chureito Pagoda)',
    lat: 35.4983,
    lon: 138.8078,
    isGps: false,
    isOutsideRegion: false,
  },
  {
    name: 'Mt. Fuji 5th Station (Subaru Line 2,305m)',
    lat: 35.3941,
    lon: 138.7328,
    isGps: false,
    isOutsideRegion: false,
  },
  {
    name: 'Lake Yamanakako (Asahigaoka Bus Terminal)',
    lat: 35.4072,
    lon: 138.8785,
    isGps: false,
    isOutsideRegion: false,
  },
  {
    name: 'Lake Saiko (Iyashi-no-Sato Nenba Stop)',
    lat: 35.5085,
    lon: 138.6653,
    isGps: false,
    isOutsideRegion: false,
  },
  {
    name: 'Lake Shoji (Tatego-hama Scenic Point)',
    lat: 35.4851,
    lon: 138.6087,
    isGps: false,
    isOutsideRegion: false,
  },
  {
    name: 'Lake Motosu (Koan & 1,000-Yen View Hub)',
    lat: 35.4660,
    lon: 138.5862,
    isGps: false,
    isOutsideRegion: false,
  },
  {
    name: 'Otsuki Station (JR Chuo & Fujikyu Junction)',
    lat: 35.6133,
    lon: 138.9422,
    isGps: false,
    isOutsideRegion: false,
  },
  {
    name: 'Gotemba Station (JR & Mount Fuji East Gateway)',
    lat: 35.3005,
    lon: 138.9344,
    isGps: false,
    isOutsideRegion: false,
  },
  {
    name: 'Shin-Fuji Station (Tokaido Shinkansen)',
    lat: 35.1421,
    lon: 138.6631,
    isGps: false,
    isOutsideRegion: false,
  },
  {
    name: 'Mishima Station (Shinkansen South Gateway)',
    lat: 35.1270,
    lon: 138.9108,
    isGps: false,
    isOutsideRegion: false,
  },
  {
    name: 'Tokyo Shinjuku (Outside Region)',
    lat: 35.6909,
    lon: 139.7003,
    isGps: false,
    isOutsideRegion: true,
  },
];

interface TripContextType {
  currentLocation: LocationInfo;
  setCurrentLocation: (loc: LocationInfo) => void;
  selectedPlaceId: string;
  selectedPlaceName: string;
  setSelectedPlace: (id: string, name?: string) => void;
  travelMode: TravelMode;
  setTravelMode: (mode: TravelMode) => void;
  discoveryView: 'recommended' | 'catalogue';
  setDiscoveryView: (view: 'recommended' | 'catalogue') => void;
  activeRouteData: TransitRouteResponse | null;
  setActiveRouteData: (route: TransitRouteResponse | null) => void;
  activePlanData: TripPlanResponse | null;
  setActivePlanData: (plan: TripPlanResponse | null) => void;
  timeBudgetHours: number;
  setTimeBudgetHours: (hours: number) => void;
  departureTime: string;
  setDepartureTime: (time: string) => void;
  adultCount: number;
  setAdultCount: (cnt: number) => void;
  childCount: number;
  setChildCount: (cnt: number) => void;
  userHasJrPass: boolean;
  setUserHasJrPass: (has: boolean) => void;
  preferQuiet: boolean;
  setPreferQuiet: (quiet: boolean) => void;
  foodExperience: string;
  setFoodExperience: (exp: string) => void;
  foodStyles: string[];
  toggleFoodStyle: (style: string) => void;
  activeTransitModalStep: any | null;
  setActiveTransitModalStep: (step: any | null) => void;
  isTransitModalOpen: boolean;
  setIsTransitModalOpen: (open: boolean) => void;
  isTripProgressActive: boolean;
  setIsTripProgressActive: (active: boolean) => void;
  completedStepIndices: number[];
  markStepCompleted: (index: number, actualMinutes?: number) => void;
  isAdaptiveModalOpen: boolean;
  setIsAdaptiveModalOpen: (open: boolean) => void;
  adaptiveMinutesAhead: number;
  applyAdaptivePlan: () => void;
  activeWorkflowStep: 'discovery' | 'modes' | 'route' | 'itinerary' | 'setup' | 'progress';
  setActiveWorkflowStep: (step: 'discovery' | 'modes' | 'route' | 'itinerary' | 'setup' | 'progress') => void;
  activeItinerary: TimeBudgetedItineraryResponse | null;
  isLoadingItinerary: boolean;
  generateTimePlan: (overrideHours?: number, overrideTarget?: string) => Promise<TimeBudgetedItineraryResponse | null>;
  fetchTransitRoute: (destinationId?: string, overrideMode?: TravelMode) => Promise<TransitRouteResponse | null>;
  fetchTripPlan: (targetId?: string, overrideHours?: number, overrideMode?: TravelMode) => Promise<TripPlanResponse | null>;
  recalibrateTrip: (completedStepIndex: number, timeDeltaMinutes: number) => Promise<TripPlanResponse | null>;
  isSoundEnabled: boolean;
  toggleSoundEnabled: () => void;
  playTimerChime: () => void;
  isWalkthroughOpen: boolean;
  openWalkthrough: () => void;
  closeWalkthrough: () => void;
  activeWalkthroughStep: number;
  nextWalkthroughStep: () => void;
  prevWalkthroughStep: () => void;
  setWalkthroughStep: (step: number) => void;
  requestGeolocation: () => Promise<void>;
  locationError: string | null;
}

const TripContext = createContext<TripContextType | undefined>(undefined);

export const TripProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [currentLocation, setCurrentLocation] = useState<LocationInfo>(STANDARD_HUBS[0]);
  const [selectedPlaceId, setSelectedPlaceId] = useState<string>('kawaguchiko_oishi_park');
  const [selectedPlaceName, setSelectedPlaceName] = useState<string>('Oishi Park');
  const [travelMode, setTravelMode] = useState<TravelMode>('fujikyu_bus');
  const [discoveryView, setDiscoveryView] = useState<'recommended' | 'catalogue'>('catalogue');
  const [activeRouteData, setActiveRouteData] = useState<TransitRouteResponse | null>(null);
  const [activePlanData, setActivePlanData] = useState<TripPlanResponse | null>(null);
  const [timeBudgetHours, setTimeBudgetHours] = useState<number>(5.0);
  const [departureTime, setDepartureTime] = useState<string>('09:30');
  const [adultCount, setAdultCount] = useState<number>(1);
  const [childCount, setChildCount] = useState<number>(0);
  const [userHasJrPass, setUserHasJrPass] = useState<boolean>(false);
  const [preferQuiet, setPreferQuiet] = useState<boolean>(true);
  const [foodExperience, setFoodExperience] = useState<string>('local');
  const [foodStyles, setFoodStyles] = useState<string[]>(['Hoto noodles', 'Soba']);
  const [activeTransitModalStep, setActiveTransitModalStep] = useState<any | null>(null);
  const [isTransitModalOpen, setIsTransitModalOpen] = useState<boolean>(false);
  const [isTripProgressActive, setIsTripProgressActive] = useState<boolean>(false);
  const [completedStepIndices, setCompletedStepIndices] = useState<number[]>([]);
  const [isAdaptiveModalOpen, setIsAdaptiveModalOpen] = useState<boolean>(false);
  const [adaptiveMinutesAhead, setAdaptiveMinutesAhead] = useState<number>(40);
  const [activeWorkflowStep, setActiveWorkflowStep] = useState<
    'discovery' | 'modes' | 'route' | 'itinerary' | 'setup' | 'progress'
  >('discovery');

  const [isSoundEnabled, setIsSoundEnabled] = useState<boolean>(() => {
    return localStorage.getItem('fujinova_sound_enabled') !== 'false';
  });

  const toggleSoundEnabled = useCallback(() => {
    setIsSoundEnabled((prev) => {
      const next = !prev;
      localStorage.setItem('fujinova_sound_enabled', String(next));
      return next;
    });
  }, []);

  const playTimerChime = useCallback(() => {
    if (!isSoundEnabled) return;
    try {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      if (!AudioCtx) return;
      const ctx = new AudioCtx();
      const now = ctx.currentTime;
      // Gentle dual-tone chime (523.25 Hz C5 -> 659.25 Hz E5)
      const osc1 = ctx.createOscillator();
      const osc2 = ctx.createOscillator();
      const gain = ctx.createGain();

      osc1.type = 'sine';
      osc1.frequency.setValueAtTime(523.25, now);
      osc1.frequency.exponentialRampToValueAtTime(659.25, now + 0.3);

      osc2.type = 'triangle';
      osc2.frequency.setValueAtTime(783.99, now);

      gain.gain.setValueAtTime(0.2, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 1.2);

      osc1.connect(gain);
      osc2.connect(gain);
      gain.connect(ctx.destination);

      osc1.start(now);
      osc2.start(now);
      osc1.stop(now + 1.2);
      osc2.stop(now + 1.2);
    } catch (e) {
      console.warn('Audio chime playback failed:', e);
    }
  }, [isSoundEnabled]);

  const toggleFoodStyle = useCallback((style: string) => {
    setFoodStyles((prev) =>
      prev.includes(style) ? prev.filter((s) => s !== style) : [...prev, style]
    );
  }, []);

  const markStepCompleted = useCallback((index: number, actualMinutes?: number) => {
    setCompletedStepIndices((prev) => (prev.includes(index) ? prev : [...prev, index]));
    if (actualMinutes !== undefined) {
      const plannedMinutes = 60;
      const diff = plannedMinutes - actualMinutes;
      if (diff > 0) {
        setAdaptiveMinutesAhead(diff);
        setIsAdaptiveModalOpen(true);
      }
    } else {
      setAdaptiveMinutesAhead(40);
      setIsAdaptiveModalOpen(true);
    }
  }, []);

  const applyAdaptivePlan = useCallback(() => {
    setIsAdaptiveModalOpen(false);
    setIsTripProgressActive(true);
    setActiveWorkflowStep('itinerary');
  }, []);
  const [activeItinerary, setActiveItinerary] = useState<TimeBudgetedItineraryResponse | null>(null);
  const [isLoadingItinerary, setIsLoadingItinerary] = useState<boolean>(false);
  const [isWalkthroughOpen, setIsWalkthroughOpen] = useState<boolean>(false);
  const [activeWalkthroughStep, setActiveWalkthroughStep] = useState<number>(0);
  const [locationError, setLocationError] = useState<string | null>(null);

  const setSelectedPlace = useCallback((id: string, name?: string) => {
    setSelectedPlaceId(id);
    if (name) setSelectedPlaceName(name);
  }, []);

  const calculateDistanceKm = (lat1: number, lon1: number, lat2: number, lon2: number) => {
    const R = 6371;
    const dLat = ((lat2 - lat1) * Math.PI) / 180;
    const dLon = ((lon2 - lon1) * Math.PI) / 180;
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos((lat1 * Math.PI) / 180) *
        Math.cos((lat2 * Math.PI) / 180) *
        Math.sin(dLon / 2) *
        Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  };

  const requestGeolocation = async () => {
    setLocationError(null);
    if (!navigator.geolocation) {
      setLocationError('Geolocation is not supported by your browser.');
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const userLat = pos.coords.latitude;
        const userLon = pos.coords.longitude;
        const distFromFuji = calculateDistanceKm(
          userLat,
          userLon,
          MOUNT_FUJI_CENTER.lat,
          MOUNT_FUJI_CENTER.lon
        );

        const isOutside = distFromFuji > 55.0; // Outside Fuji Five Lakes service boundary

        setCurrentLocation({
          name: isOutside
            ? `Your Location (${distFromFuji.toFixed(0)} km from Mount Fuji)`
            : 'Your Current GPS Location (Mount Fuji Region)',
          lat: userLat,
          lon: userLon,
          isGps: true,
          isOutsideRegion: isOutside,
        });
      },
      (err) => {
        console.warn('Geolocation permission denied or unavailable:', err.message);
        setLocationError('Location access was denied or timed out. Defaulted to Kawaguchiko Station.');
        setCurrentLocation(STANDARD_HUBS[0]);
      },
      { timeout: 8000, enableHighAccuracy: true }
    );
  };

  const generateTimePlan = async (overrideHours?: number, overrideTarget?: string) => {
    const hours = overrideHours ?? timeBudgetHours;
    const target = overrideTarget ?? selectedPlaceId;
    setIsLoadingItinerary(true);

    try {
      const payload = {
        start_location: currentLocation.isOutsideRegion ? 'Kawaguchiko Station' : currentLocation.name,
        target_place_id: target,
        available_hours: hours,
        departure_time: `${departureTime}:00`,
        party_composition: 'couple',
        adult_count: adultCount,
        child_count: childCount,
        user_has_jr_pass: userHasJrPass,
        prefer_quiet: preferQuiet,
      };

      let res = await fetch(apiUrl('/api/v1/itinerary/time-budget'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        res = await fetch(apiUrl('/api/itinerary/time-budget'), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
      }

      if (res.ok) {
        const data: TimeBudgetedItineraryResponse = await res.json();
        setActiveItinerary(data);
        setActiveWalkthroughStep(0);
        setIsLoadingItinerary(false);
        return data;
      }
    } catch (err) {
      console.error('Failed to generate time-budgeted itinerary:', err);
    } finally {
      setIsLoadingItinerary(false);
    }
    return null;
  };

  const fetchTransitRoute = async (
    destinationId?: string,
    overrideMode?: TravelMode
  ): Promise<TransitRouteResponse | null> => {
    const target = destinationId ?? selectedPlaceId;
    const mode = overrideMode ?? travelMode;
    try {
      const res = await fetch(apiUrl('/api/v1/discovery/route'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          origin_name: currentLocation.name,
          destination_id: target,
          mode: mode,
          departure_time: departureTime,
        }),
      });
      if (res.ok) {
        const data: TransitRouteResponse = await res.json();
        setActiveRouteData(data);
        return data;
      }
    } catch (err) {
      console.error('Failed to fetch transit route:', err);
    }
    return null;
  };

  const fetchTripPlan = async (
    targetId?: string,
    overrideHours?: number,
    overrideMode?: TravelMode
  ): Promise<TripPlanResponse | null> => {
    const target = targetId ?? selectedPlaceId;
    const hours = overrideHours ?? timeBudgetHours;
    const mode = overrideMode ?? travelMode;
    try {
      const res = await fetch(apiUrl('/api/v1/trip/plan'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          start_location: currentLocation.name,
          target_place_id: target,
          available_hours: hours,
          departure_time: departureTime,
          travel_mode: mode,
          food_preference: foodExperience,
          food_styles: foodStyles,
        }),
      });
      if (res.ok) {
        const data: TripPlanResponse = await res.json();
        setActivePlanData(data);
        return data;
      }
    } catch (err) {
      console.error('Failed to fetch trip plan:', err);
    }
    return null;
  };

  const recalibrateTrip = async (
    completedStepIndex: number,
    timeDeltaMinutes: number
  ): Promise<TripPlanResponse | null> => {
    try {
      const res = await fetch(apiUrl('/api/v1/trip/recalibrate'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          original_plan: activePlanData,
          completed_step_index: completedStepIndex,
          time_delta_minutes: timeDeltaMinutes,
        }),
      });
      if (res.ok) {
        const data: TripPlanResponse = await res.json();
        setActivePlanData(data);
        return data;
      }
    } catch (err) {
      console.error('Failed to recalibrate trip:', err);
    }
    return null;
  };

  const openWalkthrough = () => setIsWalkthroughOpen(true);
  const closeWalkthrough = () => setIsWalkthroughOpen(false);

  const nextWalkthroughStep = () => {
    if (activeItinerary && activeWalkthroughStep < activeItinerary.steps.length - 1) {
      setActiveWalkthroughStep((prev) => prev + 1);
    }
  };

  const prevWalkthroughStep = () => {
    if (activeWalkthroughStep > 0) {
      setActiveWalkthroughStep((prev) => prev - 1);
    }
  };

  return (
    <TripContext.Provider
      value={{
        currentLocation,
        setCurrentLocation,
        selectedPlaceId,
        selectedPlaceName,
        setSelectedPlace,
        travelMode,
        setTravelMode,
        discoveryView,
        setDiscoveryView,
        activeRouteData,
        setActiveRouteData,
        activePlanData,
        setActivePlanData,
        timeBudgetHours,
        setTimeBudgetHours,
        departureTime,
        setDepartureTime,
        adultCount,
        setAdultCount,
        childCount,
        setChildCount,
        userHasJrPass,
        setUserHasJrPass,
        preferQuiet,
        setPreferQuiet,
        foodExperience,
        setFoodExperience,
        foodStyles,
        toggleFoodStyle,
        activeTransitModalStep,
        setActiveTransitModalStep,
        isTransitModalOpen,
        setIsTransitModalOpen,
        isTripProgressActive,
        setIsTripProgressActive,
        completedStepIndices,
        markStepCompleted,
        isAdaptiveModalOpen,
        setIsAdaptiveModalOpen,
        adaptiveMinutesAhead,
        applyAdaptivePlan,
        activeWorkflowStep,
        setActiveWorkflowStep,
        activeItinerary,
        isLoadingItinerary,
        generateTimePlan,
        fetchTransitRoute,
        fetchTripPlan,
        recalibrateTrip,
        isSoundEnabled,
        toggleSoundEnabled,
        playTimerChime,
        isWalkthroughOpen,
        openWalkthrough,
        closeWalkthrough,
        activeWalkthroughStep,
        nextWalkthroughStep,
        prevWalkthroughStep,
        setWalkthroughStep: setActiveWalkthroughStep,
        requestGeolocation,
        locationError,
      }}
    >
      {children}
    </TripContext.Provider>
  );
};

const defaultTripState: TripContextType = {
  currentLocation: {
    lat: 35.4981,
    lon: 138.7690,
    name: 'Kawaguchiko Station (Main Hub)',
    isGps: false,
    isOutsideRegion: false,
  },
  setCurrentLocation: () => {},
  selectedPlaceId: 'kawaguchiko_oishi_park',
  selectedPlaceName: 'Oishi Park (Lake Kawaguchiko)',
  setSelectedPlace: () => {},
  travelMode: 'fujikyu_bus',
  setTravelMode: () => {},
  discoveryView: 'catalogue',
  setDiscoveryView: () => {},
  activeRouteData: null,
  setActiveRouteData: () => {},
  activePlanData: null,
  setActivePlanData: () => {},
  timeBudgetHours: 5.0,
  setTimeBudgetHours: () => {},
  departureTime: '09:30',
  setDepartureTime: () => {},
  adultCount: 1,
  setAdultCount: () => {},
  childCount: 0,
  setChildCount: () => {},
  userHasJrPass: false,
  setUserHasJrPass: () => {},
  preferQuiet: true,
  setPreferQuiet: () => {},
  foodExperience: 'local',
  setFoodExperience: () => {},
  foodStyles: ['Hoto noodles', 'Soba'],
  toggleFoodStyle: () => {},
  activeTransitModalStep: null,
  setActiveTransitModalStep: () => {},
  isTransitModalOpen: false,
  setIsTransitModalOpen: () => {},
  isTripProgressActive: false,
  setIsTripProgressActive: () => {},
  completedStepIndices: [],
  markStepCompleted: () => {},
  isAdaptiveModalOpen: false,
  setIsAdaptiveModalOpen: () => {},
  adaptiveMinutesAhead: 40,
  applyAdaptivePlan: () => {},
  activeWorkflowStep: 'discovery',
  setActiveWorkflowStep: () => {},
  activeItinerary: null,
  isLoadingItinerary: false,
  generateTimePlan: async () => null,
  fetchTransitRoute: async () => null,
  fetchTripPlan: async () => null,
  recalibrateTrip: async () => null,
  isSoundEnabled: true,
  toggleSoundEnabled: () => {},
  playTimerChime: () => {},
  isWalkthroughOpen: false,
  openWalkthrough: () => {},
  closeWalkthrough: () => {},
  activeWalkthroughStep: 1,
  nextWalkthroughStep: () => {},
  prevWalkthroughStep: () => {},
  setWalkthroughStep: () => {},
  requestGeolocation: async () => {},
  locationError: null,
};

export const useTrip = () => {
  const context = useContext(TripContext);
  return context || defaultTripState;
};

import React, { createContext, useContext, useState, ReactNode, useCallback } from 'react';
import { TimeBudgetedItineraryResponse } from '../types';
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
    name: 'Otsuki Station (JR & Fujikyu Junction)',
    lat: 35.6133,
    lon: 138.9422,
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
  activeItinerary: TimeBudgetedItineraryResponse | null;
  isLoadingItinerary: boolean;
  generateTimePlan: (overrideHours?: number, overrideTarget?: string) => Promise<TimeBudgetedItineraryResponse | null>;
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
  const [timeBudgetHours, setTimeBudgetHours] = useState<number>(5.0);
  const [departureTime, setDepartureTime] = useState<string>('09:30');
  const [adultCount, setAdultCount] = useState<number>(1);
  const [childCount, setChildCount] = useState<number>(0);
  const [userHasJrPass, setUserHasJrPass] = useState<boolean>(false);
  const [preferQuiet, setPreferQuiet] = useState<boolean>(true);
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
        activeItinerary,
        isLoadingItinerary,
        generateTimePlan,
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
  activeItinerary: null,
  isLoadingItinerary: false,
  generateTimePlan: async () => null,
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

import React, { useState } from 'react';
import { useTrip, STANDARD_HUBS } from '../context/TripContext';
import { 
  MapPin, 
  Clock, 
  Navigation, 
  Sparkles, 
  AlertTriangle, 
  CreditCard,
  CheckCircle2,
  ChevronDown
} from 'lucide-react';

interface TravelOnboardingBarProps {
  onAskHana?: (prompt: string) => void;
}

export const TravelOnboardingBar: React.FC<TravelOnboardingBarProps> = ({ onAskHana }) => {
  const {
    currentLocation,
    setCurrentLocation,
    selectedPlaceName,
    timeBudgetHours,
    setTimeBudgetHours,
    departureTime,
    setDepartureTime,
    userHasJrPass,
    setUserHasJrPass,
    requestGeolocation,
    generateTimePlan,
    isLoadingItinerary,
    openWalkthrough,
    activeItinerary
  } = useTrip();

  const [isHubDropdownOpen, setIsHubDropdownOpen] = useState(false);

  const handleGenerate = async () => {
    const plan = await generateTimePlan();
    if (plan) {
      openWalkthrough();
      if (onAskHana) {
        onAskHana(`I have ${timeBudgetHours} hours starting from ${currentLocation.name} to visit ${selectedPlaceName}. Explain my schedule and transit pass options.`);
      }
    }
  };

  const hourOptions = [1, 2, 3, 4, 5, 6, 8];

  return (
    <div className="bg-white rounded-2xl border border-[#E1EAF1] p-5 shadow-xs mb-6 space-y-4">
      {/* Top Banner: Step 1 & 2 Travel Prompt */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 pb-3 border-b border-[#E1EAF1]">
        <div>
          <span className="text-[10px] font-bold text-[#078ACB] uppercase tracking-wider bg-[#EBF5FB] px-2 py-0.5 rounded border border-[#BDE0F5]">
            AI Travel Companion • Time-Budget Intelligence
          </span>
          <h2 className="text-base font-bold text-[#14283F] mt-1">
            Where are you now & how much time do you have?
          </h2>
        </div>

        {activeItinerary && (
          <button
            onClick={openWalkthrough}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-semibold hover:bg-emerald-100 transition-colors shadow-2xs self-start md:self-auto"
          >
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
            <span>Active Walkthrough ({activeItinerary.total_duration_minutes} min)</span>
          </button>
        )}
      </div>

      {/* Outside Region Advisory Banner (if applicable) */}
      {currentLocation.isOutsideRegion && (
        <div className="flex items-start gap-2.5 p-3 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs">
          <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
          <div className="space-y-0.5">
            <span className="font-bold block">Regional Service Boundary Notice:</span>
            <p className="text-amber-800 leading-relaxed">
              You are currently outside FujiNova’s Fujikyu regional transport area ({currentLocation.name}).
              We are automatically planning your journey starting from our central transit hub at <strong>Kawaguchiko Station</strong>.
            </p>
          </div>
        </div>
      )}

      {/* Interactive Controls Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-12 gap-3.5 items-end">
        {/* 1. Location Selector (4 cols) */}
        <div className="lg:col-span-4 space-y-1.5">
          <label className="text-xs font-bold text-[#425466] flex items-center justify-between">
            <span className="flex items-center gap-1">
              <MapPin className="w-3.5 h-3.5 text-[#078ACB]" />
              <span>Starting Location</span>
            </span>
            <button
              onClick={requestGeolocation}
              className="text-[10px] text-[#078ACB] hover:underline font-semibold flex items-center gap-0.5"
            >
              <Navigation className="w-2.5 h-2.5" />
              <span>Use GPS</span>
            </button>
          </label>

          <div className="relative">
            <button
              onClick={() => setIsHubDropdownOpen(!isHubDropdownOpen)}
              className="w-full h-10 px-3 rounded-xl border border-[#E1EAF1] bg-[#F5F8FB] hover:bg-white text-xs font-medium text-[#14283F] flex items-center justify-between transition-colors shadow-2xs"
            >
              <span className="truncate">{currentLocation.name}</span>
              <ChevronDown className="w-3.5 h-3.5 text-[#718198] shrink-0" />
            </button>

            {isHubDropdownOpen && (
              <div className="absolute left-0 right-0 top-11 bg-white border border-[#E1EAF1] rounded-xl shadow-lg z-30 py-1 max-h-56 overflow-y-auto">
                {STANDARD_HUBS.map((hub) => (
                  <button
                    key={hub.name}
                    onClick={() => {
                      setCurrentLocation(hub);
                      setIsHubDropdownOpen(false);
                    }}
                    className={`w-full px-3 py-2 text-left text-xs hover:bg-[#F5F8FB] transition-colors flex items-center justify-between ${
                      currentLocation.name === hub.name ? 'text-[#078ACB] font-bold bg-[#EBF5FB]' : 'text-[#14283F]'
                    }`}
                  >
                    <span>{hub.name}</span>
                    {hub.isOutsideRegion && (
                      <span className="text-[10px] bg-slate-100 text-slate-500 px-1.5 py-0.5 rounded">
                        Outside
                      </span>
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* 2. Time Budget Selector (4 cols) */}
        <div className="lg:col-span-4 space-y-1.5">
          <label className="text-xs font-bold text-[#425466] flex items-center gap-1">
            <Clock className="w-3.5 h-3.5 text-[#078ACB]" />
            <span>Trip Time Budget</span>
          </label>
          <div className="flex items-center gap-1 bg-[#F5F8FB] p-1 rounded-xl border border-[#E1EAF1] h-10">
            {hourOptions.map((h) => (
              <button
                key={h}
                onClick={() => setTimeBudgetHours(h)}
                className={`flex-1 h-8 rounded-lg text-xs font-bold transition-all ${
                  timeBudgetHours === h
                    ? 'bg-[#078ACB] text-white shadow-xs'
                    : 'text-[#718198] hover:text-[#14283F] hover:bg-white/60'
                }`}
              >
                {h}h
              </button>
            ))}
          </div>
        </div>

        {/* 3. Departure Time & JR Pass (2 cols) */}
        <div className="lg:col-span-2 space-y-1.5">
          <label className="text-xs font-bold text-[#425466] block">Departure</label>
          <input
            type="time"
            value={departureTime}
            onChange={(e) => setDepartureTime(e.target.value)}
            className="w-full h-10 px-3 rounded-xl border border-[#E1EAF1] bg-[#F5F8FB] text-xs font-medium text-[#14283F] focus:outline-hidden focus:border-[#078ACB]"
          />
        </div>

        {/* 4. Action Button (2 cols) */}
        <div className="lg:col-span-2">
          <button
            onClick={handleGenerate}
            disabled={isLoadingItinerary}
            className="w-full h-10 flex items-center justify-center gap-1.5 px-3 rounded-xl bg-[#00875A] hover:bg-[#006644] text-white text-xs font-bold shadow-xs transition-colors disabled:opacity-50"
          >
            <Sparkles className="w-3.5 h-3.5 text-white" />
            <span>{isLoadingItinerary ? 'Planning...' : 'Plan Journey'}</span>
          </button>
        </div>
      </div>

      {/* Bottom Sub-Row: JR Pass Option & Target Destination Reminder */}
      <div className="flex flex-wrap items-center justify-between gap-3 pt-2 text-xs text-[#718198]">
        <label className="flex items-center gap-2 cursor-pointer select-none">
          <input
            type="checkbox"
            checked={userHasJrPass}
            onChange={(e) => setUserHasJrPass(e.target.checked)}
            className="w-3.5 h-3.5 rounded text-[#078ACB] focus:ring-0 border-slate-300"
          />
          <CreditCard className="w-3.5 h-3.5 text-slate-400" />
          <span className="text-[11px] text-[#425466]">
            I have a Japan Rail Pass (JR Pass)
          </span>
        </label>

        <div className="text-[11px] text-[#425466]">
          Target Destination: <strong className="text-[#078ACB]">{selectedPlaceName}</strong>
        </div>
      </div>
    </div>
  );
};

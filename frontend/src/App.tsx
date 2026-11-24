import React, { useState, useEffect } from 'react';
import { DiscoverView } from './components/DiscoverView';
import { HanaWorkspace } from './components/HanaWorkspace';
import { DigitalTwin3D } from './components/DigitalTwin3D';
import { LiveRegionMap } from './components/LiveRegionMap';
import { YourJourneyPanel } from './components/YourJourneyPanel';
import { TravelIntelligenceView } from './components/TravelIntelligenceView';
import { MyTravelView } from './components/MyTravelView';
import { ProfileSettingsView } from './components/ProfileSettingsView';

import { TravellerProfile, ItineraryPlan } from './types';
import { apiUrl } from './config';
import { 
  Mountain, 
  Sparkles, 
  Compass, 
  Navigation, 
  Activity, 
  Wallet, 
  Settings
} from 'lucide-react';

export type WorkspaceTab = 
  | 'discover' 
  | 'hana' 
  | 'twin' 
  | 'journey' 
  | 'intelligence' 
  | 'mytravel' 
  | 'settings';

export const App: React.FC = () => {
  // Persist current active session ID
  const [sessionId, setSessionId] = useState<string>(() => {
    return localStorage.getItem('fujinova_active_session') || `fn_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`;
  });

  const [activeTab, setActiveTab] = useState<WorkspaceTab>('discover');
  const [_profile, setProfile] = useState<TravellerProfile>({});
  const [itinerary, setItinerary] = useState<ItineraryPlan | null>(null);
  const [externalPrompt, setExternalPrompt] = useState<string | undefined>(undefined);
  const [selectedPlaceId, setSelectedPlaceId] = useState<string | null>(null);
  const [health, setHealth] = useState<{ status: string; primary_model: string } | null>(null);
  const [twinMode2D, setTwinMode2D] = useState(false);

  // Sync session ID to localStorage
  useEffect(() => {
    localStorage.setItem('fujinova_active_session', sessionId);
  }, [sessionId]);

  // System Health Check
  useEffect(() => {
    const checkHealth = async () => {
      try {
        let res = await fetch(apiUrl('/health'));
        if (!res.ok) res = await fetch(apiUrl('/api/v1/health'));
        if (res.ok) {
          const data = await res.json();
          setHealth(data);
        } else {
          setHealth({ status: 'offline', primary_model: 'gpt-4o-mini' });
        }
      } catch (_) {
        setHealth({ status: 'offline', primary_model: 'gpt-4o-mini' });
      }
    };
    checkHealth();
  }, []);

  const handleAskHana = (prompt: string) => {
    setExternalPrompt(prompt);
    setActiveTab('hana');
  };

  const handleRemoveStop = (dayNumber: number, stopIndex: number) => {
    if (!itinerary) return;
    const newDays = itinerary.days.map((d) => {
      if (d.day_number === dayNumber) {
        const newStops = [...d.stops];
        newStops.splice(stopIndex, 1);
        return { ...d, stops: newStops };
      }
      return d;
    });
    setItinerary({ ...itinerary, days: newDays });
  };

  const handleReorderStop = (dayNumber: number, stopIndex: number, direction: 'up' | 'down') => {
    if (!itinerary) return;
    const newDays = itinerary.days.map((d) => {
      if (d.day_number === dayNumber) {
        const newStops = [...d.stops];
        const targetIndex = direction === 'up' ? stopIndex - 1 : stopIndex + 1;
        if (targetIndex >= 0 && targetIndex < newStops.length) {
          const temp = newStops[stopIndex];
          newStops[stopIndex] = newStops[targetIndex];
          newStops[targetIndex] = temp;
        }
        return { ...d, stops: newStops };
      }
      return d;
    });
    setItinerary({ ...itinerary, days: newDays });
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans select-none antialiased">
      {/* Top Header Navigation */}
      <header className="bg-slate-900/95 backdrop-blur-md border-b border-slate-800 sticky top-0 z-40">
        <div className="max-w-[1920px] mx-auto px-4 h-14 flex items-center justify-between gap-4">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <button 
              onClick={() => setActiveTab('discover')}
              className="flex items-center gap-2.5 font-black text-white tracking-tight text-lg hover:opacity-90 transition-opacity"
            >
              <span className="w-8 h-8 rounded-lg bg-gradient-to-tr from-sky-600 to-indigo-600 text-white flex items-center justify-center shadow-md">
                <Mountain className="w-5 h-5" />
              </span>
              <span className="hidden sm:inline">FujiNova</span>
            </button>
            <span className="text-[10px] font-bold text-sky-300 bg-sky-500/20 border border-sky-500/30 px-1.5 py-0.5 rounded uppercase tracking-wider">
              5.0
            </span>
          </div>

          {/* 7 Primary Workspace Tabs */}
          <nav className="flex items-center gap-1 bg-slate-950/80 p-1 rounded-xl border border-slate-800/80 overflow-x-auto max-w-full">
            <button
              onClick={() => setActiveTab('discover')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all shrink-0 ${
                activeTab === 'discover'
                  ? 'bg-sky-600 text-white shadow-xs'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              <span>Discover</span>
            </button>

            <button
              onClick={() => setActiveTab('hana')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all shrink-0 ${
                activeTab === 'hana'
                  ? 'bg-sky-600 text-white shadow-xs'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              <Sparkles className="w-3.5 h-3.5 text-sky-400" />
              <span>Hana AI</span>
            </button>

            <button
              onClick={() => setActiveTab('twin')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all shrink-0 ${
                activeTab === 'twin'
                  ? 'bg-sky-600 text-white shadow-xs'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              <Compass className="w-3.5 h-3.5 text-sky-400" />
              <span>3D Digital Twin</span>
            </button>

            <button
              onClick={() => setActiveTab('journey')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all shrink-0 ${
                activeTab === 'journey'
                  ? 'bg-sky-600 text-white shadow-xs'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              <Navigation className="w-3.5 h-3.5 text-emerald-400" />
              <span>Journey Planner</span>
              {itinerary && (
                <span className="w-2 h-2 rounded-full bg-emerald-400 inline-block" />
              )}
            </button>

            <button
              onClick={() => setActiveTab('intelligence')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all shrink-0 ${
                activeTab === 'intelligence'
                  ? 'bg-sky-600 text-white shadow-xs'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              <Activity className="w-3.5 h-3.5 text-amber-400" />
              <span>Travel Intelligence</span>
            </button>

            <button
              onClick={() => setActiveTab('mytravel')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all shrink-0 ${
                activeTab === 'mytravel'
                  ? 'bg-sky-600 text-white shadow-xs'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              <Wallet className="w-3.5 h-3.5 text-purple-400" />
              <span>My Travel</span>
            </button>

            <button
              onClick={() => setActiveTab('settings')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all shrink-0 ${
                activeTab === 'settings'
                  ? 'bg-sky-600 text-white shadow-xs'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              <Settings className="w-3.5 h-3.5 text-slate-400" />
              <span>Settings</span>
            </button>
          </nav>

          {/* Model Status Indicator */}
          <div className="hidden lg:flex items-center gap-3 shrink-0">
            <div className="flex items-center gap-1.5 text-xs text-slate-300 bg-slate-800 border border-slate-700 px-2.5 py-1 rounded-lg">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="font-mono text-[11px] font-medium">
                {health?.primary_model || 'gpt-4o-mini'}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Workspace Display Container */}
      <div className="flex-1 overflow-hidden relative">
        {activeTab === 'discover' && (
          <DiscoverView
            onAskHana={handleAskHana}
            onExplore3D={() => setActiveTab('twin')}
            onPlanTrip={() => setActiveTab('journey')}
            onSelectPlace={(pid) => setSelectedPlaceId(pid)}
          />
        )}

        {activeTab === 'hana' && (
          <HanaWorkspace
            currentSessionId={sessionId}
            onSelectSession={(sid) => setSessionId(sid)}
            onItineraryUpdated={(itin) => setItinerary(itin)}
            onProfileUpdated={(p) => setProfile(p)}
            activeModel={health?.primary_model || 'gpt-4o-mini'}
            externalPrompt={externalPrompt}
          />
        )}

        {activeTab === 'twin' && (
          twinMode2D ? (
            <div className="h-full flex flex-col">
              <div className="p-2 bg-slate-900 border-b border-slate-800 flex justify-between items-center px-4">
                <span className="text-xs text-slate-300 font-semibold">Accessible 2D Vector Map</span>
                <button
                  onClick={() => setTwinMode2D(false)}
                  className="px-3 py-1 rounded-lg bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold"
                >
                  Switch to 3D Digital Twin
                </button>
              </div>
              <div className="flex-1">
                <LiveRegionMap
                  onAskHana={handleAskHana}
                  onSelectPlace={(pid) => setSelectedPlaceId(pid)}
                  selectedPlaceId={selectedPlaceId}
                />
              </div>
            </div>
          ) : (
            <DigitalTwin3D
              onAskHana={handleAskHana}
              onSelectPlace={(pid) => setSelectedPlaceId(pid)}
              selectedPlaceId={selectedPlaceId}
              onSwitchTo2D={() => setTwinMode2D(true)}
            />
          )
        )}

        {activeTab === 'journey' && (
          <div className="h-full max-w-5xl mx-auto p-4 sm:p-6 lg:p-8">
            <YourJourneyPanel
              itinerary={itinerary}
              onAskHana={handleAskHana}
              onRemoveStop={handleRemoveStop}
              onReorderStop={handleReorderStop}
            />
          </div>
        )}

        {activeTab === 'intelligence' && (
          <TravelIntelligenceView onAskHana={handleAskHana} />
        )}

        {activeTab === 'mytravel' && (
          <MyTravelView onAskHana={handleAskHana} />
        )}

        {activeTab === 'settings' && (
          <ProfileSettingsView activeModel={health?.primary_model || 'gpt-4o-mini'} />
        )}
      </div>
    </div>
  );
};

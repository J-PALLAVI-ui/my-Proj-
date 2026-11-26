import React, { useState, useEffect } from 'react';
import { AppHeader } from './components/AppHeader';
import { CrowdSenseDashboard } from './components/CrowdSenseDashboard';
import { HanaChatSidebar } from './components/HanaChatSidebar';
import { PlacesGrid } from './components/PlacesGrid';
import { DigitalTwin3D } from './components/DigitalTwin3D';
import { LiveRegionMap } from './components/LiveRegionMap';
import { TripProvider, useTrip } from './context/TripContext';
import { apiUrl } from './config';

const MainAppContent: React.FC = () => {
  const { selectedPlaceId, setSelectedPlace } = useTrip();
  const [activeView, setActiveView] = useState<'crowd' | 'places' | 'twin'>('crowd');
  const [isTwin2DMode, setIsTwin2DMode] = useState<boolean>(false);
  const [isHanaVisible, setIsHanaVisible] = useState<boolean>(true);
  const [sessionId] = useState<string>(() => {
    return (
      localStorage.getItem('fujinova_active_session') ||
      `fn_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`
    );
  });
  const [health, setHealth] = useState<{ status: string; primary_model: string } | null>(null);
  const [placesStats, setPlacesStats] = useState<{ total_destinations: number; famous_destinations: number; hidden_gems: number }>({
    total_destinations: 237,
    famous_destinations: 136,
    hidden_gems: 101,
  });
  const [externalPrompt, setExternalPrompt] = useState<string | undefined>(undefined);

  // Sync active session
  useEffect(() => {
    localStorage.setItem('fujinova_active_session', sessionId);
  }, [sessionId]);

  // System Health & Catalogue Stats Check
  useEffect(() => {
    const checkHealth = async () => {
      try {
        let res = await fetch(apiUrl('/health'));
        if (!res.ok) res = await fetch(apiUrl('/api/v1/health'));
        if (res.ok) {
          const data = await res.json();
          setHealth(data);
        } else {
          setHealth({ status: 'offline', primary_model: 'gemini-3.8-flash' });
        }
      } catch (_) {
        setHealth({ status: 'offline', primary_model: 'gemini-3.8-flash' });
      }
    };

    const fetchStats = async () => {
      try {
        const res = await fetch(apiUrl('/api/v1/places/stats'));
        if (res.ok) {
          const stats = await res.json();
          if (stats.total_destinations) {
            setPlacesStats({
              total_destinations: stats.total_destinations,
              famous_destinations: stats.famous_destinations,
              hidden_gems: stats.hidden_gems,
            });
          }
        }
      } catch (_) {}
    };

    checkHealth();
    fetchStats();
  }, []);

  const handleAskHana = (prompt: string) => {
    setExternalPrompt(prompt);
    if (!isHanaVisible) setIsHanaVisible(true);
  };

  return (
    <div className="min-h-screen bg-[#F5F8FB] text-[#14283F] flex flex-col font-sans antialiased">
      {/* 1. Header (Matches Image 1) */}
      <AppHeader
        activeView={activeView}
        onNavigate={(view) => setActiveView(view)}
        activeModel={health?.primary_model || 'gemini-3.8-flash'}
        isHanaVisible={isHanaVisible}
        onToggleHana={() => setIsHanaVisible(!isHanaVisible)}
      />

      {/* 2. Main Two-Column Layout (73% Left Workspace + 27% Right Hana Sidebar) */}
      <div className="flex-1 flex overflow-hidden max-w-[1920px] w-full mx-auto">
        {/* Left Main Workspace (approx 73% width on desktop, scrolls independently) */}
        <main
          className={`flex-1 overflow-y-auto px-4 sm:px-8 py-6 transition-all duration-200 ${
            isHanaVisible ? 'w-full lg:w-[73%]' : 'w-full'
          }`}
        >
          {activeView === 'crowd' ? (
            <CrowdSenseDashboard onAskHana={handleAskHana} />
          ) : activeView === 'twin' ? (
            <div className="space-y-4 pb-12">
              <div className="bg-white p-5 rounded-2xl border border-[#E1EAF1] shadow-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                <div>
                  <h1 className="text-xl font-bold text-[#14283F] flex items-center gap-2">
                    <span>Mount Fuji & Five Lakes 3D Digital Twin</span>
                    <span className="text-[10px] font-bold text-sky-700 bg-sky-50 border border-sky-200 px-2 py-0.5 rounded-full uppercase">
                      Spatial GIS & GTFS-JP
                    </span>
                  </h1>
                  <p className="text-xs text-[#718198] mt-1">
                    Real Three.js 3D simulation with authentic Mount Fuji elevation model, lake bathymetry, {placesStats.total_destinations} verified landmarks ({placesStats.famous_destinations} famous • {placesStats.hidden_gems} hidden gems), and Fujikyu Railway transit nodes.
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setIsTwin2DMode(false)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                      !isTwin2DMode
                        ? 'bg-[#078ACB] text-white shadow-xs'
                        : 'bg-[#F5F8FB] text-[#718198] hover:text-[#14283F] border border-[#E1EAF1]'
                    }`}
                  >
                    3D Digital Twin
                  </button>
                  <button
                    onClick={() => setIsTwin2DMode(true)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                      isTwin2DMode
                        ? 'bg-[#078ACB] text-white shadow-xs'
                        : 'bg-[#F5F8FB] text-[#718198] hover:text-[#14283F] border border-[#E1EAF1]'
                    }`}
                  >
                    2D Region Map
                  </button>
                </div>
              </div>

              {isTwin2DMode ? (
                <div className="bg-white p-5 rounded-2xl border border-[#E1EAF1] shadow-xs">
                  <LiveRegionMap
                    onAskHana={handleAskHana}
                    onSelectPlace={(id) => setSelectedPlace(id)}
                    selectedPlaceId={selectedPlaceId}
                  />
                </div>
              ) : (
                <div className="bg-white p-2 rounded-2xl border border-[#E1EAF1] shadow-xs overflow-hidden">
                  <DigitalTwin3D
                    onAskHana={handleAskHana}
                    onSelectPlace={(id) => setSelectedPlace(id)}
                    selectedPlaceId={selectedPlaceId}
                    onSwitchTo2D={() => setIsTwin2DMode(true)}
                  />
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-4 pb-12">
              <div className="bg-white p-6 rounded-2xl border border-[#E1EAF1] shadow-xs">
                <h1 className="text-xl font-bold text-[#14283F]">Places Catalogue</h1>
                <p className="text-xs text-[#718198] mt-1">
                  Explore all {placesStats.total_destinations} verified destinations ({placesStats.famous_destinations} famous attractions and {placesStats.hidden_gems} serene hidden gems) across
                  Yamanashi and Mount Fuji.
                </p>
              </div>
              <PlacesGrid />
            </div>
          )}
        </main>

        {/* Right Hana Sidebar (approx 27% width on desktop, fixed height) */}
        {isHanaVisible && (
          <aside className="hidden lg:block lg:w-[27%] shrink-0 h-[calc(100vh-66px)] sticky top-[66px]">
            <HanaChatSidebar
              sessionId={sessionId}
              activeModel={health?.primary_model || 'gemini-3.8-flash'}
              externalPrompt={externalPrompt}
              onClearExternalPrompt={() => setExternalPrompt(undefined)}
              groundedPlacesCount={placesStats.total_destinations}
            />
          </aside>
        )}
      </div>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <TripProvider>
      <MainAppContent />
    </TripProvider>
  );
};

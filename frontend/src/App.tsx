import React, { useState, useEffect } from 'react';
import { AppHeader } from './components/AppHeader';
import { CrowdSenseDashboard } from './components/CrowdSenseDashboard';
import { HanaChatSidebar } from './components/HanaChatSidebar';
import { PlacesGrid } from './components/PlacesGrid';
import { apiUrl } from './config';

export const App: React.FC = () => {
  const [activeView, setActiveView] = useState<'crowd' | 'places'>('crowd');
  const [isHanaVisible, setIsHanaVisible] = useState<boolean>(true);
  const [sessionId] = useState<string>(() => {
    return (
      localStorage.getItem('fujinova_active_session') ||
      `fn_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`
    );
  });
  const [health, setHealth] = useState<{ status: string; primary_model: string } | null>(null);
  const [externalPrompt, setExternalPrompt] = useState<string | undefined>(undefined);

  // Sync active session
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
          setHealth({ status: 'offline', primary_model: 'gemini-3.8-flash' });
        }
      } catch (_) {
        setHealth({ status: 'offline', primary_model: 'gemini-3.8-flash' });
      }
    };
    checkHealth();
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
          ) : (
            <div className="space-y-4 pb-12">
              <div className="bg-white p-6 rounded-2xl border border-[#E1EAF1] shadow-xs">
                <h1 className="text-xl font-bold text-[#14283F]">Places Catalogue</h1>
                <p className="text-xs text-[#718198] mt-1">
                  Explore all 35 verified destinations, temples, viewpoints, and hot springs across
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
              groundedPlacesCount={35}
            />
          </aside>
        )}
      </div>
    </div>
  );
};

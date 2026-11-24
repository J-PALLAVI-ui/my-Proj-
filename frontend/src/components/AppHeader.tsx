import React from 'react';
import { Mountain, Compass, MapPin, MessageSquare } from 'lucide-react';

interface AppHeaderProps {
  activeView: 'crowd' | 'places';
  onNavigate: (view: 'crowd' | 'places') => void;
  activeModel: string;
  isHanaVisible: boolean;
  onToggleHana: () => void;
}

export const AppHeader: React.FC<AppHeaderProps> = ({
  activeView,
  onNavigate,
  activeModel,
  isHanaVisible,
  onToggleHana,
}) => {
  return (
    <header className="bg-white border-b border-[#E1EAF1] sticky top-0 z-40 h-[66px] px-6 flex items-center justify-between shadow-xs">
      {/* Left: Brand + Navigation */}
      <div className="flex items-center gap-6">
        {/* FujiNova Logo & Brand */}
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-[#078ACB] text-white flex items-center justify-center shadow-sm">
            <Mountain className="w-5 h-5 text-white" />
          </div>
          <span className="font-bold text-[#14283F] tracking-tight text-xl font-sans">
            FujiNova
          </span>
        </div>

        {/* Navigation Items */}
        <nav className="flex items-center gap-2">
          {/* CrowdSense Engine */}
          <button
            onClick={() => onNavigate('crowd')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeView === 'crowd'
                ? 'bg-[#EBF5FB] text-[#078ACB] border border-[#BDE0F5]'
                : 'text-[#718198] hover:text-[#14283F] hover:bg-[#F5F8FB]'
            }`}
          >
            <Compass className="w-4 h-4 text-[#078ACB]" />
            <span>CrowdSense Engine</span>
            <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 rounded uppercase">
              Stage 3
            </span>
          </button>

          {/* Places Catalogue */}
          <button
            onClick={() => onNavigate('places')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeView === 'places'
                ? 'bg-[#EBF5FB] text-[#078ACB] border border-[#BDE0F5]'
                : 'text-[#718198] hover:text-[#14283F] hover:bg-[#F5F8FB]'
            }`}
          >
            <MapPin className="w-4 h-4 text-[#718198]" />
            <span>Places Catalogue</span>
          </button>
        </nav>
      </div>

      {/* Right: Model Status & Hide Hana Chat */}
      <div className="flex items-center gap-3">
        {/* Current Model Status Pill */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1 rounded-full bg-[#F5F8FB] border border-[#E1EAF1] text-xs font-medium text-[#718198]">
          <span className="w-2 h-2 rounded-full bg-emerald-500" />
          <span className="font-mono text-[11px] text-[#425466]">{activeModel}</span>
        </div>

        {/* Hide/Show Hana Chat Button */}
        <button
          onClick={onToggleHana}
          className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg border border-[#BDE0F5] bg-[#EBF5FB] text-[#078ACB] hover:bg-[#DDF0FA] transition-colors text-xs font-semibold shadow-2xs"
        >
          <MessageSquare className="w-3.5 h-3.5 text-[#078ACB]" />
          <span>{isHanaVisible ? 'Hide Hana Chat' : 'Show Hana Chat'}</span>
        </button>
      </div>
    </header>
  );
};

import React, { useState } from 'react';
import { Mountain, Compass, MapPin, MessageSquare, Globe2, Languages } from 'lucide-react';
import { useI18n } from '../i18n/I18nContext';
import { LanguageSelectorModal } from './LanguageSelectorModal';

interface AppHeaderProps {
  activeView: 'crowd' | 'places' | 'twin';
  onNavigate: (view: 'crowd' | 'places' | 'twin') => void;
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
  const { currentLocale, setLocale, totalLocalesCount, t } = useI18n();
  const [isLangModalOpen, setIsLangModalOpen] = useState(false);

  return (
    <>
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
              <span>{t('nav.crowdsense', 'CrowdSense Engine')}</span>
              <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 rounded uppercase">
                {t('nav.stage3', 'Stage 3')}
              </span>
            </button>

            {/* 3D Digital Twin */}
            <button
              onClick={() => onNavigate('twin')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeView === 'twin'
                  ? 'bg-[#EBF5FB] text-[#078ACB] border border-[#BDE0F5]'
                  : 'text-[#718198] hover:text-[#14283F] hover:bg-[#F5F8FB]'
              }`}
            >
              <Globe2 className="w-4 h-4 text-[#078ACB]" />
              <span>{t('nav.digitalTwin', '3D Digital Twin')}</span>
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
              <span>{t('nav.placesCatalogue', 'Places Catalogue')}</span>
            </button>
          </nav>
        </div>

        {/* Right: Language Framework + Model Status + Hide Hana Chat */}
        <div className="flex items-center gap-3">
          {/* 170+ Language Framework Selector (Matches Image Reference A, B, C, D) */}
          <div className="flex items-center gap-1.5 bg-[#F5F8FB] border border-[#E1EAF1] p-0.5 rounded-xl text-xs">
            <button
              onClick={() => setIsLangModalOpen(true)}
              className="flex items-center gap-1.5 px-2.5 py-1 text-slate-700 hover:text-[#078ACB] hover:bg-white rounded-lg transition-colors font-medium text-[11px]"
              title="Open full 170+ Global Locales catalog"
            >
              <Languages className="w-3.5 h-3.5 text-[#078ACB]" />
              <span className="hidden xl:inline">{totalLocalesCount}+ language framework</span>
              <span className="xl:hidden">170+ Lang</span>
            </button>

            <div className="h-3 w-px bg-slate-300" />

            {/* Quick English / Japanese Switcher Pills */}
            <button
              onClick={() => setLocale('en')}
              className={`px-2 py-0.5 rounded-md text-[11px] font-bold transition-all ${
                currentLocale === 'en'
                  ? 'bg-[#078ACB] text-white shadow-2xs'
                  : 'text-[#718198] hover:text-[#14283F]'
              }`}
            >
              English
            </button>
            <button
              onClick={() => setLocale('ja')}
              className={`px-2 py-0.5 rounded-md text-[11px] font-bold transition-all ${
                currentLocale === 'ja'
                  ? 'bg-[#078ACB] text-white shadow-2xs'
                  : 'text-[#718198] hover:text-[#14283F]'
              }`}
            >
              日本語
            </button>
          </div>

          {/* Current Model Status Pill */}
          <div className="hidden lg:flex items-center gap-2 px-3 py-1 rounded-full bg-[#F5F8FB] border border-[#E1EAF1] text-xs font-medium text-[#718198]">
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            <span className="font-mono text-[11px] text-[#425466]">{activeModel}</span>
          </div>

          {/* Hide/Show Hana Chat Button */}
          <button
            onClick={onToggleHana}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg border border-[#BDE0F5] bg-[#EBF5FB] text-[#078ACB] hover:bg-[#DDF0FA] transition-colors text-xs font-semibold shadow-2xs"
          >
            <MessageSquare className="w-3.5 h-3.5 text-[#078ACB]" />
            <span>{isHanaVisible ? t('nav.hideHana', 'Hide Hana Chat') : t('nav.showHana', 'Show Hana Chat')}</span>
          </button>
        </div>
      </header>

      {/* Language Selector Modal */}
      <LanguageSelectorModal
        isOpen={isLangModalOpen}
        onClose={() => setIsLangModalOpen(false)}
      />
    </>
  );
};

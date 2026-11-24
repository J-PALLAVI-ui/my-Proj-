import React, { useState } from 'react';
import { 
  Settings, 
  Eye, 
  Globe, 
  Cpu, 
  Database
} from 'lucide-react';

interface ProfileSettingsViewProps {
  activeModel?: string;
}

export const ProfileSettingsView: React.FC<ProfileSettingsViewProps> = ({
  activeModel = 'gpt-4o-mini'
}) => {
  const [highContrast, setHighContrast] = useState(false);
  const [reducedMotion, setReducedMotion] = useState(false);
  const [fontSize, setFontSize] = useState<'normal' | 'large' | 'xlarge'>('normal');
  const [selectedLanguage, setSelectedLanguage] = useState('en');

  const languages = [
    { code: 'en', name: 'English', native: 'English' },
    { code: 'ja', name: 'Japanese', native: '日本語' },
    { code: 'hi', name: 'Hindi', native: 'हिन्दी' },
    { code: 'ta', name: 'Tamil', native: 'தமிழ்' },
    { code: 'kn', name: 'Kannada', native: 'ಕನ್ನಡ' },
    { code: 'te', name: 'Telugu', native: 'తెలుగు' }
  ];

  return (
    <div className="h-full overflow-y-auto bg-slate-900 text-slate-100 p-4 sm:p-6 lg:p-8 max-w-5xl mx-auto space-y-8">
      {/* Workspace Header */}
      <div className="flex items-center gap-3 border-b border-slate-800 pb-5">
        <div className="w-10 h-10 rounded-xl bg-sky-500/20 text-sky-400 flex items-center justify-center">
          <Settings className="w-6 h-6" />
        </div>
        <div>
          <h1 className="text-xl sm:text-2xl font-black text-white">Profile & Accessibility Settings</h1>
          <p className="text-xs text-slate-400">
            WCAG 2.2 AA accessibility preferences, multilingual fluency, and AI engine telemetry.
          </p>
        </div>
      </div>

      {/* 1. WCAG 2.2 AA Accessibility Preferences */}
      <div className="bg-slate-800/90 border border-slate-700/80 rounded-2xl p-5 shadow-lg space-y-5">
        <div className="flex items-center gap-2 text-sm font-bold text-white border-b border-slate-700 pb-3">
          <Eye className="w-4 h-4 text-sky-400" />
          <span>Accessibility & Universal Design (WCAG 2.2 AA)</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
            <div>
              <span className="text-xs font-bold text-white block">High Contrast Mode</span>
              <span className="text-[11px] text-slate-400 block mt-0.5">Enhance borders and text contrast (&gt;= 4.5:1)</span>
            </div>
            <button
              onClick={() => setHighContrast(!highContrast)}
              className={`w-11 h-6 rounded-full transition-colors relative ${highContrast ? 'bg-sky-600' : 'bg-slate-700'}`}
              aria-label="Toggle high contrast mode"
            >
              <div className={`w-4 h-4 rounded-full bg-white transition-transform absolute top-1 ${highContrast ? 'left-6' : 'left-1'}`} />
            </button>
          </div>

          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
            <div>
              <span className="text-xs font-bold text-white block">Reduced Motion</span>
              <span className="text-[11px] text-slate-400 block mt-0.5">Disable intensive 3D and UI transitions</span>
            </div>
            <button
              onClick={() => setReducedMotion(!reducedMotion)}
              className={`w-11 h-6 rounded-full transition-colors relative ${reducedMotion ? 'bg-sky-600' : 'bg-slate-700'}`}
              aria-label="Toggle reduced motion"
            >
              <div className={`w-4 h-4 rounded-full bg-white transition-transform absolute top-1 ${reducedMotion ? 'left-6' : 'left-1'}`} />
            </button>
          </div>

          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
            <div>
              <span className="text-xs font-bold text-white block">Text Size Scaling</span>
              <span className="text-[11px] text-slate-400 block mt-0.5">Adjust text legibility</span>
            </div>
            <div className="flex items-center gap-1 bg-slate-800 p-1 rounded-lg text-xs">
              <button
                onClick={() => setFontSize('normal')}
                className={`px-2 py-0.5 rounded font-bold ${fontSize === 'normal' ? 'bg-sky-600 text-white' : 'text-slate-400'}`}
              >
                100%
              </button>
              <button
                onClick={() => setFontSize('large')}
                className={`px-2 py-0.5 rounded font-bold ${fontSize === 'large' ? 'bg-sky-600 text-white' : 'text-slate-400'}`}
              >
                115%
              </button>
              <button
                onClick={() => setFontSize('xlarge')}
                className={`px-2 py-0.5 rounded font-bold ${fontSize === 'xlarge' ? 'bg-sky-600 text-white' : 'text-slate-400'}`}
              >
                130%
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 2. Multilingual Fluency */}
      <div className="bg-slate-800/90 border border-slate-700/80 rounded-2xl p-5 shadow-lg space-y-4">
        <div className="flex items-center gap-2 text-sm font-bold text-white border-b border-slate-700 pb-3">
          <Globe className="w-4 h-4 text-emerald-400" />
          <span>Language & Multilingual Fluency</span>
        </div>

        <p className="text-xs text-slate-300">
          Guide Hana communicates naturally in English, Japanese with polite keigo, Hindi, Tamil, Kannada, and Telugu.
        </p>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {languages.map((l) => (
            <button
              key={l.code}
              onClick={() => setSelectedLanguage(l.code)}
              className={`p-3 rounded-xl border text-center transition-all ${
                selectedLanguage === l.code
                  ? 'bg-sky-600 border-sky-400 text-white shadow-md'
                  : 'bg-slate-900 border-slate-800 text-slate-300 hover:border-slate-700'
              }`}
            >
              <span className="text-sm font-bold block">{l.native}</span>
              <span className="text-[10px] text-slate-400 block mt-0.5">{l.name}</span>
            </button>
          ))}
        </div>
      </div>

      {/* 3. AI Engine Configuration & System Health Diagnostics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div className="bg-slate-800/90 border border-slate-700/80 rounded-2xl p-5 shadow-lg space-y-3">
          <div className="flex items-center gap-2 text-sm font-bold text-white border-b border-slate-700 pb-2">
            <Cpu className="w-4 h-4 text-sky-400" />
            <span>AI Model & LLM Pipeline Telemetry</span>
          </div>

          <ul className="text-xs text-slate-300 space-y-2.5">
            <li className="flex justify-between border-b border-slate-800 pb-1">
              <span>Primary Engine:</span>
              <strong className="text-white font-mono">OpenAI Responses API</strong>
            </li>
            <li className="flex justify-between border-b border-slate-800 pb-1">
              <span>Configured Model:</span>
              <strong className="text-sky-400 font-mono">{activeModel}</strong>
            </li>
            <li className="flex justify-between border-b border-slate-800 pb-1">
              <span>Streaming Protocol:</span>
              <strong className="text-emerald-400">Server-Sent Events (SSE)</strong>
            </li>
            <li className="flex justify-between border-b border-slate-800 pb-1">
              <span>RAG Knowledge Base:</span>
              <strong className="text-white">16 Verified Documents (Code & Tourism)</strong>
            </li>
            <li className="flex justify-between">
              <span>Max Tokens:</span>
              <strong className="text-white font-mono">3,000 output tokens</strong>
            </li>
          </ul>
        </div>

        <div className="bg-slate-800/90 border border-slate-700/80 rounded-2xl p-5 shadow-lg space-y-3">
          <div className="flex items-center gap-2 text-sm font-bold text-white border-b border-slate-700 pb-2">
            <Database className="w-4 h-4 text-amber-400" />
            <span>Database & Transit Engine Telemetry</span>
          </div>

          <ul className="text-xs text-slate-300 space-y-2.5">
            <li className="flex justify-between border-b border-slate-800 pb-1">
              <span>Database Architecture:</span>
              <strong className="text-white font-mono">SQLite 3 (WAL Mode, Foreign Keys ON)</strong>
            </li>
            <li className="flex justify-between border-b border-slate-800 pb-1">
              <span>Canonical Places:</span>
              <strong className="text-white font-mono">35 Individually Verified Records</strong>
            </li>
            <li className="flex justify-between border-b border-slate-800 pb-1">
              <span>Public Transit Algorithm:</span>
              <strong className="text-sky-400 font-mono">Deterministic RAPTOR Engine</strong>
            </li>
            <li className="flex justify-between border-b border-slate-800 pb-1">
              <span>Transit Feed:</span>
              <strong className="text-white">Fujikyu Bus GTFS-JP + Fujisanroku Rail</strong>
            </li>
            <li className="flex justify-between">
              <span>Crowd Simulation:</span>
              <strong className="text-emerald-400 font-mono">CrowdSense (Low/Mod/High)</strong>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

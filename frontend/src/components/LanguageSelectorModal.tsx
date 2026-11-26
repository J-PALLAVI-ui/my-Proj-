import React, { useState, useMemo } from 'react';
import { useI18n } from '../i18n/I18nContext';
import { Globe2, Search, X, Check } from 'lucide-react';

interface LanguageSelectorModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const LanguageSelectorModal: React.FC<LanguageSelectorModalProps> = ({ isOpen, onClose }) => {
  const { currentLocale, setLocale, locales, totalLocalesCount } = useI18n();
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    if (!search.trim()) return locales;
    const q = search.toLowerCase();
    return locales.filter(
      l =>
        l.name.toLowerCase().includes(q) ||
        l.nativeName.toLowerCase().includes(q) ||
        l.code.toLowerCase().includes(q)
    );
  }, [locales, search]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-xs animate-in fade-in duration-200">
      <div className="bg-white rounded-2xl border border-[#E1EAF1] shadow-2xl max-w-2xl w-full max-h-[85vh] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="p-4 sm:p-5 border-b border-[#E1EAF1] flex items-center justify-between bg-[#F5F8FB]">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-[#EBF5FB] text-[#078ACB] border border-[#BDE0F5] flex items-center justify-center">
              <Globe2 className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm sm:text-base font-bold text-[#14283F] flex items-center gap-2">
                <span>Select Language</span>
                <span className="text-[10px] font-mono bg-sky-100 text-sky-800 border border-sky-200 px-2 py-0.5 rounded-full font-bold">
                  {totalLocalesCount} Global Locales
                </span>
              </h2>
              <p className="text-[11px] text-[#718198]">
                Application-wide translations with native script & directional RTL support
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-[#718198] hover:text-[#14283F] hover:bg-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Search Bar */}
        <div className="p-4 border-b border-[#E1EAF1] bg-white">
          <div className="relative">
            <Search className="w-4 h-4 text-[#718198] absolute left-3 top-3" />
            <input
              type="text"
              placeholder="Search by language name or native script (e.g. Japanese, 日本語, Hindi, العربية)..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 text-xs rounded-xl border border-[#E1EAF1] bg-[#F5F8FB] focus:bg-white focus:outline-none focus:border-[#078ACB] transition-colors"
              autoFocus
            />
          </div>
        </div>

        {/* Scrollable List of 170+ Languages */}
        <div className="flex-1 overflow-y-auto p-4 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
          {filtered.map((loc) => {
            const isSelected = loc.code === currentLocale;
            return (
              <button
                key={loc.code}
                onClick={() => {
                  setLocale(loc.code);
                  onClose();
                }}
                className={`p-2.5 rounded-xl border text-left transition-all flex items-center justify-between ${
                  isSelected
                    ? 'border-[#078ACB] bg-[#EBF5FB] shadow-2xs'
                    : 'border-[#E1EAF1] hover:border-[#BDE0F5] hover:bg-[#F5F8FB]'
                }`}
              >
                <div className="min-w-0 pr-2">
                  <div className="text-xs font-bold text-[#14283F] truncate">
                    {loc.nativeName}
                  </div>
                  <div className="text-[11px] text-[#718198] truncate flex items-center gap-1.5 mt-0.5">
                    <span>{loc.name}</span>
                    <span className="text-[9px] font-mono text-slate-400">({loc.code})</span>
                  </div>
                </div>
                <div className="flex items-center gap-1.5 shrink-0">
                  <span
                    className={`text-[9px] font-mono px-1.5 py-0.5 rounded font-semibold ${
                      loc.coverage >= 90
                        ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                        : loc.coverage >= 80
                        ? 'bg-sky-50 text-sky-700 border border-sky-200'
                        : 'bg-slate-100 text-slate-600'
                    }`}
                  >
                    {loc.coverage}%
                  </span>
                  {isSelected && <Check className="w-3.5 h-3.5 text-[#078ACB]" />}
                </div>
              </button>
            );
          })}
        </div>

        {/* Footer */}
        <div className="p-3 bg-[#F5F8FB] border-t border-[#E1EAF1] text-[11px] text-[#718198] flex items-center justify-between">
          <span>Active: <strong>{locales.find(l => l.code === currentLocale)?.name}</strong></span>
          <button
            onClick={onClose}
            className="px-3 py-1 bg-white border border-[#E1EAF1] hover:bg-slate-100 rounded-lg text-xs font-semibold text-[#14283F] transition-colors"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
};

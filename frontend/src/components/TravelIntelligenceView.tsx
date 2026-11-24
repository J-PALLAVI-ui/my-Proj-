import React, { useState } from 'react';
import { 
  Compass, 
  Eye, 
  ShieldAlert, 
  AlertTriangle, 
  PhoneCall, 
  ArrowRight, 
  Thermometer, 
  Snowflake
} from 'lucide-react';
import { CrowdDashboard } from './CrowdDashboard';

interface TravelIntelligenceViewProps {
  onAskHana: (prompt: string) => void;
}

export const TravelIntelligenceView: React.FC<TravelIntelligenceViewProps> = ({ onAskHana }) => {
  const [activeTab, setActiveTab] = useState<'weather' | 'crowds' | 'safety'>('weather');
  const [selectedMonth, setSelectedMonth] = useState<number>(12);

  const months = [
    { num: 1, name: 'Jan', temp: '-6°C ~ 6°C', vis: '78%', note: 'Diamond Fuji' },
    { num: 2, name: 'Feb', temp: '-5°C ~ 7°C', vis: '75%', note: 'Winter crystal' },
    { num: 3, name: 'Mar', temp: '-1°C ~ 11°C', vis: '62%', note: 'Thaw & chill' },
    { num: 4, name: 'Apr', temp: '4°C ~ 17°C', vis: '55%', note: 'Cherry blossoms' },
    { num: 5, name: 'May', temp: '9°C ~ 21°C', vis: '48%', note: 'Shibazakura' },
    { num: 6, name: 'Jun', temp: '14°C ~ 23°C', vis: '35%', note: 'Rainy season' },
    { num: 7, name: 'Jul', temp: '19°C ~ 27°C', vis: '40%', note: 'Climbing opens' },
    { num: 8, name: 'Aug', temp: '19°C ~ 28°C', vis: '42%', note: 'Summer fireworks' },
    { num: 9, name: 'Sep', temp: '15°C ~ 23°C', vis: '38%', note: 'Climbing closes' },
    { num: 10, name: 'Oct', temp: '8°C ~ 18°C', vis: '58%', note: 'First snow' },
    { num: 11, name: 'Nov', temp: '1°C ~ 13°C', vis: '70%', note: 'Autumn foliage' },
    { num: 12, name: 'Dec', temp: '-4°C ~ 8°C', vis: '77%', note: 'Highest clarity' },
  ];

  const currentMonthData = months.find(m => m.num === selectedMonth) || months[11];

  return (
    <div className="h-full overflow-y-auto bg-slate-900 text-slate-100 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-8">
      {/* Workspace Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-8 h-8 rounded-lg bg-sky-500/20 text-sky-400 flex items-center justify-center">
              <Compass className="w-5 h-5" />
            </span>
            <h1 className="text-xl sm:text-2xl font-black text-white">Travel Intelligence Center</h1>
          </div>
          <p className="text-xs text-slate-400">
            Real-time weather analytics, CrowdSense spatial simulation, and verified alpine safety.
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center gap-1 bg-slate-800 p-1 rounded-xl self-start sm:self-auto">
          <button
            onClick={() => setActiveTab('weather')}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
              activeTab === 'weather' ? 'bg-sky-600 text-white shadow-xs' : 'text-slate-400 hover:text-white'
            }`}
          >
            Weather & Visibility
          </button>
          <button
            onClick={() => setActiveTab('crowds')}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
              activeTab === 'crowds' ? 'bg-sky-600 text-white shadow-xs' : 'text-slate-400 hover:text-white'
            }`}
          >
            CrowdSense Engine
          </button>
          <button
            onClick={() => setActiveTab('safety')}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
              activeTab === 'safety' ? 'bg-sky-600 text-white shadow-xs' : 'text-slate-400 hover:text-white'
            }`}
          >
            Emergency & Safety
          </button>
        </div>
      </div>

      {activeTab === 'weather' ? (
        /* Weather & Visibility Intelligence */
        <div className="space-y-6">
          {/* Month Selector Bar */}
          <div>
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-2">
              Select Seasonal Month
            </span>
            <div className="grid grid-cols-4 sm:grid-cols-6 lg:grid-cols-12 gap-1.5">
              {months.map((m) => (
                <button
                  key={m.num}
                  onClick={() => setSelectedMonth(m.num)}
                  className={`p-2 rounded-xl text-center border transition-all ${
                    selectedMonth === m.num
                      ? 'bg-sky-600 border-sky-400 text-white shadow-md'
                      : 'bg-slate-800/80 border-slate-700 text-slate-400 hover:border-slate-600 hover:text-white'
                  }`}
                >
                  <span className="text-xs font-bold block">{m.name}</span>
                  <span className="text-[10px] text-sky-200 block mt-0.5">{m.vis}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Visibility & Temperature Deep Dive Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            <div className="bg-slate-800/90 border border-slate-700/80 rounded-2xl p-5 shadow-lg flex flex-col justify-between">
              <div>
                <div className="w-10 h-10 rounded-xl bg-sky-500/20 text-sky-400 flex items-center justify-center mb-3">
                  <Eye className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-white mb-1">Fuji Visibility Probability</h3>
                <span className="text-3xl font-black text-sky-400">{currentMonthData.vis}</span>
                <p className="text-xs text-slate-300 mt-2 leading-relaxed">
                  Clear summit view likelihood based on 30-year historical observations from JMA Station 47674.
                </p>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-700 text-xs text-slate-400">
                Peak viewing hours: <strong>06:00 AM – 09:30 AM</strong> before convective clouds form.
              </div>
            </div>

            <div className="bg-slate-800/90 border border-slate-700/80 rounded-2xl p-5 shadow-lg flex flex-col justify-between">
              <div>
                <div className="w-10 h-10 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center mb-3">
                  <Thermometer className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-white mb-1">Temperature Profile</h3>
                <span className="text-3xl font-black text-amber-300">{currentMonthData.temp}</span>
                <p className="text-xs text-slate-300 mt-2 leading-relaxed">
                  Significant diurnal temperature swing between daytime sunshine and overnight lakeside freezing.
                </p>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-700 text-xs text-slate-400">
                Special feature: <strong>{currentMonthData.note}</strong>
              </div>
            </div>

            <div className="bg-slate-800/90 border border-slate-700/80 rounded-2xl p-5 shadow-lg flex flex-col justify-between">
              <div>
                <div className="w-10 h-10 rounded-xl bg-indigo-500/20 text-indigo-400 flex items-center justify-center mb-3">
                  <Snowflake className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-white mb-1">Packing & Gear Advice</h3>
                <p className="text-xs text-slate-200 mt-2 leading-relaxed">
                  {selectedMonth >= 11 || selectedMonth <= 3
                    ? 'Heavy winter coat, windproof thermal base layers (Heattech), gloves, beanie, and slip-resistant boots.'
                    : 'Comfortable walking sneakers, light rain jacket, sun hat, and evening cardigan.'}
                </p>
              </div>

              <button
                onClick={() => onAskHana(`What should I pack and what are the best photo spots around Mount Fuji in ${currentMonthData.name}?`)}
                className="mt-4 pt-3 border-t border-slate-700 text-xs font-semibold text-sky-400 hover:text-sky-300 flex items-center gap-1"
              >
                <span>Ask Hana for packing advice</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      ) : activeTab === 'crowds' ? (
        /* CrowdSense Intelligence Engine */
        <div className="space-y-4">
          <CrowdDashboard onAskHana={onAskHana} />
        </div>
      ) : (
        /* Emergency and Safety Center */
        <div className="space-y-6">
          <div className="bg-rose-950/40 border border-rose-800/60 rounded-2xl p-5 shadow-lg">
            <div className="flex items-start gap-3">
              <ShieldAlert className="w-6 h-6 text-rose-400 shrink-0 mt-0.5" />
              <div>
                <h3 className="text-base font-bold text-white">Official Climbing Season Notice</h3>
                <p className="text-xs text-slate-300 mt-1 leading-relaxed">
                  Mount Fuji summit trails (Yoshida trail) are <strong>strictly closed</strong> from September 11 through July 9. 
                  Climbing during off-season is extremely dangerous and strictly prohibited due to gale winds, freezing ice sheets, and avalanches.
                </p>
                <span className="text-[11px] text-rose-300 font-semibold block mt-2">
                  Authority: Yamanashi Prefectural Police & Mount Fuji Safety Council
                </span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div className="bg-slate-800/90 border border-slate-700/80 rounded-2xl p-5 shadow-lg space-y-3">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                <span>Winter Road & Morning Black Ice Alert</span>
              </h3>
              <p className="text-xs text-slate-300 leading-relaxed">
                From December to March, roads circling Lake Kawaguchiko, Saiko, and Yamanakako regularly freeze overnight. 
                Rental vehicles must be equipped with studless winter snow tires or chains.
              </p>
              <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-[11px] text-slate-400">
                Tip: Fujikyu Sightseeing Omni buses operate on snow-ready heavy chains and offer safe transport during winter.
              </div>
            </div>

            <div className="bg-slate-800/90 border border-slate-700/80 rounded-2xl p-5 shadow-lg space-y-3">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <PhoneCall className="w-4 h-4 text-sky-400" />
                <span>Key Emergency Contacts in Japan</span>
              </h3>
              <ul className="text-xs text-slate-300 space-y-2">
                <li className="flex justify-between border-b border-slate-800 pb-1">
                  <span>Police (Emergency):</span>
                  <strong className="text-white font-mono">110</strong>
                </li>
                <li className="flex justify-between border-b border-slate-800 pb-1">
                  <span>Ambulance / Fire:</span>
                  <strong className="text-white font-mono">119</strong>
                </li>
                <li className="flex justify-between border-b border-slate-800 pb-1">
                  <span>Japan Visitor Hotline (24/7 Multilingual):</span>
                  <strong className="text-sky-400 font-mono">050-3816-2720</strong>
                </li>
                <li className="flex justify-between">
                  <span>Fujiyoshida Municipal Medical Center:</span>
                  <strong className="text-white font-mono">0555-22-4111</strong>
                </li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

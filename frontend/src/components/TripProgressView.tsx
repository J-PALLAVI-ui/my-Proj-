import React, { useState } from 'react';
import { useTrip } from '../context/TripContext';
import { 
  Zap, 
  CheckCircle2, 
  Clock, 
  Calendar, 
  Navigation, 
  Bus
} from 'lucide-react';

interface TripProgressViewProps {
  onAskHana?: (prompt: string) => void;
  onOpenMap?: () => void;
  onCheckBus?: () => void;
}

export const TripProgressView: React.FC<TripProgressViewProps> = ({
  onAskHana,
  onOpenMap,
  onCheckBus,
}) => {
  const { 
    selectedPlaceName, 
    adaptiveMinutesAhead, 
    applyAdaptivePlan,
    setIsAdaptiveModalOpen
  } = useTrip();

  const [planStatus, setPlanStatus] = useState<'pending_choice' | 'applied' | 'kept'>('pending_choice');

  const handleApply = () => {
    setPlanStatus('applied');
    applyAdaptivePlan();
    if (onAskHana) {
      onAskHana(
        `I finished ${selectedPlaceName} 40 minutes ahead of schedule! I accepted your revised plan adding Kawaguchiko Music Forest Museum and Nagasaki Cape. What bus should I take next?`
      );
    }
  };

  const handleKeep = () => {
    setPlanStatus('kept');
    setIsAdaptiveModalOpen(false);
    if (onAskHana) {
      onAskHana(
        `I decided to keep my original plan and take a relaxed pace around ${selectedPlaceName}.`
      );
    }
  };

  return (
    <div className="bg-white rounded-3xl border border-[#E1EAF1] p-6 shadow-xs space-y-6 animate-in fade-in duration-200">
      {/* 1. Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-[#E1EAF1] gap-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
            <h2 className="text-xl font-bold text-[#14283F]">Trip Progress (Live)</h2>
            <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full">
              TRACKING ACTIVE
            </span>
          </div>
          <p className="text-xs text-[#718198] mt-1">
            Your journey is in progress. Hana is tracking your time, stops and plan.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {onOpenMap && (
            <button
              onClick={onOpenMap}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-sky-200 bg-sky-50 text-sky-700 text-xs font-semibold hover:bg-sky-100 transition-colors"
            >
              <Navigation className="w-3.5 h-3.5 text-[#078ACB]" />
              <span>Show on map</span>
            </button>
          )}
          {onCheckBus && (
            <button
              onClick={onCheckBus}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-700 text-xs font-semibold hover:bg-slate-100 transition-colors"
            >
              <Bus className="w-3.5 h-3.5 text-slate-500" />
              <span>Check bus times</span>
            </button>
          )}
        </div>
      </div>

      {/* 2. Current Activity Card */}
      <div className="flex flex-col sm:flex-row items-center gap-5 p-4 rounded-2xl bg-[#F5F8FB] border border-[#E1EAF1]">
        <div className="w-full sm:w-44 h-28 rounded-xl overflow-hidden shrink-0 shadow-2xs relative bg-slate-200">
          <img
            src="https://images.unsplash.com/photo-1578637387939-43c525550085?auto=format&fit=crop&w=600&q=80"
            alt="Oishi Park"
            className="w-full h-full object-cover"
          />
          <div className="absolute top-2 left-2 bg-emerald-600/90 text-white text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" />
            <span>Completed</span>
          </div>
        </div>

        <div className="flex-1 space-y-2 w-full">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-[#14283F]">{selectedPlaceName || 'Oishi Park'}</h3>
            <span className="text-xs text-slate-500 flex items-center gap-1">
              <Clock className="w-3.5 h-3.5 text-slate-400" />
              <span>Visited: 20 min • Planned: 60 min</span>
            </span>
          </div>
          <p className="text-xs text-[#425466] leading-relaxed">
            Explored scenic lakeside lavender gardens and Mount Fuji viewpoint. Activity finished early.
          </p>
        </div>
      </div>

      {/* 3. Adaptive Alert Banner */}
      <div className="flex items-start gap-3.5 p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-950 shadow-2xs">
        <div className="w-9 h-9 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center shrink-0">
          <Zap className="w-5 h-5 text-emerald-600 fill-emerald-600" />
        </div>
        <div className="flex-1 space-y-1">
          <div className="flex items-center gap-2">
            <h4 className="text-sm font-bold text-emerald-900">
              You are {adaptiveMinutesAhead} min ahead — update the rest of your plan?
            </h4>
            <span className="text-[10px] font-bold bg-emerald-200/80 text-emerald-800 px-2 py-0.5 rounded-full uppercase">
              Hana Recommendation
            </span>
          </div>
          <p className="text-xs text-emerald-800 leading-relaxed">
            I can adjust your next stops, add a hidden gem (e.g. Kawaguchiko Music Forest Museum & Nagasaki Cape), or extend your lunch time at Lake Kawaguchi.
          </p>
        </div>
      </div>

      {/* 4. Side-by-Side Comparison Tables (Revised vs Original) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Left: Revised Plan (Optimized) */}
        <div className="rounded-2xl border-2 border-emerald-300 bg-white p-4 shadow-xs space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-emerald-100">
            <div className="flex items-center gap-1.5">
              <span className="w-6 h-6 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center text-xs font-bold">
                1
              </span>
              <h5 className="text-xs font-bold text-[#14283F]">Revised Plan (5h Total)</h5>
            </div>
            <span className="text-[10px] font-bold bg-emerald-500 text-white px-2 py-0.5 rounded-full">
              Optimized
            </span>
          </div>

          <div className="space-y-2 text-xs">
            <div className="flex items-start gap-2.5 p-2 rounded-xl bg-emerald-50/50 border border-emerald-100">
              <span className="w-4 h-4 rounded-full bg-emerald-600 text-white text-[10px] font-bold flex items-center justify-center shrink-0 mt-0.5">
                2
              </span>
              <div className="flex-1">
                <div className="flex justify-between font-semibold text-[#14283F]">
                  <span>Kawaguchiko Music Forest Museum</span>
                  <span className="text-emerald-700 font-mono">(40 min)</span>
                </div>
                <div className="text-[10px] text-slate-500">10:20 - 11:00 • Scenic European garden & Mt. Fuji view</div>
              </div>
            </div>

            <div className="flex items-start gap-2.5 p-2 rounded-xl bg-slate-50 border border-slate-100">
              <span className="w-4 h-4 rounded-full bg-[#078ACB] text-white text-[10px] font-bold flex items-center justify-center shrink-0 mt-0.5">
                3
              </span>
              <div className="flex-1">
                <div className="flex justify-between font-semibold text-[#14283F]">
                  <span>Lunch at Local Café (Lake Kawaguchiko)</span>
                  <span className="text-slate-600 font-mono">(60 min)</span>
                </div>
                <div className="text-[10px] text-slate-500">11:05 - 12:05 • Hoto noodles & local seasonal sweets</div>
              </div>
            </div>

            <div className="flex items-start gap-2.5 p-2 rounded-xl bg-emerald-50/50 border border-emerald-100">
              <span className="w-4 h-4 rounded-full bg-emerald-600 text-white text-[10px] font-bold flex items-center justify-center shrink-0 mt-0.5">
                4
              </span>
              <div className="flex-1">
                <div className="flex justify-between font-semibold text-[#14283F]">
                  <span>Nagasaki Cape (Quieter Viewpoint)</span>
                  <span className="text-emerald-700 font-mono">(80 min)</span>
                </div>
                <div className="text-[10px] text-slate-500">12:10 - 13:30 • Hidden gem, serene lakeside panoramic vista</div>
              </div>
            </div>

            <div className="flex items-start gap-2.5 p-2 rounded-xl bg-slate-50 border border-slate-100">
              <span className="w-4 h-4 rounded-full bg-slate-600 text-white text-[10px] font-bold flex items-center justify-center shrink-0 mt-0.5">
                5
              </span>
              <div className="flex-1">
                <div className="flex justify-between font-semibold text-[#14283F]">
                  <span>Return to Kawaguchiko Station</span>
                  <span className="text-slate-600 font-mono">(60 min)</span>
                </div>
                <div className="text-[10px] text-slate-500">13:30 - 14:30 • Fujikyu Sightseeing bus line</div>
              </div>
            </div>
          </div>
        </div>

        {/* Right: Original Plan (For Comparison) */}
        <div className="rounded-2xl border border-slate-200 bg-slate-50/50 p-4 shadow-xs space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-slate-200">
            <h5 className="text-xs font-bold text-slate-700">Original Plan (for comparison)</h5>
            <span className="text-[10px] font-semibold text-slate-500">Baseline</span>
          </div>

          <div className="space-y-2 text-xs">
            <div className="flex items-start gap-2.5 p-2 rounded-xl bg-white border border-slate-200/80">
              <span className="w-4 h-4 rounded-full bg-slate-300 text-slate-700 text-[10px] font-bold flex items-center justify-center shrink-0 mt-0.5">
                2
              </span>
              <div className="flex-1">
                <div className="flex justify-between font-medium text-slate-700">
                  <span>Lunch (Hoto noodles)</span>
                  <span className="text-slate-500 font-mono">(60 min)</span>
                </div>
                <div className="text-[10px] text-slate-400">11:00 - 12:00</div>
              </div>
            </div>

            <div className="flex items-start gap-2.5 p-2 rounded-xl bg-white border border-slate-200/80">
              <span className="w-4 h-4 rounded-full bg-slate-300 text-slate-700 text-[10px] font-bold flex items-center justify-center shrink-0 mt-0.5">
                3
              </span>
              <div className="flex-1">
                <div className="flex justify-between font-medium text-slate-700">
                  <span>Ubuyagasaki</span>
                  <span className="text-slate-500 font-mono">(90 min)</span>
                </div>
                <div className="text-[10px] text-slate-400">12:00 - 13:30</div>
              </div>
            </div>

            <div className="flex items-start gap-2.5 p-2 rounded-xl bg-white border border-slate-200/80">
              <span className="w-4 h-4 rounded-full bg-slate-300 text-slate-700 text-[10px] font-bold flex items-center justify-center shrink-0 mt-0.5">
                4
              </span>
              <div className="flex-1">
                <div className="flex justify-between font-medium text-slate-700">
                  <span>Return to Station</span>
                  <span className="text-slate-500 font-mono">(60 min)</span>
                </div>
                <div className="text-[10px] text-slate-400">13:30 - 14:30</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 5. Bottom Action Buttons */}
      <div className="flex flex-col sm:flex-row items-center justify-end gap-3 pt-2">
        <button
          onClick={handleKeep}
          className="w-full sm:w-auto px-5 py-2.5 rounded-xl border border-slate-200 bg-white text-slate-700 text-xs font-bold hover:bg-slate-50 transition-colors shadow-2xs flex items-center justify-center gap-1.5"
        >
          <Calendar className="w-3.5 h-3.5 text-slate-500" />
          <span>Keep original plan</span>
        </button>

        <button
          onClick={handleApply}
          className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-emerald-600 text-white text-xs font-bold hover:bg-emerald-700 transition-colors shadow-sm flex items-center justify-center gap-1.5"
        >
          <CheckCircle2 className="w-4 h-4" />
          <span>Apply updated plan</span>
        </button>
      </div>

      {planStatus === 'applied' && (
        <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-200 text-emerald-800 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>Updated plan applied! Next stop: Kawaguchiko Music Forest Museum. Estimated arrival: 10:20 AM.</span>
        </div>
      )}
    </div>
  );
};

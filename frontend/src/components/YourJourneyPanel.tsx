import React from 'react';
import { ItineraryPlan, ItineraryStop } from '../types';
import { 
  Calendar, 
  Clock, 
  MapPin, 
  Navigation, 
  Star, 
  DollarSign, 
  Footprints, 
  Trash2, 
  Sparkles, 
  ArrowRight, 
  Bus, 
  ShieldCheck, 
  ChevronDown,
  ChevronUp
} from 'lucide-react';

interface YourJourneyPanelProps {
  itinerary: ItineraryPlan | null;
  onAskHana: (prompt: string) => void;
  onRemoveStop?: (dayNumber: number, stopIndex: number) => void;
  onReorderStop?: (dayNumber: number, stopIndex: number, direction: 'up' | 'down') => void;
}

export const YourJourneyPanel: React.FC<YourJourneyPanelProps> = ({
  itinerary,
  onAskHana,
  onRemoveStop,
  onReorderStop
}) => {
  if (!itinerary || !itinerary.days || itinerary.days.length === 0) {
    return (
      <div className="h-full flex flex-col bg-white border-r border-slate-200 overflow-y-auto p-6">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-8 h-8 rounded-lg bg-sky-100 text-sky-700 flex items-center justify-center">
            <Calendar className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-900">Your Journey</h2>
            <p className="text-xs text-slate-500">Adaptive Itinerary & RAPTOR Transit Schedule</p>
          </div>
        </div>

        <div className="my-auto py-8 text-center max-w-sm mx-auto">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-sky-50 to-indigo-50 border border-sky-100 flex items-center justify-center mx-auto mb-4 text-sky-600 shadow-xs">
            <Navigation className="w-8 h-8" />
          </div>
          <h3 className="text-sm font-bold text-slate-800 mb-1">No Active Itinerary Yet</h3>
          <p className="text-xs text-slate-500 leading-relaxed mb-6">
            Ask Guide Hana to generate a personalized itinerary tailored to your group, mobility needs, and pace.
          </p>

          <div className="space-y-2 text-left">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
              Quick Itinerary Starters
            </span>
            <button
              onClick={() => onAskHana('Can you recommend a 1-day itinerary around Lake Kawaguchiko with classic Mount Fuji views?')}
              className="w-full text-left p-3 rounded-xl border border-slate-200 bg-slate-50 hover:bg-sky-50 hover:border-sky-200 text-xs text-slate-700 font-medium transition-all group flex items-center justify-between"
            >
              <span>1-Day Classic Fuji & Kawaguchiko Highlights</span>
              <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-sky-600 group-hover:translate-x-0.5 transition-all" />
            </button>
            <button
              onClick={() => onAskHana('Help me plan a 2-day photography trip around the Fuji Five Lakes with quiet viewpoints.')}
              className="w-full text-left p-3 rounded-xl border border-slate-200 bg-slate-50 hover:bg-sky-50 hover:border-sky-200 text-xs text-slate-700 font-medium transition-all group flex items-center justify-between"
            >
              <span>2-Day Photography & Tranquil Lakes Tour</span>
              <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-sky-600 group-hover:translate-x-0.5 transition-all" />
            </button>
            <button
              onClick={() => onAskHana('Please plan a family-friendly 3-day itinerary with easy walking and step-free access.')}
              className="w-full text-left p-3 rounded-xl border border-slate-200 bg-slate-50 hover:bg-sky-50 hover:border-sky-200 text-xs text-slate-700 font-medium transition-all group flex items-center justify-between"
            >
              <span>3-Day Family & Barrier-Free Experience</span>
              <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-sky-600 group-hover:translate-x-0.5 transition-all" />
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Calculate high-level summary
  const totalStops = itinerary.days.reduce((acc, d) => acc + d.stops.length, 0);

  return (
    <div className="h-full flex flex-col bg-white border-r border-slate-200 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-slate-200 bg-gradient-to-r from-sky-50/50 via-white to-indigo-50/50">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <span className="w-8 h-8 rounded-lg bg-sky-600 text-white flex items-center justify-center font-bold text-xs shadow-xs">
              {itinerary.total_days}D
            </span>
            <div>
              <h2 className="text-sm font-bold text-slate-900 leading-tight">{itinerary.title}</h2>
              <p className="text-[11px] text-slate-500">
                {totalStops} destinations • {itinerary.pace} pace • {itinerary.budget_tier} budget
              </p>
            </div>
          </div>
        </div>

        {/* Quick Edit Adapt Buttons */}
        <div className="flex flex-wrap gap-1.5 pt-2">
          <button
            onClick={() => onAskHana('Please make this itinerary cheaper with more free viewpoints and low-cost options.')}
            className="flex items-center gap-1 px-2.5 py-1 rounded-md bg-white border border-slate-200 text-[11px] font-medium text-slate-700 hover:bg-slate-50 shadow-2xs transition-colors"
          >
            <DollarSign className="w-3 h-3 text-emerald-600" />
            <span>Make Cheaper</span>
          </button>
          <button
            onClick={() => onAskHana('Please reduce walking and avoid steep stairs for this itinerary.')}
            className="flex items-center gap-1 px-2.5 py-1 rounded-md bg-white border border-slate-200 text-[11px] font-medium text-slate-700 hover:bg-slate-50 shadow-2xs transition-colors"
          >
            <Footprints className="w-3 h-3 text-sky-600" />
            <span>Reduce Walking</span>
          </button>
          <button
            onClick={() => onAskHana('Can you recommend a quieter alternative for crowded stops in this plan?')}
            className="flex items-center gap-1 px-2.5 py-1 rounded-md bg-white border border-slate-200 text-[11px] font-medium text-slate-700 hover:bg-slate-50 shadow-2xs transition-colors"
          >
            <Sparkles className="w-3 h-3 text-indigo-600" />
            <span>Avoid Crowds</span>
          </button>
        </div>
      </div>

      {/* Days & Stops Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {itinerary.days.map((day) => (
          <div key={day.day_number} className="space-y-3">
            <div className="flex items-center justify-between sticky top-0 bg-white/95 backdrop-blur-xs py-1 z-10 border-b border-slate-100">
              <span className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                <span className="w-5 h-5 rounded-full bg-slate-900 text-white text-[10px] flex items-center justify-center font-bold">
                  {day.day_number}
                </span>
                <span>Day {day.day_number}: {day.title}</span>
              </span>
              <span className="text-[11px] text-slate-400 font-medium">
                {day.stops.length} stops
              </span>
            </div>

            <div className="space-y-3 pl-2 border-l-2 border-slate-100 ml-2.5">
              {day.stops.map((stop: ItineraryStop, idx: number) => (
                <div key={stop.stop_id} className="relative group">
                  {/* Timeline bullet */}
                  <div className="absolute -left-[17px] top-4 w-2.5 h-2.5 rounded-full bg-sky-500 ring-4 ring-white" />

                  {/* Stop Card */}
                  <div className="bg-white rounded-xl border border-slate-200 p-3 shadow-2xs hover:shadow-xs hover:border-slate-300 transition-all">
                    <div className="flex gap-3">
                      {stop.image_url ? (
                        <img
                          src={stop.image_url}
                          alt={stop.name_en}
                          className="w-16 h-16 rounded-lg object-cover shrink-0 bg-slate-100"
                        />
                      ) : (
                        <div className="w-16 h-16 rounded-lg bg-sky-50 text-sky-600 flex items-center justify-center shrink-0">
                          <MapPin className="w-6 h-6" />
                        </div>
                      )}

                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-1">
                          <div>
                            <h4 className="text-xs font-bold text-slate-900 truncate">
                              {stop.name_en}
                            </h4>
                            <span className="text-[10px] text-slate-500 block truncate">
                              {stop.name_ja}
                            </span>
                          </div>

                          {/* Reorder & Remove Actions */}
                          <div className="flex items-center gap-0.5 opacity-60 group-hover:opacity-100 transition-opacity">
                            {onReorderStop && idx > 0 && (
                              <button
                                onClick={() => onReorderStop(day.day_number, idx, 'up')}
                                className="p-1 text-slate-400 hover:text-slate-700 rounded hover:bg-slate-100"
                                title="Move stop up"
                              >
                                <ChevronUp className="w-3 h-3" />
                              </button>
                            )}
                            {onReorderStop && idx < day.stops.length - 1 && (
                              <button
                                onClick={() => onReorderStop(day.day_number, idx, 'down')}
                                className="p-1 text-slate-400 hover:text-slate-700 rounded hover:bg-slate-100"
                                title="Move stop down"
                              >
                                <ChevronDown className="w-3 h-3" />
                              </button>
                            )}
                            {onRemoveStop && (
                              <button
                                onClick={() => onRemoveStop(day.day_number, idx)}
                                className="p-1 text-slate-400 hover:text-rose-600 rounded hover:bg-rose-50"
                                title="Remove stop"
                              >
                                <Trash2 className="w-3 h-3" />
                              </button>
                            )}
                          </div>
                        </div>

                        {/* Timing and Fuji Rating */}
                        <div className="flex items-center gap-2 mt-1.5 text-[11px] text-slate-600">
                          <span className="flex items-center gap-1 font-semibold text-sky-700 bg-sky-50 px-1.5 py-0.5 rounded">
                            <Clock className="w-3 h-3" />
                            <span>{stop.estimated_arrival}</span>
                          </span>
                          <span className="flex items-center gap-0.5 text-amber-500 font-bold">
                            <Star className="w-3 h-3 fill-amber-400" />
                            <span>{stop.fuji_view_rating}/5</span>
                          </span>
                          <span className="text-[10px] text-slate-400 font-medium truncate">
                            {stop.admission_info}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Step-Free Accessibility Notice */}
                    {stop.accessibility_status === 'VERIFIED_ACCESSIBLE' && (
                      <div className="mt-2 pt-2 border-t border-slate-100 flex items-center gap-1 text-[10px] text-emerald-700">
                        <ShieldCheck className="w-3 h-3 text-emerald-600 shrink-0" />
                        <span className="truncate">Verified Barrier-Free & Step-Free Accessible</span>
                      </div>
                    )}
                  </div>

                  {/* RAPTOR Transit Connection to Next Stop */}
                  {stop.transit_to_next && (
                    <div className="my-2 p-2 rounded-lg bg-slate-50 border border-slate-200 text-[11px] text-slate-600 flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span
                          className="w-2.5 h-2.5 rounded-full shrink-0"
                          style={{ backgroundColor: stop.transit_to_next.route_color || '#0284c7' }}
                        />
                        <span className="font-semibold text-slate-800 flex items-center gap-1">
                          <Bus className="w-3 h-3 text-slate-500" />
                          <span>{stop.transit_to_next.route_name}</span>
                        </span>
                        <span className="text-slate-400">•</span>
                        <span>{stop.transit_to_next.duration_minutes} min</span>
                      </div>
                      <div className="font-semibold text-slate-700 text-[10px]">
                        ¥{stop.transit_to_next.fare_jpy || 0}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

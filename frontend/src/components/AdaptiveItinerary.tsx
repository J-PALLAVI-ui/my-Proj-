import React, { useState, useEffect } from 'react';
import { Journey } from '../types';
import { apiUrl } from '../config';
import { JourneyDisplay } from './JourneyDisplay';
import { Clock, Navigation, CheckCircle2, AlertCircle, RefreshCw, Sparkles, MapPin } from 'lucide-react';

interface AdaptiveItineraryProps {
  originName?: string;
  activeDestinationName: string;
  activeDestinationJa?: string;
  originalDestinationName?: string;
  isAdapted?: boolean;
  crowdReductionPercent?: number;
  onAskHana?: (prompt: string) => void;
}

export const AdaptiveItinerary: React.FC<AdaptiveItineraryProps> = ({
  originName = 'Kawaguchiko Station',
  activeDestinationName,
  activeDestinationJa,
  originalDestinationName,
  isAdapted = false,
  crowdReductionPercent,
  onAskHana,
}) => {
  const [departureTime, setDepartureTime] = useState<string>('09:00');
  const [journeys, setJourneys] = useState<Journey[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRoute = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(apiUrl('/api/transit/plan'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          origin: originName,
          destination: activeDestinationName,
          departure_time: departureTime.length === 5 ? `${departureTime}:00` : departureTime,
          max_transfers: 2,
          max_results: 2,
        }),
      });

      if (!response.ok) {
        throw new Error(`Transit calculation error: HTTP ${response.status}`);
      }

      const data = await response.json();
      if (data.journeys && data.journeys.length > 0) {
        setJourneys(data.journeys);
      } else {
        // Fallback for destination where RAPTOR stop matching was queried
        setJourneys([]);
        setError(
          `No direct scheduled bus timetable found for "${activeDestinationName}" at ${departureTime}. You may explore local shuttle or taxi connections from Kawaguchiko Station.`
        );
      }
    } catch (err: any) {
      console.warn('Adaptive transit calculation failed:', err);
      setError(
        `Unable to reach the Stage 2 RAPTOR routing engine. Check that the backend server is running.`
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRoute();
  }, [activeDestinationName, departureTime]);

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden p-6 mt-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-slate-100 gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-sky-100 text-sky-700">
              <Navigation className="w-5 h-5" />
            </span>
            <h2 className="text-lg font-bold text-slate-900">Adaptive Transit Itinerary</h2>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Deterministic GTFS RAPTOR routing engine with crowd-adapted destination re-targeting.
          </p>
        </div>

        {/* Departure Time Control */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-xs text-slate-600 bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-lg">
            <Clock className="w-4 h-4 text-slate-400" />
            <span className="font-medium">Depart at:</span>
            <select
              value={departureTime}
              onChange={(e) => setDepartureTime(e.target.value)}
              className="bg-transparent font-bold text-slate-800 outline-none cursor-pointer"
            >
              <option value="09:00">09:00 AM</option>
              <option value="10:00">10:00 AM</option>
              <option value="11:00">11:00 AM</option>
              <option value="13:00">01:00 PM</option>
              <option value="14:30">02:30 PM</option>
            </select>
          </div>

          <button
            onClick={fetchRoute}
            disabled={loading}
            className="p-2 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition-colors"
            title="Recalculate route"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Adaptive Status Banner */}
      {isAdapted ? (
        <div className="mt-4 p-4 rounded-xl bg-gradient-to-r from-emerald-500/10 via-emerald-500/5 to-transparent border border-emerald-300 flex items-start gap-3">
          <div className="p-1 rounded-full bg-emerald-100 text-emerald-700 mt-0.5">
            <CheckCircle2 className="w-5 h-5" />
          </div>
          <div className="flex-1 text-xs">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-bold text-emerald-900 uppercase tracking-wide">
                Adaptive Route Active
              </span>
              <span className="bg-emerald-600 text-white font-bold px-2 py-0.5 rounded-full text-[10px]">
                -{crowdReductionPercent || 75}% Crowd Reduction
              </span>
            </div>
            <p className="text-emerald-800 mt-1 leading-relaxed">
              Your destination was dynamically adapted from{' '}
              <strong className="text-slate-900">{originalDestinationName || 'Oishi Park'}</strong> to{' '}
              <strong className="text-emerald-950 font-bold underline decoration-emerald-500">
                {activeDestinationName} {activeDestinationJa ? `(${activeDestinationJa})` : ''}
              </strong>{' '}
              to avoid high congestion while preserving scenic Mount Fuji views.
            </p>
          </div>
        </div>
      ) : (
        <div className="mt-4 p-3 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between text-xs text-slate-600">
          <div className="flex items-center gap-2">
            <MapPin className="w-4 h-4 text-sky-600" />
            <span>
              Direct Route to: <strong>{activeDestinationName}</strong>
            </span>
          </div>
          <span className="text-[11px] text-slate-400">Original Target</span>
        </div>
      )}

      {/* Journeys List */}
      <div className="mt-6">
        {loading ? (
          <div className="py-12 flex flex-col items-center justify-center text-slate-400 gap-2">
            <RefreshCw className="w-6 h-6 animate-spin text-sky-600" />
            <span className="text-xs font-medium">Computing optimal GTFS connections...</span>
          </div>
        ) : error ? (
          <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-800 flex items-start gap-2">
            <AlertCircle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="font-semibold">{error}</p>
              {onAskHana && (
                <button
                  onClick={() =>
                    onAskHana(`How do I travel from ${originName} to ${activeDestinationName} at ${departureTime}?`)
                  }
                  className="mt-2 text-xs font-bold text-sky-700 hover:text-sky-900 flex items-center gap-1"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  Ask Hana to plan transport for {activeDestinationName}
                </button>
              )}
            </div>
          </div>
        ) : journeys.length > 0 ? (
          <JourneyDisplay journeys={journeys} />
        ) : (
          <div className="py-8 text-center text-xs text-slate-400">
            No journeys available. Select a destination or change departure time.
          </div>
        )}
      </div>
    </div>
  );
};

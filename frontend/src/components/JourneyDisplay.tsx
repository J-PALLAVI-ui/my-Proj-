import React from 'react';
import { Journey, JourneyLeg } from '../types';
import { Bus, Train, Footprints, Clock, ArrowRight, ShieldCheck, AlertTriangle } from 'lucide-react';

interface JourneyDisplayProps {
  journeys: Journey[];
}

export const JourneyDisplay: React.FC<JourneyDisplayProps> = ({ journeys }) => {
  if (!journeys || journeys.length === 0) return null;

  return (
    <div className="space-y-4 my-3">
      {journeys.map((journey, jIdx) => (
        <div
          key={journey.journey_id || `journey-${jIdx}`}
          className="border border-slate-200 rounded-xl bg-white shadow-sm overflow-hidden"
        >
          {/* Journey Header */}
          <div className="bg-slate-50 px-4 py-3 border-b border-slate-200 flex flex-wrap items-center justify-between gap-2">
            <div className="flex items-center space-x-2">
              <span className="text-base font-bold text-slate-800">
                {journey.departure_time}
              </span>
              <ArrowRight className="w-4 h-4 text-slate-400" />
              <span className="text-base font-bold text-slate-800">
                {journey.arrival_time}
              </span>
              <span className="text-xs bg-slate-200 text-slate-700 px-2 py-0.5 rounded-full font-medium flex items-center ml-2">
                <Clock className="w-3 h-3 mr-1 inline" />
                {journey.total_duration_minutes} min
              </span>
            </div>

            <div className="flex items-center space-x-2">
              <span className="text-xs bg-sky-100 text-sky-800 px-2.5 py-0.5 rounded-full font-medium">
                {journey.transfers_count === 0 ? 'Direct (0 transfers)' : `${journey.transfers_count} transfer${journey.transfers_count > 1 ? 's' : ''}`}
              </span>
              {journey.total_fare_jpy !== null && journey.total_fare_jpy !== undefined ? (
                <span className="text-xs bg-emerald-100 text-emerald-800 px-2.5 py-0.5 rounded-full font-bold">
                  ¥{journey.total_fare_jpy.toLocaleString()}
                </span>
              ) : (
                <span className="text-xs bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full font-medium">
                  Fare unavailable
                </span>
              )}
            </div>
          </div>

          {/* Journey Legs Timeline */}
          <div className="p-4 space-y-4">
            {journey.legs.map((leg, lIdx) => (
              <LegItem key={`${journey.journey_id}-leg-${lIdx}`} leg={leg} isLast={lIdx === journey.legs.length - 1} />
            ))}
          </div>

          {/* Warnings & Provenance Badges Footer */}
          <div className="bg-slate-50/70 px-4 py-2.5 border-t border-slate-100 text-xs text-slate-500 flex flex-col gap-1.5">
            {journey.warnings && journey.warnings.map((warn, wIdx) => (
              <div key={wIdx} className="flex items-center text-amber-700 bg-amber-50 px-2 py-1 rounded">
                <AlertTriangle className="w-3.5 h-3.5 mr-1.5 flex-shrink-0" />
                <span>{warn}</span>
              </div>
            ))}
            <div className="flex flex-wrap items-center gap-1.5 text-[11px]">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0" />
              <span className="font-semibold text-slate-600">Verified Sources:</span>
              {journey.provenance_badges && journey.provenance_badges.map((badge, bIdx) => (
                <span key={bIdx} className="bg-slate-200/80 text-slate-700 px-2 py-0.5 rounded font-mono">
                  {badge}
                </span>
              ))}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

const LegItem: React.FC<{ leg: JourneyLeg; isLast: boolean }> = ({ leg, isLast }) => {
  const isWalk = leg.mode === 'walk';
  const isRail = leg.mode === 'rail';

  const getModeIcon = () => {
    if (isWalk) return <Footprints className="w-4 h-4 text-slate-500" />;
    if (isRail) return <Train className="w-4 h-4 text-white" />;
    return <Bus className="w-4 h-4 text-white" />;
  };

  return (
    <div className="relative flex items-start space-x-3">
      {/* Icon Chip with Official Route Color */}
      <div
        className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 shadow-xs z-10"
        style={{
          backgroundColor: isWalk ? '#E2E8F0' : leg.route_color || '#1E3A8A'
        }}
      >
        {getModeIcon()}
      </div>

      {/* Vertical connection line if not last */}
      {!isLast && (
        <div className="absolute left-4 top-8 -bottom-4 w-0.5 bg-slate-200 -translate-x-1/2" />
      )}

      {/* Leg Details */}
      <div className="flex-1 bg-slate-50/50 p-2.5 rounded-lg border border-slate-100">
        <div className="flex items-center justify-between mb-1">
          <div className="flex items-center space-x-1.5 flex-wrap">
            <span
              className="px-2 py-0.5 rounded text-xs font-bold"
              style={{
                backgroundColor: isWalk ? '#CBD5E1' : leg.route_color || '#1E3A8A',
                color: isWalk ? '#334155' : leg.route_text_color || '#FFFFFF'
              }}
            >
              {leg.route_short_name || leg.operator}
            </span>
            <span className="text-xs font-semibold text-slate-800">
              {leg.operator}
            </span>
            {leg.trip_headsign && (
              <span className="text-[11px] text-slate-500">
                {leg.trip_headsign}
              </span>
            )}
          </div>

          {leg.fare_jpy !== null && leg.fare_jpy !== undefined && !isWalk && (
            <span className="text-xs font-bold text-slate-700 bg-white px-2 py-0.5 rounded border border-slate-200">
              ¥{leg.fare_jpy.toLocaleString()}
            </span>
          )}
        </div>

        {/* Departure & Arrival Stops */}
        <div className="text-xs space-y-1 mt-1.5">
          <div className="flex justify-between items-baseline">
            <span className="text-slate-800 font-medium">
              <span className="font-mono font-bold text-slate-900 mr-1.5">{leg.departure_time}</span>
              {leg.origin_stop_name_en}
              <span className="text-slate-400 text-[11px] ml-1">({leg.origin_stop_name})</span>
            </span>
          </div>

          {leg.intermediate_stops_count > 0 && (
            <div className="text-[11px] text-slate-500 pl-4 py-0.5 border-l-2 border-slate-300 my-0.5">
              Ride {leg.duration_minutes} min ({leg.intermediate_stops_count} intermediate stops)
            </div>
          )}

          <div className="flex justify-between items-baseline">
            <span className="text-slate-800 font-medium">
              <span className="font-mono font-bold text-slate-900 mr-1.5">{leg.arrival_time}</span>
              {leg.destination_stop_name_en}
              <span className="text-slate-400 text-[11px] ml-1">({leg.destination_stop_name})</span>
            </span>
          </div>
        </div>

        {/* Provenance and Advisory */}
        <div className="mt-2 pt-1 border-t border-slate-200/60 flex flex-wrap items-center justify-between text-[11px] text-slate-500">
          <span className="font-mono text-[10px] text-slate-600">
            {leg.provenance_badge}
          </span>
          {leg.advisory_notes && (
            <span className="text-amber-700 text-[11px]">
              {leg.advisory_notes}
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

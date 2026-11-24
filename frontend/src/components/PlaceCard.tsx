import React from 'react';
import { Place } from '../types';
import { ExternalLink, Eye, AlertTriangle, CheckCircle, Clock } from 'lucide-react';

interface PlaceCardProps {
  place: Place;
}

export const PlaceCard: React.FC<PlaceCardProps> = ({ place }) => {
  const isAccessible = place.accessibility_status === 'VERIFIED_ACCESSIBLE';
  const isSteepStairs = place.accessibility_status === 'STEEP_STAIRS';

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden hover:shadow-md transition-shadow flex flex-col justify-between">
      <div className="p-4">
        {/* Header: Name and Fuji Rating */}
        <div className="flex items-start justify-between gap-2">
          <div>
            <h3 className="font-bold text-slate-900 text-base leading-tight">
              {place.name_ja}
            </h3>
            {place.name_en && (
              <p className="text-xs text-slate-500 font-medium">{place.name_en}</p>
            )}
          </div>
          <div className="flex items-center gap-1 bg-sky-50 text-sky-700 px-2 py-0.5 rounded-full text-xs font-semibold shrink-0">
            <Eye className="w-3.5 h-3.5" />
            <span>Fuji {place.fuji_view_rating}/5</span>
          </div>
        </div>

        {/* Category & Status Badges */}
        <div className="flex flex-wrap items-center gap-1.5 mt-2.5 text-xs">
          <span className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 capitalize font-medium">
            {place.primary_category}
          </span>
          <span className={`px-2 py-0.5 rounded-md font-medium ${
            place.general_admission_type === 'FREE'
              ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
              : 'bg-amber-50 text-amber-700 border border-amber-200'
          }`}>
            {place.general_admission_type === 'FREE'
              ? 'Free Admission'
              : `¥${place.general_admission_fee_jpy?.toLocaleString() ?? 'Paid'}`}
          </span>
          {place.indoor_alternative && (
            <span className="px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-700 border border-indigo-200 font-medium">
              Indoor Option
            </span>
          )}
        </div>

        {/* Opening Hours */}
        <div className="mt-3 flex items-start gap-1.5 text-xs text-slate-600">
          <Clock className="w-3.5 h-3.5 text-slate-400 mt-0.5 shrink-0" />
          <div>
            <span className="font-semibold text-slate-700">Hours: </span>
            <span>{place.opening_hours_text || 'See official site'}</span>
            {place.opening_status === 'ALWAYS_OPEN' && (
              <span className="ml-1 text-emerald-600 font-medium">(24 Hours)</span>
            )}
          </div>
        </div>

        {/* Optional Activities / Caveat Note */}
        {place.optional_activities_fee_desc && (
          <p className="mt-2 text-xs bg-slate-50 p-2 rounded border border-slate-100 text-slate-600 italic">
            Note: {place.optional_activities_fee_desc}
          </p>
        )}

        {/* Accessibility & Stairs */}
        <div className={`mt-3 p-2 rounded-lg text-xs flex items-start gap-1.5 ${
          isAccessible
            ? 'bg-emerald-50 text-emerald-800'
            : isSteepStairs
            ? 'bg-rose-50 text-rose-800 border border-rose-200'
            : 'bg-amber-50 text-amber-800'
        }`}>
          {isAccessible ? (
            <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
          ) : (
            <AlertTriangle className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" />
          )}
          <div>
            <span className="font-semibold">
              {isAccessible ? 'Barrier-Free Accessible' : isSteepStairs ? 'Steep Stairs Warning' : 'Partial Steps'}
            </span>
            {place.stair_step_count ? ` (${place.stair_step_count} stairs)` : ''}:
            <span className="block mt-0.5 text-slate-600">
              {place.accessibility_evidence || 'Exercise standard care.'}
            </span>
          </div>
        </div>
      </div>

      {/* Footer Provenance */}
      <div className="px-4 py-2.5 bg-slate-50 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
        <span className="truncate max-w-[200px]" title={place.required_attribution}>
          {place.required_attribution}
        </span>
        <a
          href={place.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1 text-sky-600 hover:text-sky-800 font-medium shrink-0 ml-2"
        >
          <span>Official Site</span>
          <ExternalLink className="w-3 h-3" />
        </a>
      </div>
    </div>
  );
};

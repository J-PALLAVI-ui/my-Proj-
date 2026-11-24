import React from 'react';
import { PlaceCrowdStatus, CrowdAlternativeCard } from '../types';
import { X, Check, ArrowRight, Mountain, ShieldCheck, Footprints, DollarSign, Users } from 'lucide-react';

interface DestinationComparisonModalProps {
  isOpen: boolean;
  onClose: () => void;
  originalPlace: PlaceCrowdStatus | null;
  alternative: CrowdAlternativeCard | null;
  onSelectAlternative: (alternative: CrowdAlternativeCard) => void;
}

export const DestinationComparisonModal: React.FC<DestinationComparisonModalProps> = ({
  isOpen,
  onClose,
  originalPlace,
  alternative,
  onSelectAlternative,
}) => {
  if (!isOpen || !alternative) return null;

  const altNameEn = alternative.name_en || alternative.place?.name_en || 'Alternative Destination';
  const altNameJa = alternative.name_ja || alternative.place?.name_ja || '';
  const altReduction = alternative.crowd_reduction_percent ?? alternative.crowd_reduction_pct ?? 0;
  const altCrowdLevel = (alternative.crowd_level || alternative.crowd_status?.level || 'low').toLowerCase();
  const altCrowdScore = alternative.crowd_index ?? alternative.crowd_status?.score ?? 25;
  const altFujiRating = alternative.fuji_view_rating ?? alternative.place?.fuji_view_rating ?? 4;
  const altAccess = alternative.accessibility_status || alternative.place?.accessibility_status || 'VERIFIED_ACCESSIBLE';
  const altFee = alternative.admission_fee_jpy ?? alternative.place?.general_admission_fee_jpy;

  const origNameEn = originalPlace?.name_en || 'Oishi Park';
  const origNameJa = originalPlace?.name_ja || '大石公園';
  const origCrowdLevel = (originalPlace?.crowd_level || originalPlace?.level || 'high').toLowerCase();
  const origCrowdScore = originalPlace?.crowd_index ?? originalPlace?.score ?? 88;
  const origFujiRating = originalPlace?.fuji_view_rating ?? 5;
  const origAccess = originalPlace?.accessibility_status || 'VERIFIED_ACCESSIBLE';
  const origAdvisory = originalPlace?.congestion_advisory || originalPlace?.advisory || 'Heavy tourist crowding reported.';

  const getCrowdBadgeClass = (level: string) => {
    switch (level.toLowerCase()) {
      case 'low':
        return 'bg-emerald-100 text-emerald-800 border-emerald-300';
      case 'moderate':
        return 'bg-amber-100 text-amber-800 border-amber-300';
      case 'high':
        return 'bg-rose-100 text-rose-800 border-rose-300';
      case 'packed':
        return 'bg-purple-100 text-purple-800 border-purple-300';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-300';
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in duration-200"
      role="dialog"
      aria-modal="true"
      aria-labelledby="comparison-title"
    >
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto flex flex-col border border-slate-200">
        {/* Modal Header */}
        <div className="p-6 border-b border-slate-100 flex items-center justify-between sticky top-0 bg-white/95 backdrop-blur-xs z-10">
          <div>
            <span className="text-xs font-bold tracking-wider uppercase text-sky-600 bg-sky-50 px-2.5 py-1 rounded-full border border-sky-200">
              Side-by-Side Destination Comparison
            </span>
            <h2 id="comparison-title" className="text-xl font-bold text-slate-900 mt-2">
              Compare Congested vs. Quieter Alternative
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-full transition-colors"
            aria-label="Close comparison modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Delta Callout Banner */}
        <div className="bg-emerald-50 border-y border-emerald-200 px-6 py-3 flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-sm font-semibold text-emerald-900">
              Crowd Reduction Advantage: -{altReduction}% Fewer Visitors
            </span>
          </div>
          <span className="text-xs text-emerald-700 bg-white/80 px-2.5 py-0.5 rounded-full border border-emerald-300 font-medium">
            Distance: {alternative.distance_km} km away
          </span>
        </div>

        {/* Comparison Grid */}
        <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6 flex-1">
          {/* Original Destination Card */}
          <div className="border-2 border-slate-200 rounded-xl overflow-hidden bg-slate-50/50 flex flex-col">
            <div className="relative h-48 bg-slate-200 overflow-hidden">
              <img
                src={originalPlace?.image_url || 'https://images.unsplash.com/photo-1578637387939-43c525550085?auto=format&fit=crop&w=800&q=80'}
                alt={origNameEn}
                className="w-full h-full object-cover"
                onError={(e) => {
                  (e.currentTarget as HTMLImageElement).src =
                    'https://images.unsplash.com/photo-1578637387939-43c525550085?auto=format&fit=crop&w=800&q=80';
                }}
              />
              <div className="absolute top-3 left-3">
                <span className="bg-slate-900/80 backdrop-blur-xs text-white text-xs font-semibold px-2.5 py-1 rounded-md">
                  Original Destination
                </span>
              </div>
              <div className="absolute bottom-2 right-2">
                <span
                  className={`text-xs font-bold uppercase px-2.5 py-0.5 rounded-full border shadow-xs ${getCrowdBadgeClass(
                    origCrowdLevel
                  )}`}
                >
                  {origCrowdLevel} Crowd
                </span>
              </div>
            </div>

            <div className="p-5 flex-1 flex flex-col justify-between">
              <div>
                <h3 className="text-lg font-bold text-slate-900">{origNameEn}</h3>
                <p className="text-xs text-slate-500 font-medium">{origNameJa}</p>

                <div className="mt-4 space-y-3 text-xs">
                  <div className="flex items-center justify-between py-1.5 border-b border-slate-200">
                    <span className="text-slate-500 flex items-center gap-1.5">
                      <Users className="w-3.5 h-3.5 text-slate-400" />
                      Crowd Congestion
                    </span>
                    <span className="font-bold text-rose-600">
                      Level: {origCrowdLevel.toUpperCase()} ({origCrowdScore}/100)
                    </span>
                  </div>

                  <div className="flex items-center justify-between py-1.5 border-b border-slate-200">
                    <span className="text-slate-500 flex items-center gap-1.5">
                      <Mountain className="w-3.5 h-3.5 text-sky-500" />
                      Fuji View Rating
                    </span>
                    <span className="font-semibold text-slate-800">
                      {'★'.repeat(origFujiRating)} ({origFujiRating}/5)
                    </span>
                  </div>

                  <div className="flex items-center justify-between py-1.5 border-b border-slate-200">
                    <span className="text-slate-500 flex items-center gap-1.5">
                      <Footprints className="w-3.5 h-3.5 text-emerald-500" />
                      Accessibility
                    </span>
                    <span className="font-medium text-slate-700 capitalize">
                      {origAccess.replace(/_/g, ' ').toLowerCase()}
                    </span>
                  </div>

                  <div className="flex items-center justify-between py-1.5 border-b border-slate-200">
                    <span className="text-slate-500 flex items-center gap-1.5">
                      <DollarSign className="w-3.5 h-3.5 text-amber-500" />
                      Admission
                    </span>
                    <span className="font-medium text-slate-700">Free / Open</span>
                  </div>
                </div>

                <div className="mt-4 p-3 bg-rose-50 border border-rose-200 rounded-lg text-xs text-rose-800">
                  <span className="font-semibold block mb-0.5">Congestion Notice:</span>
                  {origAdvisory}
                </div>
              </div>
            </div>
          </div>

          {/* Recommended Alternative Card */}
          <div className="border-2 border-emerald-400 rounded-xl overflow-hidden bg-emerald-50/20 flex flex-col ring-2 ring-emerald-400/20 shadow-md">
            <div className="relative h-48 bg-slate-200 overflow-hidden">
              <img
                src={alternative.image_url}
                alt={altNameEn}
                className="w-full h-full object-cover"
                onError={(e) => {
                  (e.currentTarget as HTMLImageElement).src =
                    'https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=800&q=80';
                }}
              />
              <div className="absolute top-3 left-3 flex items-center gap-1.5">
                <span className="bg-emerald-600 text-white text-xs font-bold px-2.5 py-1 rounded-md shadow-xs flex items-center gap-1">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  Recommended Alternative
                </span>
              </div>
              <div className="absolute bottom-2 right-2">
                <span
                  className={`text-xs font-bold uppercase px-2.5 py-0.5 rounded-full border shadow-xs ${getCrowdBadgeClass(
                    altCrowdLevel
                  )}`}
                >
                  {altCrowdLevel} Crowd
                </span>
              </div>
            </div>

            <div className="p-5 flex-1 flex flex-col justify-between">
              <div>
                <h3 className="text-lg font-bold text-slate-900">{altNameEn}</h3>
                <p className="text-xs text-slate-500 font-medium">{altNameJa}</p>

                <div className="mt-4 space-y-3 text-xs">
                  <div className="flex items-center justify-between py-1.5 border-b border-emerald-100">
                    <span className="text-slate-500 flex items-center gap-1.5">
                      <Users className="w-3.5 h-3.5 text-emerald-600" />
                      Crowd Reduction
                    </span>
                    <span className="font-bold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded-full">
                      -{altReduction}% reduction ({altCrowdScore}/100)
                    </span>
                  </div>

                  <div className="flex items-center justify-between py-1.5 border-b border-emerald-100">
                    <span className="text-slate-500 flex items-center gap-1.5">
                      <Mountain className="w-3.5 h-3.5 text-sky-500" />
                      Fuji View Rating
                    </span>
                    <span className="font-semibold text-slate-800">
                      {'★'.repeat(altFujiRating)} ({altFujiRating}/5)
                    </span>
                  </div>

                  <div className="flex items-center justify-between py-1.5 border-b border-emerald-100">
                    <span className="text-slate-500 flex items-center gap-1.5">
                      <Footprints className="w-3.5 h-3.5 text-emerald-500" />
                      Accessibility
                    </span>
                    <span className="font-medium text-slate-700 capitalize">
                      {altAccess.replace(/_/g, ' ').toLowerCase()}
                    </span>
                  </div>

                  <div className="flex items-center justify-between py-1.5 border-b border-emerald-100">
                    <span className="text-slate-500 flex items-center gap-1.5">
                      <DollarSign className="w-3.5 h-3.5 text-amber-500" />
                      Admission
                    </span>
                    <span className="font-medium text-slate-700">
                      {altFee ? `${altFee} JPY` : 'Free Admission'}
                    </span>
                  </div>
                </div>

                <div className="mt-4 p-3 bg-emerald-100/60 border border-emerald-200 rounded-lg text-xs text-emerald-900">
                  <span className="font-semibold block mb-0.5">Why this fits:</span>
                  {alternative.recommendation_reason}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="p-6 border-t border-slate-100 bg-slate-50 flex items-center justify-between flex-wrap gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold text-slate-600 hover:text-slate-800 hover:bg-slate-200 rounded-lg transition-colors"
          >
            Keep Original Destination
          </button>
          <button
            onClick={() => {
              onSelectAlternative(alternative);
              onClose();
            }}
            className="flex items-center gap-2 px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-bold shadow-md transition-all transform active:scale-95"
          >
            <Check className="w-4 h-4" />
            <span>Select {altNameEn} & Recalculate Route</span>
            <ArrowRight className="w-4 h-4 ml-1" />
          </button>
        </div>
      </div>
    </div>
  );
};

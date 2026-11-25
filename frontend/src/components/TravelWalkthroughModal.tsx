import React from 'react';
import { useTrip } from '../context/TripContext';
import { 
  X, 
  ChevronLeft, 
  ChevronRight, 
  MapPin, 
  Bus, 
  Footprints, 
  Utensils, 
  Mountain, 
  RotateCcw, 
  CreditCard,
  MessageSquare,
  AlertCircle
} from 'lucide-react';

interface TravelWalkthroughModalProps {
  onAskHana?: (prompt: string) => void;
}

export const TravelWalkthroughModal: React.FC<TravelWalkthroughModalProps> = ({ onAskHana }) => {
  const {
    isWalkthroughOpen,
    closeWalkthrough,
    activeItinerary,
    activeWalkthroughStep,
    nextWalkthroughStep,
    prevWalkthroughStep,
    setWalkthroughStep
  } = useTrip();

  if (!isWalkthroughOpen || !activeItinerary) return null;

  const currentStep = activeItinerary.steps[activeWalkthroughStep] || activeItinerary.steps[0];
  const totalSteps = activeItinerary.steps.length;

  const getStepIcon = (type: string) => {
    switch (type.toUpperCase()) {
      case 'WALK':
        return <Footprints className="w-5 h-5 text-emerald-600" />;
      case 'TRANSIT':
        return <Bus className="w-5 h-5 text-sky-600" />;
      case 'SIGHTSEEING':
        return <Mountain className="w-5 h-5 text-indigo-600" />;
      case 'MEAL':
        return <Utensils className="w-5 h-5 text-amber-600" />;
      case 'RETURN':
        return <RotateCcw className="w-5 h-5 text-blue-600" />;
      default:
        return <MapPin className="w-5 h-5 text-slate-600" />;
    }
  };

  const cost = activeItinerary.cost_summary;
  const recommendedPass = cost?.recommended_option;

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto animate-in fade-in duration-200">
      <div className="bg-white rounded-3xl max-w-2xl w-full border border-[#E1EAF1] shadow-2xl overflow-hidden flex flex-col my-auto max-h-[92vh]">
        {/* Header */}
        <div className="p-5 border-b border-[#E1EAF1] flex items-center justify-between bg-[#F5F8FB]">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-bold text-[#078ACB] uppercase tracking-wider bg-[#EBF5FB] px-2 py-0.5 rounded border border-[#BDE0F5]">
                Step-by-Step Travel Guide • {activeItinerary.time_budget_hours} Hours
              </span>
              <span className="text-[10px] font-bold text-slate-500 bg-white px-2 py-0.5 rounded border border-slate-200">
                {activeItinerary.departure_time} - {activeItinerary.return_time}
              </span>
            </div>
            <h2 className="text-base font-bold text-[#14283F] mt-1 truncate">
              {activeItinerary.title}
            </h2>
          </div>

          <button
            onClick={closeWalkthrough}
            className="w-8 h-8 rounded-full bg-white hover:bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-500 transition-colors shadow-2xs"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Step Progression Tabs */}
        <div className="flex items-center gap-1.5 px-5 py-3 border-b border-[#E1EAF1] overflow-x-auto bg-white shrink-0 scrollbar-none">
          {activeItinerary.steps.map((st, idx) => (
            <button
              key={st.step_number}
              onClick={() => setWalkthroughStep(idx)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all whitespace-nowrap shrink-0 ${
                activeWalkthroughStep === idx
                  ? 'bg-[#078ACB] text-white shadow-xs'
                  : 'bg-[#F5F8FB] text-[#718198] hover:bg-[#E1EAF1]'
              }`}
            >
              <span>{st.step_number}.</span>
              <span className="truncate max-w-[110px]">{st.title}</span>
            </button>
          ))}
        </div>

        {/* Modal Main Content */}
        <div className="p-6 space-y-5 overflow-y-auto flex-1">
          {/* Active Step Card */}
          <div className="bg-[#F5F8FB] border border-[#E1EAF1] rounded-2xl p-5 space-y-4 shadow-2xs">
            <div className="flex items-start gap-3.5">
              <div className="w-10 h-10 rounded-2xl bg-white border border-[#E1EAF1] shadow-xs flex items-center justify-center shrink-0">
                {getStepIcon(currentStep.step_type)}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-[#078ACB]">
                    STEP {currentStep.step_number} of {totalSteps} • {currentStep.step_type}
                  </span>
                  <span className="text-xs font-mono font-bold text-[#14283F] bg-white px-2 py-0.5 rounded border border-[#E1EAF1]">
                    {currentStep.departure_time} - {currentStep.arrival_time} ({currentStep.duration_minutes} min)
                  </span>
                </div>
                <h3 className="text-base font-bold text-[#14283F] mt-0.5">
                  {currentStep.title}
                </h3>
                <p className="text-xs text-[#718198] mt-0.5">
                  Location: {currentStep.location_name}
                </p>
              </div>
            </div>

            {/* Instruction Callout */}
            <div className="p-4 bg-white rounded-xl border border-[#E1EAF1] space-y-2">
              <p className="text-xs font-medium text-[#14283F] leading-relaxed">
                {currentStep.instruction}
              </p>
              {currentStep.notes && (
                <p className="text-[11px] text-[#718198] pt-1.5 border-t border-slate-100">
                  💡 {currentStep.notes}
                </p>
              )}
            </div>

            {/* Transit Specifics (if transit leg) */}
            {currentStep.step_type === 'TRANSIT' && (
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 text-xs">
                <div className="p-2.5 bg-white rounded-xl border border-[#E1EAF1]">
                  <span className="text-[10px] text-[#718198] block">Service Line</span>
                  <span className="font-bold text-[#14283F] truncate block">
                    {currentStep.route_name || 'Sightseeing Bus'}
                  </span>
                </div>
                <div className="p-2.5 bg-white rounded-xl border border-[#E1EAF1]">
                  <span className="text-[10px] text-[#718198] block">Operator</span>
                  <span className="font-bold text-[#14283F] block">
                    {currentStep.operator || 'Fujikyu Bus'}
                  </span>
                </div>
                <div className="p-2.5 bg-white rounded-xl border border-[#E1EAF1]">
                  <span className="text-[10px] text-[#718198] block">Estimated Fare</span>
                  <span className="font-bold text-emerald-700 block">
                    ¥{currentStep.fare_jpy ?? 570}
                  </span>
                </div>
              </div>
            )}

            {/* Crowd Forecast Pill (if attraction) */}
            {currentStep.crowd_forecast && (
              <div className="flex items-center justify-between p-3 bg-white rounded-xl border border-[#E1EAF1] text-xs">
                <span className="text-[#718198]">Seasonal Crowd Forecast:</span>
                <span className="font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                  {currentStep.crowd_forecast.level_label} ({currentStep.crowd_forecast.score}/100)
                </span>
              </div>
            )}
          </div>

          {/* Fare & Pass Optimization Section */}
          {recommendedPass && (
            <div className="p-4 rounded-2xl bg-sky-50/70 border border-sky-200 space-y-2.5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <CreditCard className="w-4 h-4 text-[#078ACB]" />
                  <span className="text-xs font-bold text-[#14283F]">
                    Transport Fare & Pass Optimization
                  </span>
                </div>
                <span className="text-[10px] font-bold text-emerald-700 bg-emerald-100/70 px-2 py-0.5 rounded">
                  Best Option: {recommendedPass.title}
                </span>
              </div>

              <p className="text-xs text-[#425466] leading-relaxed">
                {recommendedPass.recommendation_reason} Total Estimated Travel Cost: <strong>¥{recommendedPass.total_cost_jpy.toLocaleString()}</strong>.
              </p>

              {/* Mandatory JR Pass Exclusion Alert */}
              <div className="flex items-start gap-2 pt-2 border-t border-sky-200/60 text-[11px] text-amber-900 bg-amber-50/90 p-2.5 rounded-xl border border-amber-200/80">
                <AlertCircle className="w-3.5 h-3.5 text-amber-600 shrink-0 mt-0.5" />
                <span>
                  <strong>JR Pass Notice:</strong> The Japan Rail Pass does not cover Fujikyu Railway (Otsuki to Kawaguchiko) or sightseeing buses. Local fares or a Fujikyu Pass are required.
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Footer Navigation */}
        <div className="p-5 border-t border-[#E1EAF1] bg-[#F5F8FB] flex items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <button
              onClick={prevWalkthroughStep}
              disabled={activeWalkthroughStep === 0}
              className="flex items-center gap-1 px-3 py-2 rounded-xl border border-[#E1EAF1] bg-white hover:bg-slate-50 text-xs font-bold text-[#14283F] disabled:opacity-40 transition-colors shadow-2xs"
            >
              <ChevronLeft className="w-4 h-4" />
              <span>Previous Step</span>
            </button>

            <button
              onClick={nextWalkthroughStep}
              disabled={activeWalkthroughStep === totalSteps - 1}
              className="flex items-center gap-1 px-3 py-2 rounded-xl bg-[#078ACB] hover:bg-[#0070A8] text-xs font-bold text-white disabled:opacity-40 transition-colors shadow-xs"
            >
              <span>Next Step</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>

          {onAskHana && (
            <button
              onClick={() => {
                onAskHana(`Explain Step ${currentStep.step_number}: ${currentStep.title}. Where do I board and what should I prepare?`);
                closeWalkthrough();
              }}
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-white border border-[#BDE0F5] text-[#078ACB] hover:bg-[#EBF5FB] text-xs font-semibold transition-colors shadow-2xs"
            >
              <MessageSquare className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Ask Hana About This Step</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

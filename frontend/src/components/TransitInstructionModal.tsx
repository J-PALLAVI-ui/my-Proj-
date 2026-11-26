import React from 'react';
import { useTrip } from '../context/TripContext';
import { 
  Bus, 
  X, 
  MapPin, 
  Navigation, 
  Clock, 
  Coins, 
  RefreshCw, 
  ArrowRight, 
  Footprints
} from 'lucide-react';

interface TransitInstructionModalProps {
  isOpen: boolean;
  onClose: () => void;
  destinationName?: string;
  destinationNameJa?: string;
  onOpenRoute?: () => void;
  onConfirmDepart?: () => void;
}

export const TransitInstructionModal: React.FC<TransitInstructionModalProps> = ({
  isOpen,
  onClose,
  destinationName = 'Oishi Park',
  destinationNameJa = '大石公園',
  onOpenRoute,
  onConfirmDepart,
}) => {
  const { currentLocation, activeTransitModalStep } = useTrip();

  if (!isOpen) return null;

  const currentStep = activeTransitModalStep || {
    bus_photo: 'https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?auto=format&fit=crop&w=800&q=80',
    walking_time_min: 4,
    walking_dist_m: 320,
    stop_name: `${currentLocation.name.split('(')[0].trim()} bus stop`,
    operator: 'Fujikyu Bus',
    route_name: 'Red Line (Kawaguchiko Sightseeing Bus)',
    destination_stop: `${destinationName} (${destinationNameJa})`,
    departure_time: '09:55 (Scheduled)',
    fare_adult_jpy: 580,
    has_live_telemetry: false,
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in duration-200">
      <div 
        className="bg-white rounded-3xl shadow-2xl border border-slate-100 max-w-2xl w-full overflow-hidden transition-all transform scale-100"
        role="dialog"
        aria-modal="true"
        aria-labelledby="transit-modal-title"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-[#F8FAFC]">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-full bg-[#078ACB]/10 flex items-center justify-center text-[#078ACB]">
              <Bus className="w-4 h-4" />
            </div>
            <h3 id="transit-modal-title" className="text-base font-bold text-[#14283F]">
              Next bus
            </h3>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full flex items-center justify-center text-slate-400 hover:text-slate-600 hover:bg-slate-200/50 transition-colors"
            aria-label="Close modal"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6">
          <div className="grid grid-cols-1 sm:grid-cols-12 gap-5 items-center">
            {/* Bus Photo Column */}
            <div className="sm:col-span-5">
              <div className="relative rounded-2xl overflow-hidden aspect-4/3 shadow-sm border border-slate-100 bg-slate-100">
                <img
                  src={currentStep.bus_photo || 'https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?auto=format&fit=crop&w=800&q=80'}
                  alt="Fujikyu Transit Bus"
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    (e.currentTarget as HTMLImageElement).src =
                      'https://images.unsplash.com/photo-1570125909232-eb263c188f7e?auto=format&fit=crop&w=800&q=80';
                  }}
                />
                <div className="absolute top-2 left-2 bg-[#14283F]/80 backdrop-blur-xs text-white text-[10px] font-bold px-2 py-0.5 rounded-full">
                  Fujikyu Sightseeing
                </div>
              </div>
            </div>

            {/* Instruction Details Column */}
            <div className="sm:col-span-7 space-y-3.5">
              {/* Walking Direction Banner */}
              <div className="flex items-start gap-3 p-3 rounded-xl bg-sky-50/80 border border-sky-100 text-[#14283F]">
                <Footprints className="w-5 h-5 text-[#078ACB] shrink-0 mt-0.5" />
                <div className="text-xs">
                  <span className="font-bold text-[#078ACB] block text-sm">
                    Walk {currentStep.walking_time_min} min to {currentStep.stop_name}
                  </span>
                  <span className="text-[#425466]">
                    Approx. {currentStep.walking_dist_m} m from your current location
                  </span>
                </div>
              </div>

              {/* Transit Parameters Table */}
              <div className="rounded-xl border border-slate-100 divide-y divide-slate-100 text-xs">
                <div className="flex items-center justify-between py-2 px-3">
                  <span className="text-slate-500 flex items-center gap-1.5">
                    <Bus className="w-3.5 h-3.5 text-slate-400" />
                    <span>Operator</span>
                  </span>
                  <span className="font-semibold text-[#14283F]">{currentStep.operator}</span>
                </div>

                <div className="flex items-center justify-between py-2 px-3">
                  <span className="text-slate-500 flex items-center gap-1.5">
                    <RefreshCw className="w-3.5 h-3.5 text-slate-400" />
                    <span>Route / Service</span>
                  </span>
                  <div className="flex items-center gap-1.5 text-right">
                    <span className="text-amber-700 bg-amber-50 border border-amber-200 px-1.5 py-0.5 rounded text-[10px] font-medium">
                      Checking live timetable...
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between py-2 px-3">
                  <span className="text-slate-500 flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5 text-slate-400" />
                    <span>Destination Stop</span>
                  </span>
                  <span className="font-semibold text-[#14283F] max-w-[200px] truncate text-right">
                    {currentStep.destination_stop}
                  </span>
                </div>

                <div className="flex items-center justify-between py-2 px-3">
                  <span className="text-slate-500 flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5 text-slate-400" />
                    <span>Departure Time</span>
                  </span>
                  <div className="text-right">
                    <span className="font-semibold text-[#14283F]">{currentStep.departure_time}</span>
                    <span className="text-[10px] text-slate-400 block">(Live data unavailable)</span>
                  </div>
                </div>

                <div className="flex items-center justify-between py-2 px-3">
                  <span className="text-slate-500 flex items-center gap-1.5">
                    <Coins className="w-3.5 h-3.5 text-slate-400" />
                    <span>Fare (Adult)</span>
                  </span>
                  <div className="text-right">
                    <span className="font-semibold text-[#14283F]">¥{currentStep.fare_adult_jpy}</span>
                    <span className="text-[10px] text-slate-400 block">(IC / Cash accepted)</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer Buttons */}
        <div className="px-6 py-4 bg-[#F8FAFC] border-t border-slate-100 flex items-center justify-end gap-3">
          <button
            onClick={() => {
              if (onOpenRoute) onOpenRoute();
              onClose();
            }}
            className="flex items-center gap-1.5 px-4 py-2.5 rounded-xl border border-sky-300 bg-white text-sky-700 text-xs font-bold hover:bg-sky-50 transition-colors shadow-2xs"
          >
            <Navigation className="w-3.5 h-3.5 text-[#078ACB]" />
            <span>Open route</span>
          </button>

          <button
            onClick={() => {
              if (onConfirmDepart) onConfirmDepart();
              onClose();
            }}
            className="flex items-center gap-1.5 px-5 py-2.5 rounded-xl bg-emerald-600 text-white text-xs font-bold hover:bg-emerald-700 transition-colors shadow-sm"
          >
            <span>I'm on my way</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
};

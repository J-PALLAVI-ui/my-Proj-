import React, { useState } from 'react';
import { 
  Search, 
  Sparkles, 
  Compass, 
  Sun, 
  Eye, 
  Star, 
  ArrowRight, 
  ShieldCheck, 
  ChevronRight,
  Navigation
} from 'lucide-react';
interface DiscoverViewProps {
  onAskHana: (prompt: string) => void;
  onExplore3D: () => void;
  onPlanTrip: () => void;
  onSelectPlace?: (placeId: string) => void;
}

const FEATURED_PLACES = [
  {
    place_id: 'kawaguchiko_oishi_park',
    name_en: 'Oishi Park & Flower Promenade',
    name_ja: '大石公園',
    lake: 'Lake Kawaguchiko',
    rating: 5,
    tag: 'Classic View',
    image: 'https://images.unsplash.com/photo-1578637387939-43c525550085?auto=format&fit=crop&w=800&q=80',
    description: 'Premier lakeside promenade with lavender in summer and vibrant Kochia in autumn framing Mount Fuji.'
  },
  {
    place_id: 'arakurayama_chureito',
    name_en: 'Arakurayama Sengen Park (Chureito Pagoda)',
    name_ja: '新倉山浅間公園 忠霊塔',
    lake: 'Fujiyoshida',
    rating: 5,
    tag: 'World Famous',
    image: 'https://images.unsplash.com/photo-1528164344705-475426879c0d?auto=format&fit=crop&w=800&q=80',
    description: 'Iconic five-story red pagoda perched on a hillside with Mount Fuji and hundreds of cherry trees.'
  },
  {
    place_id: 'oshino_hakkai',
    name_en: 'Oshino Hakkai Spring Ponds',
    name_ja: '忍野八海',
    lake: 'Oshino',
    rating: 4,
    tag: 'UNESCO Heritage',
    image: 'https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=800&q=80',
    description: 'Eight crystalline volcanic ponds fed by snowmelt from Mount Fuji, filtered naturally for 80 years.'
  },
  {
    place_id: 'saiko_iyashi_nenba',
    name_en: 'Saiko Iyashi-no-Sato Nenba',
    name_ja: '西湖いやしの里根場',
    lake: 'Lake Saiko',
    rating: 4,
    tag: 'Quiet Cultural',
    image: 'https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=800&q=80',
    description: 'Restored thatched-roof village on the serene shores of Lake Saiko with traditional craft shops and tea.'
  }
];

const SEASONAL_HIGHLIGHTS = [
  {
    season: 'Spring (Late March – April)',
    title: 'Fuji Cherry Blossom Festival',
    spot: 'Kawaguchiko North Shore & Chureito Pagoda',
    tip: 'Summit snow meets thousands of Somei Yoshino cherry trees. Early mornings offer glass-like water reflections.',
    color: 'from-pink-500/20 to-rose-500/10 border-pink-500/30'
  },
  {
    season: 'Autumn (October – November)',
    title: 'Fuji-Kawaguchiko Autumn Leaves Festival',
    spot: 'Momiji Tunnel & Maple Corridor',
    tip: 'Fiery red maple leaves canopy illuminated at sunset. Clear photographic visibility averages over 65%.',
    color: 'from-amber-500/20 to-orange-500/10 border-amber-500/30'
  },
  {
    season: 'Winter (December – February)',
    title: 'Diamond Fuji & Sparkling Clear Skies',
    spot: 'Lake Yamanakako Nagaike Park & Lake Motosu',
    tip: 'Winter provides the highest visibility (78%). Sun aligns perfectly atop Mount Fuji summit like a diamond.',
    color: 'from-sky-500/20 to-indigo-500/10 border-sky-500/30'
  }
];

export const DiscoverView: React.FC<DiscoverViewProps> = ({
  onAskHana,
  onExplore3D,
  onPlanTrip,
  onSelectPlace: _onSelectPlace
}) => {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      onAskHana(`What are the best attractions or information about ${searchQuery.trim()} around Mount Fuji?`);
    }
  };

  return (
    <div className="h-full overflow-y-auto bg-slate-900 text-slate-100 pb-16">
      {/* Hero Banner Section */}
      <div className="relative min-h-[460px] lg:min-h-[520px] flex items-center justify-center overflow-hidden border-b border-slate-800">
        {/* Background Mount Fuji Image with luxury subtle gradient overlays */}
        <div 
          className="absolute inset-0 bg-cover bg-center transition-transform duration-1000 scale-105"
          style={{
            backgroundImage: `url('https://images.unsplash.com/photo-1490806843957-31f4c9a91c65?auto=format&fit=crop&w=2000&q=85')`
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/70 to-slate-900/40" />

        {/* Hero Content */}
        <div className="relative z-10 max-w-4xl mx-auto px-6 text-center py-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-500/20 border border-sky-400/30 backdrop-blur-md text-sky-300 text-xs font-semibold mb-4 shadow-lg">
            <Sparkles className="w-3.5 h-3.5 text-sky-400" />
            <span>FujiNova 5.0 • AI-Powered Tourism Ecosystem</span>
          </div>

          <h1 className="text-3xl sm:text-5xl lg:text-6xl font-black text-white tracking-tight leading-tight mb-4 drop-shadow-md">
            Journey Into The Sacred Majesty of <br className="hidden sm:inline" />
            <span className="bg-gradient-to-r from-sky-300 via-sky-100 to-indigo-200 bg-clip-text text-transparent">
              Mount Fuji & The Five Lakes
            </span>
          </h1>

          <p className="text-sm sm:text-base text-slate-300 max-w-2xl mx-auto mb-8 leading-relaxed font-normal drop-shadow">
            Explore authentic Japanese alpine heritage with ChatGPT-grade conversational intelligence, 
            interactive 3D geographic terrain, and deterministic public transit routing.
          </p>

          {/* Search Bar */}
          <form 
            onSubmit={handleSearchSubmit}
            className="max-w-xl mx-auto relative flex items-center bg-slate-900/90 backdrop-blur-xl border border-slate-700/80 rounded-2xl shadow-2xl p-1.5 focus-within:border-sky-500 focus-within:ring-2 focus-within:ring-sky-500/20 transition-all mb-6"
          >
            <Search className="w-5 h-5 text-slate-400 ml-3 shrink-0" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search destinations, viewpoints, transit, or culture..."
              className="w-full bg-transparent border-none text-white text-xs sm:text-sm px-3 py-2.5 focus:outline-none placeholder:text-slate-500"
            />
            <button
              type="submit"
              className="px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white text-xs sm:text-sm font-semibold rounded-xl shadow-xs transition-colors shrink-0"
            >
              Search
            </button>
          </form>

          {/* Call to Action Buttons */}
          <div className="flex flex-wrap items-center justify-center gap-3">
            <button
              onClick={() => onAskHana("Can you plan a personalized 1-day itinerary for me with great Mount Fuji views?")}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 text-white text-xs sm:text-sm font-bold shadow-lg transition-all"
            >
              <Sparkles className="w-4 h-4" />
              <span>Plan with Hana AI</span>
            </button>
            <button
              onClick={onExplore3D}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-white text-xs sm:text-sm font-semibold backdrop-blur-md shadow-lg transition-all"
            >
              <Compass className="w-4 h-4 text-sky-400" />
              <span>Explore 3D Digital Twin</span>
            </button>
            <button
              onClick={onPlanTrip}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-white text-xs sm:text-sm font-semibold backdrop-blur-md shadow-lg transition-all"
            >
              <Navigation className="w-4 h-4 text-emerald-400" />
              <span>Journey Planner</span>
            </button>
          </div>
        </div>
      </div>

      {/* Live Regional Telemetry Bar */}
      <div className="max-w-7xl mx-auto px-4 -mt-6 relative z-20">
        <div className="bg-slate-800/95 backdrop-blur-md border border-slate-700/80 rounded-2xl p-4 shadow-xl grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center gap-3.5 p-2 rounded-xl bg-slate-900/60 border border-slate-800">
            <div className="w-10 h-10 rounded-lg bg-sky-500/20 text-sky-400 flex items-center justify-center shrink-0">
              <Sun className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Lake Kawaguchi Climate</span>
              <span className="text-sm font-bold text-white">4°C to 12°C • Clear & Dry</span>
            </div>
          </div>

          <div className="flex items-center gap-3.5 p-2 rounded-xl bg-slate-900/60 border border-slate-800">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0">
              <Eye className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Mount Fuji Visibility Likelihood</span>
              <span className="text-sm font-bold text-emerald-400">77% (Peak Winter Photographic View)</span>
            </div>
          </div>

          <div className="flex items-center gap-3.5 p-2 rounded-xl bg-slate-900/60 border border-slate-800">
            <div className="w-10 h-10 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center shrink-0">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Summit Trail Status</span>
              <span className="text-sm font-bold text-amber-300">Closed (Seasonal Off-Season Safety)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Featured Destinations */}
      <div className="max-w-7xl mx-auto px-4 mt-12">
        <div className="flex items-end justify-between mb-6">
          <div>
            <span className="text-xs font-bold text-sky-400 uppercase tracking-wider block mb-1">
              Curated Heritage
            </span>
            <h2 className="text-xl sm:text-2xl font-black text-white">
              Signature Mount Fuji Experiences
            </h2>
          </div>
          <button 
            onClick={() => onAskHana("What are the top 5 must-visit places around Mount Fuji for first-time travelers?")}
            className="flex items-center gap-1 text-xs text-sky-400 hover:text-sky-300 font-semibold transition-colors"
          >
            <span>Ask Hana to guide you</span>
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {FEATURED_PLACES.map((place) => (
            <div 
              key={place.place_id}
              className="bg-slate-800/80 rounded-2xl border border-slate-700/80 overflow-hidden shadow-lg hover:shadow-2xl hover:border-slate-600 transition-all group flex flex-col"
            >
              <div className="relative h-44 overflow-hidden bg-slate-900">
                <img
                  src={place.image}
                  alt={place.name_en}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
                <span className="absolute top-2.5 left-2.5 px-2.5 py-0.5 rounded-full bg-slate-950/80 backdrop-blur-md text-[10px] font-bold text-sky-300 border border-slate-700">
                  {place.tag}
                </span>
                <span className="absolute bottom-2.5 right-2.5 px-2 py-0.5 rounded-full bg-slate-950/80 backdrop-blur-md text-[11px] font-bold text-amber-400 flex items-center gap-1">
                  <Star className="w-3 h-3 fill-amber-400" />
                  <span>{place.rating}/5</span>
                </span>
              </div>

              <div className="p-4 flex-1 flex flex-col justify-between">
                <div>
                  <h3 className="text-sm font-bold text-white group-hover:text-sky-300 transition-colors line-clamp-1">
                    {place.name_en}
                  </h3>
                  <span className="text-[11px] text-slate-400 block mb-2">
                    {place.name_ja} • {place.lake}
                  </span>
                  <p className="text-xs text-slate-300 line-clamp-2 leading-relaxed">
                    {place.description}
                  </p>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-700 flex items-center justify-between">
                  <button
                    onClick={() => onAskHana(`Tell me how to reach ${place.name_en} by bus and what to see there.`)}
                    className="text-xs font-semibold text-sky-400 hover:text-sky-300 flex items-center gap-1 transition-colors"
                  >
                    <span>Ask Hana</span>
                    <ArrowRight className="w-3 h-3" />
                  </button>
                  <button
                    onClick={() => onAskHana(`Add ${place.name_en} to my trip itinerary.`)}
                    className="text-xs font-medium text-slate-400 hover:text-white transition-colors"
                  >
                    Add to Trip
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Seasonal Highlights */}
      <div className="max-w-7xl mx-auto px-4 mt-14">
        <div className="mb-6">
          <span className="text-xs font-bold text-amber-400 uppercase tracking-wider block mb-1">
            Phenology & Seasons
          </span>
          <h2 className="text-xl sm:text-2xl font-black text-white">
            When To Visit Mount Fuji & The Five Lakes
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {SEASONAL_HIGHLIGHTS.map((s, idx) => (
            <div
              key={idx}
              className={`p-5 rounded-2xl bg-gradient-to-br ${s.color} backdrop-blur-md border shadow-lg flex flex-col justify-between`}
            >
              <div>
                <span className="text-[11px] font-bold text-slate-300 uppercase tracking-wider block mb-1">
                  {s.season}
                </span>
                <h3 className="text-base font-bold text-white mb-1">
                  {s.title}
                </h3>
                <span className="text-xs text-sky-300 block mb-3 font-medium">
                  {s.spot}
                </span>
                <p className="text-xs text-slate-200 leading-relaxed">
                  {s.tip}
                </p>
              </div>

              <button
                onClick={() => onAskHana(`What is the weather and best itinerary for Mount Fuji during ${s.season}?`)}
                className="mt-4 pt-3 border-t border-white/10 text-xs font-semibold text-white hover:text-sky-300 flex items-center gap-1.5 transition-colors"
              >
                <span>Explore seasonal guide</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

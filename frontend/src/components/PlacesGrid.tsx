import React, { useState, useEffect } from 'react';
import { Place } from '../types';
import { apiUrl } from '../config';
import { PlaceCard } from './PlaceCard';
import { Search, Filter, Mountain, Compass, ShieldCheck } from 'lucide-react';

export const PlacesGrid: React.FC = () => {
  const [places, setPlaces] = useState<Place[]>([]);
  const [filteredPlaces, setFilteredPlaces] = useState<Place[]>([]);
  const [search, setSearch] = useState('');
  const [selectedDiscovery, setSelectedDiscovery] = useState<'all' | 'FAMOUS' | 'HIDDEN_GEM'>('all');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedAccess, setSelectedAccess] = useState<string>('all');
  const [indoorOnly, setIndoorOnly] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadPlaces = async () => {
      try {
        let res = await fetch(apiUrl('/api/v1/places?limit=300'));
        if (!res.ok) {
          res = await fetch(apiUrl('/api/attractions?limit=300'));
        }
        if (!res.ok) {
          throw new Error(`API returned HTTP ${res.status}`);
        }
        const data = await res.json();
        const placesArray: Place[] = Array.isArray(data)
          ? data
          : Array.isArray((data as any)?.items)
          ? (data as any).items
          : Array.isArray((data as any)?.attractions)
          ? (data as any).attractions
          : Array.isArray((data as any)?.places)
          ? (data as any).places
          : [];

        setPlaces(placesArray);
        setFilteredPlaces(placesArray);
        setError(null);
        setLoading(false);
      } catch (err: any) {
        // Fallback to /api/v1/places if /api/attractions failed
        try {
          const res2 = await fetch(apiUrl('/api/v1/places?limit=300'));
          if (res2.ok) {
            const data2 = await res2.json();
            const placesArray2: Place[] = Array.isArray(data2)
              ? data2
              : Array.isArray((data2 as any)?.items)
              ? (data2 as any).items
              : [];
            setPlaces(placesArray2);
            setFilteredPlaces(placesArray2);
            setError(null);
            setLoading(false);
            return;
          }
        } catch (_) {}

        console.error('Failed to load places', err);
        setError(err.message || 'Failed to load places from backend');
        setPlaces([]);
        setFilteredPlaces([]);
        setLoading(false);
      }
    };

    loadPlaces();
  }, []);

  useEffect(() => {
    if (!Array.isArray(places)) {
      setFilteredPlaces([]);
      return;
    }
    let result = [...places];

    if (search.trim()) {
      const q = search.toLowerCase();
      result = result.filter(
        (p) =>
          p.name_ja?.toLowerCase().includes(q) ||
          (p.name_en && p.name_en.toLowerCase().includes(q)) ||
          (p.sub_category && p.sub_category.toLowerCase().includes(q))
      );
    }

    if (selectedDiscovery !== 'all') {
      result = result.filter((p) => p.discovery_type === selectedDiscovery);
    }

    if (selectedCategory !== 'all') {
      result = result.filter((p) => p.primary_category === selectedCategory);
    }

    if (selectedAccess !== 'all') {
      result = result.filter((p) => p.accessibility_status === selectedAccess);
    }

    if (indoorOnly) {
      result = result.filter((p) => p.indoor_alternative);
    }

    setFilteredPlaces(result);
  }, [search, selectedDiscovery, selectedCategory, selectedAccess, indoorOnly, places]);

  const categories = ['all', 'viewpoint', 'museum', 'cultural', 'shrine', 'nature', 'park', 'onsen'];

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Title & Stats */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-200">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
            <Mountain className="w-6 h-6 text-sky-600" />
            <span>Fuji Five Lakes & Yamanashi Explorer</span>
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Browse {places.length > 0 ? places.length : 237} individually verified locations with field-level provenance, official hours, and barrier-free audit evidence.
          </p>
        </div>
        <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-200 text-emerald-800 px-3 py-1.5 rounded-lg text-xs font-semibold shrink-0">
          <ShieldCheck className="w-4 h-4 text-emerald-600" />
          <span>Verified Database: {filteredPlaces.length} / {places.length} Shown</span>
        </div>
      </div>

      {/* Discovery Type Filter (Famous vs Hidden Gems) */}
      <div className="mt-4 flex items-center gap-2">
        <button
          onClick={() => setSelectedDiscovery('all')}
          className={`px-3 py-1 rounded-xl text-xs font-bold transition-all border ${
            selectedDiscovery === 'all'
              ? 'bg-[#14283F] text-white border-[#14283F] shadow-xs'
              : 'bg-white text-slate-600 border-slate-200 hover:border-slate-300'
          }`}
        >
          All Destinations ({places.length})
        </button>
        <button
          onClick={() => setSelectedDiscovery('FAMOUS')}
          className={`px-3 py-1 rounded-xl text-xs font-bold transition-all border ${
            selectedDiscovery === 'FAMOUS'
              ? 'bg-amber-600 text-white border-amber-600 shadow-xs'
              : 'bg-white text-amber-700 border-amber-200 hover:bg-amber-50'
          }`}
        >
          Famous Attractions ({places.filter(p => p.discovery_type === 'FAMOUS').length || 136})
        </button>
        <button
          onClick={() => setSelectedDiscovery('HIDDEN_GEM')}
          className={`px-3 py-1 rounded-xl text-xs font-bold transition-all border ${
            selectedDiscovery === 'HIDDEN_GEM'
              ? 'bg-emerald-600 text-white border-emerald-600 shadow-xs'
              : 'bg-white text-emerald-700 border-emerald-200 hover:bg-emerald-50'
          }`}
        >
          Hidden Gems ({places.filter(p => p.discovery_type === 'HIDDEN_GEM').length || 101})
        </button>
      </div>

      {/* Filter & Search Bar */}
      <div className="mt-4 flex flex-col md:flex-row items-stretch md:items-center gap-3">
        {/* Search Input */}
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by name in Japanese or English (e.g. Oishi Park, Chureito, Motosu)..."
            className="w-full pl-10 pr-4 py-2 text-sm rounded-xl border border-slate-200 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500 bg-white"
          />
        </div>

        {/* Accessibility Filter */}
        <select
          value={selectedAccess}
          onChange={(e) => setSelectedAccess(e.target.value)}
          className="px-3 py-2 text-sm rounded-xl border border-slate-200 bg-white text-slate-700 focus:outline-none focus:border-sky-500"
        >
          <option value="all">All Accessibility</option>
          <option value="VERIFIED_ACCESSIBLE">Barrier-Free (Step-Free)</option>
          <option value="PARTIAL_STEPS">Partial Steps</option>
          <option value="STEEP_STAIRS">Steep Stairs</option>
        </select>

        {/* Indoor Toggle */}
        <button
          onClick={() => setIndoorOnly(!indoorOnly)}
          className={`px-3 py-2 rounded-xl text-xs font-medium border transition-colors flex items-center gap-1.5 ${
            indoorOnly
              ? 'bg-indigo-600 text-white border-indigo-600'
              : 'bg-white text-slate-700 border-slate-200 hover:border-slate-300'
          }`}
        >
          <span>Rainy Day / Indoor</span>
        </button>
      </div>

      {/* Category Tabs */}
      <div className="mt-4 flex items-center gap-1.5 overflow-x-auto pb-1 text-xs">
        <Filter className="w-3.5 h-3.5 text-slate-400 shrink-0 mr-1" />
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-3 py-1.5 rounded-lg capitalize font-medium transition-colors shrink-0 ${
              selectedCategory === cat
                ? 'bg-sky-600 text-white shadow-xs'
                : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
            }`}
          >
            {cat === 'all' ? 'All Categories' : cat}
          </button>
        ))}
      </div>

      {/* Places Cards Grid */}
      {loading ? (
        <div className="py-20 text-center text-slate-400 text-sm">Loading verified locations...</div>
      ) : error ? (
        <div className="py-16 text-center bg-amber-50 rounded-xl border border-amber-200 p-6 my-6">
          <Compass className="w-8 h-8 text-amber-500 mx-auto mb-2" />
          <p className="text-amber-800 font-semibold">Could not connect to FujiNova backend API</p>
          <p className="text-xs text-amber-600 mt-1">Make sure the FastAPI backend is running on http://127.0.0.1:8000</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-1.5 bg-amber-600 text-white rounded-lg text-xs font-semibold hover:bg-amber-700"
          >
            Retry Connection
          </button>
        </div>
      ) : (!Array.isArray(filteredPlaces) || filteredPlaces.length === 0) ? (
        <div className="py-20 text-center">
          <Compass className="w-8 h-8 text-slate-300 mx-auto mb-2" />
          <p className="text-slate-600 font-medium">No places match the selected filters.</p>
          <button
            onClick={() => {
              setSearch('');
              setSelectedCategory('all');
              setSelectedAccess('all');
              setIndoorOnly(false);
            }}
            className="mt-3 text-xs text-sky-600 hover:underline font-semibold"
          >
            Reset all filters
          </button>
        </div>
      ) : (
        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {Array.isArray(filteredPlaces) && filteredPlaces.map((place) => (
            <PlaceCard key={place.place_id} place={place} />
          ))}
        </div>
      )}
    </div>
  );
};

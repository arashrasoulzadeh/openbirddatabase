'use client';

import { Species } from '@/lib/types';

interface SpeciesListProps {
  species: Species[];
  onSelect: (species: Species) => void;
}

export default function SpeciesList({ species, onSelect }: SpeciesListProps) {
  if (!species.length) return null;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <ul className="divide-y divide-gray-200">
        {species.map((sp) => (
          <li key={sp.id} className="hover:bg-gray-50 transition-colors">
            <button
              onClick={() => onSelect(sp)}
              className="w-full px-4 py-3 text-left hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-inset"
            >
              <div className="flex items-center gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-gray-900 truncate">{sp.common_name_en || sp.scientific_name}</span>
                    {sp.common_name_fa && (
                      <span className="text-sm text-gray-500 font-vazir" dir="rtl">{sp.common_name_fa}</span>
                    )}
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-500 mt-1">
                    <span className="font-mono text-gray-400">{sp.scientific_name}</span>
                    <span className="px-2 py-0.5 bg-gray-100 rounded text-xs">{sp.order}</span>
                    <span className="px-2 py-0.5 bg-gray-100 rounded text-xs">{sp.family}</span>
                    <span className={`px-2 py-0.5 rounded text-xs ${
                      sp.iucn_status === 'LC' ? 'bg-green-100 text-green-700' :
                      sp.iucn_status === 'NT' ? 'bg-yellow-100 text-yellow-700' :
                      sp.iucn_status === 'VU' ? 'bg-orange-100 text-orange-700' :
                      sp.iucn_status === 'EN' ? 'bg-red-100 text-red-700' :
                      sp.iucn_status === 'CR' ? 'bg-red-200 text-red-800' :
                      'bg-gray-100 text-gray-700'
                    }`}>{sp.iucn_status}</span>
                  </div>
                </div>
                <svg className="w-5 h-5 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
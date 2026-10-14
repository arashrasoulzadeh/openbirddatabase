'use client';

import Link from 'next/link';
import { useI18n } from '@/lib/i18n/I18nProvider';
import { iucnLabel, nameFromHit } from '@/lib/i18n/translate';

const IUCN_STYLE: Record<string, string> = {
  LC: 'bg-green-100 text-green-700',
  NT: 'bg-yellow-100 text-yellow-700',
  VU: 'bg-orange-100 text-orange-700',
  EN: 'bg-red-100 text-red-700',
  CR: 'bg-red-200 text-red-800',
};

export default function SpeciesList({ species }: { species: any[] }) {
  const { lang } = useI18n();
  if (!species.length) return null;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <ul className="divide-y divide-gray-200">
        {species.map((sp) => {
          const name = nameFromHit(sp, lang);
          const english = sp.common_name_en;
          return (
            <li key={sp.id} className="hover:bg-gray-50 transition-colors">
              <Link
                href={`/species/${encodeURIComponent(sp.scientific_name)}`}
                className="flex items-center gap-3 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-inset"
              >
                <div className="flex-1 min-w-0">
                  <div className="flex flex-wrap items-baseline gap-x-2">
                    <span className="font-medium text-gray-900">{name}</span>
                    {/* the original English name stays visible in every language */}
                    {lang !== 'en' && english && english !== name && (
                      <span className="text-sm text-gray-500" dir="ltr">{english}</span>
                    )}
                  </div>
                  <div className="flex flex-wrap items-center gap-2 text-sm text-gray-500 mt-1">
                    <span className="italic text-gray-400" dir="ltr">{sp.scientific_name}</span>
                    <span className="px-2 py-0.5 bg-gray-100 rounded text-xs">{sp.order}</span>
                    <span className="px-2 py-0.5 bg-gray-100 rounded text-xs">{sp.family}</span>
                    {sp.iucn_status && (
                      <span className={`px-2 py-0.5 rounded text-xs ${IUCN_STYLE[sp.iucn_status] ?? 'bg-gray-100 text-gray-700'}`}>
                        {iucnLabel(lang, sp.iucn_status)}
                      </span>
                    )}
                  </div>
                </div>
                <svg className="w-5 h-5 text-gray-400 flex-shrink-0 rtl:rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Link>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

'use client';

import Link from 'next/link';
import { useI18n } from '@/lib/i18n/I18nProvider';
import { nameFromHit } from '@/lib/i18n/translate';
import IucnBadge from './IucnBadge';

export default function SpeciesList({ species }: { species: any[] }) {
  const { lang } = useI18n();
  if (!species.length) return null;

  return (
    <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {species.map((sp) => {
        const name = nameFromHit(sp, lang);
        const english = sp.common_name_en;
        return (
          <li key={sp.id}>
            <Link
              href={`/species/${encodeURIComponent(sp.scientific_name)}`}
              className="group block h-full rounded-xl border border-stone-200 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:border-brand-300 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-brand-500"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <h3 className="font-semibold leading-snug text-stone-900 group-hover:text-brand-800">{name}</h3>
                  {/* the original English name stays visible in every language */}
                  {lang !== 'en' && english && english !== name && (
                    <p className="text-sm text-stone-500" dir="ltr">{english}</p>
                  )}
                  <p className="text-sm italic text-stone-400" dir="ltr">{sp.scientific_name}</p>
                </div>
                <IucnBadge status={sp.iucn_status} />
              </div>
              <div className="mt-3 flex flex-wrap gap-1.5 text-xs text-stone-600">
                <span className="rounded-md bg-stone-100 px-2 py-0.5">{sp.order}</span>
                <span className="rounded-md bg-stone-100 px-2 py-0.5">{sp.family}</span>
              </div>
            </Link>
          </li>
        );
      })}
    </ul>
  );
}

'use client';

import { useEffect, useMemo, useState } from 'react';
import { useI18n } from '@/lib/i18n/I18nProvider';
import { countryLabel, sortCountryCodes } from '@/lib/i18n/countries';

type Paths = Record<string, string>;

const VIEW = { w: 960, h: 480 };

/** World map with GBIF occurrence countries highlighted; names under the map in the UI language. */
export default function DistributionMap({ countries }: { countries: string[] }) {
  const { t, lang } = useI18n();
  const [paths, setPaths] = useState<Paths | null>(null);
  const [hover, setHover] = useState<string | null>(null);

  const codes = useMemo(
    () =>
      sortCountryCodes(
        lang,
        Array.from(new Set(countries.map((c) => String(c).toUpperCase()).filter((c) => /^[A-Z]{2}$/.test(c)))),
      ),
    [countries, lang],
  );
  const active = useMemo(() => new Set(codes), [codes]);

  useEffect(() => {
    let cancelled = false;
    fetch('/maps/countries-110m-paths.json')
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then((data: Paths) => {
        if (!cancelled) setPaths(data);
      })
      .catch(() => {
        if (!cancelled) setPaths({});
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (!codes.length) return null;

  const tip = hover ? countryLabel(lang, hover) : null;

  return (
    <div className="mb-5 space-y-3">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h3 className="text-sm font-semibold text-brand-800">{t('occurrenceCountries')}</h3>
        <span className="text-xs text-stone-400">{t('countriesCount', { count: codes.length })}</span>
      </div>

      <div className="relative overflow-hidden rounded-xl border border-stone-200 bg-sky-50/40">
        {!paths ? (
          <div className="flex h-40 items-center justify-center text-xs text-stone-400 sm:h-56">{t('loading')}</div>
        ) : (
          <svg
            viewBox={`0 0 ${VIEW.w} ${VIEW.h}`}
            role="img"
            aria-label={t('occurrenceCountries')}
            className="block h-auto w-full"
          >
            <rect width={VIEW.w} height={VIEW.h} fill="#e8f2f8" />
            {Object.entries(paths).map(([code, d]) => {
              const on = active.has(code);
              const isHover = hover === code;
              return (
                <path
                  key={code}
                  d={d}
                  data-code={code}
                  className={on ? 'cursor-pointer transition-colors' : undefined}
                  fill={on ? (isHover ? '#0f766e' : '#0d9488') : '#d6d3d1'}
                  stroke={on ? '#134e4a' : '#f5f5f4'}
                  strokeWidth={on ? 0.6 : 0.35}
                  onMouseEnter={on ? () => setHover(code) : undefined}
                  onMouseLeave={on ? () => setHover(null) : undefined}
                  onFocus={on ? () => setHover(code) : undefined}
                  onBlur={on ? () => setHover(null) : undefined}
                  tabIndex={on ? 0 : undefined}
                >
                  {on && <title>{countryLabel(lang, code)}</title>}
                </path>
              );
            })}
          </svg>
        )}
        {tip && (
          <div className="pointer-events-none absolute bottom-2 start-2 rounded-md bg-stone-900/85 px-2 py-1 text-xs text-white">
            {tip}
          </div>
        )}
      </div>

      <ul className="flex max-h-36 flex-wrap gap-1.5 overflow-y-auto">
        {codes.map((code) => (
          <li key={code}>
            <button
              type="button"
              onMouseEnter={() => setHover(code)}
              onMouseLeave={() => setHover(null)}
              onFocus={() => setHover(code)}
              onBlur={() => setHover(null)}
              className={`rounded-md px-2 py-0.5 text-xs ring-1 ring-inset transition ${
                hover === code
                  ? 'bg-teal-700 text-white ring-teal-700'
                  : 'bg-teal-50 text-teal-900 ring-teal-200 hover:bg-teal-100'
              }`}
            >
              {countryLabel(lang, code)}
              <span className="ms-1 text-[10px] opacity-60" dir="ltr">
                {code}
              </span>
            </button>
          </li>
        ))}
      </ul>
      <p className="text-xs text-stone-400">{t('mapAttribution')}</p>
    </div>
  );
}

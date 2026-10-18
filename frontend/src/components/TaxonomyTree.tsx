'use client';

import TrackedLink from './TrackedLink';
import { memo, useMemo, useState } from 'react';
import { useI18n } from '@/lib/i18n/I18nProvider';
import { displayName, nameFromTree } from '@/lib/i18n/translate';
import { taxonLabel } from '@/lib/i18n/taxa';

type Genus = any[]; // species entries: { scientific, common_en, common_fa, names?, id }
type Tree = Record<string, Record<string, Record<string, Genus>>>;

const countGenera = (families: Record<string, Genus>) =>
  Object.values(families).reduce((n, species) => n + species.length, 0);

function Chevron({ open }: { open: boolean }) {
  return (
    <svg
      className={`w-4 h-4 text-gray-400 transition-transform flex-shrink-0 ${open ? 'rotate-90' : 'rtl:rotate-180'}`}
      fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"
    >
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
    </svg>
  );
}

function Row({
  label, count, open, onToggle, level,
}: { label: string; count: number; open: boolean; onToggle: () => void; level: number }) {
  const { t, lang } = useI18n();
  const local = level < 2 ? taxonLabel(lang, label) : ''; // orders and families have common names, genera do not
  return (
    <button
      type="button"
      onClick={onToggle}
      aria-expanded={open}
      className="w-full flex items-center gap-2 py-1.5 px-2 rounded text-start hover:bg-brand-50 focus:outline-none focus:ring-2 focus:ring-brand-500"
    >
      <Chevron open={open} />
      <span className={`${level === 0 ? 'font-semibold text-gray-900' : level === 1 ? 'font-medium text-gray-800' : 'text-sm text-gray-700'}`} dir="ltr">
        {label}
      </span>
      {local && <span className="truncate text-sm text-stone-500">{local}</span>}
      <span className="text-xs text-gray-400 ms-auto">{t('speciesCount', { count: count.toLocaleString() })}</span>
    </button>
  );
}

const SpeciesRows = memo(function SpeciesRows({ species }: { species: Genus }) {
  const { lang } = useI18n();
  return (
    <ul className="ms-6 border-s border-gray-200 ps-2 space-y-0.5">
      {species.map((sp) => {
        const name = displayName(lang, nameFromTree(sp, lang));
        return (
          <li key={sp.id || sp.scientific}>
            <TrackedLink
              href={`/species/${encodeURIComponent(sp.scientific)}`}
              bird={sp.scientific}
              source="taxonomy"
              className="flex flex-wrap items-baseline gap-x-2 py-1 px-2 text-sm rounded hover:bg-brand-50"
            >
              <span className="italic text-gray-700" dir="ltr">{sp.scientific}</span>
              {name && <span className="text-gray-500 text-xs">{name}</span>}
              {/* keep the original English name visible when another language is selected */}
              {lang !== 'en' && sp.common_en && sp.common_en !== name && (
                <span className="text-gray-400 text-xs" dir="ltr">({sp.common_en})</span>
              )}
            </TrackedLink>
          </li>
        );
      })}
    </ul>
  );
});

export default function TaxonomyTree({ tree }: { tree: Tree | null }) {
  const { t } = useI18n();
  const [open, setOpen] = useState<Set<string>>(new Set());

  const toggle = (path: string) =>
    setOpen((prev) => {
      const next = new Set(prev);
      if (next.has(path)) next.delete(path);
      else next.add(path);
      return next;
    });

  // Counts are computed once per tree, not on every expand/collapse
  const orders = useMemo(() => {
    if (!tree) return [];
    return Object.entries(tree)
      .map(([order, families]) => ({
        order,
        families: Object.entries(families)
          .map(([family, genera]) => ({ family, genera, count: countGenera(genera) }))
          .sort((a, b) => a.family.localeCompare(b.family)),
      }))
      .map((o) => ({ ...o, count: o.families.reduce((n, f) => n + f.count, 0) }))
      .sort((a, b) => a.order.localeCompare(b.order));
  }, [tree]);

  if (!tree) return <div className="text-center py-12 text-gray-500">{t('loading')}</div>;

  return (
    <div className="overflow-hidden rounded-xl border border-stone-200 bg-white shadow-sm">
      <div className="border-b border-stone-200 bg-brand-50 p-4 sm:p-5">
        <h2 className="text-lg font-semibold text-brand-900">{t('taxonomyBrowser')}</h2>
        <p className="mt-1 text-sm text-stone-500">{t('taxonomyBrowserHint')}</p>
      </div>
      <div className="p-3 max-h-[70vh] overflow-y-auto">
        {orders.map(({ order, families, count }) => {
          const orderOpen = open.has(order);
          return (
            <div key={order}>
              <Row label={order} count={count} open={orderOpen} onToggle={() => toggle(order)} level={0} />
              {/* children are only rendered while expanded: ~11k species stay out of the DOM */}
              {orderOpen && (
                <div className="ms-4 border-s border-gray-200 ps-2">
                  {families.map(({ family, genera, count: familyCount }) => {
                    const fPath = `${order}/${family}`;
                    const familyOpen = open.has(fPath);
                    return (
                      <div key={family}>
                        <Row label={family} count={familyCount} open={familyOpen} onToggle={() => toggle(fPath)} level={1} />
                        {familyOpen && (
                          <div className="ms-4 border-s border-gray-200 ps-2">
                            {Object.entries(genera).sort(([a], [b]) => a.localeCompare(b)).map(([genus, species]) => {
                              const gPath = `${fPath}/${genus}`;
                              const genusOpen = open.has(gPath);
                              return (
                                <div key={genus}>
                                  <Row label={genus} count={species.length} open={genusOpen} onToggle={() => toggle(gPath)} level={2} />
                                  {genusOpen && <SpeciesRows species={species} />}
                                </div>
                              );
                            })}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

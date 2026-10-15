'use client';

import { useState } from 'react';
import { Filters } from '@/lib/api';
import { useI18n } from '@/lib/i18n/I18nProvider';
import { iucnLabel, valueLabel } from '@/lib/i18n/translate';

type Options = Record<string, Record<string, number>>;

// filter field -> [message key for the label, path used to translate the values]
const FIELDS: [keyof Filters, string, string | null][] = [
  ['iucn_status', 'iucnStatus', null],
  ['primary_habitat', 'primaryHabitat', 'habitat.primary'],
  ['primary_diet', 'primaryDiet', 'diet.primary'],
  ['migration_status', 'migrationStatus', 'behavior.migration_status'],
  ['order', 'order', null],
];

const IUCN_ORDER = ['LC', 'NT', 'VU', 'EN', 'CR', 'EW', 'EX', 'DD'];

interface Props {
  options: Options | null;
  value: Filters;
  onChange: (next: Filters) => void;
}

export default function FilterBar({ options, value, onChange }: Props) {
  const { t, lang } = useI18n();
  const [open, setOpen] = useState(false);
  if (!options) return null;

  const label = (field: keyof Filters, path: string | null, v: string) =>
    field === 'iucn_status' ? iucnLabel(lang, v) : path ? valueLabel(lang, path, v) : v;

  const activeCount = Object.values(value).filter(Boolean).length;

  return (
    <div className="rounded-xl border border-stone-200 bg-white p-3 shadow-sm sm:p-4">
      {/* Phones: collapsed behind a button. md and up: always visible. */}
      <div className="flex items-center justify-between md:hidden">
        <button
          type="button"
          onClick={() => setOpen((o) => !o)}
          aria-expanded={open}
          className="flex items-center gap-2 text-sm font-medium text-stone-700"
        >
          <svg className="h-4 w-4 text-brand-700" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5h18l-7 8v6l-4-2v-4L3 5z" />
          </svg>
          {t('filters')}
          {activeCount > 0 && (
            <span className="rounded-full bg-brand-700 px-2 py-0.5 text-xs text-white">{activeCount}</span>
          )}
        </button>
        {activeCount > 0 && (
          <button type="button" onClick={() => onChange({})} className="text-sm text-brand-700 hover:underline">
            {t('clearFilters')}
          </button>
        )}
      </div>

      <div className={`${open ? 'grid' : 'hidden'} mt-3 grid-cols-2 gap-3 md:mt-0 md:flex md:flex-wrap md:items-end`}>
        {FIELDS.map(([field, labelKey, path]) => {
          const entries = Object.entries(options[field] || {}).filter(([v]) => v);
          const sorted =
            field === 'iucn_status'
              ? entries.sort(([a], [b]) => IUCN_ORDER.indexOf(a) - IUCN_ORDER.indexOf(b))
              : entries.sort(([a], [b]) => label(field, path, a).localeCompare(label(field, path, b), lang));
          return (
            <label key={field} className="flex min-w-0 flex-col gap-1 text-xs font-medium text-stone-500">
              {t(labelKey)}
              <select
                value={value[field] || ''}
                onChange={(e) => onChange({ ...value, [field]: e.target.value || undefined })}
                className="w-full min-w-0 rounded-lg border border-stone-300 bg-white px-2.5 py-2 text-sm font-normal text-stone-800 focus:outline-none focus:ring-2 focus:ring-brand-500 md:w-44"
              >
                <option value="">{t('filterAll')}</option>
                {sorted.map(([v, count]) => (
                  <option key={v} value={v}>
                    {label(field, path, v)} ({count.toLocaleString()})
                  </option>
                ))}
              </select>
            </label>
          );
        })}
        {activeCount > 0 && (
          <button
            type="button"
            onClick={() => onChange({})}
            className="hidden pb-2 text-sm text-brand-700 hover:underline md:block"
          >
            {t('clearFilters')}
          </button>
        )}
      </div>
    </div>
  );
}

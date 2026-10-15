'use client';

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
  if (!options) return null;

  const label = (field: keyof Filters, path: string | null, v: string) =>
    field === 'iucn_status' ? iucnLabel(lang, v) : path ? valueLabel(lang, path, v) : v;

  const active = Object.values(value).some(Boolean);

  return (
    <div className="flex flex-wrap items-end gap-3">
      {FIELDS.map(([field, labelKey, path]) => {
        const entries = Object.entries(options[field] || {}).filter(([v]) => v);
        const sorted =
          field === 'iucn_status'
            ? entries.sort(([a], [b]) => IUCN_ORDER.indexOf(a) - IUCN_ORDER.indexOf(b))
            : entries.sort(([a], [b]) => label(field, path, a).localeCompare(label(field, path, b), lang));
        return (
          <label key={field} className="flex flex-col gap-1 text-xs text-gray-500">
            {t(labelKey)}
            <select
              value={value[field] || ''}
              onChange={(e) => onChange({ ...value, [field]: e.target.value || undefined })}
              className="border border-gray-300 rounded-md px-2 py-1.5 bg-white text-sm text-gray-800 max-w-[12rem] focus:outline-none focus:ring-2 focus:ring-blue-500"
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
      {active && (
        <button
          type="button"
          onClick={() => onChange({})}
          className="text-sm text-blue-600 hover:underline pb-1.5"
        >
          {t('clearFilters')}
        </button>
      )}
    </div>
  );
}

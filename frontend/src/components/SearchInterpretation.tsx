'use client';

import { useI18n } from '@/lib/i18n/I18nProvider';
import { iucnLabel, valueLabel } from '@/lib/i18n/translate';
import { taxonLabel } from '@/lib/i18n/taxa';

export interface Interpretation {
  interpreted?: { filters: Record<string, string[]>; words: string[]; ignored: string[] };
  corrected_query?: string;
}

const PATH_OF: Record<string, string> = {
  primary_habitat: 'habitat.primary',
  primary_diet: 'diet.primary',
  migration_status: 'behavior.migration_status',
};

/** One line under the search box when the search was a sentence ("endangered owls in forests") or a typo was fixed. */
export default function SearchInterpretation({ info }: { info: Interpretation | null }) {
  const { t, lang } = useI18n();
  if (!info || (!info.interpreted && !info.corrected_query)) return null;

  const label = (field: string, value: string) => {
    if (field === 'iucn_status') return iucnLabel(lang, value);
    if (field === 'order' || field === 'family') return taxonLabel(lang, value) || value;
    return PATH_OF[field] ? valueLabel(lang, PATH_OF[field], value) : value;
  };

  if (info.corrected_query) {
    return (
      <p className="text-sm text-stone-600">
        {t('showingResultsFor')} <strong className="font-semibold text-stone-800">{info.corrected_query}</strong>
      </p>
    );
  }
  const { filters, words, ignored } = info.interpreted!;
  return (
    <p className="flex flex-wrap items-center gap-2 text-sm text-stone-600">
      <span>{t('understoodAs')}:</span>
      {Object.entries(filters).map(([field, values]) => (
        <span key={field} className="rounded-full bg-brand-50 px-3 py-0.5 text-brand-800">
          {values.map((v) => label(field, v)).join(' · ')}
        </span>
      ))}
      {words.map((w) => (
        <span key={w} className="rounded-full bg-stone-100 px-3 py-0.5">{w}</span>
      ))}
      {ignored.length > 0 && (
        <span className="text-stone-400">({t('ignoredWords')}: {ignored.join(', ')})</span>
      )}
    </p>
  );
}

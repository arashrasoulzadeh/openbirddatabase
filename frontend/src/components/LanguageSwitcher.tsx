'use client';

import { useI18n } from '@/lib/i18n/I18nProvider';
import { LOCALES, isLang } from '@/lib/i18n/locales';

export default function LanguageSwitcher() {
  const { lang, setLang, t } = useI18n();
  return (
    <label className="relative inline-flex items-center shrink-0">
      <span className="sr-only">{t('language')}</span>
      <svg className="pointer-events-none absolute start-2.5 h-4 w-4 text-brand-700" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <circle cx="12" cy="12" r="9" strokeWidth={1.8} />
        <path strokeWidth={1.8} d="M3 12h18M12 3c2.5 2.5 3.8 5.5 3.8 9s-1.3 6.5-3.8 9c-2.5-2.5-3.8-5.5-3.8-9S9.5 5.5 12 3z" />
      </svg>
      <select
        value={lang}
        onChange={(e) => isLang(e.target.value) && setLang(e.target.value)}
        aria-label={t('language')}
        className="appearance-none cursor-pointer rounded-full border border-stone-300 bg-white py-1.5 ps-8 pe-7 text-sm font-medium text-stone-700 hover:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-500"
      >
        {LOCALES.map((l) => (
          <option key={l.code} value={l.code}>{l.name}</option>
        ))}
      </select>
      <svg className="pointer-events-none absolute end-2.5 h-3.5 w-3.5 text-stone-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
      </svg>
    </label>
  );
}

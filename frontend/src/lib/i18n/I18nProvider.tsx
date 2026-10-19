'use client';

import { createContext, useCallback, useContext, useMemo, useState } from 'react';
import { Lang, LANG_COOKIE, dirOf } from './locales';
import { translate } from './translate';
import { Tables, register } from './store';
import { localePath, splitLang } from './routes';
import { track } from '../analytics';

interface I18nValue {
  lang: Lang;
  dir: 'ltr' | 'rtl';
  setLang: (lang: Lang) => void;
  t: (key: string, params?: Record<string, string | number>) => string;
}

const I18nContext = createContext<I18nValue | null>(null);

export function I18nProvider({ initialLang, tables, children }: { initialLang: Lang; tables?: Tables; children: React.ReactNode }) {
  if (tables) register(tables); // before any child renders; the browser only receives the current language + English
  const [lang, setLangState] = useState<Lang>(initialLang);

  const setLang = useCallback(
    (next: Lang) => {
      track('language_change', { source: lang, query: next });
      document.cookie = `${LANG_COOKIE}=${next}; path=/; max-age=31536000; samesite=lax`;
      // every language has its own URL (/fa/species/X): open this page's address in the new language
      const { path } = splitLang(window.location.pathname);
      window.location.assign(localePath(next, path) + window.location.search + window.location.hash);
    },
    [lang],
  );

  const value = useMemo<I18nValue>(
    () => ({ lang, dir: dirOf(lang), setLang, t: (key, params) => translate(lang, key, params) }),
    [lang, setLang],
  );

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n(): I18nValue {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error('useI18n must be used inside <I18nProvider>');
  return ctx;
}

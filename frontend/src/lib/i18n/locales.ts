export const LOCALES = [
  { code: 'en', name: 'English', dir: 'ltr' },
  { code: 'fa', name: 'فارسی', dir: 'rtl' },
  { code: 'ar', name: 'العربية', dir: 'rtl' },
  { code: 'es', name: 'Español', dir: 'ltr' },
  { code: 'fr', name: 'Français', dir: 'ltr' },
  { code: 'de', name: 'Deutsch', dir: 'ltr' },
  { code: 'pt', name: 'Português', dir: 'ltr' },
  { code: 'ru', name: 'Русский', dir: 'ltr' },
  { code: 'ja', name: '日本語', dir: 'ltr' },
  { code: 'zh', name: '中文', dir: 'ltr' },
  { code: 'nl', name: 'Nederlands', dir: 'ltr' },
  { code: 'pl', name: 'Polski', dir: 'ltr' },
  { code: 'tr', name: 'Türkçe', dir: 'ltr' },
] as const;

export type Lang = (typeof LOCALES)[number]['code'];

export const DEFAULT_LANG: Lang = 'en';
export const LANG_COOKIE = 'lang';

export const isLang = (v: unknown): v is Lang => LOCALES.some((l) => l.code === v);

export const dirOf = (lang: Lang): 'ltr' | 'rtl' => LOCALES.find((l) => l.code === lang)?.dir ?? 'ltr';

export const nativeName = (code: string): string => LOCALES.find((l) => l.code === code)?.name ?? code;

/** Pick the best supported language from an Accept-Language header. */
export function langFromAcceptLanguage(header: string | null | undefined): Lang {
  for (const part of (header || '').split(',')) {
    const code = part.split(';')[0].trim().slice(0, 2).toLowerCase();
    if (isLang(code)) return code;
  }
  return DEFAULT_LANG;
}

/** Open Graph locale codes ("fa_IR") for social previews. */
export const OG_LOCALE: Record<Lang, string> = {
  en: 'en_US', fa: 'fa_IR', ar: 'ar_AR', es: 'es_ES', fr: 'fr_FR', de: 'de_DE', pt: 'pt_BR',
  ru: 'ru_RU', ja: 'ja_JP', zh: 'zh_CN', nl: 'nl_NL', pl: 'pl_PL', tr: 'tr_TR',
};

import { Lang } from './locales';

const cache = new Map<string, Intl.DisplayNames>();

function displayNames(lang: Lang): Intl.DisplayNames {
  let dn = cache.get(lang);
  if (!dn) {
    dn = new Intl.DisplayNames([lang, 'en'], { type: 'region' });
    cache.set(lang, dn);
  }
  return dn;
}

/** Localised country name for an ISO 3166-1 alpha-2 code (e.g. IR → ایران). */
export function countryLabel(lang: Lang, code: string): string {
  const iso = String(code || '').trim().toUpperCase();
  if (!/^[A-Z]{2}$/.test(iso)) return code;
  try {
    return displayNames(lang).of(iso) ?? iso;
  } catch {
    return iso;
  }
}

/** Sort country codes by their localised name. */
export function sortCountryCodes(lang: Lang, codes: string[]): string[] {
  return [...codes].sort((a, b) => countryLabel(lang, a).localeCompare(countryLabel(lang, b), lang));
}

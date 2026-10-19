import { DEFAULT_LANG, LOCALES, Lang, isLang } from './locales';

/**
 * Every language has its own URL, which is what lets search engines index each one:
 *   English (default)  https://site/species/Parus%20major
 *   other languages    https://site/fa/species/Parus%20major
 * `path` below always starts with "/" and may carry a ?query or #hash.
 */
export const PREFIXED_LANGS = LOCALES.map((l) => l.code).filter((c) => c !== DEFAULT_LANG);

export const LANG_HEADER = 'x-lang'; // set by middleware.ts for every request

/** "/fa/species/X" -> { lang: "fa", path: "/species/X" }; unprefixed paths are English. */
export function splitLang(pathname: string): { lang: Lang; path: string } {
  const m = pathname.match(/^\/([a-z]{2})(\/.*)?$/);
  if (m && isLang(m[1]) && m[1] !== DEFAULT_LANG) return { lang: m[1], path: m[2] || '/' };
  return { lang: DEFAULT_LANG, path: pathname || '/' };
}

/** The URL path of `path` in `lang`. */
export function localePath(lang: Lang, path: string): string {
  if (!path.startsWith('/') || lang === DEFAULT_LANG) return path;
  return path === '/' ? `/${lang}` : `/${lang}${path}`;
}

/** Full URL of `path` in `lang` (the home page has no trailing slash, like its sitemap entry and canonical). */
export function fullUrl(siteUrl: string, lang: Lang, path: string): string {
  const local = localePath(lang, path);
  return local === '/' ? siteUrl : siteUrl + local;
}

/** hreflang values for one page: every language plus x-default (the English URL). */
export function languageUrls(siteUrl: string, path: string): Record<string, string> {
  const urls: Record<string, string> = {};
  for (const { code } of LOCALES) urls[code] = fullUrl(siteUrl, code, path);
  urls['x-default'] = fullUrl(siteUrl, DEFAULT_LANG, path);
  return urls;
}

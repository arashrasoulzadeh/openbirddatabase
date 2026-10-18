import { cookies, headers } from 'next/headers';
import HomeClient, { InitialSearch } from './HomeClient';
import { searchSpecies, Filters } from '@/lib/api';
import { DEFAULT_LANG, LANG_COOKIE, isLang, langFromAcceptLanguage } from '@/lib/i18n/locales';

const PAGE_SIZE = 50;
const FILTER_KEYS: (keyof Filters)[] = ['iucn_status', 'primary_habitat', 'primary_diet', 'migration_status', 'order'];

const first = (v: string | string[] | undefined) => (Array.isArray(v) ? v[0] : v) || '';

/**
 * Fetches the first page of results on the server so the bird list is part of the HTML (no wait for JavaScript, then
 * the API). If the API is slow or down the page still renders and the browser fetches as before.
 */
export default async function Page({ searchParams }: { searchParams: Record<string, string | string[] | undefined> }) {
  const cookie = cookies().get(LANG_COOKIE)?.value;
  const lang = isLang(cookie) ? cookie : langFromAcceptLanguage(headers().get('accept-language')) || DEFAULT_LANG;
  const query = first(searchParams.q);
  const filters: Filters = Object.fromEntries(FILTER_KEYS.filter((k) => first(searchParams[k])).map((k) => [k, first(searchParams[k])]));

  let initial: InitialSearch | undefined;
  if (first(searchParams.view) !== 'taxonomy') {
    try {
      const data = await searchSpecies(query, PAGE_SIZE, 0, filters, lang, {
        next: { revalidate: 60 },
        signal: AbortSignal.timeout(1500),
      } as RequestInit);
      initial = { query, filters, lang, hits: data.hits || [], total: data.total ?? data.estimatedTotalHits ?? 0, interpreted: data.interpreted, corrected_query: data.corrected_query };
    } catch (error) {
      console.warn('home: server-side search failed, the browser will fetch it:', error);
      initial = undefined; // the client fetches
    }
  }
  return <HomeClient initial={initial} />;
}

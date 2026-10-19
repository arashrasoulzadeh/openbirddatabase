import type { Metadata } from 'next';
import Link from 'next/link';
import HomeClient, { InitialSearch } from './HomeClient';
import JsonLd from '@/components/JsonLd';
import { getFilterOptions, searchSpecies, Filters } from '@/lib/api';
import { SITE_URL } from '@/lib/config';
import { LOCALES, Lang } from '@/lib/i18n/locales';
import { helpText } from '@/lib/i18n/help';
import { localePath } from '@/lib/i18n/routes';
import { requestLang } from '@/lib/i18n/server';
import { taxonLabel } from '@/lib/i18n/taxa';
import { pageMetadata } from '@/lib/seo';

const PAGE_SIZE = 50;
const FILTER_KEYS: (keyof Filters)[] = ['iucn_status', 'primary_habitat', 'primary_diet', 'migration_status', 'order'];
type SearchParams = Record<string, string | string[] | undefined>;

const first = (v: string | string[] | undefined) => (Array.isArray(v) ? v[0] : v) || '';
const text = (lang: Lang, key: string, params: Record<string, string | number> = {}) =>
  Object.entries(params).reduce((s, [k, v]) => s.replaceAll(`{${k}}`, String(v)), helpText(lang, key) ?? '');

export function generateMetadata({ searchParams }: { searchParams: SearchParams }): Metadata {
  const lang = requestLang();
  const meta = pageMetadata({
    lang,
    path: '/',
    title: text(lang, 'seo.homeTitle'),
    description: text(lang, 'seo.homeDescription'),
  });
  // searches and filtered lists (?q=, ?iucn_status=...) are for people; the clean home page is the one to index
  const filtered = ['q', 'view', ...FILTER_KEYS].some((k) => first(searchParams[k]));
  return filtered ? { ...meta, robots: { index: false, follow: true } } : meta;
}

/** Links to every order: gives crawlers (and people without JavaScript) a path to all the taxonomy pages. */
async function BrowseOrders({ lang }: { lang: Lang }) {
  let orders: [string, number][] = [];
  try {
    orders = Object.entries((await getFilterOptions()).order || {}).sort((a, b) => b[1] - a[1]);
  } catch {
    return null;
  }
  if (!orders.length) return null;
  return (
    <section aria-labelledby="browse-orders" className="mt-10 border-t border-stone-200 pt-6">
      <h2 id="browse-orders" className="mb-3 text-lg font-semibold text-brand-900">{text(lang, 'taxon.browseOrders')}</h2>
      <ul className="grid gap-x-4 gap-y-1 text-sm sm:grid-cols-2 lg:grid-cols-3">
        {orders.map(([order, n]) => (
          <li key={order}>
            <Link href={localePath(lang, `/order/${encodeURIComponent(order)}`)} className="text-brand-700 hover:underline">
              {taxonLabel(lang, order) || order}
            </Link>{' '}
            <span className="text-stone-400" dir="ltr">({order} · {n})</span>
          </li>
        ))}
      </ul>
    </section>
  );
}

/**
 * Fetches the first page of results on the server so the bird list is part of the HTML (no wait for JavaScript, then
 * the API). If the API is slow or down the page still renders and the browser fetches as before.
 */
export default async function Page({ searchParams }: { searchParams: SearchParams }) {
  const lang = requestLang();
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
  const homeUrl = SITE_URL + localePath(lang, '/');
  return (
    <>
      <JsonLd
        data={[
          {
            '@context': 'https://schema.org',
            '@type': 'WebSite',
            '@id': `${SITE_URL}/#website`,
            name: 'OpenBird',
            url: homeUrl,
            description: text(lang, 'seo.homeDescription'),
            inLanguage: LOCALES.map((l) => l.code),
            potentialAction: {
              '@type': 'SearchAction',
              target: { '@type': 'EntryPoint', urlTemplate: `${homeUrl}${homeUrl.endsWith('/') ? '' : '/'}?q={search_term_string}` },
              'query-input': 'required name=search_term_string',
            },
          },
          {
            '@context': 'https://schema.org',
            '@type': 'Organization',
            '@id': `${SITE_URL}/#organization`,
            name: 'OpenBird',
            url: SITE_URL,
            logo: `${SITE_URL}/icon.svg`,
          },
        ]}
      />
      <HomeClient initial={initial} browse={<BrowseOrders lang={lang} />} />
    </>
  );
}

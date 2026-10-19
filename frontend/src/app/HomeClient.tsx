'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import SearchBar from '@/components/SearchBar';
import SpeciesList from '@/components/SpeciesList';
import TaxonomyTree from '@/components/TaxonomyTree';
import FilterBar from '@/components/FilterBar';
import SearchInterpretation, { Interpretation } from '@/components/SearchInterpretation';
import SiteHeader from '@/components/SiteHeader';
import { searchSpecies, getTaxonomy, getFilterOptions, getRandomSpecies, Filters } from '@/lib/api';
import { useI18n } from '@/lib/i18n/I18nProvider';
import { localePath } from '@/lib/i18n/routes';
import { track } from '@/lib/analytics';

const PAGE_SIZE = 50;
const FILTER_KEYS: (keyof Filters)[] = ['iucn_status', 'primary_habitat', 'primary_diet', 'migration_status', 'order'];

export interface InitialSearch {
  query: string;
  filters: Filters;
  lang: string;
  hits: any[];
  total: number;
  interpreted?: Interpretation['interpreted'];
  corrected_query?: string;
}

/** `initial` is the first page of results the server already fetched (so the list is in the HTML, no spinner). */
export default function HomeClient({ initial, browse }: { initial?: InitialSearch; browse?: React.ReactNode }) {
  const { t, lang } = useI18n();
  const router = useRouter();
  const [query, setQuery] = useState(initial?.query ?? '');
  const [species, setSpecies] = useState<any[]>(initial?.hits ?? []);
  const [loading, setLoading] = useState(!initial);
  const [total, setTotal] = useState(initial?.total ?? 0);
  const [error, setError] = useState(false);
  const [interpretation, setInterpretation] = useState<Interpretation | null>(initial ? { interpreted: initial.interpreted, corrected_query: initial.corrected_query } : null);
  const [view, setView] = useState<'list' | 'taxonomy'>('list');
  const [taxonomy, setTaxonomy] = useState<any>(null);
  const [filters, setFilters] = useState<Filters>(initial?.filters ?? {});
  const [filterOptions, setFilterOptions] = useState<Record<string, Record<string, number>> | null>(null);

  const [ready, setReady] = useState(false); // URL state has been read
  const [loadingMore, setLoadingMore] = useState(false);
  // skips identical consecutive searches; starts as the server-fetched search so it is not repeated
  const lastKey = useRef(initial ? JSON.stringify([initial.query, initial.filters, initial.lang]) : '');
  const requestId = useRef(0);  // discards responses that arrive out of order

  const runSearch = useCallback(async (q: string, f: Filters = {}) => {
    const key = JSON.stringify([q, f, lang]);
    if (key === lastKey.current) return;
    lastKey.current = key;
    const id = ++requestId.current;
    setLoading(true);
    setError(false);
    try {
      const data = await searchSpecies(q, PAGE_SIZE, 0, f, lang);
      if (id !== requestId.current) return;
      setSpecies(data.hits || []);
      setInterpretation({ interpreted: data.interpreted, corrected_query: data.corrected_query });
      const count = data.total ?? data.estimatedTotalHits ?? 0;
      setTotal(count);
      if (q.trim()) track('search', { query: q.trim(), value: count, props: { filters: f } });
    } catch (e) {
      if (id !== requestId.current) return;
      console.error('Search error:', e);
      setError(true);
    } finally {
      if (id === requestId.current) setLoading(false);
    }
  }, [lang]);

  const loadMore = async () => {
    setLoadingMore(true);
    track('load_more', { value: species.length });
    const id = requestId.current;
    try {
      const data = await searchSpecies(query, PAGE_SIZE, species.length, filters, lang);
      if (id !== requestId.current) return;
      setSpecies((prev) => [...prev, ...(data.hits || [])]);
    } catch (e) {
      console.error('Load more error:', e);
    } finally {
      setLoadingMore(false);
    }
  };

  const surprise = async () => {
    try {
      const sp = await getRandomSpecies();
      track('random_bird', { bird: sp.scientific_name });
      track('bird_click', { bird: sp.scientific_name, source: 'random' });
      router.push(localePath(lang, `/species/${encodeURIComponent(sp.scientific_name)}`));
    } catch (e) {
      console.error('Random species error:', e);
    }
  };

  // Restore search, filters and tab from the URL (shareable links)
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    setQuery(params.get('q') || '');
    setFilters(Object.fromEntries(FILTER_KEYS.filter((k) => params.get(k)).map((k) => [k, params.get(k) as string])));
    if (params.get('view') === 'taxonomy') setView('taxonomy');
    setReady(true);
  }, []);

  useEffect(() => {
    if (!ready) return;
    const params = new URLSearchParams();
    if (query) params.set('q', query);
    for (const k of FILTER_KEYS) if (filters[k]) params.set(k, filters[k] as string);
    if (view === 'taxonomy') params.set('view', 'taxonomy');
    const qs = params.toString();
    window.history.replaceState(null, '', qs ? `?${qs}` : window.location.pathname);
  }, [ready, query, filters, view]);

  useEffect(() => {
    getFilterOptions().then(setFilterOptions).catch((e) => console.error('Filter options error:', e));
  }, []);

  // Re-run the search when a filter changes (typing is debounced inside SearchBar)
  useEffect(() => {
    if (!ready) return;
    runSearch(query, filters);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ready, filters, runSearch]);

  // The taxonomy tree is large: fetch it only when its tab is opened, one common name per species in the chosen language
  useEffect(() => {
    if (view !== 'taxonomy') return;
    let cancelled = false;
    getTaxonomy(lang).then((tree) => !cancelled && setTaxonomy(tree)).catch((e) => console.error('Taxonomy load error:', e));
    return () => {
      cancelled = true;
    };
  }, [view, lang]);

  const tab = (id: 'list' | 'taxonomy', label: string) => (
    <button
      onClick={() => {
        if (id === 'taxonomy' && view !== 'taxonomy') track('tab_view', { source: 'taxonomy' });
        setView(id);
      }}
      aria-current={view === id ? 'page' : undefined}
      className={`flex-1 rounded-lg px-4 py-1.5 text-sm font-medium transition-colors sm:flex-none ${
        view === id ? 'bg-brand-700 text-white shadow-sm' : 'text-stone-600 hover:bg-stone-100'
      }`}
    >
      {label}
    </button>
  );

  return (
    <div className="flex min-h-screen flex-col bg-stone-50">
      <SiteHeader>
        <nav className="flex gap-1 rounded-xl bg-stone-100 p-1 sm:bg-transparent sm:p-0">
          {tab('list', t('search'))}
          {tab('taxonomy', t('taxonomy'))}
        </nav>
      </SiteHeader>

      {view === 'list' && (
        <section className="bg-gradient-to-b from-brand-800 to-brand-700 text-white">
          <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 sm:py-12">
            <h1 className="text-2xl font-semibold tracking-tight sm:text-4xl">{t('openBirdDatabase')}</h1>
            <p className="mt-2 max-w-2xl text-brand-100">{t('openBirdDatabaseSubtitle')}</p>
            <div className="mt-6 max-w-2xl">
              <SearchBar
                value={query}
                onChange={setQuery}
                onSearch={(q) => runSearch(q, filters)}
                loading={loading}
                placeholder={t('searchHint')}
              />
              <button
                type="button"
                onClick={surprise}
                className="mt-3 inline-flex items-center gap-2 rounded-full border border-white/30 px-4 py-1.5 text-sm text-white/90 transition hover:bg-white/10"
              >
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <rect x="4" y="4" width="16" height="16" rx="3" strokeWidth={1.8} />
                  <circle cx="9" cy="9" r="1.2" fill="currentColor" /><circle cx="15" cy="15" r="1.2" fill="currentColor" /><circle cx="12" cy="12" r="1.2" fill="currentColor" />
                </svg>
                {t('randomBird')}
              </button>
            </div>
          </div>
        </section>
      )}

      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-6 sm:px-6">
        {view === 'list' ? (
          <div className="flex flex-col gap-5">
            <SearchInterpretation info={interpretation} />
            <FilterBar
              options={filterOptions}
              value={filters}
              onChange={(next) => {
                for (const k of FILTER_KEYS) {
                  if (next[k] && next[k] !== filters[k]) track('filter', { source: k, query: next[k] });
                }
                setFilters(next);
              }}
            />
            {!loading && !error && species.length > 0 && (
              <p className="text-sm text-stone-500">
                {t('speciesCount', { count: total.toLocaleString() })}
              </p>
            )}
            {error && <div className="rounded-xl bg-red-50 py-8 text-center text-red-700">{t('searchError')}</div>}
            {!loading && !error && species.length === 0 && (
              <div className="py-16 text-center text-lg text-stone-500">{t('noResults')}</div>
            )}
            {loading && species.length === 0 && <div className="py-16 text-center text-stone-400">{t('searching')}</div>}
            <div className={loading && species.length > 0 ? 'opacity-60 transition-opacity' : 'transition-opacity'}>
              <SpeciesList species={species} query={query} />
            </div>
            {!error && species.length > 0 && species.length < total && (
              <div className="flex flex-col items-center gap-2 pt-2">
                <p className="text-sm text-stone-500">
                  {t('showingCount', { shown: species.length.toLocaleString(), total: total.toLocaleString() })}
                </p>
                <button
                  type="button"
                  onClick={loadMore}
                  disabled={loadingMore}
                  className="rounded-full bg-brand-700 px-6 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-brand-800 disabled:opacity-60"
                >
                  {loadingMore ? t('loading') : t('loadMore')}
                </button>
              </div>
            )}
          </div>
        ) : (
          <TaxonomyTree tree={taxonomy} />
        )}
        {browse}
      </main>

      <footer className="border-t border-stone-200 bg-white py-6">
        <div className="mx-auto max-w-6xl px-4 text-center text-sm text-stone-500 sm:px-6">
          <p>{t('footerText')}</p>
          <p className="mt-1">{t('dataSources')}: {t('dataSourcesSubtitle')}</p>
          <p className="mt-2">
            <Link href={localePath(lang, '/analytics')} className="font-medium text-brand-700 hover:underline">{t('siteStatistics')}</Link>
          </p>
        </div>
      </footer>
    </div>
  );
}

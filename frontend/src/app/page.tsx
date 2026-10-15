'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import SearchBar from '@/components/SearchBar';
import SpeciesList from '@/components/SpeciesList';
import TaxonomyTree from '@/components/TaxonomyTree';
import FilterBar from '@/components/FilterBar';
import SiteHeader from '@/components/SiteHeader';
import { searchSpecies, getTaxonomy, getFilterOptions, getRandomSpecies, Filters } from '@/lib/api';
import { useI18n } from '@/lib/i18n/I18nProvider';

const PAGE_SIZE = 50;
const FILTER_KEYS: (keyof Filters)[] = ['iucn_status', 'primary_habitat', 'primary_diet', 'migration_status', 'order'];

export default function Home() {
  const { t } = useI18n();
  const router = useRouter();
  const [query, setQuery] = useState('');
  const [species, setSpecies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState(false);
  const [view, setView] = useState<'list' | 'taxonomy'>('list');
  const [taxonomy, setTaxonomy] = useState<any>(null);
  const [filters, setFilters] = useState<Filters>({});
  const [filterOptions, setFilterOptions] = useState<Record<string, Record<string, number>> | null>(null);

  const [ready, setReady] = useState(false); // URL state has been read
  const [loadingMore, setLoadingMore] = useState(false);
  const lastKey = useRef('');   // skips identical consecutive searches
  const requestId = useRef(0);  // discards responses that arrive out of order

  const runSearch = useCallback(async (q: string, f: Filters = {}) => {
    const key = JSON.stringify([q, f]);
    if (key === lastKey.current) return;
    lastKey.current = key;
    const id = ++requestId.current;
    setLoading(true);
    setError(false);
    try {
      const data = await searchSpecies(q, PAGE_SIZE, 0, f);
      if (id !== requestId.current) return;
      setSpecies(data.hits || []);
      setTotal(data.total ?? data.estimatedTotalHits ?? 0);
    } catch (e) {
      if (id !== requestId.current) return;
      console.error('Search error:', e);
      setError(true);
    } finally {
      if (id === requestId.current) setLoading(false);
    }
  }, []);

  const loadMore = async () => {
    setLoadingMore(true);
    const id = requestId.current;
    try {
      const data = await searchSpecies(query, PAGE_SIZE, species.length, filters);
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
      router.push(`/species/${encodeURIComponent(sp.scientific_name)}`);
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

  // The taxonomy tree is large; fetch it only when its tab is opened
  useEffect(() => {
    if (view === 'taxonomy' && !taxonomy) {
      getTaxonomy().then(setTaxonomy).catch((e) => console.error('Taxonomy load error:', e));
    }
  }, [view, taxonomy]);

  const tab = (id: 'list' | 'taxonomy', label: string) => (
    <button
      onClick={() => setView(id)}
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
            <FilterBar options={filterOptions} value={filters} onChange={setFilters} />
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
              <SpeciesList species={species} />
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
      </main>

      <footer className="border-t border-stone-200 bg-white py-6">
        <div className="mx-auto max-w-6xl px-4 text-center text-sm text-stone-500 sm:px-6">
          <p>{t('footerText')}</p>
          <p className="mt-1">{t('dataSources')}: {t('dataSourcesSubtitle')}</p>
        </div>
      </footer>
    </div>
  );
}

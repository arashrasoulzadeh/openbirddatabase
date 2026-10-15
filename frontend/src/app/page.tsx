'use client';

import { useCallback, useEffect, useState } from 'react';
import SearchBar from '@/components/SearchBar';
import SpeciesList from '@/components/SpeciesList';
import TaxonomyTree from '@/components/TaxonomyTree';
import FilterBar from '@/components/FilterBar';
import SiteHeader from '@/components/SiteHeader';
import { searchSpecies, getTaxonomy, getFilterOptions, Filters } from '@/lib/api';
import { useI18n } from '@/lib/i18n/I18nProvider';

export default function Home() {
  const { t } = useI18n();
  const [query, setQuery] = useState('');
  const [species, setSpecies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState(false);
  const [view, setView] = useState<'list' | 'taxonomy'>('list');
  const [taxonomy, setTaxonomy] = useState<any>(null);
  const [filters, setFilters] = useState<Filters>({});
  const [filterOptions, setFilterOptions] = useState<Record<string, Record<string, number>> | null>(null);

  const runSearch = useCallback(async (q: string, f: Filters = {}) => {
    setLoading(true);
    setError(false);
    try {
      const data = await searchSpecies(q, 50, 0, f);
      setSpecies(data.hits || []);
      setTotal(data.total ?? data.estimatedTotalHits ?? 0);
    } catch (e) {
      console.error('Search error:', e);
      setError(true);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    getFilterOptions().then(setFilterOptions).catch((e) => console.error('Filter options error:', e));
  }, []);

  // Re-run the search when a filter changes (typing is debounced inside SearchBar)
  useEffect(() => {
    runSearch(query, filters);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters, runSearch]);

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
            </div>
          </div>
        </section>
      )}

      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-6 sm:px-6">
        {view === 'list' ? (
          <div className="flex flex-col gap-5">
            <FilterBar options={filterOptions} value={filters} onChange={setFilters} />
            {!loading && !error && species.length > 0 && (
              <p className="text-sm text-stone-500">{t('speciesCount', { count: total.toLocaleString() })}</p>
            )}
            {error && <div className="rounded-xl bg-red-50 py-8 text-center text-red-700">{t('searchError')}</div>}
            {!loading && !error && species.length === 0 && (
              <div className="py-16 text-center text-lg text-stone-500">{t('noResults')}</div>
            )}
            {loading && species.length === 0 && <div className="py-16 text-center text-stone-400">{t('searching')}</div>}
            <div className={loading && species.length > 0 ? 'opacity-60 transition-opacity' : 'transition-opacity'}>
              <SpeciesList species={species} />
            </div>
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

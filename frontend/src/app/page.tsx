'use client';

import { useCallback, useEffect, useState } from 'react';
import SearchBar from '@/components/SearchBar';
import SpeciesList from '@/components/SpeciesList';
import TaxonomyTree from '@/components/TaxonomyTree';
import LanguageSwitcher from '@/components/LanguageSwitcher';
import FilterBar from '@/components/FilterBar';
import { searchSpecies, getTaxonomy, getFilterOptions, Filters } from '@/lib/api';
import { useI18n } from '@/lib/i18n/I18nProvider';

export default function Home() {
  const { t } = useI18n();
  const [query, setQuery] = useState('');
  const [species, setSpecies] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
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
      className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
        view === id ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:bg-gray-100'
      }`}
    >
      {label}
    </button>
  );

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 gap-3">
            <div className="flex items-center gap-2">
              <span className="text-2xl" aria-hidden="true">🐦</span>
              <h1 className="text-xl font-bold text-gray-900">OpenBird</h1>
            </div>
            <nav className="flex items-center gap-2 sm:gap-4">
              {tab('list', t('search'))}
              {tab('taxonomy', t('taxonomy'))}
              <span className="hidden md:inline text-sm text-gray-500">{t('speciesCount', { count: total.toLocaleString() })}</span>
              <LanguageSwitcher />
            </nav>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-6">
        {view === 'list' ? (
          <div className="flex flex-col gap-4">
            <SearchBar value={query} onChange={setQuery} onSearch={(q) => runSearch(q, filters)} loading={loading} placeholder={t('searchHint')} />
            <FilterBar options={filterOptions} value={filters} onChange={setFilters} />
            {loading && <div className="text-center py-8 text-gray-500">{t('searching')}</div>}
            {error && <div className="text-center py-8 text-red-600">{t('searchError')}</div>}
            {!loading && !error && species.length === 0 && (
              <div className="text-center py-12">
                <p className="text-gray-500 text-lg">{query ? t('noResults') : t('searchPrompt')}</p>
              </div>
            )}
            <SpeciesList species={species} />
          </div>
        ) : (
          <TaxonomyTree tree={taxonomy} />
        )}
      </main>

      <footer className="bg-white border-t border-gray-200 py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-sm text-gray-500">
          <p>{t('footerText')}</p>
          <p className="mt-1">{t('dataSources')}: {t('dataSourcesSubtitle')}</p>
        </div>
      </footer>
    </div>
  );
}

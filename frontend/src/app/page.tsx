'use client';

import { useState, useEffect } from 'react';
import SearchBar from '@/components/SearchBar';
import SpeciesList from '@/components/SpeciesList';
import SpeciesDetail from '@/components/SpeciesDetail';
import TaxonomyTree from '@/components/TaxonomyTree';
import { Species } from '@/lib/types';

export default function Home() {
  const [searchQuery, setSearchQuery] = useState('');
  const [species, setSpecies] = useState<Species[]>([]);
  const [selectedSpecies, setSelectedSpecies] = useState<Species | null>(null);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [viewMode, setViewMode] = useState<'list' | 'detail' | 'taxonomy'>('list');
  const [taxonomyTree, setTaxonomyTree] = useState<any>(null);

  const searchSpecies = async (query: string) => {
    setLoading(true);
    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ q: query, limit: 50 }),
      });
      const data = await response.json();
      setSpecies(data.hits || []);
      setTotal(data.total || 0);
      setSelectedSpecies(null);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSpeciesClick = (species: Species) => {
    setSelectedSpecies(species);
    setViewMode('detail');
  };

  const loadTaxonomy = async () => {
    try {
      const response = await fetch('/api/taxonomy');
      const data = await response.json();
      setTaxonomyTree(data);
    } catch (error) {
      console.error('Taxonomy load error:', error);
    }
  };

  useEffect(() => {
    loadTaxonomy();
    searchSpecies('');
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <span className="text-2xl">🐦</span>
              <h1 className="text-xl font-bold text-gray-900">OpenBird</h1>
              <span className="text-xs text-gray-500 px-2 py-1 bg-gray-100 rounded">v1.0</span>
            </div>
            <nav className="flex items-center gap-4">
              <button
                onClick={() => setViewMode('list')}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  viewMode === 'list' ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                Search
              </button>
              <button
                onClick={() => { setViewMode('taxonomy'); loadTaxonomy(); }}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  viewMode === 'taxonomy' ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                Taxonomy
              </button>
              <span className="text-sm text-gray-500">{total.toLocaleString()} species</span>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-6">
        {viewMode === 'list' && (
          <div className="flex flex-col gap-4">
            <SearchBar 
              value={searchQuery} 
              onChange={setSearchQuery} 
              onSearch={searchSpecies}
              loading={loading}
              placeholder="Search birds (scientific, English, Persian)..."
            />
            {loading && <div className="text-center py-8 text-gray-500">Searching...</div>}
            {!loading && species.length === 0 && searchQuery && (
              <div className="text-center py-8 text-gray-500">No results found</div>
            )}
            <SpeciesList species={species} onSelect={handleSpeciesClick} />
          </div>
        )}

        {viewMode === 'detail' && selectedSpecies && (
          <div className="max-w-4xl mx-auto">
            <button
              onClick={() => { setViewMode('list'); setSelectedSpecies(null); }}
              className="mb-4 text-sm text-blue-600 hover:underline flex items-center gap-1"
            >
              ← Back to search
            </button>
            <SpeciesDetail species={selectedSpecies} />
          </div>
        )}

        {viewMode === 'taxonomy' && (
          <div>
            <TaxonomyTree tree={taxonomyTree} onSelect={handleSpeciesClick} />
          </div>
        )}

        {viewMode === 'list' && !loading && species.length === 0 && !searchQuery && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">Start typing to search 11,149 bird species</p>
            <p className="text-gray-400 text-sm mt-1">Search by scientific name, English name, or Persian name</p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-sm text-gray-500">
          <p>OpenBird Database • 11,149 species • Multilingual (Persian, English + 430+)</p>
          <p className="mt-1">Data sources: BirdNET, BIRDBASE, AVONICHE, BirdFYI, GBIF, eBird</p>
        </div>
      </footer>
    </div>
  );
}
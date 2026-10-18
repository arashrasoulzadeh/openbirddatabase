'use client';

import { useRef, useEffect } from 'react';

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  onSearch: (query: string) => void;
  loading: boolean;
  placeholder?: string;
}

export default function SearchBar({ value, onChange, onSearch, loading, placeholder }: SearchBarProps) {
  const timeoutRef = useRef<NodeJS.Timeout>();
  // Keep the latest callback in a ref so a new function identity on each parent
  // render does not retrigger the debounce (which caused an endless search loop).
  const onSearchRef = useRef(onSearch);
  onSearchRef.current = onSearch;
  const isFirstRun = useRef(true);

  useEffect(() => {
    // The page already loads the initial results on mount
    if (isFirstRun.current) {
      isFirstRun.current = false;
      return;
    }
    timeoutRef.current = setTimeout(() => onSearchRef.current(value), 120);
    return () => clearTimeout(timeoutRef.current);
  }, [value]);

  return (
    <div className="relative">
      <svg className="pointer-events-none absolute inset-y-0 start-4 my-auto h-5 w-5 text-stone-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
      <input
        type="search"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && onSearch(value)}
        placeholder={placeholder || 'Search birds...'}
        aria-label={placeholder || 'Search birds'}
        className="w-full rounded-xl border-0 bg-white py-3.5 ps-12 pe-12 text-sm text-stone-900 sm:text-base shadow-lg ring-1 ring-black/5 placeholder:text-stone-400 focus:outline-none focus:ring-2 focus:ring-brand-400"
      />
      {loading && (
        <span className="absolute inset-y-0 end-4 my-auto h-5 w-5 animate-spin rounded-full border-2 border-stone-200 border-t-brand-600" aria-hidden="true" />
      )}
    </div>
  );
}

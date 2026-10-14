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
    timeoutRef.current = setTimeout(() => onSearchRef.current(value), 300);
    return () => clearTimeout(timeoutRef.current);
  }, [value]);

  return (
    <div className="relative">
      <div className="relative">
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && onSearch(value)}
          disabled={false}
          className="w-full px-4 py-3 ps-10 text-base border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow"
          placeholder={placeholder || 'Search birds...'}
        />
        <div className="absolute inset-y-0 start-0 ps-3 flex items-center pointer-events-none">
          <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>
    </div>
  );
}
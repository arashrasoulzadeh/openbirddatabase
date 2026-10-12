import { API_URL, API_SERVER_URL } from './config';

// In the browser use the public API domain; during SSR prefer the internal URL.
const base = () => (typeof window === 'undefined' ? API_SERVER_URL : API_URL);

async function getJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${base()}${path}`, init);
  if (!res.ok) throw new Error(`API ${res.status} for ${path}`);
  return res.json() as Promise<T>;
}

export interface SearchResponse {
  hits: any[];
  total?: number;
  estimatedTotalHits?: number;
}

export function searchSpecies(q: string, limit = 50, offset = 0): Promise<SearchResponse> {
  const params = new URLSearchParams({ q, limit: String(limit), offset: String(offset) });
  return getJson(`/search?${params}`);
}

export function getTaxonomy(): Promise<any> {
  return getJson('/taxonomy', { next: { revalidate: 3600 } } as RequestInit);
}

export function getSpecies(scientificName: string, lang = 'en'): Promise<any> {
  return getJson(`/species/${encodeURIComponent(scientificName)}?lang=${lang}`, {
    next: { revalidate: 3600 },
  } as RequestInit);
}

export function getStats(): Promise<any> {
  return getJson('/stats', { next: { revalidate: 3600 } } as RequestInit);
}

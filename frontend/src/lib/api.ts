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
  interpreted?: { filters: Record<string, string[]>; words: string[]; ignored: string[] };
  corrected_query?: string;
  total?: number;
  estimatedTotalHits?: number;
}

export type Filters = Partial<Record<
  'iucn_status' | 'order' | 'primary_habitat' | 'primary_diet' | 'migration_status',
  string
>>;

/** `lang` makes each hit carry only English + that language's name (about a third of the bytes). */
export function searchSpecies(q: string, limit = 50, offset = 0, filters: Filters = {}, lang?: string, init?: RequestInit): Promise<SearchResponse> {
  const params = new URLSearchParams({ q, limit: String(limit), offset: String(offset) });
  if (lang) params.set('lang', lang);
  for (const [k, v] of Object.entries(filters)) if (v) params.set(k, v);
  return getJson(`/search?${params}`, init);
}

/** Available filter values with counts: { iucn_status: { LC: 1234, ... }, ... } */
export function getFilterOptions(): Promise<Record<string, Record<string, number>>> {
  return getJson('/filters', { next: { revalidate: 3600 } } as RequestInit);
}

/** The taxonomy tree. With a language the API returns one common name per species (about a quarter of the size). */
export function getTaxonomy(lang?: string): Promise<any> {
  return getJson(lang ? `/taxonomy?lang=${encodeURIComponent(lang)}` : '/taxonomy', { next: { revalidate: 3600 } } as RequestInit);
}

export function getSpecies(scientificName: string, lang = 'en'): Promise<any> {
  return getJson(`/species/${encodeURIComponent(scientificName)}?lang=${lang}`, {
    next: { revalidate: 3600 },
  } as RequestInit);
}

export function getStats(): Promise<any> {
  return getJson('/stats', { next: { revalidate: 3600 } } as RequestInit);
}

export function getRandomSpecies(): Promise<any> {
  return getJson('/random', { cache: 'no-store' });
}

/** Genera of one family: { genus: [{ scientific, common_en, common_fa, names? }] } */
export function getFamily(order: string, family: string): Promise<Record<string, any[]>> {
  return getJson(`/taxonomy/${encodeURIComponent(order)}/${encodeURIComponent(family)}`, {
    next: { revalidate: 3600 },
  } as RequestInit);
}

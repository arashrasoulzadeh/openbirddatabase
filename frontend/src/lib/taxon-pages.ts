import { getTaxonomy } from './api';
import { Lang } from './i18n/locales';
import { helpText } from './i18n/help';

export const fill = (lang: Lang, key: string, params: Record<string, string | number> = {}) =>
  Object.entries(params).reduce((s, [k, v]) => s.replaceAll(`{${k}}`, String(v)), helpText(lang, key) ?? '');

export interface FamilyInfo {
  name: string;
  species: number;
}
export interface SpeciesEntry {
  scientific: string;
  id?: string;
  name?: string;
  common_en?: string;
}

/** Orders > families > genera > species, with one common name per species in `lang` (cached by Next for an hour). */
export async function loadTree(lang: Lang): Promise<Record<string, Record<string, Record<string, SpeciesEntry[]>>>> {
  return getTaxonomy(lang);
}

const count = (genera: Record<string, SpeciesEntry[]>) => Object.values(genera).reduce((n, list) => n + list.length, 0);

export function familiesOf(tree: Awaited<ReturnType<typeof loadTree>>, order: string): FamilyInfo[] {
  return Object.entries(tree[order] || {})
    .map(([name, genera]) => ({ name, species: count(genera) }))
    .sort((a, b) => b.species - a.species || a.name.localeCompare(b.name));
}

/** The key in `keys` that equals `wanted` ignoring case ("passeriformes" -> "Passeriformes"). */
export const matchKey = (keys: string[], wanted: string) => keys.find((k) => k.toLowerCase() === wanted.toLowerCase());

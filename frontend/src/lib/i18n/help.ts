import { tables } from './store';
import { Lang } from './locales';

const table = tables.help;

/** Plain-language explanation for a key like "field.habitat.primary" or "value.Resident"; falls back to English. */
export function helpText(lang: Lang, key: string): string | undefined {
  return table[key]?.[lang] ?? table[key]?.en;
}

export const fieldHelp = (lang: Lang, path: string) => helpText(lang, `field.${path}`);
export const valueHelp = (lang: Lang, value: string) => helpText(lang, `value.${value}`);

// --- biogeographic realms ---------------------------------------------------
// The data stores realms as letter codes (e.g. "LN" = Neotropical + Nearctic). Meanings derived from the species that
// carry each code; E and C describe very wide ranges rather than a single region.
export const REALMS: Record<string, { color: string; emoji: string }> = {
  L: { color: '#059669', emoji: '🌎' },
  N: { color: '#2563eb', emoji: '🌎' },
  F: { color: '#d97706', emoji: '🌍' },
  M: { color: '#ea580c', emoji: '🌍' },
  P: { color: '#7c3aed', emoji: '🌍' },
  E: { color: '#c026d3', emoji: '🌍' },
  I: { color: '#e11d48', emoji: '🌏' },
  A: { color: '#0284c7', emoji: '🌏' },
  W: { color: '#0d9488', emoji: '🌏' },
  O: { color: '#0891b2', emoji: '🌏' },
  Z: { color: '#65a30d', emoji: '🌏' },
  S: { color: '#64748b', emoji: '🧊' },
  C: { color: '#78716c', emoji: '🌐' },
};

/** ["LN", "p"] -> ["L", "N", "P"] (each element can hold several codes; duplicates and unknown codes are dropped). */
export function splitRealms(values: unknown[]): string[] {
  const out: string[] = [];
  for (const v of values) {
    for (const ch of String(v).toUpperCase()) {
      if (REALMS[ch] && !out.includes(ch)) out.push(ch);
    }
  }
  return out;
}

// --- external links for identifiers ------------------------------------------
export const ID_LINKS: Record<string, { site: string; url: (v: string) => string }> = {
  ebird_code: { site: 'eBird', url: (v) => `https://ebird.org/species/${encodeURIComponent(v)}` },
  gbif_key: { site: 'GBIF', url: (v) => `https://www.gbif.org/species/${encodeURIComponent(v)}` },
  avibase_id: { site: 'Avibase', url: (v) => `https://avibase.bsc-eoc.org/species.jsp?avibaseid=${encodeURIComponent(v)}` },
};

export const xenoCantoUrl = (id: string) => `https://xeno-canto.org/${String(id).replace(/^XC/i, '')}`;

// --- units ------------------------------------------------------------------------
const UNIT_BY_SUFFIX: [string, string][] = [['_g', 'g'], ['_cm', 'cm'], ['_mm', 'mm'], ['_m', 'm']];

/** Number with its unit, e.g. 18.37 -> "18.4 g"; survival rates (0-1) become percentages. */
export function formatMeasurement(lang: Lang, path: string, value: number, unitWord: (k: string) => string): string {
  const name = path.split('.').pop() as string;
  if (name.startsWith('annual_survival') && value <= 1) return `${Math.round(value * 100)}%`;
  const digits = Number.isInteger(value) ? 0 : value >= 100 ? 0 : value >= 10 ? 1 : 2;
  const text = new Intl.NumberFormat(lang, { maximumFractionDigits: digits }).format(value);
  if (name === 'density_individuals_per_km2') return `${text} / km²`;
  if (name === 'range_size_km2') return `${text} km²`;
  if (name.endsWith('_days')) return `${text} ${unitWord('days')}`;
  if (name.endsWith('_months')) return `${text} ${unitWord('months')}`;
  if (name.endsWith('_years')) return `${text} ${unitWord('years')}`;
  const unit = UNIT_BY_SUFFIX.find(([suffix]) => name.endsWith(suffix))?.[1];
  return unit ? `${text} ${unit}` : text;
}

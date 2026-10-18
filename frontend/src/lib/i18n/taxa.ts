import { tables } from './store';
import { Lang } from './locales';

const table = tables.taxa;

/** Common name of an order or family in the chosen language ("Passeriformes" -> "Passerines"), or '' if there is none. */
export function taxonLabel(lang: Lang, latin: string): string {
  const text = table[latin]?.[lang];
  if (!text || text.toLowerCase() === latin.toLowerCase()) return '';
  return /^[぀-ヿ㐀-鿿]/.test(text) ? text : text.charAt(0).toLocaleUpperCase(lang) + text.slice(1);
}

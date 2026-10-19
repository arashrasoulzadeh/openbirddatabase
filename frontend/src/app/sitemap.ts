import type { MetadataRoute } from 'next';
import { SITE_URL } from '@/lib/config';
import { languageUrls } from '@/lib/i18n/routes';
import { loadTree } from '@/lib/taxon-pages';

// Built per request (the API is not reachable at Docker build time) but remembered for an hour, so crawlers never trigger
// a rebuild of the ~12,000 entries. Every entry lists all 13 language versions (hreflang), which is how search engines
// find the translated pages; the English URL is the entry itself.
export const dynamic = 'force-dynamic';

const TTL_MS = 60 * 60 * 1000;
let cached: { at: number; entries: MetadataRoute.Sitemap } | null = null;

const entry = (path: string, changeFrequency: 'weekly' | 'monthly', priority: number): MetadataRoute.Sitemap[number] => ({
  url: SITE_URL + (path === '/' ? '' : path),
  changeFrequency,
  priority,
  alternates: { languages: languageUrls(SITE_URL, path) },
});

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  if (cached && Date.now() - cached.at < TTL_MS) return cached.entries;
  const entries: MetadataRoute.Sitemap = [entry('/', 'weekly', 1)];
  try {
    const tree = await loadTree('en');
    const encode = encodeURIComponent;
    for (const [order, families] of Object.entries(tree)) {
      entries.push(entry(`/order/${encode(order)}`, 'monthly', 0.7));
      for (const [family, genera] of Object.entries(families)) {
        entries.push(entry(`/family/${encode(order)}/${encode(family)}`, 'monthly', 0.6));
        for (const list of Object.values(genera)) {
          for (const sp of list) entries.push(entry(`/species/${encode(sp.scientific)}`, 'monthly', 0.8));
        }
      }
    }
    cached = { at: Date.now(), entries };
  } catch (e) {
    console.error('sitemap: could not load taxonomy', e);
  }
  return entries; // on an API failure only the home page is listed, and the next request tries again
}

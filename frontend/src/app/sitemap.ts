import type { MetadataRoute } from 'next';
import { getTaxonomy } from '@/lib/api';
import { SITE_URL } from '@/lib/config';

// Rendered per request (the API is not reachable at Docker build time); the taxonomy fetch
// underneath is cached for an hour, so this stays cheap. Lists the home page and every species page.
export const dynamic = 'force-dynamic';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const entries: MetadataRoute.Sitemap = [{ url: SITE_URL, changeFrequency: 'weekly', priority: 1 }];
  try {
    const tree = await getTaxonomy();
    for (const families of Object.values<any>(tree)) {
      for (const genera of Object.values<any>(families)) {
        for (const species of Object.values<any[]>(genera)) {
          for (const sp of species) {
            entries.push({
              url: `${SITE_URL}/species/${encodeURIComponent(sp.scientific)}`,
              changeFrequency: 'monthly',
              priority: 0.6,
            });
          }
        }
      }
    }
  } catch (e) {
    console.error('sitemap: could not load taxonomy', e);
  }
  return entries;
}

import type { MetadataRoute } from 'next';
import { SITE_URL } from '@/lib/config';

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        disallow: [
          '/analytics', // the private statistics dashboard (also under every language prefix)
          '/*/analytics',
          '/*?', // searches and filters (?q=, ?iucn_status=...) are endless and not worth indexing: pages have clean URLs
        ],
      },
    ],
    sitemap: `${SITE_URL}/sitemap.xml`,
    host: SITE_URL,
  };
}

import type { MetadataRoute } from 'next';

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: 'OpenBird Database',
    short_name: 'OpenBird',
    description: 'Free bird database: 11,000+ species with names in 13 languages.',
    start_url: '/',
    display: 'standalone',
    background_color: '#f1f7f3',
    theme_color: '#27523d',
    icons: [
      { src: '/icon.svg', sizes: 'any', type: 'image/svg+xml', purpose: 'any' },
      { src: '/apple-icon.png', sizes: '180x180', type: 'image/png' },
    ],
  };
}

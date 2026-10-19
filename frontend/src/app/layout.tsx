import './globals.css';
import type { Metadata, Viewport } from 'next';
import { Inter, Vazirmatn } from 'next/font/google';
import { I18nProvider } from '@/lib/i18n/I18nProvider';
import Tracker from '@/components/Tracker';
import { SITE_URL } from '@/lib/config';
import { sliceFor } from '@/lib/i18n/bundle';
import { dirOf } from '@/lib/i18n/locales';
import { requestLang } from '@/lib/i18n/server';

// Fonts are downloaded at build time and served from this site (no render-blocking request to Google), with only the
// character sets a page needs loaded.
const inter = Inter({ subsets: ['latin', 'latin-ext', 'cyrillic'], display: 'swap', variable: '--ff-inter' });
const vazir = Vazirmatn({ subsets: ['arabic', 'latin'], display: 'swap', variable: '--ff-vazir' });

// Page-level metadata (title, description, canonical, hreflang, social cards) is set by each page with lib/seo.ts.
export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: { default: 'OpenBird Database', template: '%s' },
  applicationName: 'OpenBird',
  robots: {
    index: true,
    follow: true,
    googleBot: { index: true, follow: true, 'max-image-preview': 'large', 'max-snippet': -1, 'max-video-preview': -1 },
  },
  formatDetection: { telephone: false },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#27523d',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const lang = requestLang(); // from the URL: /fa/... is Persian, everything else English

  return (
    <html lang={lang} dir={dirOf(lang)} className={`${inter.variable} ${vazir.variable}`}>
      <body className="min-h-screen bg-gray-50 font-sans antialiased">
        <I18nProvider initialLang={lang} tables={sliceFor(lang)}>
          <Tracker />
          {children}
        </I18nProvider>
      </body>
    </html>
  );
}

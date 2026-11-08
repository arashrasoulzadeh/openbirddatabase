import './globals.css';
import type { Metadata, Viewport } from 'next';
import { Inter, Vazirmatn } from 'next/font/google';
import { I18nProvider } from '@/lib/i18n/I18nProvider';
import Tracker from '@/components/Tracker';
import { SITE_URL } from '@/lib/config';
import { sliceFor } from '@/lib/i18n/bundle';
import { dirOf } from '@/lib/i18n/locales';
import { requestLang } from '@/lib/i18n/server';
import Script from 'next/script';

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
        <Script async src="https://www.googletagmanager.com/gtm.js?id=GTM-MBCW9VJH" />
        <Script id="gtm-init" strategy="afterInteractive">{`window.dataLayer = window.dataLayer || []; function gtag(){dataLayer.push(arguments);} gtag('js', new Date());`}</Script>
        <I18nProvider initialLang={lang} tables={sliceFor(lang)}>
          <Tracker />
          {children}
        </I18nProvider>
        <footer className="border-t border-stone-200 bg-white py-4 text-center text-sm text-stone-500">
          <a href="https://takhfifbazaar.ir?utm_source=birds.meetarash.ir&utm_medium=referral&utm_campaign=footer" target="_blank" rel="noopener noreferrer" className="font-medium text-brand-700 hover:underline">تخفیف های لحظه ای</a>
        </footer>
      </body>
    </html>
  );
}

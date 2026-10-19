import type { Metadata } from 'next';
import { SITE_URL } from './config';
import { LOCALES, Lang, OG_LOCALE } from './i18n/locales';
import { fullUrl, languageUrls } from './i18n/routes';

export const SITE_NAME = 'OpenBird';

interface PageSeo {
  lang: Lang;
  /** English-URL path of the page ("/species/Parus%20major"); the language prefix is added here. */
  path: string;
  title: string;
  description: string;
  /** Absolute image URL for link previews (defaults to the site image). */
  image?: string;
  imageAlt?: string;
  type?: 'website' | 'article';
  noindex?: boolean;
}

/** Title, description, canonical URL, hreflang alternates, Open Graph and Twitter card for one page in one language. */
export function pageMetadata({ lang, path, title, description, image, imageAlt, type = 'website', noindex }: PageSeo): Metadata {
  const url = fullUrl(SITE_URL, lang, path);
  // pages without their own photo use the site's preview image (page metadata replaces the layout's, so it is set here)
  const shown = image || `${SITE_URL}/opengraph-image`;
  const images = [{ url: shown, alt: imageAlt || title, ...(image ? {} : { width: 1200, height: 630 }) }];
  return {
    title,
    description,
    alternates: { canonical: url, languages: languageUrls(SITE_URL, path) },
    robots: noindex ? { index: false, follow: false } : undefined,
    openGraph: {
      type,
      url,
      siteName: SITE_NAME,
      title,
      description,
      locale: OG_LOCALE[lang],
      alternateLocale: LOCALES.filter((l) => l.code !== lang).map((l) => OG_LOCALE[l.code]),
      images,
    },
    twitter: { card: 'summary_large_image', title, description, images: [shown] },
  };
}

/** Shortens text at a word boundary for meta descriptions (search engines show about 155 characters). */
export function clip(text: string, max = 158): string {
  const t = text.replace(/\s+/g, ' ').trim();
  if (t.length <= max) return t;
  const cut = t.slice(0, max - 1);
  return cut.slice(0, Math.max(cut.lastIndexOf(' '), max - 25)).replace(/[,;:(\-–]\s*$/, '') + '…';
}

/** Absolute URL of a page in a language. */
export const absoluteUrl = (lang: Lang, path: string) => fullUrl(SITE_URL, lang, path);

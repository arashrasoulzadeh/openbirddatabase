import { PREFIXED_LANGS, fullUrl, languageUrls, localePath, splitLang } from '@/lib/i18n/routes';
import { clip, pageMetadata } from '@/lib/seo';

describe('language URLs', () => {
  it('English has no prefix, every other language has one', () => {
    expect(PREFIXED_LANGS).toHaveLength(12);
    expect(localePath('en', '/species/Parus%20major')).toBe('/species/Parus%20major');
    expect(localePath('fa', '/species/Parus%20major')).toBe('/fa/species/Parus%20major');
    expect(localePath('fa', '/')).toBe('/fa');
  });

  it('splits a URL path back into language and page', () => {
    expect(splitLang('/fa/species/X')).toEqual({ lang: 'fa', path: '/species/X' });
    expect(splitLang('/fa')).toEqual({ lang: 'fa', path: '/' });
    expect(splitLang('/species/X')).toEqual({ lang: 'en', path: '/species/X' });
    expect(splitLang('/analytics')).toEqual({ lang: 'en', path: '/analytics' }); // "an" is not a language
    expect(splitLang('/de-fake/x').lang).toBe('en');
  });

  it('lists all 13 languages plus x-default for hreflang, English being the default', () => {
    const urls = languageUrls('https://s.org', '/order/Strigiformes');
    expect(Object.keys(urls)).toHaveLength(14);
    expect(urls.en).toBe('https://s.org/order/Strigiformes');
    expect(urls['x-default']).toBe(urls.en);
    expect(urls.ja).toBe('https://s.org/ja/order/Strigiformes');
    expect(fullUrl('https://s.org', 'en', '/')).toBe('https://s.org'); // same form as the sitemap entry
    expect(languageUrls('https://s.org', '/').tr).toBe('https://s.org/tr');
  });
});

describe('page metadata', () => {
  it('sets canonical, alternates, social cards and the language of the page', () => {
    const m = pageMetadata({ lang: 'fa', path: '/species/X', title: 'T', description: 'D' });
    expect(String(m.alternates?.canonical)).toMatch(/\/fa\/species\/X$/);
    expect(Object.keys(m.alternates?.languages as object)).toHaveLength(14);
    expect(m.openGraph).toMatchObject({ locale: 'fa_IR', title: 'T', siteName: 'OpenBird' });
    expect((m.twitter as { card: string }).card).toBe('summary_large_image');
    expect(JSON.stringify(m.openGraph)).toContain('opengraph-image'); // site preview image when the page has no photo
  });

  it('uses the species photo for link previews and can mark a page noindex', () => {
    const m = pageMetadata({ lang: 'en', path: '/', title: 'T', description: 'D', image: 'https://api/images/a/1.jpg', noindex: true });
    expect(JSON.stringify(m.openGraph)).toContain('https://api/images/a/1.jpg');
    expect(m.robots).toEqual({ index: false, follow: false });
  });
});

describe('clip', () => {
  it('keeps short text and cuts long text on a word boundary', () => {
    expect(clip('short text')).toBe('short text');
    const out = clip('word '.repeat(60), 100);
    expect(out.length).toBeLessThanOrEqual(100);
    expect(out.endsWith('…')).toBe(true);
    expect(out).not.toMatch(/wor…$/);
  });
});

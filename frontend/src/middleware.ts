import { NextRequest, NextResponse } from 'next/server';
import { DEFAULT_LANG, LANG_COOKIE, isLang, langFromAcceptLanguage } from '@/lib/i18n/locales';
import { LANG_HEADER, localePath, splitLang } from '@/lib/i18n/routes';

const BOT = /bot|crawl|spider|slurp|bing|yandex|baidu|duckduck|facebookexternalhit|twitter|whatsapp|telegram|linkedin|preview|lighthouse|pagespeed|gtmetrix/i;

/**
 * Language lives in the URL (/fa/species/...), so every language version can be indexed.
 *  - /fa/x          -> served from /x in Persian (rewrite, the address stays /fa/x)
 *  - /en/x          -> 308 to /x (English has no prefix, one URL per page)
 *  - /x for a visitor who chose another language (cookie) or whose browser asks for one (Accept-Language) -> 302 to /fa/x.
 *    Crawlers are never redirected: they get the English page at /x and find the others through hreflang.
 */
export function middleware(req: NextRequest) {
  const { pathname, search } = req.nextUrl;
  const m = pathname.match(/^\/([a-z]{2})(\/.*)?$/);

  if (m && m[1] === DEFAULT_LANG) {
    const url = req.nextUrl.clone();
    url.pathname = m[2] || '/';
    return NextResponse.redirect(url, 308);
  }

  const { lang, path } = splitLang(pathname);
  const headers = new Headers(req.headers);
  headers.set(LANG_HEADER, lang);

  if (lang !== DEFAULT_LANG) {
    const url = req.nextUrl.clone();
    url.pathname = path;
    const res = NextResponse.rewrite(url, { request: { headers } });
    res.cookies.set(LANG_COOKIE, lang, { path: '/', maxAge: 31536000, sameSite: 'lax' }); // remember the choice
    return res;
  }

  // unprefixed = English; send people who want another language to it (GET pages only, never crawlers)
  if ((req.method === 'GET' || req.method === 'HEAD') && !BOT.test(req.headers.get('user-agent') || '')) {
    const cookie = req.cookies.get(LANG_COOKIE)?.value;
    const wanted = isLang(cookie) ? cookie : cookie ? DEFAULT_LANG : langFromAcceptLanguage(req.headers.get('accept-language'));
    if (wanted !== DEFAULT_LANG) {
      const url = req.nextUrl.clone();
      url.pathname = localePath(wanted, pathname);
      url.search = search;
      const res = NextResponse.redirect(url, 302);
      res.headers.set('Vary', 'Accept-Language, Cookie');
      return res;
    }
  }
  const res = NextResponse.next({ request: { headers } });
  res.headers.set('Vary', 'Accept-Language, Cookie');
  return res;
}

export const config = {
  // pages only: not static files, Next internals, or the files search engines fetch
  matcher: ['/((?!_next/|api/|favicon|icon|apple-icon|opengraph-image|twitter-image|robots.txt|sitemap|manifest|maps/|.*\\.[a-zA-Z0-9]+$).*)'],
};

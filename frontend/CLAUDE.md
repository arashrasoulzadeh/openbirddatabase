# Frontend (Next.js)

Next.js + Tailwind web app for browsing the bird database. Source in `src/`.

- Test: `npm test` (Jest, config in `jest.config.js`, setup in `jest.setup.ts`); also `test:watch`, `test:coverage`
- Dev: `npm run dev`
- Data comes from the API in `../_scripts/api.py`; species data lives in `../birds/`.

## Website notes

- Public URLs come from the repo-root `.env` (`API_DOMAIN`, `SITE_DOMAIN`); see `docs/DEPLOYMENT.md`.
- i18n: UI strings come from the Flutter `.arb` files via `npm run i18n` (regenerates `src/lib/i18n/messages.json`, commit it).
  Categorical data values are translated in `src/lib/i18n/values.json`. The language is part of the URL: English at `/species/X`, the other
  12 languages under a prefix (`/fa/species/X`); `src/middleware.ts` rewrites the prefix away and sets the `x-lang` header that server code reads with
  `requestLang()` (`src/lib/i18n/server.ts`). Build internal links with `localePath(lang, path)` (`src/lib/i18n/routes.ts`).
- SEO: each page exports `generateMetadata` built with `pageMetadata()` (`src/lib/seo.ts`: title, description, canonical, hreflang, Open Graph,
  Twitter) and renders `<JsonLd>` structured data. `sitemap.ts` lists every page with its 13 language versions, `robots.ts` blocks `/analytics`
  and query URLs. Taxonomy landing pages: `/order/[order]` and `/family/[order]/[family]`. New website-only strings go in `help.json` (`seo.*`, `taxon.*`).
- The API is the only data source; there are no Next.js API routes.
- Analytics: `src/lib/analytics.ts` posts events to the API (text/plain, no preflight); `Tracker` records page views and visible time,
  `TrackedLink` records bird clicks with their source. Add `track(...)` calls for new interactions. Charts live in
  `src/components/charts/` (plain SVG).

# OpenBird Website

Next.js 14 (App Router, Tailwind) public website for the OpenBird Database. It reads everything from the API
(`_scripts/api.py`); there are no Next.js API routes.

## Features

- **Search** across 11,149 species by scientific name or any of 13 languages; keyword + vector search when MeiliSearch is configured
- **Filters**: conservation status, habitat, diet, migration, order (translated, with counts)
- **Load more** pagination and **shareable URLs** (`?q=tit&iucn_status=LC`) that restore search, filters and tab
- **Taxonomy browser**: orders → families → genera → species with counts; children render only when opened
- **Species pages** (`/species/<scientific name>`): quick facts, every data section, names in all languages, related species
- **Random bird** button
- **13 languages** (en, fa, ar, es, fr, de, pt, ru, ja, zh, nl, pl, tr) with right-to-left layout for Persian and Arabic;
  species names are shown in the chosen language with the English and scientific names alongside
- **SEO**: `/sitemap.xml` (all species), `/robots.txt`, canonical links, Open Graph tags
- Responsive design; language switcher visible on phones

## Getting started

Prerequisites: Node.js 20+ and the API running on `http://localhost:8000`
(`uvicorn _scripts.api:app --reload` from the repo root).

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev        # http://localhost:3000
```

## Environment variables

| Variable | Purpose | Default |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Public API address; used by the browser and baked into the build | `http://localhost:8000` |
| `NEXT_PUBLIC_SITE_URL` | Public address of the site (sitemap, canonical links) | `http://localhost:3000` |
| `API_INTERNAL_URL` | Address server-side rendering uses to reach the API (e.g. `http://api:8000` in Docker) | `NEXT_PUBLIC_API_URL` |

In production these come from the repo-root `.env` (`API_DOMAIN`, `SITE_DOMAIN`) through `docker-compose.yml`.
Because the public URLs are baked in at build time, change `.env` and rebuild (`docker compose up -d --build`).

## Project structure

```
frontend/
├── scripts/sync-i18n.mjs        # builds src/lib/i18n/messages.json from the Flutter .arb files
├── src/
│   ├── app/
│   │   ├── layout.tsx           # <html lang/dir> from the language cookie, i18n provider
│   │   ├── page.tsx             # search, filters, taxonomy tab, URL state
│   │   ├── species/[name]/      # species page (server-rendered)
│   │   ├── sitemap.ts, robots.ts
│   │   └── globals.css
│   ├── components/              # SiteHeader, LanguageSwitcher, SearchBar, FilterBar, SpeciesList,
│   │                            # TaxonomyTree, IucnBadge (SpeciesDetail*.tsx are older and unused by the pages)
│   └── lib/
│       ├── api.ts, config.ts    # API client and URLs
│       └── i18n/                # locales, translate helpers, provider, messages.json, values.json
├── Dockerfile                   # standalone Next.js build (node_modules kept in a BuildKit cache)
└── tailwind.config.js           # brand colour palette
```

## Translations

- UI strings and field labels come from `../flutter_app/lib/l10n/*.arb`. After editing them run `npm run i18n` and commit
  the regenerated `src/lib/i18n/messages.json` (the Docker build cannot read `flutter_app/`).
- Fixed-vocabulary data values (habitat "Forest", sociality "Small groups", ...) are in `src/lib/i18n/values.json`; add
  an entry (all 13 languages) when new values appear in the data.
- The chosen language is stored in the `lang` cookie; without it the browser's `Accept-Language` is used.

## Scripts

```bash
npm run dev       # development server
npm run build     # production build
npm start         # run the build
npm test          # Jest (26 tests)
npm run i18n      # regenerate messages.json
```

## Deployment

See [../docs/DEPLOYMENT.md](../docs/DEPLOYMENT.md): `docker compose up -d --build` runs the website behind Caddy (or
behind your own nginx) together with the API, MeiliSearch and Redis.

## License

Code: MIT. Data: CC-BY 4.0 (see the repository README).

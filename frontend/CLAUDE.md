# Frontend (Next.js)

Next.js + Tailwind web app for browsing the bird database. Source in `src/`.

- Test: `npm test` (Jest, config in `jest.config.js`, setup in `jest.setup.ts`); also `test:watch`, `test:coverage`
- Dev: `npm run dev`
- Data comes from the API in `../_scripts/api.py`; species data lives in `../birds/`.

## Website notes

- Public URLs come from the repo-root `.env` (`API_DOMAIN`, `SITE_DOMAIN`); see `docs/DEPLOYMENT.md`.
- i18n: UI strings come from the Flutter `.arb` files via `npm run i18n` (regenerates `src/lib/i18n/messages.json`, commit it).
  Categorical data values are translated in `src/lib/i18n/values.json`. The language is stored in the `lang` cookie.
- The API is the only data source; there are no Next.js API routes.

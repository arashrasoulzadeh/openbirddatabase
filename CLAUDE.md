# OpenBird Database

Global bird species database (~11,000 species) stored as Markdown files with YAML frontmatter. Persian (`fa`) is the priority language; English is used for keys. See `README.md` and `docs/AI_CONTEXT.md` for full background.

## Layout

- `birds/{order}/{family}/{species}.md` — canonical species files (the data; edit with care, ~11k files)
- `translations/{lang}/...` — per-language overrides
- `curations/` — curated corrections applied by `_scripts/apply_curations.py`
- `_scripts/` — Python ingestion/export/API pipeline (`ingest.py`, `generate_md.py`, `validate.py`, `index.py`, `api.py`, `mcp_server/`)
- `_schemas/`, `_templates/` — JSON Schemas and Jinja2 templates for species files
- `_index/`, `exports/` — generated outputs; regenerate rather than hand-edit
- `_data/` — raw downloads (gitignored)
- `frontend/` (Next.js website), `flutter_app/` (Flutter app), `mobile/` (older Expo app, not adapted to the API yet) — clients
- `docker-compose.yml`, `Caddyfile`, `.env.example` — deployment (Caddy, website, API, MeiliSearch, Redis, worker)
- `docs/` — `DEPLOYMENT.md`, `SCHEMA_GUIDE.md`, `DATA_SOURCES.md`, `CONTRIBUTING.md`, `AI_CONTEXT.md`

## Commands

- Run all tests: `./run_all_tests.sh` (sets `PYTHONPATH` for Python tests)
- Python: `pip install -r requirements.txt`; `python _scripts/download.py`, `python _scripts/ingest.py`, `python _scripts/validate.py`
- Indexes: `python _scripts/index.py` (after species files change), then the MeiliSearch indexer; the Compose `worker` warms Redis and refreshes content stats / analytics backups
- Analytics: events in SQLite (`ANALYTICS_DB`), dashboard at `/analytics`; preview with `_scripts/seed_analytics.py` (fake data, never in production)
- API: `uvicorn _scripts.api:app --reload` (works without MeiliSearch/Redis); tests: `pytest _scripts/test_cache.py _scripts/test_analytics.py _scripts/test_backup.py`
- Website: `cd frontend && npm run dev`; tests `npm test`; after editing `.arb` files `npm run i18n` and commit `messages.json`
- Flutter: `cd flutter_app && flutter test`; build with `--dart-define=API_BASE_URL=https://api.example.org`
- Deploy: set `SITE_DOMAIN` / `API_DOMAIN` in `.env`, then `docker compose up -d --build`; updates: `./deploy.sh` (downloads the images CI built, health-checks, supports `--if-changed` for cron; `./backup.sh` backs up analytics; `--build` builds on the server and caps the build cache at 1 GB). See `docs/DEPLOYMENT.md`
- CI: every push to `main` builds the Android debug APK (attached to that commit's `Build ...` release) and publishes the website/API Docker images to ghcr.io

## Conventions

- Species files: frontmatter holds structured attributes (78 BIRDBASE traits, 32 AVONICHE niches); body has fixed sections (Overview, Identification, Habitat, Diet, Behavior, Breeding, Conservation). Follow `_schemas/` and `docs/SCHEMA_GUIDE.md`.
- Prefer changing scripts/templates/curations and regenerating over bulk hand-editing species files.
- Commits use conventional prefixes (`feat:`, `fix:`, `docs:`, `test:`, `chore:`). Species changes are git-tracked per species.
- Data is CC-BY 4.0; keep source attribution in `sources`.
- Translations: Flutter `.arb` files are the single source for UI strings (website reuses them via `npm run i18n`).
- Never commit `.env`, `docker-compose.override.yml`, `meili_data/` or `backups/`; they are server-specific.

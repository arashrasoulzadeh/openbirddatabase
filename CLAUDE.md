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
- `frontend/` (Next.js), `mobile/` (Expo/React Native), `flutter_app/` (Flutter) — client apps
- `docs/` — `SCHEMA_GUIDE.md`, `DATA_SOURCES.md`, `CONTRIBUTING.md`, `AI_CONTEXT.md`

## Commands

- Run all tests: `./run_all_tests.sh` (sets `PYTHONPATH` for Python tests)
- Python: `pip install -r requirements.txt`; `python _scripts/download.py`, `python _scripts/ingest.py`, `python _scripts/validate.py`
- API: `uvicorn _scripts.api:app --reload`; search via `docker-compose up -d` + `python _scripts/index.py`
- Frontend: `cd frontend && npm test` (Jest)
- Mobile: `cd mobile && npm start`
- Flutter: `cd flutter_app && flutter test`

## Conventions

- Species files: frontmatter holds structured attributes (78 BIRDBASE traits, 32 AVONICHE niches); body has fixed sections (Overview, Identification, Habitat, Diet, Behavior, Breeding, Conservation). Follow `_schemas/` and `docs/SCHEMA_GUIDE.md`.
- Prefer changing scripts/templates/curations and regenerating over bulk hand-editing species files.
- Commits use conventional prefixes (`feat:`, `fix:`, `docs:`, `test:`, `chore:`). Species changes are git-tracked per species.
- Data is CC-BY 4.0; keep source attribution in `sources`.

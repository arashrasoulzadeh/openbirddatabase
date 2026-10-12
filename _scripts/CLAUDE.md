# Python pipeline (`_scripts/`)

Ingestion, curation, export, search and API tooling. Run from repo root with `PYTHONPATH` set (see `../run_all_tests.sh`).

- Pipeline order: `download.py` → `ingest.py` → `apply_curations.py` → `validate.py` → `index.py`/`populate_meili.py`
- `generate_md.py` renders species files from `../_templates/`; validation uses `../_schemas/`
- `api.py` (FastAPI), `graphql_schema.py`, `mcp_server/` expose the data
- Tests: `test_ingestion.py`
- Scripts that rewrite `../birds/` touch thousands of files: run on a subset first and check `git diff --stat`.

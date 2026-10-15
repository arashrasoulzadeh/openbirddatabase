# Python pipeline (`_scripts/`)

Ingestion, curation, export, search and API tooling. Run from repo root with `PYTHONPATH` set (see `../run_all_tests.sh`).

- Pipeline order: `download.py` → `ingest.py` → `apply_curations.py` → `validate.py` → `index.py`/`populate_meili.py`
- `generate_md.py` renders species files from `../_templates/`; validation uses `../_schemas/`
- `api.py` (FastAPI), `graphql_schema.py`, `mcp_server/` expose the data
- `index.py` regenerates `../_index/` (names in all languages); `populate_meili.py` loads MeiliSearch and configures the
  vector embedder (`VECTOR_SEARCH=false` skips it)
- `api.py` environment: `MEILI_HOST`, `SITE_DOMAIN`, `CORS_ORIGINS`, `VECTOR_SEARCH`, `SEMANTIC_RATIO`, `REDIS_URL`,
  `CACHE_SEARCH_TTL`, `CACHE_STATIC_TTL`. Redis and MeiliSearch are optional: failures fall back to a slower path.
- `cache_utils.py` (keys, JSON sanitising) is shared by `api.py` and `warm_cache.py`; keep their keys in sync
  (`CACHE_PREFIX` is versioned: bump it if the cached JSON shape changes)
- Tests: `test_ingestion.py`, `test_cache.py` (fake Redis, no server needed)
- Scripts that rewrite `../birds/` touch thousands of files: run on a subset first and check `git diff --stat`.

# Deployment: public website + API

Two public hostnames, both configured in the repo-root `.env`:

| Variable | Example | Serves |
|---|---|---|
| `SITE_DOMAIN` | `openbird.org` | Next.js website (`frontend/`) |
| `API_DOMAIN` | `api.openbird.org` | FastAPI (`_scripts/api.py`) |

## Server setup

1. Point DNS `A`/`AAAA` records for `SITE_DOMAIN`, `www.SITE_DOMAIN` and `API_DOMAIN` at the server.
2. `cp .env.example .env` and set the domains and `ACME_EMAIL`.
3. `docker compose up -d --build`. Caddy obtains HTTPS certificates automatically.
4. Optional search index: `docker compose --profile indexing run --rm indexer`. Without MeiliSearch the API falls back to `_index/species-index.json`.

Services started by `docker-compose.yml`: `caddy` (HTTPS), `web` (Next.js), `api` (FastAPI), `meilisearch`, `redis`,
and the one-shot `cache-warmer`. The `indexer` runs only on request (`--profile indexing`).

The website talks to `https://API_DOMAIN` from the browser and to `http://api:8000` during server-side rendering. The API only allows CORS from `SITE_DOMAIN`.

## Flutter releases

`flutter_app` reads the API address at build time:

```
flutter build apk --dart-define=API_BASE_URL=https://$API_DOMAIN --dart-define=SITE_URL=https://$SITE_DOMAIN
```

The "Build Debug App" workflow does this from GitHub repository **variables** named `API_DOMAIN` and `SITE_DOMAIN`
(Settings → Secrets and variables → Actions → Variables). If unset, the app defaults to `http://localhost:8000`.

## API reference

`GET /search?q=&limit=&offset=` (optional exact filters: `iucn_status`, `order`, `family`, `primary_habitat`, `primary_diet`, `migration_status`, plus `semantic_ratio`), `POST /search`, `GET /species/{scientific_name}?lang=`, `GET /taxonomy[/{order}[/{family}]]`, `GET /random`, `GET /filters`, `GET /stats`, `/graphql`, interactive docs at `/docs`.

## Languages (website)

The site has a language selector (13 languages, right-to-left for Persian and Arabic). Interface text and field labels
come from the Flutter app's ARB files so both apps share one set of translations. After editing
`flutter_app/lib/l10n/*.arb` run:

```
cd frontend && npm run i18n
```

and commit the regenerated `frontend/src/lib/i18n/messages.json` (the Docker build cannot read `flutter_app/`).
Species names are shown in the selected language with the original English and scientific names alongside.
Categorical values such as habitat "Forest", diet "Invertebrate" or sociality "Small groups" are translated from
`frontend/src/lib/i18n/values.json` (edit it by hand when new values appear in the data). Free-text veterinary and
enrichment notes stay in English, as does the biogeographic realm code list.

## Vector (semantic) search

MeiliSearch runs hybrid keyword + vector search with the multilingual `intfloat/multilingual-e5-small` model, so a
query like "small blue forest bird" or the same in Persian finds relevant species even without matching names.

- Build the index (first run downloads the model and computes vectors, this can take a long time on CPU):
  `docker compose --profile indexing run --rm indexer`
- `GET /health` reports `"vector_search": true` once the embedder is configured.
- `SEMANTIC_RATIO` (default `0.5`) balances keywords vs vectors; override per request with `?semantic_ratio=0..1`.
- `VECTOR_SEARCH=false` in `.env` turns it off. If the embedder is unavailable the API falls back to keyword search.
- Upgrading from the old MeiliSearch 1.7 image: the compose file enables a dumpless upgrade; if the container still
  refuses to start, remove `meili_data/` and re-run the indexer (the index is rebuildable).

After regenerating `_index/` (`python _scripts/index.py`) re-run the indexer and restart the API.

## SEO

The website serves `/sitemap.xml` (home page plus every species page, generated from the API's taxonomy and cached for an hour)
and `/robots.txt`. Submit `https://SITE_DOMAIN/sitemap.xml` in Google Search Console and Bing Webmaster Tools.

## Redis cache

`docker compose up` also starts Redis and a one-shot `cache-warmer`. The API caches species details, search results
(10 minutes), the taxonomy, filters and stats in Redis; if Redis is missing or down the API still works, just slower.

- The warmer loads all species files and the common API responses (home-page search, one page per conservation
  status, taxonomy, filters, stats). Run it again after changing data: `docker compose run --rm cache-warmer`
  (it clears this app's keys first; pass `--no-flush` to keep them).
- Check it: `curl -I https://API_DOMAIN/species/Parus%20major` shows `X-Cache: HIT` once cached, and
  `curl https://API_DOMAIN/health` shows `"cache": true`.
- Settings (environment of the `api` service): `CACHE_SEARCH_TTL` (default 600 s), `CACHE_STATIC_TTL` (default 7 days).
  Redis memory is capped by `REDIS_MAXMEMORY` (default 768mb) with least-recently-used eviction.
- Wipe it any time with `docker compose exec redis redis-cli FLUSHALL`; it refills on demand.

## Faster rebuilds

`docker compose up -d --build` reuses what the previous build downloaded: the website image keeps `node_modules`, npm's
download cache and the Next.js compile cache, and the API image keeps pip's cache, all as BuildKit cache mounts stored on
the server (needs Docker with BuildKit, the default in current Docker). The first build is slow; later builds only
install changed packages. To start from scratch run `docker builder prune`.

**Limiting the build cache (about 1 GB):** `./deploy.sh` runs `git pull`, `docker compose up -d --build` and then trims
Docker's build cache to `BUILD_CACHE_LIMIT` (default `1GB`; least recently used entries go first). To have Docker enforce
it automatically on every build instead, add this to `/etc/docker/daemon.json` and restart Docker. Note that it applies
to all builds on that server, not just this project:

```json
{ "builder": { "gc": { "enabled": true, "defaultKeepStorage": "1GB" } } }
```

The Redis cache is separate and capped by `REDIS_MAXMEMORY` (default `768mb`).

## Behind an existing nginx (ports 80/443 already in use)

If another web server already owns ports 80 and 443, Caddy cannot start. Skip it and publish the app on local ports with
a `docker-compose.override.yml` (server-specific, do not commit it):

```yaml
services:
  caddy:
    profiles: ["disabled"]
  web:
    ports: ["127.0.0.1:13000:3000"]
  api:
    ports: ["127.0.0.1:18000:8000"]
```

Then run `docker compose rm -sf caddy && docker compose up -d --build` and add two nginx server blocks that
`proxy_pass` to `127.0.0.1:13000` (site, with `www`) and `127.0.0.1:18000` (API), each setting
`proxy_set_header Host $host;` and `X-Forwarded-Proto $scheme;`. Get certificates with
`certbot --nginx -d SITE_DOMAIN -d www.SITE_DOMAIN -d API_DOMAIN`.

## Updating and troubleshooting

- Update: `./deploy.sh` (or `git pull && docker compose up -d --build`; re-run the indexer after the species data or `_index/` changed).
- Changing `.env`: rebuild with `--build`; the public URLs are baked into the website build.
- Logs: `docker compose logs -f api web`; add `meilisearch indexer` for search problems, `redis cache-warmer` for the cache.
- MeiliSearch refuses to start after an upgrade: remove `meili_data/` and re-run the indexer (the index is rebuildable).
- Site shows no styles or the language switcher is missing: you are on an old build; rebuild and hard-refresh.

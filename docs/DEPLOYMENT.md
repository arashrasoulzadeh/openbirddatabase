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

The species data and `_index/` are baked into the API image, so code and data always match. After regenerating `_index/`
(`python _scripts/index.py`) commit and push; CI publishes new images, then `./deploy.sh` and re-run the indexer.

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

## Prebuilt images (recommended)

The "Publish Images" workflow (`.github/workflows/publish-images.yml`) builds the website and API images on GitHub on
every push to `main` and publishes them to GitHub Container Registry as `ghcr.io/<owner>/openbird-web` and
`openbird-api` (tags `latest` and `sha-<commit>`). The server then only downloads them, with no compiling.

- **Deploy:** `./deploy.sh` runs `git pull`, waits until CI has published the images for that exact commit (up to
  `WAIT_MINUTES`, default 15), pulls them and restarts. No `npm install`, no Next.js build on the server.
- **Build locally instead:** `./deploy.sh --build` (or `docker compose up -d --build`), for example while testing changes
  that are not pushed yet.
- **The website image has your domains baked in**, taken from the repository variables `API_DOMAIN` and `SITE_DOMAIN`.
  After changing them run the workflow again (Actions -> Publish Images -> Run workflow) and redeploy.
- **First time:** push once so the images exist. This repository is public, but GitHub creates the two packages as
  private. Either make them public (GitHub -> your profile -> Packages -> `openbird-web` / `openbird-api` -> Package
  settings -> Change visibility -> Public, repeat for both) or log the server in once with a token that has
  `read:packages`: `echo <TOKEN> | docker login ghcr.io -u <github-user> --password-stdin`.
- **Architecture:** images are built for `linux/amd64`. For an ARM server set the repository variable `IMAGE_PLATFORMS`
  to `linux/arm64` (or `linux/amd64,linux/arm64`; slower to build). `uname -m` shows `x86_64` (amd64) or `aarch64` (arm64).
- **Pin or roll back:** set `IMAGE_TAG=sha-<7 characters>` in `.env` and run `docker compose pull && docker compose up -d`.
- **Forks:** set `IMAGE_PREFIX=ghcr.io/<your-user>` in `.env`.

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
`proxy_set_header Host $host;`, `proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;` and
`proxy_set_header X-Forwarded-Proto $scheme;` (the analytics rate limit uses the forwarded address). Get certificates with
`certbot --nginx -d SITE_DOMAIN -d www.SITE_DOMAIN -d API_DOMAIN`.

## Updating and troubleshooting

- Update: `./deploy.sh` (prebuilt images; `./deploy.sh --build` builds on the server; re-run the indexer after the species data or `_index/` changed). It checks `/health` afterwards and prints a rollback command if the new version does not start.
- Changing `.env`: rebuild with `--build`; the public URLs are baked into the website build.
- Logs: `docker compose logs -f api web`; add `meilisearch indexer` for search problems, `redis cache-warmer` for the cache.
- MeiliSearch refuses to start after an upgrade: remove `meili_data/` and re-run the indexer (the index is rebuildable).
- Site shows no styles or the language switcher is missing: you are on an old build; rebuild and hard-refresh.

## Analytics

The site records anonymous usage in its own database (no third-party service). Events are posted by the browser to
`POST /analytics/event` and stored in SQLite on the `analytics_data` Docker volume (`/data/analytics.db`).

**What is recorded:** page views and time spent on each page, bird clicks (and where the click came from: search,
taxonomy, related species, random), searches (text and number of results, so searches with no result show up as content
gaps), filter use, language changes, taxonomy tab opens, "load more" and random-bird clicks.

**Privacy:** no IP addresses or user agents are stored. Visitors and sessions are random ids kept in the browser
(`localStorage` / `sessionStorage`, no cookies). Bots are ignored, visitors sending Do-Not-Track or Global Privacy
Control are not tracked, and the dashboard itself is never counted. Depending on your jurisdiction you may still want
to mention analytics in a privacy notice. Raw events are deleted after `ANALYTICS_RETENTION_DAYS` (default 400).

**Dashboard:** `https://SITE_DOMAIN/analytics` shows live visitors, KPIs with change vs the previous period, traffic,
home/bird/search/click graphs, top birds, top and zero-result searches, per-page history (click a row), languages,
devices, referrers, busiest hours and weekdays, plus content statistics (birds added over time, species names and UI
translations per language, data completeness by bird, order and section). Times are UTC.

**Protect it:** set `ANALYTICS_TOKEN` in `.env` (a long random value) and rebuild. The dashboard then asks for the token
(it is kept in the browser session only); the read endpoints (`GET /analytics/*`) require it as
`Authorization: Bearer <token>` or `?token=`. Collecting events stays public. Without a token the dashboard is public.
Set `ANALYTICS_ENABLED=false` to stop collecting.

**API:** `POST /analytics/event` (one event or `{"events": [...]}`; types `pageview`, `page_leave`, `bird_click`,
`search`, `filter`, `language_change`, `tab_view`, `load_more`, `random_bird`; the Flutter app posts page views, searches, bird clicks and language changes the same way, and users can turn that off in Settings),
`GET /analytics/dashboard?days=`, `/pages`, `/page?path=`, `/birds/{name}`, `/live`, `/content`.

**Content statistics** come from `_index/content-stats.json`. Regenerate it after the species data changes and rebuild:
`python _scripts/content_stats.py` (about a minute; "birds added over time" uses the git history, so run it in the
checkout, not in the container).

**Back up** the events with `docker compose cp api:/data/analytics.db ./analytics-backup.db`.

**Try it with fake data** (never on the production database):
`ANALYTICS_DB=data/analytics-demo.db python _scripts/seed_analytics.py --days 30`, then start the API with the same
`ANALYTICS_DB` and open `/analytics`.

## Running it on your own (private) server

**Private images.** GitHub creates the container packages as private. That is fine for your own server: log in once with
a token that has the `read:packages` scope (GitHub -> Settings -> Developer settings -> Personal access tokens), and
Docker remembers it:

```
echo <TOKEN> | docker login ghcr.io -u <github-user> --password-stdin
```

`./deploy.sh` prints this hint when the registry refuses a pull. Making the packages public instead is optional; the
images contain only open data and code from this repository.

**Automatic updates.** `./deploy.sh --if-changed` does nothing unless a newer commit exists (it compares the commit
the running website was built from with the latest on GitHub), waits for CI to publish the images, restarts, and checks
`/health`. Run it from cron every 10 minutes, with a lock so runs never overlap:

```
*/10 * * * * cd ~/openbirddatabase && ./deploy.sh --if-changed >> deploy.log 2>&1
```

**Rollback.** Every image is also tagged `sha-<7 characters>`. If a deploy fails its health check, `deploy.sh` prints
the exact command, for example `IMAGE_TAG=sha-1a2b3c4 docker compose up -d`. Put `IMAGE_TAG=...` in `.env` to stay on
that version, and remove it to follow `latest` again.

**Backups.** Only the analytics events need backing up (everything else is rebuilt from the repository).
`./backup.sh` makes a consistent compressed copy with SQLite's online backup, copies it to `./backups` and keeps the newest
14 (`KEEP=30 ./backup.sh` to change). Daily from cron:

```
0 3 * * * cd ~/openbirddatabase && ./backup.sh >> backup.log 2>&1
```

Restore a copy (this replaces the current analytics data):

```
docker compose stop api
docker compose run --rm --no-deps -v "$PWD/backups:/restore:ro" api \
  python _scripts/backup_analytics.py --restore /restore/analytics-YYYYMMDD-HHMMSS.db.gz --db /data/analytics.db
docker compose start api
```

Copy `./backups` to another machine regularly; a backup on the same disk does not survive a disk failure.

**Exposure.** Only Caddy (ports 80/443) or your own reverse proxy needs to be reachable. MeiliSearch, Redis and the
containers' ports are not published (the override file in the nginx section binds to `127.0.0.1` only). Keep
`ANALYTICS_TOKEN` set, and keep `.env` out of git.

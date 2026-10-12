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

The website talks to `https://API_DOMAIN` from the browser and to `http://api:8000` during server-side rendering. The API only allows CORS from `SITE_DOMAIN`.

## Flutter releases

`flutter_app` reads the API address at build time:

```
flutter build apk --dart-define=API_BASE_URL=https://$API_DOMAIN --dart-define=SITE_URL=https://$SITE_DOMAIN
```

The "Build Debug App" workflow does this from GitHub repository **variables** named `API_DOMAIN` and `SITE_DOMAIN`
(Settings → Secrets and variables → Actions → Variables). If unset, the app defaults to `http://localhost:8000`.

## API reference

`GET /search?q=&limit=&offset=`, `POST /search`, `GET /species/{scientific_name}?lang=`, `GET /taxonomy[/{order}[/{family}]]`, `GET /filters`, `GET /stats`, `/graphql`, interactive docs at `/docs`.

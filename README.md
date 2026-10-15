# OpenBird Database

Global bird species database (~11,000 species) as Markdown files with comprehensive attributes, multilingual support (Persian priority), and git-tracked changes.

## Features

- **11,000+ species** from unified AviList 2025 taxonomy
- **78 BIRDBASE traits** across 10 categories (morphology, habitat, diet, behavior, reproduction, demography, conservation, etc.)
- **32 AVONICHE foraging niches** (diet × foraging strategy combinations)
- **Multilingual**: species names in 13 languages (Persian primary; en, fa, ar, es, fr, de, pt, ru, ja, zh, nl, pl, tr), 430+ more via BirdNET
- **Per-species git commits** - full change history for every bird
- **Public website** (Next.js) with a language selector, search filters, taxonomy browser and per-species pages
- **REST + GraphQL API** (FastAPI) with MeiliSearch keyword + vector search and a Redis cache
- **Analytics** (first-party, privacy-friendly): page views, bird clicks, searches, languages, time on page, with a dashboard at `/analytics`
- **Mobile app** (Flutter) in 13 languages, debug APKs published with every push
- **Extensible** - JSON Schema validation, Jinja2 templates

## Data Sources

| Source | Species | Key Data | License |
|--------|---------|----------|---------|
| BirdNET Taxonomy | 16,193 | Taxonomy, 434 languages, IDs, descriptions, images | CC-BY 4.0 |
| BIRDBASE 2025 | 11,589 | 78 traits (morphology, ecology, behavior, conservation) | CC-BY 4.0 |
| AVONICHE 2025 | 10,981 | 32 foraging niches, 4 taxonomy crosswalks | CC-BY 4.0 |
| BirdFYI API | 11,251 | Habitat details, regional presence, comparisons | Free tier |

## Directory Structure

```
birds-db/
├── birds/                    # Main species files (English keys, Persian values)
│   └── {order}/{family}/{species}.md
├── translations/
│   ├── fa/                   # Persian overrides
│   ├── en/                   # English overrides
│   └── ar/                   # Future languages
├── _schemas/                 # JSON Schemas for validation
├── _templates/               # Jinja2 templates for markdown generation
├── _scripts/                 # Ingestion pipeline, API, indexer, cache warmer
├── _index/                   # Generated search indexes (regenerate with _scripts/index.py)
├── _data/                    # Raw downloads (gitignored)
├── frontend/                 # Public website (Next.js)
├── flutter_app/              # Mobile app (Flutter)
├── mobile/                   # Older React Native/Expo app (see TODO.md)
├── docs/                     # Documentation (DEPLOYMENT.md for running the site)
├── docker-compose.yml        # Caddy + website + API + MeiliSearch + Redis
├── Caddyfile                 # HTTPS for SITE_DOMAIN and API_DOMAIN
└── .env.example              # SITE_DOMAIN / API_DOMAIN / ACME_EMAIL
```

## Quick Start

### Prerequisites
- Python 3.11+
- Git
- Docker (for MeiliSearch)

### Development Setup

```bash
# Clone
git clone https://github.com/yourusername/openbird.git
cd openbird

# Install dependencies
pip install -r requirements.txt

# Download data sources
python _scripts/download.py

# Run full ingestion (generates all species files)
python _scripts/ingest.py

# Build the search indexes (needed after the species files change)
python _scripts/index.py
```

### Run the API and website locally

```bash
# API (http://localhost:8000, docs at /docs)
pip install -r requirements-api.txt
uvicorn _scripts.api:app --reload

# Website (http://localhost:3000)
cd frontend && npm install && npm run dev
```

Without MeiliSearch or Redis the API falls back to `_index/species-index.json` and no caching, which is fine for development.

### Publish it on your own domains

Two hostnames, set in `.env` (copy `.env.example`): `SITE_DOMAIN` for the website and `API_DOMAIN` for the API.

```bash
cp .env.example .env     # then edit the domains
docker compose up -d --build                         # later updates: ./deploy.sh
docker compose --profile indexing run --rm indexer   # fills MeiliSearch (keyword + vector search)
```

Full guide, including running behind an existing nginx: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

### Tests

```bash
./run_all_tests.sh            # Python, frontend and Flutter suites
cd frontend && npm test       # website only
cd flutter_app && flutter test
```

## Species Markdown Format

Each species file (`birds/passeriformes/paridae/parus-major.md`) contains:

```markdown
---
# Frontmatter with all 78+ attributes as structured YAML
taxon_id: "BT00012345"
names:
  scientific: "Parus major"
  fa: "تیت بزرگ"
  en: "Great Tit"
taxonomy:
  order: "Passeriformes"
  family: "Paridae"
  ...
morphology:
  body_mass_g: 18.5
  ...
habitat:
  primary: "Temperate forest"
  ...
diet:
  primary: "Omnivore"
  categories:
    invertebrates: 6
    seeds: 2
    ...
  foraging_niches:
    invertebrates_glean_elevated: 0.45
    ...
behavior:
  sociality: "Pairs and family groups"
  ...
reproduction:
  clutch_size_mean: 8.5
  ...
veterinary:
  common_diseases: [...]
  ...
enrichment:
  foraging_toys: [...]
  training:
    target_training: true
    ...
sources: [...]
last_updated: "2026-10-02"
---

# Parus major (تیت بزرگ)

## Overview
...

## Identification
...

## Habitat & Distribution
...

## Diet & Foraging
...

## Behavior & Ecology
...

## Breeding
...

## Conservation
...

## Veterinary Care
...

## Enrichment & Training
...
```

## Multilingual Strategy

- **Base files** (`birds/.../species.md`): English keys, Persian values
- **Translation overrides** (`translations/fa/.../species.md`): Only changed values
- **Merge at build/runtime** → complete localized output

## Git Commit Convention

```
feat(birds): add Parus major (Great Tit) - Passeriformes/Paridae

Taxon IDs: BirdNET=BT00012345, eBird=gretit, GBIF=2480498
Sources: BirdNET, BIRDBASE, AVONICHE, BirdFYI
Quality: High
Languages: fa, en, +432 more
```

## Search & API

- **Search**: MeiliSearch hybrid keyword + vector search (multilingual model), with a JSON-index fallback
- **Endpoints**: `GET/POST /search` (exact filters: IUCN status, order, family, habitat, diet, migration), `GET /species/{name}`,
  `GET /taxonomy[/{order}[/{family}]]`, `GET /random`, `GET /filters`, `GET /stats`, `/analytics/*`, `/graphql`, `/docs`
- **Cache**: Redis for species, search, taxonomy, filters and stats; a warm-up job pre-fills it
- **Website**: language selector with 13 languages (right-to-left for Persian and Arabic), shareable search URLs, sitemap
- **Apps**: the Flutter app reads the API address at build time (`--dart-define=API_BASE_URL=...`)

## Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for:
- Adding new species data
- Improving translations
- Veterinary/enrichment contributions
- Schema changes

## License

Data: CC-BY 4.0 (from sources)
Code: MIT

## Citation

If you use this database, please cite the original sources:
- BirdNET Taxonomy (Cornell Lab of Ornithology)
- BIRDBASE (Şekercioğlu Lab, University of Utah)
- AVONICHE (Sayol et al., 2025)
- BirdFYI (fyipedia)
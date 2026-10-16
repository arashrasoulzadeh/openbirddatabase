# OpenBird Database - Implementation TODO

## Project Overview
Global bird database (~10,000+ species) as Markdown files with:
- All 78 BIRDBASE traits + 32 AVONICHE foraging niches
- Multilingual (Persian priority, English keys)
- Per-species git commits
- Searchable via the API (MeiliSearch + Redis) and the public website

---

## Phase 1: Foundation (Week 1) ✅ COMPLETE

### 1.1 Repository Setup
- [x] Initialize git repo
- [x] Create `.gitignore`
- [x] Create `README.md`
- [x] Create directory structure

### 1.2 Schemas & Templates
- [x] `bird-attributes.schema.json` - JSON Schema for species frontmatter
- [x] `foraging-niches.schema.json` - JSON Schema for AVONICHE data
- [x] `species-template.md.j2` - Jinja2 template for markdown generation
- [x] `translation-template.md.j2` - Template for translation overrides

### 1.3 Documentation for AI
- [x] `AI_CONTEXT.md` - Project context for AI assistants
- [x] `DATA_SOURCES.md` - Document all data sources with URLs, licenses, fields
- [x] `SCHEMA_GUIDE.md` - Field-by-field documentation
- [x] `CONTRIBUTING.md` - How to add/edit data

---

## Phase 2: Data Acquisition (Week 1-2) ✅ COMPLETE

### 2.1 Download Sources
- [x] BirdNET Taxonomy v0.3 (CSV/JSON/ZIP) - 16,193 species, 434 languages
- [x] BIRDBASE 2025 (Excel) - 11,589 species, 78 traits
- [x] AVONICHE 2025 (CSV) - 10,981 species, 32 foraging niches
- [x] BirdFYI API - 11,251 species, habitat/behavior details

### 2.2 Taxonomy Crosswalk
- [x] Download AviList 2025 (unified checklist)
- [x] Build mapping: AviList ↔ eBird/Clements ↔ BirdLife ↔ BirdTree
- [x] Create unified species master list (~11,000 species)

### 2.3 Data Inspection
- [x] Profile each dataset (columns, missing values, quality)
- [x] Document field mappings between sources
- [x] Identify gaps (vet, enrichment, play data)

---

## Phase 3: Ingestion Pipeline (Week 2-3) ✅ COMPLETE

### 3.1 Pipeline Skeleton
- [x] `ingest.py` - Main orchestrator
- [x] `download.py` - Fetch all sources
- [x] `crosswalk.py` - Taxonomy mapping
- [x] `merge.py` - Merge sources into unified records
- [x] `generate_md.py` - Render markdown from template
- [x] `validate.py` - Schema validation
- [x] `commit.py` - Per-species git commits

### 3.2 Prototype: Paridae Family
- [x] Generate ~60 species (tits, chickadees)
- [x] Validate output
- [x] Test git commit automation
- [x] Verify Persian translations

### 3.3 Full Ingestion
- [x] Process all orders/families in parallel
- [x] Handle errors gracefully
- [x] Generate commit per species (11,584 commits)
- [x] Progress tracking & resume capability

**Result: 11,149 species generated as Markdown files**

---

## Phase 4: Search & API (Week 3-4) ✅ COMPLETE

### 4.1 Search Index
- [x] `index.py` - Generate MeiliSearch-compatible JSON
- [x] `species-index.json` - Full-text search
- [x] `taxonomy-tree.json` - Hierarchical navigation
- [x] `field-stats.json` - Faceted filters

### 4.2 Server
- [x] FastAPI app with MeiliSearch (`api.py`)
- [x] REST endpoints: search, filter, get species, taxonomy
- [x] GraphQL endpoint (planned)
- [x] i18n merge at request time (base + translation overrides)
- [x] Docker compose for local dev

---

## Phase 5: Apps (Ongoing) ✅ MAJOR PROGRESS

- [x] Web app (Next.js/React) - `frontend/` with search, species detail, taxonomy browser
- [x] Mobile (React Native/Expo) - `mobile/` with search, taxonomy browser, species detail, favorites, settings
- [x] Mobile (Flutter) - `flutter_app/` with Material 3, 13 languages, dark mode, full test suite
- [x] CLI tool (various scripts)
- [x] MCP server for AI assistants (`_scripts/mcp_server/`)

---

## Additional Completed Features

### Veterinary & Enrichment Curation
- [x] `curate_vet.py` - Veterinary data curation tools
- [x] `translate_qa.py` - Translation quality assurance
- [x] `curations/` directory for expert contributions

### Export Pipeline
- [x] `export_unified.py` - Unified exports for all 11,149 species
- [x] CSV export
- [x] XLSX export
- [x] SQL export

### AVONICHE Processing
- [x] `download_avoniche.py` - AVONICHE download helper
- [x] `watch_avoniche.py` - File watcher for AVONICHE updates

---

## Data Source Details

### BirdNET Taxonomy
- URL: https://birdnet.cornell.edu/taxonomy/download
- 16,193 species
- 434 languages including Persian (fa)
- Fields: BirdNET ID, scientific name, common names (all locales), eBird code, GBIF key, Avibase ID, iNaturalist ID, NCBI taxid, BirdLife ID, Macaulay Library ID, Xeno-Canto ID, descriptions, image URLs, observation counts
- License: CC-BY 4.0

### BIRDBASE 2025
- URL: https://doi.org/10.6084/m9.figshare.27051040
- 11,589 species
- 78 traits in 10 categories:
  1. Conservation (IUCN status, population, trends)
  2. Geographic Distribution (range, realms, endemism)
  3. Morphology (mass, length, wingspan, bill, tarsus, wing, tail)
  4. Elevational Distribution (min, max, limits)
  5. Habitat (primary, secondary, breadth, types)
  6. Diet (8 categories, breadth, primary diet)
  7. Social Behavior (sociality, flock size, territoriality)
  8. Reproductive Behavior (clutch, nest, mating system, parental care)
  9. Demography (generation length, longevity, survival, density)
  10. Mobility (migration, movement type, dispersal)
- License: CC-BY 4.0

### AVONICHE 2025
- URL: https://datadryad.org/dataset/doi:10.5061/dryad.1zcrjdg56
- 10,981 species (AviList taxonomy)
- 9 dietary niches + 32 foraging niches (diet × foraging strategy)
- 4 taxonomy crosswalks included
- License: CC-BY 4.0

### BirdFYI API
- URL: https://birdfyi.com/api/v1/
- 11,251 species
- REST API with OpenAPI spec
- Fields: habitat details, regional presence, comparisons, glossary, guides
- Python client: `pip install birdfyi`

---

## Directory Structure

```
birds-db/
├── birds/                          # Main species files (11,149 .md files)
│   ├── passeriformes/
│   │   ├── paridae/
│   │   │   ├── parus-major.md
│   │   │   └── ...
│   │   └── ...
│   └── ...
├── translations/
│   ├── fa/                         # Persian overrides
│   │   ├── passeriformes/
│   │   │   └── paridae/
│   │   │       └── parus-major.md
│   │   └── ...
│   ├── en/                         # English overrides
│   └── ar/                         # Future languages
├── _schemas/
│   ├── bird-attributes.schema.json
│   └── foraging-niches.schema.json
├── _templates/
│   ├── species-template.md.j2
│   └── translation-template.md.j2
├── _scripts/
│   ├── ingest.py
│   ├── download.py
│   ├── crosswalk.py
│   ├── merge.py
│   ├── generate_md.py
│   ├── validate.py
│   ├── commit.py
│   ├── index.py
│   ├── api.py
│   ├── curate_vet.py
│   ├── translate_qa.py
│   ├── export_unified.py
│   ├── download_avoniche.py
│   ├── watch_avoniche.py
│   ├── populate_meili.py           # MeiliSearch index + vector embedder
│   ├── cache_utils.py              # Redis key/JSON helpers shared by API and warmer
│   ├── warm_cache.py               # pre-fills the Redis cache
│   └── test_cache.py
├── _index/
│   ├── species-index.json
│   ├── taxonomy-tree.json
│   └── field-stats.json
├── _data/                          # Raw downloaded data (gitignored)
│   ├── birdnet/
│   ├── birdbase/
│   ├── avoniche/
│   └── birdfyi/
├── docs/
│   ├── AI_CONTEXT.md
│   ├── DATA_SOURCES.md
│   ├── SCHEMA_GUIDE.md
│   └── CONTRIBUTING.md
├── frontend/                       # Next.js web app
├── mobile/                         # React Native/Expo mobile app
├── flutter_app/                    # Flutter mobile app
├── curations/                      # Expert curation files
├── exports/                        # Generated exports (CSV, XLSX, SQL)
├── dumps/                          # Database dumps
├── data.ms/                        # MeiliSearch data
├── .gitignore
├── README.md
├── TODO.md
├── docker-compose.yml              # Caddy + website + API + MeiliSearch + Redis + cache warmer
├── Caddyfile                       # HTTPS for SITE_DOMAIN / API_DOMAIN
├── .env.example                    # SITE_DOMAIN, API_DOMAIN, ACME_EMAIL
├── .github/workflows/              # release-exports.yml, build-debug-app.yml
├── Dockerfile
├── requirements.txt
└── requirements-api.txt
```

---

## Git Commit Convention

```
feat(birds): add Parus major (Great Tit) - Passeriformes/Paridae

Taxon IDs: BirdNET=BT00012345, eBird=gretit, GBIF=2480498
Sources: BirdNET, BIRDBASE, AVONICHE, BirdFYI
Quality: High (all sources agree)
Languages: fa, en, +432 more
```

---

## Key Decisions Made

1. **Taxonomy**: AviList 2025 (unified global checklist)
2. **Vet/Enrichment**: Start empty, schema ready for expert contributions
3. **Git Host**: GitHub
4. **Search**: MeiliSearch (Persian support, typo-tolerant)
5. **Structure**: `birds/` (base) + `translations/fa/` (overrides)
6. **Commits**: One per species file

---

## Next Actions

1. **Continuous curation** of veterinary/enrichment data (expand to more species)
2. **Add more languages** (Hebrew, Hindi, Indonesian, Korean, Italian, etc.). UI strings live in `flutter_app/lib/l10n/*.arb`, data values in `frontend/src/lib/i18n/values.json`
3. **Species images** (needs a licensed source such as Wikimedia Commons; the species files hold none yet)
4. **Mobile app enhancements** (offline sync, audio playback)
5. **Fill the data gaps** (average completeness is about 40%): AVONET (bill/tarsus/wing/tail length, mass), IUCN generation length + AnAge (demography), GBIF (countries), Xeno-canto (recordings), Arabic/Chinese names; each needs a source decision, taxonomy matching and a licence check
6. **Web app enhancements** (dark mode, comparison tool, range maps, stats page, checklist export)
7. **Release builds**: signed release APK and an iOS build in CI (only unsigned debug APKs are built today)
8. **Expo app** (`mobile/`): still calls the old `/api/...` endpoints; adapt it to the real API like `flutter_app/lib/services/api_mapper.dart`
9. **Verify vector search** on the server (`/health` should report `"vector_search": true` after the indexer ran)

---

## Completed (Recent)

- [x] **Data completeness**: measured against the 56 core schema fields (`_scripts/completeness.py`); shown on every species page and on the dashboard (biggest gaps, by section/order, least complete birds); `deploy.sh` warms the cache after deploying
- [x] **Private-server operations**: `./deploy.sh --if-changed` for cron, post-deploy health check with rollback hint, private-registry login guidance, `./backup.sh` + `backup_analytics.py` (restore documented), images carry their own data (no bind mounts)
- [x] **Prebuilt Docker images**: `publish-images.yml` builds the website and API images in CI and publishes them to ghcr.io; `./deploy.sh` waits for the images of the pulled commit and restarts without compiling on the server
- [x] **Analytics**: event collection (`POST /analytics/event`, SQLite on a volume), dashboard at `/analytics` (live visitors, KPIs, traffic, bird clicks, searches incl. zero-result, per-page history, languages, devices, referrers, content stats: birds added over time, language coverage, completeness), token protection, demo data generator, tests; the Flutter app reports the same events (with an opt-out in Settings)
- [x] **Public website** (`frontend/`): search with filters, load more, shareable URLs, taxonomy browser, species pages with related species, random bird, sitemap + robots, responsive redesign
- [x] **13-language selector** on the website (UI, field labels, IUCN badges, categorical values, species names; English + scientific names always shown), right-to-left support
- [x] **Deployment**: `docker-compose.yml` (Caddy, website, API, MeiliSearch, Redis, cache warmer), `.env` with `SITE_DOMAIN` / `API_DOMAIN`, `docs/DEPLOYMENT.md`
- [x] **API**: env-based config and CORS, exact filters, `/random`, gzip, hybrid keyword + vector search with fallback, Redis cache (+ `warm_cache.py`)
- [x] **Search indexes** regenerated with names in all languages
- [x] **Flutter app** adapted to the real API (`api_mapper.dart`), tolerant JSON parsing, real-data regression test, 10 new language files
- [x] **CI**: `build-debug-app.yml` builds the Android debug APK on every push and attaches it to the commit's `Build` release; API/site addresses come from the `API_DOMAIN` / `SITE_DOMAIN` repository variables
- [x] GitHub Actions workflow for release exports (.sql, .csv, .xlsx, .yaml) with translations
- [x] YAML export format added to unified exports
- [x] SQL dump (.sql) export format added
- [x] **MCP server** for AI assistants (`_scripts/mcp_server/`)
- [x] **GraphQL endpoint** for API (`/graphql`)
- [x] **Mobile app** (React Native/Expo) with full species browsing
- [x] **Flutter mobile app** with Material 3, 13 languages, dark/light/system themes, full test suite, GitHub Actions CI/CD
- [x] **Veterinary curations** for 45 key species (parrots, raptors, waterfowl, gamebirds, passerines, hummingbirds, seabirds)
- [x] **Enrichment curations** for 45 key species (foraging, cognitive, social, training)
- [x] **10 new languages** added (es, fr, de, pt, ru, ja, zh, nl, pl, tr) - ~11K species each
- [x] **Comprehensive test suite** - unit, widget, and integration tests for all apps

---

## Statistics (as of last update)

- **Species generated**: 11,149
- **Git commits**: 11,584+
- **Orders covered**: 47
- **Families covered**: 200+
- **Data sources integrated**: 4 (BirdNET, BIRDBASE, AVONICHE, BirdFYI)
- **Languages available**: 434 (via BirdNET) + 13 high-coverage languages (en, fa, ar, es, fr, de, pt, ru, ja, zh, nl, pl, tr); the apps and website are fully translated into the 13
- **Veterinary curations**: 45 species
- **Enrichment curations**: 45 species
- **Schema validation**: 100% pass
- **Search index**: 11,149 documents (MeiliSearch keyword + vector, JSON fallback), Redis cache in front of the API
- **Tests**: frontend Jest (26), Flutter unit/widget/real-data tests (run in CI), Python cache and ingestion tests
- **Mobile apps**: 2 (React Native/Expo + Flutter)
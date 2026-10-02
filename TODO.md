# OpenBird Database - Implementation TODO

## Project Overview
Global bird database (~10,000+ species) as Markdown files with:
- All 78 BIRDBASE traits + 32 AVONICHE foraging niches
- Multilingual (Persian priority, English keys)
- Per-species git commits
- Searchable via future API/server

---

## Phase 1: Foundation (Week 1)

### 1.1 Repository Setup
- [ ] Initialize git repo
- [ ] Create `.gitignore`
- [ ] Create `README.md`
- [ ] Create directory structure

### 1.2 Schemas & Templates
- [ ] `bird-attributes.schema.json` - JSON Schema for species frontmatter
- [ ] `foraging-niches.schema.json` - JSON Schema for AVONICHE data
- [ ] `species-template.md.j2` - Jinja2 template for markdown generation
- [ ] `translation-template.md.j2` - Template for translation overrides

### 1.3 Documentation for AI
- [ ] `AI_CONTEXT.md` - Project context for AI assistants
- [ ] `DATA_SOURCES.md` - Document all data sources with URLs, licenses, fields
- [ ] `SCHEMA_GUIDE.md` - Field-by-field documentation
- [ ] `CONTRIBUTING.md` - How to add/edit data

---

## Phase 2: Data Acquisition (Week 1-2)

### 2.1 Download Sources
- [ ] BirdNET Taxonomy v0.3 (CSV/JSON/ZIP) - 16,193 species, 434 languages
- [ ] BIRDBASE 2025 (Excel) - 11,589 species, 78 traits
- [ ] AVONICHE 2025 (CSV) - 10,981 species, 32 foraging niches
- [ ] BirdFYI API - 11,251 species, habitat/behavior details

### 2.2 Taxonomy Crosswalk
- [ ] Download AviList 2025 (unified checklist)
- [ ] Build mapping: AviList ↔ eBird/Clements ↔ BirdLife ↔ BirdTree
- [ ] Create unified species master list (~11,000 species)

### 2.3 Data Inspection
- [ ] Profile each dataset (columns, missing values, quality)
- [ ] Document field mappings between sources
- [ ] Identify gaps (vet, enrichment, play data)

---

## Phase 3: Ingestion Pipeline (Week 2-3)

### 3.1 Pipeline Skeleton
- [ ] `ingest.py` - Main orchestrator
- [ ] `download.py` - Fetch all sources
- [ ] `crosswalk.py` - Taxonomy mapping
- [ ] `merge.py` - Merge sources into unified records
- [ ] `generate_md.py` - Render markdown from template
- [ ] `validate.py` - Schema validation
- [ ] `commit.py` - Per-species git commits

### 3.2 Prototype: Paridae Family
- [ ] Generate ~60 species (tits, chickadees)
- [ ] Validate output
- [ ] Test git commit automation
- [ ] Verify Persian translations

### 3.3 Full Ingestion
- [ ] Process all orders/families in parallel
- [ ] Handle errors gracefully
- [ ] Generate commit per species
- [ ] Progress tracking & resume capability

---

## Phase 4: Search & API (Week 3-4)

### 4.1 Search Index
- [ ] `index.py` - Generate MeiliSearch-compatible JSON
- [ ] `species-index.json` - Full-text search
- [ ] `taxonomy-tree.json` - Hierarchical navigation
- [ ] `field-stats.json` - Faceted filters

### 4.2 Server
- [ ] FastAPI app with MeiliSearch
- [ ] REST endpoints: search, filter, get species, taxonomy
- [ ] GraphQL endpoint
- [ ] i18n merge at request time (base + translation overrides)
- [ ] Docker compose for local dev

---

## Phase 5: Apps (Ongoing)

- [ ] Web app (React/Next.js)
- [ ] Mobile (React Native/Flutter)
- [ ] CLI tool
- [ ] MCP server for AI assistants

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
├── birds/                          # Main species files
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
│   └── index.py
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
├── .gitignore
├── README.md
├── TODO.md
└── docker-compose.yml              # For MeiliSearch + API
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

1. Create repository structure
2. Write JSON schemas
3. Write Jinja2 templates
4. Download all data sources
5. Build crosswalk
6. Prototype with Paridae
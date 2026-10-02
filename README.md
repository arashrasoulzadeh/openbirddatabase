# OpenBird Database

Global bird species database (~11,000 species) as Markdown files with comprehensive attributes, multilingual support (Persian priority), and git-tracked changes.

## Features

- **11,000+ species** from unified AviList 2025 taxonomy
- **78 BIRDBASE traits** across 10 categories (morphology, habitat, diet, behavior, reproduction, demography, conservation, etc.)
- **32 AVONICHE foraging niches** (diet × foraging strategy combinations)
- **Multilingual**: Persian (primary), English (keys), 430+ other languages via BirdNET
- **Per-species git commits** - full change history for every bird
- **Searchable** - designed for MeiliSearch/Typesense indexing
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
├── _scripts/                 # Ingestion pipeline
├── _index/                   # Generated search indexes
├── _data/                    # Raw downloads (gitignored)
└── docs/                     # Documentation
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

# Start search server
docker-compose up -d
python _scripts/index.py
uvicorn _scripts.api:app --reload
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

## Search & API (Planned)

- MeiliSearch for full-text + faceted search
- FastAPI REST + GraphQL endpoints
- i18n merge on-the-fly
- Filter by: taxonomy, habitat, diet, conservation, range, morphology, etc.

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
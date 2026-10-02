# AI Context - OpenBird Database

## Project Summary
Building a comprehensive global bird database (~11,000 species) as Markdown files with:
- All 78 BIRDBASE traits + 32 AVONICHE foraging niches
- Multilingual (Persian primary, English keys, 430+ languages)
- Per-species git commits for full audit trail
- Designed for search API (MeiliSearch) and apps

## Directory Structure
```
birds-db/
├── birds/{order}/{family}/{species}.md      # Main files (English keys, Persian values)
├── translations/{lang}/{order}/{family}/{species}.md  # Override files
├── _schemas/                                 # JSON Schemas for validation
├── _templates/                               # Jinja2 templates
├── _scripts/                                 # Ingestion pipeline
├── _index/                                   # Generated search indexes
└── _data/                                    # Raw downloads (gitignored)
```

## Data Sources (All Free, CC-BY 4.0)

### 1. BirdNET Taxonomy v0.3-Jul2026
- **URL**: https://birdnet.cornell.edu/taxonomy/download
- **Species**: 16,193
- **Key fields**: BirdNET ID, scientific name, 434 language common names, eBird code, GBIF key, Avibase ID, iNaturalist ID, NCBI taxid, BirdLife ID, Macaulay Library ID, Xeno-Canto ID, descriptions, image URLs
- **Format**: CSV, JSON, ZIP + REST API
- **Persian**: Included in 434 languages

### 2. BIRDBASE 2025
- **URL**: https://doi.org/10.6084/m9.figshare.27051040
- **Species**: 11,589
- **Traits**: 78 across 10 categories
- **Format**: Excel (multiple worksheets)
- **License**: CC-BY 4.0

### 3. AVONICHE 2025
- **URL**: https://datadryad.org/dataset/doi:10.5061/dryad.1zcrjdg56
- **Species**: 10,981 (AviList taxonomy)
- **Traits**: 9 dietary niches + 32 foraging niches
- **Format**: CSV (4 taxonomy versions + crosswalks)
- **License**: CC-BY 4.0

### 4. BirdFYI API
- **URL**: https://birdfyi.com/api/v1/
- **Species**: 11,251
- **Fields**: Habitat details, regional presence, comparisons, glossary, guides
- **Client**: `pip install birdfyi`
- **Format**: REST API (OpenAPI spec)

## Taxonomy Authority: AviList 2025
First unified global bird checklist (June 2025). Used by BIRDBASE. Crosswalks to eBird/Clements, BirdLife, BirdTree provided by AVONICHE.

## Key Implementation Details

### Markdown Frontmatter Schema
All fields defined in `_schemas/bird-attributes.schema.json`. Key sections:
- Core IDs (BirdNET, eBird, GBIF)
- Names (scientific + 434 locales)
- Taxonomy (order, family, genus, species, subspecies)
- Morphology (7 measurements)
- Distribution (countries, realms, ranges)
- Habitat (primary/secondary, breadth, elevation, types)
- Diet (8 categories 0-10, 32 foraging niches 0-1)
- Behavior (sociality, migration, vocalizations)
- Reproduction (clutch, nest, mating system)
- Demography (longevity, survival, population)
- Conservation (IUCN, CITES, threats)
- Veterinary (manual curation - may be empty)
- Enrichment (manual curation - may be empty)

### Multilingual Strategy
- Base: `birds/.../species.md` - English keys, Persian values
- Overrides: `translations/fa/.../species.md` - Only changed values
- Merge at build/runtime for complete localization

### Git Commits
One commit per species file:
```
feat(birds): add Parus major (Great Tit) - Passeriformes/Paridae

Taxon IDs: BirdNET=BT00012345, eBird=gretit, GBIF=2480498
Sources: BirdNET, BIRDBASE, AVONICHE, BirdFYI
Quality: High
Languages: fa, en, +432 more
```

### Validation
JSON Schema validation via `jsonschema` Python package before write.

### Search Index
MeiliSearch-compatible JSON with:
- Full-text search across all fields
- Faceted filters: order, family, habitat, diet, conservation, range, etc.
- Taxonomy tree for navigation

## Common Tasks for AI Assistants

### Adding a New Species
1. Check if species exists in `birds/{order}/{family}/`
2. If not, create from template with merged data sources
3. Validate against schema
4. Commit with proper message

### Updating Translations
1. Edit `translations/fa/{order}/{family}/{species}.md`
2. Only include changed fields
3. Commit with `i18n(fa): update Parus major - habitat, diet`

### Adding Veterinary/Enrichment Data
1. Edit base species file (or translation for locale-specific)
2. Fill `veterinary` and/or `enrichment` sections
3. Add source citation
4. Commit with `feat(vet): add Parus major - common diseases, enrichment`

### Schema Changes
1. Update `_schemas/bird-attributes.schema.json`
2. Update `_templates/species-template.md.j2`
3. Regenerate affected species
4. Commit with `refactor(schema): add new field X`

## File Naming Convention
- Species files: `{genus}-{species}.md` (lowercase, hyphenated)
- Example: `parus-major.md`, `cyanistes-caeruleus.md`
- Directory: `birds/{order}/{family}/` (lowercase)

## Quality Levels
- **High**: All 4 sources agree, primary literature
- **Medium**: 2-3 sources agree, some interpolation
- **Low**: Single source, expert opinion
- **Interpolated**: Estimated from congeners (BIRDBASE convention)

## Persian Language Notes
- BirdNET provides Persian names for most species
- Some names may need review by native speakers
- Regional variants (Iran vs Afghanistan vs Tajik) possible
- Store primary in base, variants in translations/fa/

## Missing Data Strategy
- Veterinary/enrichment: Empty arrays/objects, add via expert PRs
- Morphology: Use genus/family averages if species missing
- Diet: BIRDBASE interpolates from congeners (flagged in data_quality)
- Foraging: AVONICHE covers all species via interpolation

## API Integration Points
- BirdFYI Python client: `from birdfyi import BirdFYI`
- BirdNET REST API: https://birdnet.cornell.edu/taxonomy/docs
- GBIF API: https://api.gbif.org/v1/
- eBird API: https://documenter.getpostman.com/view/664302/S1ENwy59
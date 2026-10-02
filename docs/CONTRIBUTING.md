# Contributing to OpenBird Database

## Ways to Contribute

### 1. Add/Update Species Data
- Fill missing fields in existing species files
- Add new species from taxonomy updates
- Improve data quality assessments

### 2. Improve Translations
- Persian (fa): Primary target - review BirdNET translations
- Add regional variants (Iran, Afghanistan, Tajik Persian)
- Add other languages (Arabic, Turkish, etc.)

### 3. Veterinary & Enrichment Data
- **Critical gap**: These sections are largely empty
- Need avian veterinarians, zookeepers, rehabilitators
- Add: common diseases, vaccination, enrichment, training

### 4. Images & Media
- Verify BirdNET image URLs
- Add Xeno-Canto audio IDs
- Add Macaulay Library media IDs

### 5. Schema & Pipeline Improvements
- Add new fields to schema
- Improve ingestion pipeline
- Fix crosswalk issues

---

## Getting Started

### Prerequisites
```bash
# Clone
git clone https://github.com/yourusername/openbird.git
cd openbird

# Install Python dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install
```

### Development Workflow
1. Create feature branch: `git checkout -b feat/add-vet-data-parus-major`
2. Make changes
3. Validate: `python _scripts/validate.py birds/passeriformes/paridae/parus-major.md`
4. Commit with conventional message
5. Push and create PR

---

## Editing Species Files

### File Location
```
birds/{order}/{family}/{genus}-{species}.md
```
Example: `birds/passeriformes/paridae/parus-major.md`

### Adding Data
1. Open the markdown file
2. Edit YAML frontmatter (between `---` delimiters)
3. Keep section order consistent
4. Add source to `sources` array
5. Update `last_updated` to today
6. Set appropriate `data_quality`

### Adding Translations
```
translations/{lang}/{order}/{family}/{genus}-{species}.md
```
Only include fields that DIFFER from base file.

### Validation
```bash
# Validate single file
python _scripts/validate.py birds/passeriformes/paridae/parus-major.md

# Validate all
python _scripts/validate.py --all
```

---

## Commit Message Convention

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat` - New data field or species
- `fix` - Correct erroneous data
- `i18n` - Translation updates
- `refactor` - Schema/template changes
- `docs` - Documentation updates
- `chore` - Maintenance

### Scopes
- `birds` - Species data
- `fa` / `en` / `ar` - Translations
- `vet` - Veterinary data
- `enrichment` - Enrichment data
- `schema` - Schema changes
- `pipeline` - Ingestion scripts

### Examples
```
feat(birds): add Parus major (Great Tit) - Passeriformes/Paridae

Taxon IDs: BirdNET=BT00012345, eBird=gretit, GBIF=2480498
Sources: BirdNET, BIRDBASE, AVONICHE, BirdFYI
Quality: High
Languages: fa, en, +432 more

---

fix(birds): correct Parus major clutch size - was 12, now 8.5

Source: BIRDBASE 2025 (Handbook of Birds of World)
Quality: High

---

i18n(fa): update Parus major - habitat, diet translations

Reviewed by native speaker
Regional variant added for Iran

---

feat(vet): add Parus major veterinary data

Common diseases: Avian pox, Trichomonosis
Enrichment: Puzzle feeders, target training
Source: Avian Medicine and Surgery (2023)
```

---

## Adding Veterinary/Enrichment Data (Priority)

### Sources to Use
- Peer-reviewed avian medicine journals
- Zoo/aquarium husbandry manuals (AZA, EAZA)
- Wildlife rehabilitator guides
- Avian veterinarian textbooks
- Species-specific care sheets from reputable organizations

### Format
```yaml
veterinary:
  common_diseases:
    - "Disease name (pathogen if known)"
  vaccination_schedule:
    - "Vaccine name - age/frequency"
  deworming_frequency_months: 6
  health_check_frequency_months: 12
  zoonotic_risks:
    - "Pathogen - transmission route"
  emergency_signs:
    - "Specific observable sign"
  vet_specialist_type: "Avian veterinarian"

enrichment:
  foraging_toys:
    - "Specific toy type"
  social_enrichment: "Conspecifics required / mirror acceptable"
  cognitive_toys:
    - "Puzzle type"
  bathing: "Method preference"
  training:
    target_training: true
    recall_training: true
    harness_training: "Possible with patience / Not recommended"
  play_behaviors:
    - "Observed play behavior"
  environmental_enrichment:
    - "Perch variety, UV lighting, etc."
```

### Citation Format
Add to `sources`:
- `"Avian Medicine and Surgery, 3rd Ed. (2023)"`
- `"AZA Paridae Care Manual (2022)"`
- `"Personal communication: Dr. Name, DVM, Dipl. ABVP (Avian)"`

---

## Schema Changes

### Process
1. Propose in GitHub Issue with rationale
2. Update `_schemas/bird-attributes.schema.json`
3. Update `_templates/species-template.md.j2`
4. Update `_scripts/validate.py` if needed
5. Regenerate affected species (or migrate incrementally)
6. Document in `SCHEMA_GUIDE.md`

### Versioning
Schema version in `$id` URL: `.../bird-attributes.schema.v1.json`

---

## Data Quality Guidelines

### When to Use Each Level
- **High**: Multiple authoritative sources agree (BIRDBASE + BirdFYI + primary lit)
- **Medium**: Two sources agree, or one strong source + expert knowledge
- **Low**: Single secondary source, or conflicting sources
- **Interpolated**: Explicitly marked as interpolated in BIRDBASE/AVONICHE

### Updating Quality
When adding better data, upgrade quality level and note in commit.

---

## Taxonomy Updates

### Annual Cycle
- AviList updates ~June
- eBird/Clements updates ~October
- BirdLife updates ~January
- IOC updates ~January

### Process
1. Download new taxonomy
2. Crosswalk to AviList
3. Identify splits/lumps/new species
4. Create/modify species files
5. Update crosswalk mappings

---

## Code Style

### Python
- Black formatter (line length 100)
- Type hints required
- Docstrings for public functions
- Pytest for tests

### YAML/Markdown
- 2-space indentation
- No trailing spaces
- Consistent section ordering

---

## Review Checklist

Before submitting PR:
- [ ] Validates against schema (`python _scripts/validate.py`)
- [ ] Commit messages follow convention
- [ ] Sources cited in `sources` array
- [ ] `last_updated` set to today
- [ ] `data_quality` appropriate
- [ ] Translations only include changed fields
- [ ] No merge conflicts

---

## Community

- **Issues**: Bug reports, data requests, schema proposals
- **Discussions**: General questions, translation help
- **Experts needed**: Avian veterinarians, ornithologists, native Persian speakers

---

## License

By contributing, you agree your contributions are licensed under:
- **Data**: CC-BY 4.0 (same as sources)
- **Code**: MIT
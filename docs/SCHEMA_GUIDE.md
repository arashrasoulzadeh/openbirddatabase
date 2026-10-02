# Schema Guide - Field-by-Field Documentation

## bird-attributes.schema.json

### Core Identifiers
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `taxon_id` | string | Yes | BirdNET ID (BT + 8 digits) |
| `ebird_code` | string | Yes | 6-letter eBird species code |
| `gbif_key` | integer | Yes | GBIF taxon key |
| `avibase_id` | string | No | Avibase identifier |
| `iucn_status` | enum | Yes | EX/EW/CR/EN/VU/NT/LC/DD/NE |
| `taxon_order` | number | Yes | Taxonomic sort order |

### Names
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `names.scientific` | string | Yes | Binomial nomenclature |
| `names.fa` | string | Yes | Persian common name |
| `names.en` | string | Yes | English common name |
| `names.{lang}` | string | No | Additional ISO 639-1 languages |

### Taxonomy
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `taxonomy.order` | string | Yes | Order name (e.g., Passeriformes) |
| `taxonomy.family` | string | Yes | Family name (e.g., Paridae) |
| `taxonomy.genus` | string | Yes | Genus name |
| `taxonomy.species` | string | Yes | Species epithet |
| `taxonomy.subspecies` | array | No | Subspecies objects with name, scientific, range |

### Morphology (BIRDBASE)
| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `body_mass_g` | number | g | Body mass |
| `body_length_cm` | number | cm | Total length |
| `wingspan_cm` | number | cm | Wingspan |
| `bill_length_mm` | number | mm | Culmen length |
| `tarsus_length_mm` | number | mm | Tarsus length |
| `wing_length_mm` | number | mm | Wing chord |
| `tail_length_mm` | number | mm | Tail length |

### Distribution
| Field | Type | Description |
|-------|------|-------------|
| `breeding_range` | string | Text description |
| `non_breeding_range` | string | Text description |
| `countries` | array | ISO 3166-1 alpha-2 codes |
| `biogeographic_realms` | array | e.g., Palearctic, Nearctic |
| `endemic` | boolean | Country/region endemic |
| `island_endemic` | boolean | Island endemic |

### Habitat (BIRDBASE + BirdFYI)
| Field | Type | Description |
|-------|------|-------------|
| `primary` | string | Primary habitat |
| `secondary` | array | Additional habitats |
| `habitat_breadth` | integer | 1-15 (number of habitat types) |
| `elevational_min_m` | integer | Minimum elevation |
| `elevational_max_m` | integer | Maximum elevation |
| `habitat_types` | array | BirdFYI 15 types |
| `microhabitat` | string | Specific microhabitat |

**BirdFYI Habitat Types**: Tropical Forest, Temperate Forest, Boreal Forest, Grassland/Savanna, Shrubland, Desert, Wetland, Marine/Pelagic, Coastal, Urban/Suburban, Agricultural, Rocky, Arctic/Alpine, Artificial, Other

### Diet (BIRDBASE + AVONICHE)
#### Categories (8, scores 0-10, sum=10)
| Field | Type | Range |
|-------|------|-------|
| `invertebrates` | number | 0-10 |
| `seeds` | number | 0-10 |
| `fruit` | number | 0-10 |
| `nectar` | number | 0-10 |
| `vertebrates` | number | 0-10 |
| `fish` | number | 0-10 |
| `carrion` | number | 0-10 |
| `plant_material` | number | 0-10 |

#### Primary Diet (enum)
`Carnivore`, `Herbivore`, `Omnivore`, `Invertivore`, `Frugivore`, `Granivore`, `Nectarivore`, `Piscivore`, `Scavenger`

#### Foraging Niches (32, AVONICHE, proportional 0-1)
All 32 niches from `plants_aquatic_ground` to `carrion_ground` - see schema for full list.

### Behavior (BIRDBASE + BirdFYI)
| Field | Type | Values |
|-------|------|--------|
| `sociality` | enum | Solitary/Pairs/Pairs and family groups/Small groups/Large flocks/Colonial/Lekking |
| `flock_size_typical` | string | e.g., "2-6" |
| `flock_size_max` | integer | Maximum observed |
| `territorial` | boolean | |
| `migration_status` | enum | Resident/Partial migrant/Full migrant/Nomadic/Altitudinal migrant |
| `movement_type` | enum | Sedentary/Migratory/Nomadic/Dispersive/Altitudinal |
| `activity_pattern` | enum | Diurnal/Nocturnal/Crepuscular/Cathemeral |
| `vocalizations.song` | string | Song description |
| `vocalizations.calls` | array | Call descriptions |
| `xeno_canto_ids` | array | XC##### format |

### Reproduction (BIRDBASE)
| Field | Type | Description |
|-------|------|-------------|
| `clutch_size_mean` | number | Mean clutch size |
| `clutch_size_min/max` | integer | Range |
| `egg_length_mm/width_mm` | number | Egg dimensions |
| `incubation_days` | integer | Incubation period |
| `fledging_days` | integer | Fledging period |
| `broods_per_year` | integer | Annual broods |
| `nest_type` | string | Cavity, Open cup, Platform, etc. |
| `nest_placement` | string | Tree hole, Ground, Cliff, etc. |
| `nest_material` | array | Materials used |
| `mating_system` | enum | Monogamous/Polygynous/Polyandrous/Cooperative/Lek |
| `parental_care` | enum | Female only/Male only/Biparental/Cooperative/None |

### Demography (BIRDBASE)
| Field | Type | Description |
|-------|------|-------------|
| `generation_length_years` | number | IUCN generation length |
| `max_longevity_years` | integer | Maximum recorded age |
| `annual_survival_adult` | number | 0-1 |
| `annual_survival_juvenile` | number | 0-1 |
| `population_trend` | enum | Increasing/Stable/Decreasing/Unknown |
| `population_size` | string | Estimate text |
| `density_individuals_per_km2` | number | Population density |

### Conservation
| Field | Type | Values |
|-------|------|--------|
| `iucn_status` | enum | EX/EW/CR/EN/VU/NT/LC/DD/NE |
| `iucn_criteria` | string | e.g., "A2bc+3bc+4bc" |
| `cites_appendix` | enum | I/II/III/Not listed |
| `threats` | array | Threat descriptions |
| `conservation_actions` | array | Action descriptions |

### Veterinary (Manual Curation)
| Field | Type | Description |
|-------|------|-------------|
| `common_diseases` | array | Disease names |
| `vaccination_schedule` | array | Vaccine schedule |
| `deworming_frequency_months` | integer | Months between treatments |
| `health_check_frequency_months` | integer | Months between checkups |
| `zoonotic_risks` | array | Zoonotic pathogens |
| `emergency_signs` | array | Emergency symptoms |
| `vet_specialist_type` | string | Specialist type |

### Enrichment (Manual Curation)
| Field | Type | Description |
|-------|------|-------------|
| `foraging_toys` | array | Toy types |
| `social_enrichment` | string | Social needs |
| `cognitive_toys` | array | Puzzle types |
| `bathing` | string | Bathing preferences |
| `training.target_training` | boolean | Target training possible |
| `training.recall_training` | boolean | Recall training possible |
| `training.harness_training` | string | Harness training notes |
| `play_behaviors` | array | Observed play |
| `environmental_enrichment` | array | Environmental needs |

### Metadata
| Field | Type | Description |
|-------|------|-------------|
| `sources` | array | Source citations |
| `last_updated` | date | ISO 8601 |
| `data_quality` | enum | High/Medium/Low/Interpolated |

---

## foraging-niches.schema.json

### Dietary Niches (9, proportional 0-1, sum=1)
1. `plants_aquatic`
2. `plants_terrestrial`
3. `nectar`
4. `seeds`
5. `fruit`
6. `invertebrates`
7. `aquatic_prey`
8. `vertebrates`
9. `carrion`

### Foraging Niches (32, proportional 0-1, sum=1)
**Plants Aquatic** (3): `ground`, `surface`, `dive`
**Plants Terrestrial** (2): `elevated`, `ground`
**Nectar** (2): `aerial`, `glean`
**Seeds** (2): `elevated`, `ground`
**Fruit** (3): `aerial`, `glean`, `ground`
**Invertebrates** (7): `aerial_screening`, `sally_to_air`, `sally_to_surface`, `sally_to_ground`, `vertical_substrate`, `glean_elevated`, `glean_ground`
**Aquatic Prey** (6): `air`, `plunge`, `perch`, `ground`, `surface`, `dive`
**Vertebrates** (5): `aerial_screening`, `air_to_surface`, `perch`, `glean_elevated`, `glean_ground`
**Carrion** (2): `aquatic`, `ground`

---

## Validation Rules

### Diet Categories
- All 8 categories present
- Each 0-10
- Sum ≈ 10 (allow 9.5-10.5 for rounding)

### Foraging Niches
- All 32 niches present
- Each 0-1
- Sum ≈ 1.0 (allow 0.95-1.05)

### IUCN Status
Must be valid 2024 category

### Country Codes
ISO 3166-1 alpha-2 (2 uppercase letters)

### Dates
ISO 8601 (YYYY-MM-DD)

### Required Fields by Source
| Source | Required Fields |
|--------|-----------------|
| BirdNET | taxon_id, ebird_code, gbif_key, names, taxonomy |
| BIRDBASE | morphology, distribution, habitat, diet.categories, behavior, reproduction, demography, conservation |
| AVONICHE | diet.foraging_niches |
| BirdFYI | habitat.habitat_types, behavior.vocalizations, distribution.countries |
| Manual | veterinary, enrichment |

---

## Data Quality Levels

| Level | Criteria |
|-------|----------|
| **High** | All 4 sources agree, primary literature, direct measurements |
| **Medium** | 2-3 sources agree, some extrapolation from congeners |
| **Low** | Single source, expert opinion, coarse estimates |
| **Interpolated** | BIRDBASE/AVONICHE interpolated from congeners (flagged in source) |

Set `data_quality` to lowest level among all fields for that species.
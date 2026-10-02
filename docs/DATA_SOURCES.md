# Data Sources Documentation

## Overview
All sources are free, openly licensed (CC-BY 4.0 or CC0), and programmatically accessible.

---

## 1. BirdNET Taxonomy v0.3-Jul2026

### Access
- **Download**: https://birdnet.cornell.edu/taxonomy/download
- **API**: https://birdnet.cornell.edu/taxonomy/docs (REST, OpenAPI)
- **Formats**: CSV, JSON, ZIP (CSV + JSON)

### Coverage
- **Species**: 16,193
- **Languages**: 434 (including Persian `fa`)
- **Taxonomy**: Based on eBird/Clements with BirdNET IDs

### Key Fields
| Field | Description | Example |
|-------|-------------|---------|
| `birdnet_id` | Unique BirdNET identifier | `BT00012345` |
| `scientific_name` | Binomial nomenclature | `Parus major` |
| `common_name` | English common name | `Great Tit` |
| `common_names` | Object with 434 locale keys | `{"fa": "تیت بزرگ", "en": "Great Tit", ...}` |
| `ebird_code` | 6-letter eBird code | `gretit` |
| `gbif_key` | GBIF taxon key | `2480498` |
| `avibase_id` | Avibase identifier | `E5F3A2B1C4D6` |
| `inaturalist_id` | iNaturalist taxon ID | `12345` |
| `ncbi_taxid` | NCBI taxonomy ID | `123456` |
| `birdlife_id` | BirdLife International ID | `22710567` |
| `macaulay_library_id` | Macaulay Library ID | `ML123456` |
| `xeno_canto_id` | Xeno-Canto ID | `XC123456` |
| `description` | Species description | `A widespread tit...` |
| `image_url` | Representative image | `https://...` |
| `observation_count` | iNaturalist observations | `15420` |

### Download Command
```bash
# CSV (flat, one row per species, one column per language)
curl -L "https://birdnet.cornell.edu/taxonomy/download/csv" -o _data/birdnet/birdnet_taxonomy.csv

# JSON (nested common names)
curl -L "https://birdnet.cornell.edu/taxonomy/download/json" -o _data/birdnet/birdnet_taxonomy.json

# ZIP (both)
curl -L "https://birdnet.cornell.edu/taxonomy/download/zip" -o _data/birdnet/birdnet_taxonomy.zip
```

### License
CC-BY 4.0 - Attribution required: "BirdNET Taxonomy, Cornell Lab of Ornithology"

---

## 2. BIRDBASE 2025

### Access
- **Download**: https://doi.org/10.6084/m9.figshare.27051040
- **Direct**: https://springernature.figshare.com/articles/dataset/BIRDBASE_A_Global_Database_of_Avian_Biogeography_Conservation_Ecology_and_Life_History_Traits/27051040

### Coverage
- **Species**: 11,589 (AviList 2025 taxonomy)
- **Traits**: 78 across 10 categories
- **Sources**: 367 publications (1957-2025) + field observations (9,300+ species)

### Trait Categories (78 total)

#### 1. Conservation (5)
- `iucn_status` - IUCN Red List category (2024)
- `population_trend` - Increasing/Stable/Decreasing/Unknown
- `population_size` - Mature individuals estimate
- `range_size_km2` - Geographic range size
- `endemic` - Endemic status

#### 2. Geographic Distribution (6)
- `latitudinal_min` - Minimum latitude
- `latitudinal_max` - Maximum latitude
- `latitudinal_midpoint` - Midpoint latitude
- `biogeographic_realms` - Realm(s) occupied
- `island_endemic` - True/False
- `island_type` - Oceanic/Continental/None

#### 3. Morphology (7)
- `body_mass_g` - Body mass (grams)
- `body_length_cm` - Total length (cm)
- `wingspan_cm` - Wingspan (cm)
- `bill_length_mm` - Culmen length (mm)
- `tarsus_length_mm` - Tarsus length (mm)
- `wing_length_mm` - Wing chord (mm)
- `tail_length_mm` - Tail length (mm)

#### 4. Elevational Distribution (4)
- `elevational_min_m` - Minimum elevation (m)
- `elevational_max_m` - Maximum elevation (m)
- `elevational_range_m` - Range (m)
- `elevational_midpoint_m` - Midpoint (m)

#### 5. Habitat (6)
- `primary_habitat` - Primary habitat type
- `secondary_habitats` - Additional habitats
- `habitat_breadth` - Number of habitat types (1-15)
- `habitat_specialization` - Specialist/Generalist index
- `forest_dependency` - High/Medium/Low/None
- `migratory_habitat` - Breeding/Non-breeding habitat

#### 6. Diet (10)
- `diet_invertebrates` - Score 0-10
- `diet_fruit` - Score 0-10
- `diet_nectar` - Score 0-10
- `diet_seeds` - Score 0-10
- `diet_vertebrates` - Score 0-10
- `diet_fish` - Score 0-10
- `diet_carrion` - Score 0-10
- `diet_plant_material` - Score 0-10
- `primary_diet` - Carnivore/Herbivore/Omnivore/Invertivore/etc.
- `diet_breadth` - Number of diet categories used

#### 7. Social Behavior (4)
- `sociality` - Solitary/Pairs/Family groups/Small flocks/Large flocks/Colonial/Lekking
- `flock_size_typical` - Typical group size
- `flock_size_max` - Maximum group size
- `territoriality` - Territorial/Non-territorial

#### 8. Reproductive Behavior (10)
- `clutch_size_mean` - Mean clutch size
- `clutch_size_min` - Minimum clutch size
- `clutch_size_max` - Maximum clutch size
- `egg_mass_g` - Egg mass (g)
- `incubation_period_days` - Incubation days
- `fledging_period_days` - Fledging days
- `broods_per_year` - Number of broods
- `nest_type` - Cavity/Open/Cup/Platform/etc.
- `nest_site` - Ground/Tree/Cliff/Building/etc.
- `mating_system` - Monogamous/Polygynous/Polyandrous/Cooperative/Lek

#### 9. Demography (6)
- `generation_length_years` - Generation length
- `max_longevity_years` - Maximum recorded age
- `annual_survival_adult` - Adult survival rate
- `annual_survival_juvenile` - Juvenile survival rate
- `age_at_first_breeding_years` - Age at first breeding
- `population_density` - Individuals/km²

#### 10. Mobility (5)
- `migration_status` - Resident/Partial migrant/Full migrant/Nomadic/Altitudinal
- `movement_type` - Sedentary/Migratory/Nomadic/Dispersive/Altitudinal
- `dispersal_distance_km` - Natal dispersal distance
- `home_range_km2` - Home range size
- `flight_style` - Flapping/Soaring/Gliding/Hovering

### Format
Excel (.xlsx) with worksheets:
- `Traits` - Main data (11,589 rows × 78 columns)
- `Legend` - Trait definitions, units, sources
- `Nests` - Detailed nest descriptions
- `Sources` - 367 source references

### License
CC-BY 4.0 - Cite: "BIRDBASE: A Global Database of Avian Biogeography, Conservation, Ecology and Life History Traits" (Şekercioğlu et al., 2025)

---

## 3. AVONICHE 2025

### Access
- **Download**: https://datadryad.org/dataset/doi:10.5061/dryad.1zcrjdg56
- **DOI**: 10.5061/dryad.1zcrjdg56

### Coverage
- **Species**: 10,981 (AviList 2025)
- **Niches**: 9 dietary + 32 foraging niches
- **Taxonomies**: 4 versions with crosswalks

### Dietary Niches (9) - Proportional 0-1, sum=1
1. `plants_aquatic` (Pa)
2. `plants_terrestrial` (Pt)
3. `nectar` (Ne)
4. `seeds` (Se)
5. `fruit` (Fr)
6. `invertebrates` (In)
7. `aquatic_prey` (Ap)
8. `vertebrates` (Vt)
9. `carrion` (Ca)

### Foraging Niches (32) - Diet × Foraging Strategy
| Diet | Strategies | Niches |
|------|------------|--------|
| Plants aquatic | Ground, Surface, Dive | 3 |
| Plants terrestrial | Elevated, Ground | 2 |
| Nectar | Aerial, Glean | 2 |
| Seeds | Elevated, Ground | 2 |
| Fruit | Aerial, Glean, Ground | 3 |
| Invertebrates | Aerial screening, Sally-to-air, Sally-to-surface, Sally-to-ground, Vertical substrate, Glean elevated, Glean ground | 7 |
| Aquatic prey | Air, Plunge, Perch, Ground, Surface, Dive | 6 |
| Vertebrates | Aerial screening, Air-to-surface, Perch, Glean elevated, Glean ground | 5 |
| Carrion | Aquatic, Ground | 2 |
| **Total** | | **32** |

### Files
| File | Description |
|------|-------------|
| `Avoniche4_AviList_2025.csv` | Main data (AviList taxonomy) |
| `Avoniche1_BirdLife_2020.csv` | BirdLife taxonomy |
| `Avoniche2_eBird_2021.csv` | eBird/Clements taxonomy |
| `Avoniche3_BirdTree_2012.csv` | BirdTree taxonomy |
| `Crosswalk_sp1_sp2.csv` | BirdLife ↔ eBird |
| `Crosswalk_sp1_sp3.csv` | BirdLife ↔ BirdTree |
| `Avoniche_metadata.xlsx` | Variable descriptions |

### License
CC-BY 4.0 - Cite: "AVONICHE: A global dataset of dietary and foraging niches for birds" (Sayol et al., 2025)

---

## 4. BirdFYI API

### Access
- **Base URL**: https://birdfyi.com/api/v1/
- **Docs**: https://birdfyi.com/developers/
- **OpenAPI**: https://birdfyi.com/api/v1/openapi.json
- **Python**: `pip install birdfyi`

### Coverage
- **Species**: 11,251
- **Families**: 258
- **Orders**: 40
- **Countries**: 197
- **Habitats**: 15 types
- **Languages**: 15 (guides)

### Endpoints
| Endpoint | Description |
|----------|-------------|
| `/birds/` | List all birds (paginated) |
| `/birds/{slug}/` | Bird detail |
| `/orders/` | List orders |
| `/families/` | List families |
| `/habitats/` | List habitat types |
| `/countries/` | List countries |
| `/regional-presences/` | Regional presence records |
| `/comparisons/` | Species comparisons |
| `/search/?q={query}` | Full-text search |
| `/guides/` | Educational guides |
| `/glossary/` | Glossary terms |

### Bird Detail Fields
- Taxonomy (order, family, genus, species)
- Names (scientific, common, 15 languages)
- Conservation (IUCN status, population)
- Physical traits (size, weight, plumage, bill)
- Habitat preferences (primary, secondary, types)
- Diet description
- Behavior (social, nesting, vocalizations)
- Regional presence (country, migratory status, seasonality)
- Identification clues (silhouette, plumage, bill, flight, habitat, vocalization)
- Xeno-Canto audio IDs
- Comparison species

### Python Usage
```python
from birdfyi import BirdFYI

with BirdFYI() as api:
    bird = api.get_bird("great-tit")
    print(bird["habitat"])  # Habitat details
    print(bird["diet"])     # Diet description
    print(bird["regional_presences"])  # Country presence
```

### Rate Limits
- Free tier: 1000 requests/hour
- Respectful usage recommended

### License
Free for non-commercial use. Commercial use requires agreement.

---

## 5. GBIF / eBird (Supplementary)

### GBIF API
- **Base**: https://api.gbif.org/v1/
- **Species**: https://api.gbif.org/v1/species/match?name=Parus+major
- **Occurrences**: https://api.gbif.org/v1/occurrence/search?taxonKey=2480498

### eBird API 2.0
- **Docs**: https://documenter.getpostman.com/view/664302/S1ENwy59
- **Requires**: API key (free with eBird account)
- **Taxonomy**: https://ebird.org/ws1.1/ref/taxa/ebird?cat=species&fmt=json

### Use Cases
- Range maps and occurrence data
- Taxonomic crosswalk verification
- Regional checklists

---

## Crosswalk Strategy

### Primary: AviList 2025
- Unified checklist (June 2025)
- Used by BIRDBASE
- AVONICHE provides crosswalks to other taxonomies

### Crosswalk Files (from AVONICHE)
- `Crosswalk_sp1_sp2.csv` - BirdLife (sp1) ↔ eBird 2021 (sp2)
- `Crosswalk_sp1_sp3.csv` - BirdLife (sp1) ↔ BirdTree (sp3)

### Mapping Approach
1. Load AviList as master (BIRDBASE taxonomy)
2. Use BirdNET for 434 languages + IDs
3. Crosswalk BIRDBASE traits via AviList → eBird codes
4. Crosswalk AVONICHE niches via provided crosswalks
5. Enrich with BirdFYI via eBird codes

---

## Download Script Template

```python
# _scripts/download.py
import requests
from pathlib import Path

DATA_DIR = Path("_data")

def download_birdnet():
    urls = {
        "csv": "https://birdnet.cornell.edu/taxonomy/download/csv",
        "json": "https://birdnet.cornell.edu/taxonomy/download/json",
    }
    for fmt, url in urls.items():
        resp = requests.get(url, stream=True)
        resp.raise_for_status()
        (DATA_DIR / "birdnet" / f"birdnet_taxonomy.{fmt}").write_bytes(resp.content)

def download_birdbase():
    # Figshare requires manual download or API token
    # Place manually in _data/birdbase/BIRDBASE_2025.xlsx
    pass

def download_avoniche():
    base = "https://datadryad.org/stash/downloads/"
    files = [
        "Avoniche4_AviList_2025.csv",
        "Crosswalk_sp1_sp2.csv",
        "Crosswalk_sp1_sp3.csv",
        "Avoniche_metadata.xlsx",
    ]
    for f in files:
        resp = requests.get(base + f)
        resp.raise_for_status()
        (DATA_DIR / "avoniche" / f).write_bytes(resp.content)

if __name__ == "__main__":
    download_birdnet()
    download_avoniche()
    print("Manual download needed: BIRDBASE from Figshare")
```
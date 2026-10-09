# Bird Image Download Plan - Wikipedia/Wikimedia Commons

## Overview
Download high-quality bird images for all 11,149+ species from Wikimedia Commons using structured APIs.

## Data Sources

### 1. Wikimedia Commons API
- **Primary**: `https://commons.wikimedia.org/w/api.php`
- **Image info**: `action=query&prop=imageinfo&iiprop=url|size|mime|extmetadata`
- **Search**: `action=query&list=search&srsearch=` + scientific name
- **Categories**: `Category:Birds by scientific name`, `Category:Birds by common name`

### 2. Wikidata (for structured mapping)
- **SPARQL endpoint**: `https://query.wikidata.org/sparql`
- **Maps**: Scientific name → Commons media (P18), taxon ID (P225), image (P18)
- **Query example**: Get all birds with images

### 3. Wikipedia API
- **Page images**: `action=query&prop=pageimages&piprop=original`
- **Language variants**: Get Persian/English Wikipedia pages

## Implementation Phases

### Phase 1: Species-Wikidata Mapping (Week 1)
```python
# 1. Query Wikidata for all bird taxa with images
SPARQL_QUERY = """
SELECT ?taxon ?scientificName ?commonName ?image ?commonsCategory WHERE {
  ?taxon wdt:P31/wdt:P279* wd:Q814987 .  # Bird taxa
  ?taxon wdt:P225 ?scientificName .
  OPTIONAL { ?taxon wdt:P18 ?image . }
  OPTIONAL { ?taxon wdt:P1843 ?commonName . FILTER(LANG(?commonName) = "en") }
  OPTIONAL { ?taxon wdt:P373 ?commonsCategory . }
}
"""

# 2. Cross-reference with our species list (11,149 species)
# 3. Build mapping: scientific_name → [wikidata_id, image_url, commons_category]
```

### Phase 2: Wikimedia Commons Bulk Download (Week 1-2)

#### Strategy A: Category-based (most reliable)
```python
# For each family/order, get category members
# Category:Paridae, Category:Accipitridae, etc.
# Use categorymembers API with cmtype=file
```

#### Strategy B: Search-based (fallback)
```python
# Search for scientific name + "bird"
# Filter by license (CC-BY, CC-BY-SA, Public Domain)
# Prefer high-res (>1000px)
```

#### Strategy C: Wikidata direct (most accurate)
```python
# Use P18 (image) property from Wikidata
# Get file page → download original
```

### Phase 3: Image Selection & Quality (Week 2)

#### Criteria:
1. **License**: CC0, CC-BY, CC-BY-SA only (no NC/ND)
2. **Resolution**: Min 800px, prefer 2000px+
3. **Aspect**: Landscape/portrait both OK
4. **Content**: Adult plumage, clear view, minimal watermarks
5. **Multiple**: 1 primary + 2-3 alternatives per species

#### Selection algorithm:
```python
def select_best_images(candidates):
    scored = []
    for img in candidates:
        score = 0
        score += min(img.width, 3000) / 100  # Resolution
        score += 50 if img.license in ['CC0', 'CC-BY'] else 20
        score += 30 if 'adult' in img.description.lower() else 0
        score -= 100 if 'watermark' in img.description.lower() else 0
        scored.append((score, img))
    return sorted(scored, reverse=True)[:3]
```

### Phase 4: Download & Organization (Week 2-3)

#### Directory Structure:
```
images/
├── passeriformes/
│   ├── paridae/
│   │   ├── parus-major/
│   │   │   ├── primary.jpg
│   │   │   ├── alt1.jpg
│   │   │   ├── alt2.jpg
│   │   │   └── metadata.json
│   │   └── ...
```

#### Metadata JSON per species:
```json
{
  "scientific_name": "Parus major",
  "images": [
    {
      "filename": "primary.jpg",
      "source_url": "https://commons.wikimedia.org/...",
      "license": "CC-BY-SA 4.0",
      "author": "User:Example",
      "width": 3000,
      "height": 2000,
      "commons_file": "File:Parus_major.jpg",
      "wikidata_id": "Q12345",
      "is_primary": true
    }
  ]
}
```

### Phase 5: Integration with Species Files (Week 3)

#### Update frontmatter:
```yaml
images:
  primary: "images/passeriformes/paridae/parus-major/primary.jpg"
  alternatives:
    - "images/passeriformes/paridae/parus-major/alt1.jpg"
  metadata: "images/passeriformes/paridae/parus-major/metadata.json"
```

## Technical Implementation

### Required Python Packages:
```bash
pip install wikimedia-commons requests sparqlwrapper tqdm tenacity
```

### Rate Limiting:
- Wikimedia: 200 req/sec (with bot flag)
- Wikidata SPARQL: 60 sec timeout, respect retry-after
- Use `tenacity` for exponential backoff

### Resume Capability:
```python
# Track downloaded: species_id → status
# Checkpoint every 100 species
# Skip existing files (verify checksum)
```

### Parallel Download:
```python
# Use asyncio/aiohttp or ThreadPoolExecutor
# Max 10 concurrent downloads
# Per-domain rate limiting
```

## Estimated Scale
- **Species with images**: ~8,000-10,000 (70-90% coverage)
- **Total images**: ~25,000-30,000 (2-3 per species)
- **Storage**: ~15-25 GB (compressed JPEGs)
- **Time**: 2-3 days with parallel downloads

## Legal Compliance
- ✅ Only CC0, CC-BY, CC-BY-SA
- ✅ Attribution metadata stored
- ✅ No NC (non-commercial) or ND (no derivatives)
- ✅ Source URLs preserved for verification

## Next Steps
1. Run Wikidata SPARQL query to get baseline mapping
2. Build prototype for Paridae family (60 species)
3. Validate quality/license filtering
4. Scale to all orders in parallel batches
5. Integrate with existing species markdown files
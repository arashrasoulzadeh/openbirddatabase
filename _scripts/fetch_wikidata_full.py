#!/usr/bin/env python3
"""Phase 1b: Fetch all bird species from Wikidata using paginated queries."""

import json
import time
from pathlib import Path
from SPARQLWrapper import SPARQLWrapper, JSON

OUTPUT_DIR = Path("_data/wikidata")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql.setReturnFormat(JSON)

# Paginated query for bird species with images
# Q5113 = Aves (bird class)
def build_query(limit, offset):
    return f"""
SELECT ?taxon ?scientificName ?image ?commonsCategory WHERE {{
  ?taxon wdt:P31/wdt:P279* wd:Q5113 .
  ?taxon wdt:P225 ?scientificName .
  OPTIONAL {{ ?taxon wdt:P18 ?image . }}
  OPTIONAL {{ ?taxon wdt:P373 ?commonsCategory . }}
}}
ORDER BY ?scientificName
LIMIT {limit}
OFFSET {offset}
"""

def run_paginated_query(batch_size=1000):
    """Run query in batches."""
    all_results = []
    offset = 0
    
    while True:
        query = build_query(batch_size, offset)
        sparql.setQuery(query)
        sparql.setTimeout(120)
        
        print(f"Fetching batch: offset={offset}, limit={batch_size}...")
        
        try:
            results = sparql.query().convert()
            bindings = results["results"]["bindings"]
            
            if not bindings:
                print("No more results")
                break
            
            all_results.extend(bindings)
            print(f"  Got {len(bindings)} results (total: {len(all_results)})")
            
            if len(bindings) < batch_size:
                break
                
            offset += batch_size
            time.sleep(1)  # Rate limiting
            
        except Exception as e:
            print(f"Query failed at offset {offset}: {e}")
            time.sleep(5)
            # Try smaller batch
            if batch_size > 100:
                batch_size = 100
            else:
                break
    
    return all_results

def process_results(bindings):
    species_map = {}
    
    for row in bindings:
        sci_name = row.get("scientificName", {}).get("value", "")
        if not sci_name:
            continue
        
        taxon_uri = row.get("taxon", {}).get("value", "")
        wikidata_id = taxon_uri.split("/")[-1] if taxon_uri else ""
        
        # Use scientific name as key (may have duplicates, keep first)
        if sci_name not in species_map:
            species_map[sci_name] = {
                "wikidata_id": wikidata_id,
                "scientific_name": sci_name,
                "taxon_uri": taxon_uri,
                "image": row.get("image", {}).get("value", ""),
                "commons_category": row.get("commonsCategory", {}).get("value", "")
            }
    
    return species_map

def save_results(species_map):
    output_file = OUTPUT_DIR / "wikidata_bird_mapping_full.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(species_map, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(species_map)} species to {output_file}")
    
    # Stats
    with_images = sum(1 for s in species_map.values() if s["image"])
    with_category = sum(1 for s in species_map.values() if s["commons_category"])
    print(f"Species with direct image (P18): {with_images}")
    print(f"Species with Commons category: {with_category}")

def main():
    print("=== Wikidata Bird Mapping (Paginated) ===")
    start = time.time()
    
    bindings = run_paginated_query(batch_size=5000)
    print(f"\nTotal raw results: {len(bindings)}")
    
    species_map = process_results(bindings)
    print(f"Unique species: {len(species_map)}")
    
    save_results(species_map)
    
    print(f"\nCompleted in {time.time() - start:.1f}s")

if __name__ == "__main__":
    main()
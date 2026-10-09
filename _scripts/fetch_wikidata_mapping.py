#!/usr/bin/env python3
"""Phase 1: Query Wikidata for bird species with images."""

import json
import time
from pathlib import Path
from SPARQLWrapper import SPARQLWrapper, JSON

OUTPUT_DIR = Path("_data/wikidata")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Wikidata SPARQL endpoint
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql.setReturnFormat(JSON)

# Query: All bird taxa with scientific names and images
# Q5113 = Aves (bird class)
QUERY = """
SELECT ?taxon ?taxonLabel ?scientificName ?image ?commonsCategory ?commonName_en ?commonName_fa WHERE {
  ?taxon wdt:P31/wdt:P279* wd:Q5113 .  # Instance/subclass of Aves
  ?taxon wdt:P225 ?scientificName .      # Taxon name (scientific)
  OPTIONAL { ?taxon wdt:P18 ?image . }   # Image (P18)
  OPTIONAL { ?taxon wdt:P373 ?commonsCategory . }  # Commons category
  OPTIONAL { 
    ?taxon rdfs:label ?commonName_en . 
    FILTER(LANG(?commonName_en) = "en")
  }
  OPTIONAL { 
    ?taxon rdfs:label ?commonName_fa . 
    FILTER(LANG(?commonName_fa) = "fa")
  }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,fa". }
}
ORDER BY ?scientificName
"""

def run_query():
    print("Running Wikidata SPARQL query...")
    sparql.setQuery(QUERY)
    sparql.setTimeout(120)
    
    try:
        results = sparql.query().convert()
        return results["results"]["bindings"]
    except Exception as e:
        print(f"Query failed: {e}")
        return []

def process_results(bindings):
    """Process SPARQL results into species mapping."""
    species_map = {}
    
    for row in bindings:
        sci_name = row.get("scientificName", {}).get("value", "")
        if not sci_name:
            continue
        
        taxon_uri = row.get("taxon", {}).get("value", "")
        wikidata_id = taxon_uri.split("/")[-1] if taxon_uri else ""
        
        species_map[sci_name] = {
            "wikidata_id": wikidata_id,
            "scientific_name": sci_name,
            "taxon_uri": taxon_uri,
            "image": row.get("image", {}).get("value", ""),
            "commons_category": row.get("commonsCategory", {}).get("value", ""),
            "common_name_en": row.get("commonName_en", {}).get("value", ""),
            "common_name_fa": row.get("commonName_fa", {}).get("value", ""),
            "taxon_label": row.get("taxonLabel", {}).get("value", "")
        }
    
    return species_map

def save_results(species_map):
    """Save mapping to JSON."""
    output_file = OUTPUT_DIR / "wikidata_bird_mapping.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(species_map, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(species_map)} species to {output_file}")
    
    # Also save CSV for easy viewing
    import csv
    csv_file = OUTPUT_DIR / "wikidata_bird_mapping.csv"
    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "scientific_name", "wikidata_id", "image", "commons_category",
            "common_name_en", "common_name_fa", "taxon_label", "taxon_uri"
        ])
        writer.writeheader()
        for data in species_map.values():
            writer.writerow(data)
    print(f"CSV saved to {csv_file}")

def main():
    print("=== Wikidata Bird Image Mapping ===")
    start = time.time()
    
    bindings = run_query()
    print(f"Got {len(bindings)} results from Wikidata")
    
    species_map = process_results(bindings)
    print(f"Processed {len(species_map)} unique species")
    
    # Count with images
    with_images = sum(1 for s in species_map.values() if s["image"])
    print(f"Species with direct image (P18): {with_images}")
    
    with_category = sum(1 for s in species_map.values() if s["commons_category"])
    print(f"Species with Commons category: {with_category}")
    
    save_results(species_map)
    
    print(f"\nCompleted in {time.time() - start:.1f}s")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""Generate search indexes from markdown files for MeiliSearch/Typesense."""

import json
import yaml
from pathlib import Path
from collections import defaultdict

BIRDS_DIR = Path("birds")
INDEX_DIR = Path("_index")
INDEX_DIR.mkdir(exist_ok=True)

def parse_frontmatter(filepath):
    """Extract YAML frontmatter from markdown file."""
    content = filepath.read_text(encoding='utf-8')
    if not content.startswith('---'):
        return None
    parts = content.split('---', 2)
    if len(parts) < 3:
        return None
    try:
        return yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return None

def get_body_text(filepath):
    """Extract body text (after frontmatter) for full-text search."""
    content = filepath.read_text(encoding='utf-8')
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return content

def build_indexes():
    """Build all search indexes."""
    print("Scanning species files...")
    
    files = list(BIRDS_DIR.glob("**/*.md"))
    print(f"Found {len(files)} species files")
    
    # Indexes
    species_index = []  # For MeiliSearch
    taxonomy_tree = {}  # Hierarchical navigation
    field_stats = defaultdict(lambda: defaultdict(int))  # Faceted search stats
    
    for filepath in files:
        fm = parse_frontmatter(filepath)
        if not fm:
            continue
        
        # Build species index document
        doc = {
            'id': fm.get('taxon_id', ''),
            'scientific_name': fm.get('names', {}).get('scientific', ''),
            'common_name_fa': fm.get('names', {}).get('fa', ''),
            'common_name_en': fm.get('names', {}).get('en', ''),
            'order': fm.get('taxonomy', {}).get('order', ''),
            'family': fm.get('taxonomy', {}).get('family', ''),
            'genus': fm.get('taxonomy', {}).get('genus', ''),
            'iucn_status': fm.get('iucn_status', '') or fm.get('conservation', {}).get('iucn_status', ''),
            'primary_habitat': fm.get('habitat', {}).get('primary', ''),
            'primary_diet': fm.get('diet', {}).get('primary', ''),
            'migration_status': fm.get('behavior', {}).get('migration_status', ''),
            'countries': fm.get('distribution', {}).get('countries', []),
            'body_mass_g': fm.get('morphology', {}).get('body_mass_g'),
            'body_length_cm': fm.get('morphology', {}).get('body_length_cm'),
            'wingspan_cm': fm.get('morphology', {}).get('wingspan_cm'),
            'data_quality': fm.get('data_quality', ''),
            'sources': fm.get('sources', []),
            # Body text for full-text search
            'body_text': get_body_text(filepath)[:5000],  # Limit size
        }
        
        # Add all language names
        names = fm.get('names', {})
        for lang, name in names.items():
            if lang not in ['scientific', 'fa', 'en']:
                doc[f'common_name_{lang}'] = name
        
        species_index.append(doc)
        
        # Build taxonomy tree
        order = doc['order']
        family = doc['family']
        genus = doc['genus']
        sci = doc['scientific_name']
        
        if order not in taxonomy_tree:
            taxonomy_tree[order] = {}
        if family not in taxonomy_tree[order]:
            taxonomy_tree[order][family] = {}
        if genus not in taxonomy_tree[order][family]:
            taxonomy_tree[order][family][genus] = []
        
        taxonomy_tree[order][family][genus].append({
            'scientific': sci,
            'common_fa': doc['common_name_fa'],
            'common_en': doc['common_name_en'],
            'id': doc['id']
        })
        
        # Update field stats for faceted search
        if doc['iucn_status']:
            field_stats['iucn_status'][doc['iucn_status']] += 1
        if doc['primary_habitat']:
            field_stats['primary_habitat'][doc['primary_habitat']] += 1
        if doc['primary_diet']:
            field_stats['primary_diet'][doc['primary_diet']] += 1
        if doc['migration_status']:
            field_stats['migration_status'][doc['migration_status']] += 1
        if doc['order']:
            field_stats['order'][doc['order']] += 1
        if doc['family']:
            field_stats['family'][doc['family']] += 1
        
        for country in doc['countries']:
            field_stats['countries'][country] += 1
    
    # Save indexes
    print("Saving indexes...")
    
    # Species index (MeiliSearch format)
    with open(INDEX_DIR / "species-index.json", 'w') as f:
        json.dump(species_index, f, ensure_ascii=False)
    print(f"  species-index.json: {len(species_index)} documents")
    
    # Taxonomy tree
    with open(INDEX_DIR / "taxonomy-tree.json", 'w') as f:
        json.dump(taxonomy_tree, f, ensure_ascii=False)
    print(f"  taxonomy-tree.json: {len(taxonomy_tree)} orders")
    
    # Field stats (convert defaultdict to dict)
    field_stats_dict = {k: dict(v) for k, v in field_stats.items()}
    with open(INDEX_DIR / "field-stats.json", 'w') as f:
        json.dump(field_stats_dict, f, ensure_ascii=False)
    print(f"  field-stats.json: {len(field_stats_dict)} fields")
    
    # Summary
    print(f"\nTotal species indexed: {len(species_index)}")
    print(f"Orders: {len(taxonomy_tree)}")
    print(f"Families: {sum(len(f) for f in taxonomy_tree.values())}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate search indexes")
    parser.add_argument("--rebuild", action="store_true", help="Force rebuild")
    args = parser.parse_args()
    
    build_indexes()

if __name__ == "__main__":
    main()
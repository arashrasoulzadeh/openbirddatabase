#!/usr/bin/env python3
"""Apply veterinary and enrichment curations to species markdown files."""

import json
import yaml
import re
from pathlib import Path

BIRDS_DIR = Path("birds")
CURATIONS_DIR = Path("curations")

def parse_frontmatter(filepath):
    """Extract YAML frontmatter from markdown file."""
    content = filepath.read_text(encoding='utf-8')
    if not content.startswith('---'):
        return None, content
    parts = content.split('---', 2)
    if len(parts) < 3:
        return None, content
    try:
        fm = yaml.safe_load(parts[1])
        return fm, content
    except yaml.YAMLError:
        return None, content

def write_frontmatter(filepath, fm, body_content):
    """Write updated frontmatter back to file."""
    new_fm = yaml.dump(fm, allow_unicode=True, sort_keys=False, default_flow_style=False)
    new_content = f'---\n{new_fm}---\n{body_content}'
    filepath.write_text(new_content, encoding='utf-8')

def load_curation(sci_name, curation_type):
    """Load curation data for a species."""
    filename = sci_name.lower().replace(' ', '-')
    curation_file = CURATIONS_DIR / f"{curation_type}_{filename}.json"
    if curation_file.exists():
        with open(curation_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def merge_veterinary(fm, vet_data):
    """Merge veterinary data into frontmatter."""
    if 'veterinary' not in fm:
        fm['veterinary'] = {}
    
    # Only add fields that don't exist or are empty
    for key, value in vet_data.items():
        if key in ['species', 'common_name', 'source', 'contributor', 'date_added', 'verified']:
            continue
        if key not in fm['veterinary'] or not fm['veterinary'][key]:
            fm['veterinary'][key] = value
    
    # Add metadata
    fm['veterinary']['source'] = vet_data.get('source', '')
    fm['veterinary']['contributor'] = vet_data.get('contributor', '')
    fm['veterinary']['date_added'] = vet_data.get('date_added', '')
    fm['veterinary']['verified'] = vet_data.get('verified', False)
    
    return fm

def merge_enrichment(fm, enrich_data):
    """Merge enrichment data into frontmatter."""
    if 'enrichment' not in fm:
        fm['enrichment'] = {}
    
    for key, value in enrich_data.items():
        if key in ['species', 'common_name', 'source', 'contributor', 'date_added', 'verified']:
            continue
        if key not in fm['enrichment'] or not fm['enrichment'][key]:
            if key == 'training' and isinstance(value, dict):
                if 'training' not in fm['enrichment']:
                    fm['enrichment']['training'] = {}
                for tk, tv in value.items():
                    if tk not in fm['enrichment']['training'] or not fm['enrichment']['training'][tk]:
                        fm['enrichment']['training'][tk] = tv
            else:
                fm['enrichment'][key] = value
    
    # Add metadata
    fm['enrichment']['source'] = enrich_data.get('source', '')
    fm['enrichment']['contributor'] = enrich_data.get('contributor', '')
    fm['enrichment']['date_added'] = enrich_data.get('date_added', '')
    fm['enrichment']['verified'] = enrich_data.get('verified', False)
    
    return fm

def find_species_file(sci_name):
    """Find the markdown file for a species."""
    # Search recursively
    for filepath in BIRDS_DIR.glob(f"**/{sci_name.lower().replace(' ', '-')}.md"):
        return filepath
    return None

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Apply curations to species files")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument("--vet-only", action="store_true", help="Only apply veterinary")
    parser.add_argument("--enrich-only", action="store_true", help="Only apply enrichment")
    args = parser.parse_args()
    
    if args.dry_run:
        print("DRY RUN MODE")
    
    updated = 0
    vet_updated = 0
    enrich_updated = 0
    not_found = 0
    
    # Get all species files
    species_files = list(BIRDS_DIR.glob("**/*.md"))
    print(f"Found {len(species_files)} species files")
    
    for filepath in species_files:
        fm, content = parse_frontmatter(filepath)
        if not fm:
            continue
        
        sci_name = fm.get('names', {}).get('scientific', '')
        if not sci_name:
            continue
        
        file_updated = False
        
        # Apply veterinary curation
        if not args.enrich_only:
            vet_data = load_curation(sci_name, "vet")
            if vet_data:
                if args.dry_run:
                    print(f"  Would update veterinary: {sci_name}")
                else:
                    fm = merge_veterinary(fm, vet_data)
                    file_updated = True
                    vet_updated += 1
        
        # Apply enrichment curation
        if not args.vet_only:
            enrich_data = load_curation(sci_name, "enrich")
            if enrich_data:
                if args.dry_run:
                    print(f"  Would update enrichment: {sci_name}")
                else:
                    fm = merge_enrichment(fm, enrich_data)
                    file_updated = True
                    enrich_updated += 1
        
        if file_updated:
            if not args.dry_run:
                # Extract body content (after frontmatter)
                parts = content.split('---', 2)
                body = parts[2] if len(parts) >= 3 else ''
                write_frontmatter(filepath, fm, body)
                updated += 1
    
    if args.dry_run:
        print(f"\nWould update {vet_updated} species with veterinary data")
        print(f"Would update {enrich_updated} species with enrichment data")
    else:
        print(f"\nUpdated {updated} species files")
        print(f"  Veterinary: {vet_updated}")
        print(f"  Enrichment: {enrich_updated}")

if __name__ == "__main__":
    main()
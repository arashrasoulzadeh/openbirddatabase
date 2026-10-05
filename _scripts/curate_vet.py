#!/usr/bin/env python3
"""Veterinary/Enrichment curation interface - manage expert-contributed care data."""

import json
import yaml
from pathlib import Path
import argparse

BIRDS_DIR = Path("birds")
CURATION_DIR = Path("curations")
CURATION_DIR.mkdir(exist_ok=True)

VET_TEMPLATE = {
    "common_diseases": [],
    "vaccination_schedule": [],
    "deworming_frequency_months": 0,
    "health_check_frequency_months": 0,
    "zoonotic_risks": [],
    "emergency_signs": [],
    "vet_specialist_type": "",
    "source": "",
    "contributor": "",
    "date_added": "",
    "verified": False
}

ENRICHMENT_TEMPLATE = {
    "foraging_toys": [],
    "social_enrichment": "",
    "cognitive_toys": [],
    "bathing": "",
    "training": {
        "target_training": False,
        "recall_training": False,
        "harness_training": ""
    },
    "play_behaviors": [],
    "environmental_enrichment": [],
    "source": "",
    "contributor": "",
    "date_added": "",
    "verified": False
}

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

def write_frontmatter(filepath, fm):
    """Write frontmatter back to markdown file."""
    content = filepath.read_text(encoding='utf-8')
    parts = content.split('---', 2)
    if len(parts) < 3:
        return False
    
    new_fm = yaml.dump(fm, allow_unicode=True, sort_keys=False, default_flow_style=False)
    new_content = f"---\n{new_fm}---{parts[2]}"
    filepath.write_text(new_content, encoding='utf-8')
    return True

def list_species():
    """List all species with their current vet/enrichment status."""
    files = list(Path("birds").glob("**/*.md"))
    results = []
    
    for filepath in files:
        fm = parse_frontmatter(filepath)
        if not fm:
            continue
        
        sci_name = fm.get('names', {}).get('scientific', '')
        fa_name = fm.get('names', {}).get('fa', '')
        en_name = fm.get('names', {}).get('en', '')
        
        vet = fm.get('veterinary', {})
        enrich = fm.get('enrichment', {})
        
        has_vet = any(vet.values()) if isinstance(vet, dict) else False
        has_enrich = any(enrich.values()) if isinstance(enrich, dict) else False
        
        results.append({
            'scientific': sci_name,
            'fa': fa_name,
            'en': en_name,
            'file': str(filepath),
            'has_vet': has_vet,
            'has_enrich': has_enrich,
            'vet_keys': list(vet.keys()) if isinstance(vet, dict) else [],
            'enrich_keys': list(enrich.keys()) if isinstance(enrich, dict) else []
        })
    
    return results

def create_curation_entry(sci_name, entry_type, data):
    """Create a curation entry file for a species."""
    slug = sci_name.lower().replace(' ', '-')
    filename = f"{slug}_{entry_type}.json"
    filepath = CURATION_DIR / filename
    
    entry = {
        "scientific_name": sci_name,
        "entry_type": entry_type,
        "data": data,
        "status": "pending_review",
        "created": pd.Timestamp.now().isoformat()
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(entry, f, ensure_ascii=False, indent=2)
    
    print(f"Created curation entry: {filepath}")

def apply_curation(sci_name, entry_type):
    """Apply a curation entry to the species markdown file."""
    slug = sci_name.lower().replace(' ', '-')
    filename = f"{slug}_{entry_type}.json"
    filepath = CURATION_DIR / filename
    
    if not filepath.exists():
        print(f"Curation entry not found: {filepath}")
        return False
    
    with open(filepath) as f:
        entry = json.load(f)
    
    # Find species file
    species_files = list(Path("birds").glob(f"**/{slug}.md"))
    if not species_files:
        print(f"Species file not found: {slug}")
        return False
    
    species_file = species_files[0]
    fm = parse_frontmatter(species_file)
    if not fm:
        print(f"Could not parse frontmatter: {species_file}")
        return False
    
    # Apply the data
    if entry_type == 'veterinary':
        fm['veterinary'] = entry['data']
    elif entry_type == 'enrichment':
        fm['enrichment'] = entry['data']
    
    # Update sources
    if 'sources' not in fm:
        fm['sources'] = []
    source_str = f"Expert curation: {entry['data'].get('source', 'Expert contribution')}"
    if source_str not in fm['sources']:
        fm['sources'].append(source_str)
    
    # Update last_updated
    from datetime import date
    fm['last_updated'] = date.today().isoformat()
    fm['data_quality'] = 'High'
    
    # Write back
    write_frontmatter(species_file, fm)
    print(f"Applied {entry_type} curation to {sci_name}")
    return True

def create_template():
    """Create template files for curation."""
    vet_template_path = CURATION_DIR / "veterinary_template.json"
    enrich_template_path = CURATION_DIR / "enrichment_template.json"
    
    vet_example = VET_TEMPLATE.copy()
    vet_example.update({
        "common_diseases": ["Aspergillosis", "Psittacine Beak and Feather Disease"],
        "vaccination_schedule": ["Polyomavirus at 30 days", "Psittacine Herpesvirus annually"],
        "deworming_frequency_months": 6,
        "health_check_frequency_months": 12,
        "zoonotic_risks": ["Chlamydia psittaci", "Salmonella"],
        "emergency_signs": ["Labored breathing", "Anorexia >24h", "Severe diarrhea"],
        "vet_specialist_type": "Avian veterinarian (ABVP certified preferred)",
        "source": "Avian Medicine and Surgery, 3rd Ed. (2023)",
        "contributor": "Dr. Jane Smith, DVM, Dipl. ABVP (Avian)",
        "date_added": "2026-10-05",
        "verified": True
    })
    
    enrich_example = ENRICHMENT_TEMPLATE.copy()
    enrich_example.update({
        "foraging_toys": ["Puzzle feeders", "Scatter feeding trays", "Browse branches"],
        "social_enrichment": "Conspecifics required; mirrors acceptable for single birds",
        "cognitive_toys": ["Color discrimination puzzles", "Tool use tasks", "String pulling"],
        "bathing": "Daily misting or shallow water dish",
        "training": {
            "target_training": True,
            "recall_training": True,
            "harness_training": "Possible with positive reinforcement"
        },
        "play_behaviors": ["Object manipulation", "Swinging", "Social allopreening"],
        "environmental_enrichment": ["Variable perch diameters", "UV lighting", "Seasonal diet variation"],
        "source": "AZA Parrot Husbandry Manual (2022)",
        "contributor": "AZA Parrot TAG",
        "date_added": "2026-10-05",
        "verified": True
    })
    
    with open(vet_template_path, 'w') as f:
        json.dump(vet_example, f, ensure_ascii=False, indent=2)
    
    with open(enrich_template_path, 'w') as f:
        json.dump(enrich_example, f, ensure_ascii=False, indent=2)
    
    print(f"Templates created: {vet_template_path}, {enrich_template_path}")

def generate_report():
    """Generate a report of vet/enrichment coverage."""
    results = list_species()
    
    has_vet = sum(1 for r in results if r['has_vet'])
    has_enrich = sum(1 for r in results if r['has_enrich'])
    total = len(results)
    
    print(f"Total species: {total}")
    print(f"With veterinary data: {has_vet} ({has_vet/total*100:.1f}%)")
    print(f"With enrichment data: {has_enrich} ({has_enrich/total*100:.1f}%)")
    
    # Show species with data
    if has_vet > 0:
        print("\nSpecies with veterinary data:")
        for r in results:
            if r['has_vet']:
                print(f"  {r['scientific']} ({r['en']}) - {r['fa']}")
    
    if has_enrich > 0:
        print("\nSpecies with enrichment data:")
        for r in results:
            if r['has_enrich']:
                print(f"  {r['scientific']} ({r['en']}) - {r['fa']}")

def main():
    parser = argparse.ArgumentParser(description="Veterinary/Enrichment curation tools")
    parser.add_argument("--report", action="store_true", help="Generate coverage report")
    parser.add_argument("--template", action="store_true", help="Create template files")
    parser.add_argument("--apply", nargs=2, metavar=('SCIENTIFIC', 'TYPE'), help="Apply curation to species")
    parser.add_argument("--list", action="store_true", help="List all species with status")
    args = parser.parse_args()
    
    if args.report:
        generate_report()
    elif args.template:
        create_template()
    elif args.apply:
        sci_name, entry_type = args.apply
        if entry_type not in ['veterinary', 'enrichment']:
            print("Type must be 'veterinary' or 'enrichment'")
            return
        slug = sci_name.lower().replace(' ', '-')
        filename = f"{slug}_{entry_type}.json"
        filepath = CURATION_DIR / filename
        if filepath.exists():
            apply_curation(sci_name, entry_type)
        else:
            print(f"Curation file not found: {filepath}")
    elif args.list:
        results = list_species()
        for r in results:
            status = []
            if r['has_vet']: status.append("VET")
            if r['has_enrich']: status.append("ENRICH")
            status_str = f"[{', '.join(status)}]" if status else "[EMPTY]"
            print(f"{status_str} {r['scientific']} ({r['en']}) - {r['fa']}")
    else:
        parser.print_help()

if __name__ == "__main__":
    import pandas as pd
    from datetime import date
    main()
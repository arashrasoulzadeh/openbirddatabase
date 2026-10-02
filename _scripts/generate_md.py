#!/usr/bin/env python3
"""Generate markdown files for bird species from merged data."""

import sys
import yaml
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

# Add _scripts to path
sys.path.insert(0, str(Path(__file__).parent))

# Import crosswalk functions
from crosswalk import load_birdnet, build_master_taxonomy, build_crosswalk_dicts

TEMPLATE_DIR = Path("_templates")
BIRDS_DIR = Path("birds")
DATA_DIR = Path("_data")

def load_template():
    """Load Jinja2 template."""
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True
    )
    return env.get_template("species-template.md.j2")

def load_data_sources():
    """Load all available data sources."""
    data = {}
    
    # BirdNET (primary)
    print("Loading BirdNET...")
    birdnet_df = load_birdnet()
    data['birdnet'] = birdnet_df.set_index('scientific_name').to_dict('index')
    print(f"  {len(data['birdnet'])} species")
    
    # AVONICHE (foraging niches)
    avoniche_dir = DATA_DIR / "avoniche"
    avoniche_file = avoniche_dir / "Avoniche4_AviList_2025.csv"
    if avoniche_file.exists():
        import pandas as pd
        print("Loading AVONICHE...")
        df = pd.read_csv(avoniche_file)
        data['avoniche'] = df.set_index('Scientific_Name').to_dict('index')
        print(f"  {len(data['avoniche'])} species")
    else:
        print("AVONICHE not found - will use empty foraging niches")
        data['avoniche'] = {}
    
    # BIRDBASE (78 traits)
    birdbase_dir = DATA_DIR / "birdbase"
    birdbase_files = list(birdbase_dir.glob("*.xlsx"))
    if birdbase_files:
        import pandas as pd
        print("Loading BIRDBASE...")
        df = pd.read_excel(birdbase_files[0], sheet_name="Traits")
        data['birdbase'] = df.set_index('Scientific_Name').to_dict('index')
        print(f"  {len(data['birdbase'])} species")
    else:
        print("BIRDBASE not found - will use empty traits")
        data['birdbase'] = {}
    
    # BirdFYI (habitat, behavior details)
    birdfyi_dir = DATA_DIR / "birdfyi"
    # Could load from API or cached files
    
    return data

def build_species_record(sci_name, birdnet_data, avoniche_data, birdbase_data):
    """Build complete species record from all sources."""
    # Start with BirdNET data
    bn = birdnet_data.get(sci_name, {})
    
    # Parse scientific name
    parts = sci_name.split(' ', 1)
    genus = parts[0] if parts else ''
    species = parts[1] if len(parts) > 1 else ''
    
    # Get family/order from taxonomy (would need eBird API or taxonomy file)
    # For now, use placeholder
    order = "Passeriformes"  # Default, should be looked up
    family = "Unknown"
    
    # Build record
    record = {
        # Core IDs
        'taxon_id': bn.get('birdnet_id', ''),
        'ebird_code': bn.get('ebird_code', ''),
        'gbif_key': int(bn['gbif_id']) if bn.get('gbif_id') and not pd.isna(bn['gbif_id']) else None,
        'avibase_id': bn.get('avibase_id', ''),
        'iucn_status': 'LC',  # Default, should come from BIRDBASE
        'taxon_order': 0,
        
        # Names
        'names': {
            'scientific': sci_name,
            'fa': bn.get('common_name_fa', ''),
            'en': bn.get('common_name', ''),
        },
        
        # Taxonomy
        'taxonomy': {
            'order': order,
            'family': family,
            'genus': genus,
            'species': species,
            'subspecies': []
        },
        
        # Morphology (from BIRDBASE)
        'morphology': {},
        
        # Distribution
        'distribution': {
            'breeding_range': '',
            'non_breeding_range': '',
            'countries': [],
            'biogeographic_realms': [],
            'endemic': False,
            'island_endemic': False
        },
        
        # Habitat
        'habitat': {
            'primary': '',
            'secondary': [],
            'habitat_breadth': 1,
            'elevational_min_m': 0,
            'elevational_max_m': 0,
            'habitat_types': [],
            'microhabitat': ''
        },
        
        # Diet
        'diet': {
            'primary': 'Unknown',
            'diet_breadth': 1,
            'categories': {
                'invertebrates': 0, 'seeds': 0, 'fruit': 0, 'nectar': 0,
                'vertebrates': 0, 'fish': 0, 'carrion': 0, 'plant_material': 0
            },
            'foraging_niches': {},
            'diet_sources': []
        },
        
        # Behavior
        'behavior': {
            'sociality': 'Unknown',
            'flock_size_typical': '',
            'flock_size_max': 0,
            'territorial': False,
            'migration_status': 'Unknown',
            'movement_type': 'Unknown',
            'activity_pattern': 'Diurnal',
            'vocalizations': {'song': '', 'calls': []},
            'xeno_canto_ids': []
        },
        
        # Reproduction
        'reproduction': {},
        
        # Demography
        'demography': {},
        
        # Conservation
        'conservation': {
            'iucn_status': 'LC',
            'iucn_criteria': '',
            'cites_appendix': 'Not listed',
            'threats': [],
            'conservation_actions': []
        },
        
        # Veterinary (manual)
        'veterinary': {
            'common_diseases': [],
            'vaccination_schedule': [],
            'deworming_frequency_months': 0,
            'health_check_frequency_months': 0,
            'zoonotic_risks': [],
            'emergency_signs': [],
            'vet_specialist_type': ''
        },
        
        # Enrichment (manual)
        'enrichment': {
            'foraging_toys': [],
            'social_enrichment': '',
            'cognitive_toys': [],
            'bathing': '',
            'training': {
                'target_training': False,
                'recall_training': False,
                'harness_training': ''
            },
            'play_behaviors': [],
            'environmental_enrichment': []
        },
        
        # Metadata
        'sources': ['BirdNET Taxonomy v0.3'],
        'last_updated': '2026-10-02',
        'data_quality': 'Low',
        
        # Markdown body sections
        'overview': f'{sci_name} is a species of bird...',
        'identification': '',
        'habitat_distribution': '',
        'diet_foraging': '',
        'behavior_ecology': '',
        'breeding': '',
        'conservation': '',
        'veterinary_care': '',
        'enrichment_training': ''
    }
    
    # Merge BIRDBASE data if available
    bb = birdbase_data.get(sci_name, {})
    if bb:
        record['sources'].append('BIRDBASE 2025')
        record['data_quality'] = 'High'
        # Map BIRDBASE fields to our schema
        # This would need detailed field mapping
    
    # Merge AVONICHE data if available
    av = avoniche_data.get(sci_name, {})
    if av:
        record['sources'].append('AVONICHE 2025')
        # Map foraging niches
        niche_mapping = {
            'plants_aquatic_ground': 'Plants_Aquatic_Ground',
            'plants_aquatic_surface': 'Plants_Aquatic_Surface',
            'plants_aquatic_dive': 'Plants_Aquatic_Dive',
            'plants_elevated': 'Plants_Elevated',
            'plants_ground': 'Plants_Ground',
            'nectar_aerial': 'Nectar_Aerial',
            'nectar_glean': 'Nectar_Glean',
            'seeds_elevated': 'Seeds_Elevated',
            'seeds_ground': 'Seeds_Ground',
            'fruit_aerial': 'Fruit_Aerial',
            'fruit_glean': 'Fruit_Glean',
            'fruit_ground': 'Fruit_Ground',
            'invertebrates_aerial_screening': 'Invertebrates_Aerial_Screening',
            'invertebrates_sally_to_air': 'Invertebrates_Sally_to_Air',
            'invertebrates_sally_to_surface': 'Invertebrates_Sally_to_Surface',
            'invertebrates_sally_to_ground': 'Invertebrates_Sally_to_Ground',
            'invertebrates_vertical_substrate': 'Invertebrates_Vertical_Substrate',
            'invertebrates_glean_elevated': 'Invertebrates_Glean_Elevated',
            'invertebrates_glean_ground': 'Invertebrates_Glean_Ground',
            'aquatic_predator_air': 'Aquatic_Predator_Air',
            'aquatic_predator_plunge': 'Aquatic_Predator_Plunge',
            'aquatic_predator_perch': 'Aquatic_Predator_Perch',
            'aquatic_predator_ground': 'Aquatic_Predator_Ground',
            'aquatic_predator_surface': 'Aquatic_Predator_Surface',
            'aquatic_predator_dive': 'Aquatic_Predator_Dive',
            'vertebrates_aerial_screening': 'Vertebrates_Aerial_Screening',
            'vertebrates_air_to_surface': 'Vertebrates_Air_to_Surface',
            'vertebrates_perch': 'Vertebrates_Perch',
            'vertebrates_glean_elevated': 'Vertebrates_Glean_Elevated',
            'vertebrates_glean_ground': 'Vertebrates_Glean_Ground',
            'carrion_aquatic': 'Carrion_Aquatic',
            'carrion_ground': 'Carrion_Ground',
        }
        for our_key, their_key in niche_mapping.items():
            if their_key in av and not pd.isna(av[their_key]):
                record['diet']['foraging_niches'][our_key] = float(av[their_key])
    
    # Ensure all 32 foraging niches exist
    all_niches = [
        'plants_aquatic_ground', 'plants_aquatic_surface', 'plants_aquatic_dive',
        'plants_elevated', 'plants_ground',
        'nectar_aerial', 'nectar_glean',
        'seeds_elevated', 'seeds_ground',
        'fruit_aerial', 'fruit_glean', 'fruit_ground',
        'invertebrates_aerial_screening', 'invertebrates_sally_to_air',
        'invertebrates_sally_to_surface', 'invertebrates_sally_to_ground',
        'invertebrates_vertical_substrate', 'invertebrates_glean_elevated',
        'invertebrates_glean_ground',
        'aquatic_predator_air', 'aquatic_predator_plunge', 'aquatic_predator_perch',
        'aquatic_predator_ground', 'aquatic_predator_surface', 'aquatic_predator_dive',
        'vertebrates_aerial_screening', 'vertebrates_air_to_surface',
        'vertebrates_perch', 'vertebrates_glean_elevated', 'vertebrates_glean_ground',
        'carrion_aquatic', 'carrion_ground'
    ]
    for niche in all_niches:
        if niche not in record['diet']['foraging_niches']:
            record['diet']['foraging_niches'][niche] = 0.0
    
    return record

def generate_species_file(sci_name, record, template, dry_run=False):
    """Generate markdown file for a species."""
    # Create directory structure
    # For now, use placeholder order/family
    order = record['taxonomy']['order'].lower().replace(' ', '_')
    family = record['taxonomy']['family'].lower().replace(' ', '_')
    species_slug = sci_name.lower().replace(' ', '-')
    
    out_dir = BIRDS_DIR / order / family
    out_dir.mkdir(parents=True, exist_ok=True)
    
    out_file = out_dir / f"{species_slug}.md"
    
    # Render template
    content = template.render(**record)
    
    if dry_run:
        print(f"Would write: {out_file}")
        return True
    
    out_file.write_text(content, encoding='utf-8')
    return True

def main():
    import argparse
    import pandas as pd
    
    parser = argparse.ArgumentParser(description="Generate species markdown files")
    parser.add_argument("--family", help="Filter by family")
    parser.add_argument("--order", help="Filter by order")
    parser.add_argument("--species", help="Generate single species")
    parser.add_argument("--dry-run", action="store_true", help="Don't write files")
    parser.add_argument("--limit", type=int, help="Limit number of species")
    args = parser.parse_args()
    
    print("=" * 50)
    print("Generating Species Markdown Files")
    print("=" * 50)
    
    # Load template
    template = load_template()
    
    # Load data sources
    data = load_data_sources()
    birdnet_data = data['birdnet']
    avoniche_data = data['avoniche']
    birdbase_data = data['birdbase']
    
    # Get species list
    if args.species:
        species_list = [args.species]
    else:
        species_list = list(birdnet_data.keys())
        
        # Filter by family/order if specified
        # Would need taxonomy data
        
        if args.limit:
            species_list = species_list[:args.limit]
    
    print(f"\nProcessing {len(species_list)} species...")
    
    # Generate files
    success = 0
    failed = 0
    
    for sci_name in species_list:
        try:
            record = build_species_record(sci_name, birdnet_data, avoniche_data, birdbase_data)
            generate_species_file(sci_name, record, template, args.dry_run)
            success += 1
        except Exception as e:
            print(f"  ERROR {sci_name}: {e}")
            failed += 1
        
        if success % 100 == 0:
            print(f"  Processed {success}...")
    
    print(f"\nDone: {success} generated, {failed} failed")

if __name__ == "__main__":
    main()
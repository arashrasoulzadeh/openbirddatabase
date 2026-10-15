#!/usr/bin/env python3
"""Generate markdown files for bird species from merged data."""

import re
import sys
import yaml
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

# Add _scripts to path
sys.path.insert(0, str(Path(__file__).parent))

# Import crosswalk functions
from crosswalk import load_birdnet, build_master_taxonomy, build_crosswalk_dicts

# BirdLife marks some Critically Endangered species "Possibly Extinct" (PE) or "Possibly Extinct in the Wild" (PEW),
# written like "CR (PE)". The status stays a plain IUCN category; the tag is stored separately.
_IUCN_TAG = re.compile(r"^\s*([A-Z]{2})\s*\(\s*(PEW|PE)\s*\)\s*$")


def parse_iucn_category(raw):
    """'CR (PE)' -> ('CR', 'PE'); 'LC' -> ('LC', None)."""
    text = str(raw).strip()
    match = _IUCN_TAG.match(text)
    return (match.group(1), match.group(2)) if match else (text, None)


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
    import pandas as pd
    data = {}
    
    # BirdNET (primary)
    print("Loading BirdNET...")
    birdnet_df = load_birdnet()
    data['birdnet'] = birdnet_df.set_index('scientific_name').to_dict('index')
    print(f"  {len(data['birdnet'])} species")
    
    # eBird taxonomy (for family/order lookup)
    ebird_file = DATA_DIR / "ebird" / "ebird_taxonomy.csv"
    if ebird_file.exists():
        print("Loading eBird taxonomy...")
        df = pd.read_csv(ebird_file)
        # Filter to species only
        df = df[df['CATEGORY'] == 'species']
        data['ebird_taxonomy'] = df.set_index('SCIENTIFIC_NAME')[['ORDER', 'FAMILY_SCI_NAME', 'TAXON_ORDER']].to_dict('index')
        print(f"  {len(data['ebird_taxonomy'])} species")
    else:
        print("eBird taxonomy not found")
        data['ebird_taxonomy'] = {}
    
    # AVONICHE (foraging niches)
    avoniche_dir = DATA_DIR / "avoniche"
    avoniche_file = avoniche_dir / "Avoniche4_AviList_2025.csv"
    if avoniche_file.exists() and avoniche_file.stat().st_size > 1000:
        print("Loading AVONICHE...")
        df = pd.read_csv(avoniche_file)
        # Try different possible column names for scientific name
        sci_col = None
        for col in ['Scientific_Name', 'ScientificName', 'scientific_name', 'Species', 'species']:
            if col in df.columns:
                sci_col = col
                break
        if sci_col:
            data['avoniche'] = df.set_index(sci_col).to_dict('index')
            print(f"  {len(data['avoniche'])} species")
        else:
            print(f"  AVONICHE file missing expected column, columns: {list(df.columns)}")
            data['avoniche'] = {}
    else:
        print("AVONICHE not found - will use empty foraging niches")
        data['avoniche'] = {}
    
    # BIRDBASE (78 traits)
    birdbase_dir = DATA_DIR / "birdbase"
    birdbase_files = list(birdbase_dir.glob("*.xlsx"))
    if birdbase_files:
        print("Loading BIRDBASE...")
        df = pd.read_excel(birdbase_files[0], sheet_name="Data", header=1)
        # Use scientific name (Latin) as index - column 'Latin (BirdLife > IOC > Clements>AviList)'
        sci_col = 'Latin (BirdLife > IOC > Clements>AviList)'
        data['birdbase'] = df.set_index(sci_col).to_dict('index')
        print(f"  {len(data['birdbase'])} species")
    else:
        print("BIRDBASE not found - will use empty traits")
        data['birdbase'] = {}
    
    # BirdFYI (habitat, behavior details)
    birdfyi_dir = DATA_DIR / "birdfyi"
    # Could load from API or cached files
    
    return data

def build_species_record(sci_name, birdnet_data, avoniche_data, birdbase_data, ebird_taxonomy):
    """Build complete species record from all sources."""
    import pandas as pd
    
    # Start with BirdNET data
    bn = birdnet_data.get(sci_name, {})
    
    # Get taxonomy from eBird
    ebird_tax = ebird_taxonomy.get(sci_name, {})
    order = ebird_tax.get('ORDER', 'Passeriformes')
    family = ebird_tax.get('FAMILY_SCI_NAME', 'Unknown')
    taxon_order = ebird_tax.get('TAXON_ORDER', 0)
    
    # Parse scientific name
    parts = sci_name.split(' ', 1)
    genus = parts[0] if parts else ''
    species = parts[1] if len(parts) > 1 else ''
    
    # Build record
    record = {
        # Core IDs
        'taxon_id': bn.get('birdnet_id', ''),
        'ebird_code': bn.get('ebird_code', ''),
        'gbif_key': int(bn['gbif_id']) if bn.get('gbif_id') and not pd.isna(bn['gbif_id']) else None,
        'avibase_id': bn.get('avibase_id', ''),
        'iucn_status': 'LC',  # Default, should come from BIRDBASE
        'taxon_order': float(taxon_order) if taxon_order else 0,
        
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
        'veterinary_care': '',
        'enrichment_training': ''
    }
    
    # Merge BIRDBASE data if available
    bb = birdbase_data.get(sci_name, {})
    if bb:
        record['sources'].append('BIRDBASE 2025')
        record['data_quality'] = 'High'
        # Map BIRDBASE fields to our schema
        # Morphology
        if pd.notna(bb.get('Average Mass')):
            record['morphology']['body_mass_g'] = float(bb['Average Mass'])
        if pd.notna(bb.get('Female MinMass')) or pd.notna(bb.get('Male MinMass')):
            # Use average of male/female or unsexed
            pass
        
        # Distribution
        if pd.notna(bb.get('RR')):
            record['distribution']['breeding_range'] = f"Range size: {bb['RR']}" if bb['RR'] > 0 else ""
        if pd.notna(bb.get('LAT')):
            record['distribution']['biogeographic_realms'] = [bb['RLM']] if pd.notna(bb.get('RLM')) else []
        if pd.notna(bb.get('ISL')):
            record['distribution']['island_endemic'] = bool(bb['ISL'])
        
        # Elevational
        if pd.notna(bb.get('NormMin')):
            val = bb['NormMin']
            if val == 'L' or val == 'l':
                record['habitat']['elevational_min_m'] = 0
            else:
                try:
                    record['habitat']['elevational_min_m'] = int(float(val))
                except (ValueError, TypeError):
                    pass
        if pd.notna(bb.get('NormMax')):
            val = bb['NormMax']
            if val == 'L' or val == 'l':
                record['habitat']['elevational_max_m'] = 0
            else:
                try:
                    record['habitat']['elevational_max_m'] = int(float(val))
                except (ValueError, TypeError):
                    pass
        
        # Habitat
        habitat_codes = {
            'F': 'Forest', 'BM': 'Bamboo', 'WD': 'Woodland', 'SH': 'Shrubland',
            'SV': 'Savanna', 'G': 'Grassland', 'PL': 'Plains', 'R': 'Rocky',
            'D': 'Desert', 'A': 'Artificial', 'RV': 'Riverine', 'C': 'Coastal',
            'W': 'Wetland', 'SE': 'Sea/Pelagic', 'O': 'Other'
        }
        habitat_list = []
        for code, name in habitat_codes.items():
            if pd.notna(bb.get(code)) and bb.get(code):
                habitat_list.append(name)
        if habitat_list:
            record['habitat']['habitat_types'] = habitat_list
            record['habitat']['habitat_breadth'] = len(habitat_list)
        if pd.notna(bb.get('Primary Habitat')):
            record['habitat']['primary'] = str(bb['Primary Habitat'])
        
        # Diet
        diet_mapping = {
            'invertebrates': 'IN-Wt',
            'fruit': 'FR-Wt',
            'nectar': 'NE-Wt',
            'seeds': 'SE-Wt',
            'vertebrates': 'VE-Wt',
            'fish': 'FI-Wt',
            'carrion': 'SC-Wt',
            'plant_material': 'PL-Wt'
        }
        diet_sum = 0
        for our_key, bb_key in diet_mapping.items():
            val = bb.get(bb_key)
            if pd.notna(val):
                if val == 'T' or val == 't':
                    val = 0.01  # Trace amount
                else:
                    try:
                        val = float(val)
                    except (ValueError, TypeError):
                        val = 0
                record['diet']['categories'][our_key] = val
                diet_sum += val
        if diet_sum > 0:
            record['diet']['diet_breadth'] = sum(1 for v in record['diet']['categories'].values() if v > 0)
        if pd.notna(bb.get('Primary Diet')):
            record['diet']['primary'] = str(bb['Primary Diet'])
        if pd.notna(bb.get('DB')):
            record['diet']['diet_breadth'] = int(bb['DB'])
        
        # Conservation
        if pd.notna(bb.get('2024 IUCN Red List category')):
            status, tag = parse_iucn_category(bb['2024 IUCN Red List category'])
            record['conservation']['iucn_status'] = status
            record['iucn_status'] = status
            if tag:
                record['conservation']['iucn_tag'] = tag
        
        # Behavior - Social
        social_map = {
            0: 'Solitary', 1: 'Pairs', 2: 'Pairs and family groups',
            3: 'Small groups', 4: 'Large flocks', 5: 'Colonial', 6: 'Lekking'
        }
        for i in range(1, 7):
            if pd.notna(bb.get(f'Social_{i}')) and bb.get(f'Social_{i}') == 1:
                record['behavior']['sociality'] = social_map.get(i, 'Unknown')
                break
        
        # Behavior - Migration
        if pd.notna(bb.get('Mig')) and bb.get('Mig') == 1:
            record['behavior']['migration_status'] = 'Full migrant'
            record['behavior']['movement_type'] = 'Migratory'
        elif pd.notna(bb.get('Alt')) and bb.get('Alt') == 1:
            record['behavior']['migration_status'] = 'Altitudinal migrant'
            record['behavior']['movement_type'] = 'Altitudinal'
        elif pd.notna(bb.get('Sed')) and bb.get('Sed') == 1:
            record['behavior']['migration_status'] = 'Resident'
            record['behavior']['movement_type'] = 'Sedentary'
        elif pd.notna(bb.get('Irreg')) and bb.get('Irreg') == 1:
            record['behavior']['migration_status'] = 'Nomadic'
            record['behavior']['movement_type'] = 'Nomadic'
        elif pd.notna(bb.get('Disp')) and bb.get('Disp') == 1:
            record['behavior']['movement_type'] = 'Dispersive'
        
        # Reproduction
        if pd.notna(bb.get('Clutch_Min')):
            record['reproduction']['clutch_size_min'] = int(bb['Clutch_Min'])
        if pd.notna(bb.get('Clutch_Max')):
            record['reproduction']['clutch_size_max'] = int(bb['Clutch_Max'])
        if pd.notna(bb.get('Clutch_Min')) and pd.notna(bb.get('Clutch_Max')):
            record['reproduction']['clutch_size_mean'] = (float(bb['Clutch_Min']) + float(bb['Clutch_Max'])) / 2
        if pd.notna(bb.get('Incu1')):
            record['reproduction']['incubation_days'] = int(bb['Incu1'])
        if pd.notna(bb.get('Fldg1')):
            record['reproduction']['fledging_days'] = int(bb['Fldg1'])
        if pd.notna(bb.get('Incu_Sex')):
            incu_sex = str(bb['Incu_Sex']).upper()
            if 'B' in incu_sex and ('F' in incu_sex or 'M' in incu_sex):
                record['reproduction']['parental_care'] = 'Biparental'
            elif 'B' in incu_sex:
                record['reproduction']['parental_care'] = 'Biparental'
            elif 'F' in incu_sex and 'M' in incu_sex:
                record['reproduction']['parental_care'] = 'Biparental'
            elif 'F' in incu_sex:
                record['reproduction']['parental_care'] = 'Female only'
            elif 'M' in incu_sex:
                record['reproduction']['parental_care'] = 'Male only'
            else:
                record['reproduction']['parental_care'] = 'Unknown'
        
        nest_type_map = {'SC': 'Scrape', 'CA': 'Cavity', 'PL': 'Platform', 'CU': 'Cup', 'HO': 'Hole', 'BU': 'Burrow'}
        if pd.notna(bb.get('Nest_Type')):
            record['reproduction']['nest_type'] = nest_type_map.get(str(bb['Nest_Type']), str(bb['Nest_Type']))
        nest_placement_map = {
            'G': 'Ground', 'T': 'Tree', 'W': 'Water', 'Z': 'Cliff/Crevice',
            'S': 'Shrub/Bush', 'R': 'Rock', 'B': 'Building', 'N': 'Cavity',
            'S': 'Shrub'
        }
        if pd.notna(bb.get('Nest_SBS')):
            sbs = str(bb['Nest_SBS']).split(',')
            placements = []
            for code in sbs:
                code = code.strip()
                if code in nest_placement_map:
                    placements.append(nest_placement_map[code])
                else:
                    placements.append(code)
            record['reproduction']['nest_placement'] = ', '.join(placements)
        
        # Demography
        if pd.notna(bb.get('Flightlessness')):
            record['behavior']['activity_pattern'] = 'Flightless' if str(bb['Flightlessness']) == 'Yes' else 'Diurnal'
    
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
    ebird_taxonomy = data.get('ebird_taxonomy', {})
    
    # Get species list
    if args.species:
        species_list = [args.species]
    else:
        species_list = list(birdnet_data.keys())
        
        # Filter by family/order if specified
        if args.family and ebird_taxonomy:
            species_list = [s for s in species_list 
                          if ebird_taxonomy.get(s, {}).get('FAMILY_SCI_NAME') == args.family]
        if args.order and ebird_taxonomy:
            species_list = [s for s in species_list 
                          if ebird_taxonomy.get(s, {}).get('ORDER') == args.order]
        
        if args.limit:
            species_list = species_list[:args.limit]
    
    print(f"\nProcessing {len(species_list)} species...")
    
    # Generate files
    success = 0
    failed = 0
    
    for sci_name in species_list:
        try:
            record = build_species_record(sci_name, birdnet_data, avoniche_data, birdbase_data, ebird_taxonomy)
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
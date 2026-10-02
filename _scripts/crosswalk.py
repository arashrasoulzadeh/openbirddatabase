#!/usr/bin/env python3
"""Build taxonomy crosswalk between BirdNET, eBird, BirdLife, BirdTree, GBIF."""

import json
import csv
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path("_data")
OUTPUT_DIR = Path("_data/crosswalk")
OUTPUT_DIR.mkdir(exist_ok=True)

def load_birdnet():
    """Load filtered BirdNET birds."""
    import pandas as pd
    df = pd.read_csv(DATA_DIR / "birdnet" / "birdnet_birds.csv")
    return df

def load_avoniche_crosswalks():
    """Load AVONICHE crosswalk files if available."""
    crosswalks = {}
    avoniche_dir = DATA_DIR / "avoniche"
    
    for fname in ["Crosswalk_sp1_sp2.csv", "Crosswalk_sp1_sp3.csv"]:
        fpath = avoniche_dir / fname
        if fpath.exists():
            import pandas as pd
            crosswalks[fname] = pd.read_csv(fpath)
            print(f"Loaded {fname}: {len(crosswalks[fname])} rows")
        else:
            print(f"Missing: {fname}")
    
    return crosswalks

def load_birdbase():
    """Load BIRDBASE data if available."""
    birdbase_dir = DATA_DIR / "birdbase"
    xlsx_files = list(birdbase_dir.glob("*.xlsx"))
    if not xlsx_files:
        print("BIRDBASE not found - manual download required")
        return None
    
    import pandas as pd
    # Read main traits sheet
    df = pd.read_excel(xlsx_files[0], sheet_name="Traits")
    print(f"Loaded BIRDBASE: {len(df)} rows")
    return df

def build_master_taxonomy(birdnet_df):
    """Build master species list from BirdNET as primary taxonomy."""
    # Select key columns
    cols = [
        'birdnet_id', 'scientific_name', 'common_name', 'common_name_fa',
        'ebird_code', 'gbif_id', 'ncbi_id', 'avibase_id', 'birdlife_id',
        'ml_taxon_code', 'xc_name', 'inat_id', 'observationorg_id', 'wikidata_qid',
        'taxon_group', 'record_type', 'observations_count',
        'description_source', 'metadata_quality_score', 'metadata_quality_flags',
        'image_url', 'image_author', 'image_license', 'image_source'
    ]
    
    # Add all language columns
    lang_cols = [c for c in birdnet_df.columns if c.startswith('common_name_')]
    cols.extend([c for c in lang_cols if c not in cols])
    
    master = birdnet_df[cols].copy()
    
    # Add taxonomy fields (will be filled from eBird/BirdLife APIs)
    master['order'] = ''
    master['family'] = ''
    master['genus'] = ''
    master['species_epithet'] = ''
    
    # Parse scientific name
    master[['genus', 'species_epithet']] = master['scientific_name'].str.split(' ', n=1, expand=True)
    
    return master

def build_crosswalk_dicts(master_df):
    """Build lookup dictionaries for crosswalking."""
    import pandas as pd
    crosswalks = {
        'by_birdnet_id': {},
        'by_scientific_name': {},
        'by_ebird_code': {},
        'by_gbif_id': {},
        'by_avibase_id': {},
        'by_birdlife_id': {},
    }
    
    for _, row in master_df.iterrows():
        idx = row.name
        
        if pd.notna(row['birdnet_id']):
            crosswalks['by_birdnet_id'][str(row['birdnet_id'])] = idx
        
        if pd.notna(row['scientific_name']):
            crosswalks['by_scientific_name'][str(row['scientific_name']).lower()] = idx
        
        if pd.notna(row['ebird_code']):
            crosswalks['by_ebird_code'][str(row['ebird_code']).lower()] = idx
        
        if pd.notna(row['gbif_id']):
            crosswalks['by_gbif_id'][int(row['gbif_id'])] = idx
        
        if pd.notna(row['avibase_id']):
            crosswalks['by_avibase_id'][str(row['avibase_id'])] = idx
        
        if pd.notna(row['birdlife_id']):
            crosswalks['by_birdlife_id'][str(row['birdlife_id'])] = idx
    
    return crosswalks

def match_avoniche(avoniche_df, crosswalks, master_df):
    """Match AVONICHE species to master taxonomy."""
    matched = 0
    unmatched = []
    
    # AVONICHE uses scientific names - try matching
    for _, row in avoniche_df.iterrows():
        sci_name = str(row.get('Scientific_Name', '')).lower()
        if sci_name in crosswalks['by_scientific_name']:
            matched += 1
        else:
            unmatched.append(sci_name)
    
    print(f"AVONICHE matched: {matched}/{len(avoniche_df)}")
    if unmatched:
        print(f"  Unmatched examples: {unmatched[:5]}")
    
    return matched, unmatched

def match_birdbase(birdbase_df, crosswalks, master_df):
    """Match BIRDBASE species to master taxonomy."""
    matched = 0
    unmatched = []
    
    # BIRDBASE uses scientific names
    for _, row in birdbase_df.iterrows():
        sci_name = str(row.get('Scientific_Name', '')).lower()
        if sci_name in crosswalks['by_scientific_name']:
            matched += 1
        else:
            unmatched.append(sci_name)
    
    print(f"BIRDBASE matched: {matched}/{len(birdbase_df)}")
    if unmatched:
        print(f"  Unmatched examples: {unmatched[:5]}")
    
    return matched, unmatched

def save_master_taxonomy(master_df):
    """Save master taxonomy to CSV and JSON."""
    # CSV
    csv_path = OUTPUT_DIR / "master_taxonomy.csv"
    master_df.to_csv(csv_path, index=False)
    print(f"Saved master taxonomy: {csv_path} ({len(master_df)} species)")
    
    # JSON (lighter version for API)
    json_cols = [
        'birdnet_id', 'scientific_name', 'common_name', 'common_name_fa',
        'ebird_code', 'gbif_id', 'order', 'family', 'genus', 'species_epithet'
    ]
    json_path = OUTPUT_DIR / "master_taxonomy.json"
    master_df[json_cols].to_json(json_path, orient='records', force_ascii=False)
    print(f"Saved master taxonomy JSON: {json_path}")
    
    # Lookup dictionaries
    crosswalks = build_crosswalk_dicts(master_df)
    for name, d in crosswalks.items():
        path = OUTPUT_DIR / f"{name}.json"
        with open(path, 'w') as f:
            json.dump(d, f, ensure_ascii=False)
        print(f"Saved {name}: {len(d)} entries")

def main():
    print("=" * 50)
    print("Building Taxonomy Crosswalk")
    print("=" * 50)
    
    # Load BirdNET (primary)
    print("\n1. Loading BirdNET taxonomy...")
    birdnet_df = load_birdnet()
    print(f"   Bird species: {len(birdnet_df)}")
    
    # Build master taxonomy
    print("\n2. Building master taxonomy...")
    master_df = build_master_taxonomy(birdnet_df)
    
    # Load AVONICHE crosswalks
    print("\n3. Loading AVONICHE crosswalks...")
    avoniche_crosswalks = load_avoniche_crosswalks()
    
    # Load BIRDBASE
    print("\n4. Loading BIRDBASE...")
    birdbase_df = load_birdbase()
    
    # Build crosswalk dicts
    print("\n5. Building crosswalk dictionaries...")
    crosswalks = build_crosswalk_dicts(master_df)
    print(f"   by_birdnet_id: {len(crosswalks['by_birdnet_id'])}")
    print(f"   by_scientific_name: {len(crosswalks['by_scientific_name'])}")
    print(f"   by_ebird_code: {len(crosswalks['by_ebird_code'])}")
    print(f"   by_gbif_id: {len(crosswalks['by_gbif_id'])}")
    print(f"   by_avibase_id: {len(crosswalks['by_avibase_id'])}")
    print(f"   by_birdlife_id: {len(crosswalks['by_birdlife_id'])}")
    
    # Try matching if data available
    if avoniche_crosswalks.get('Crosswalk_sp1_sp2.csv') is not None:
        print("\n6. Matching AVONICHE...")
        # This would need the actual AVONICHE data files
        pass
    
    if birdbase_df is not None:
        print("\n6. Matching BIRDBASE...")
        match_birdbase(birdbase_df, crosswalks, master_df)
    
    # Save
    print("\n7. Saving outputs...")
    save_master_taxonomy(master_df)
    
    print("\nDone!")

if __name__ == "__main__":
    main()
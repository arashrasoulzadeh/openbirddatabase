#!/usr/bin/env python3
"""Create unified exports (CSV, XLSX, SQL) of all birds with all data."""

import json
import yaml
import sqlite3
import pandas as pd
from pathlib import Path
from tqdm import tqdm

BIRDS_DIR = Path("birds")
INDEX_DIR = Path("_index")
EXPORT_DIR = Path("exports")
EXPORT_DIR.mkdir(exist_ok=True)

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

def flatten_record(fm, prefix=''):
    """Flatten nested dict for CSV export."""
    flat = {}
    for key, value in fm.items():
        new_key = f"{prefix}{key}" if prefix else key
        if isinstance(value, dict):
            flat.update(flatten_record(value, f"{new_key}_"))
        elif isinstance(value, list):
            flat[new_key] = '; '.join(str(v) for v in value)
        else:
            flat[new_key] = value
    return flat

def create_exports():
    """Create CSV, XLSX, and SQL exports."""
    print("Scanning species files...")
    files = list(BIRDS_DIR.glob("**/*.md"))
    print(f"Found {len(files)} species files")
    
    records = []
    
    for filepath in tqdm(files, desc="Processing"):
        fm = parse_frontmatter(filepath)
        if not fm:
            continue
        
        # Flatten for CSV/XLSX
        flat = flatten_record(fm)
        flat['file_path'] = str(filepath)
        records.append(flat)
    
    if not records:
        print("No valid records found!")
        return
    
    # Create DataFrame
    df = pd.DataFrame(records)
    print(f"DataFrame shape: {df.shape}")
    
    # CSV export
    csv_path = EXPORT_DIR / "all_birds.csv"
    df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"CSV saved: {csv_path}")
    
    # XLSX export (multiple sheets)
    xlsx_path = EXPORT_DIR / "all_birds.xlsx"
    with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
        # Main sheet with all data
        df.to_excel(writer, sheet_name='All_Birds', index=False)
        
        # Summary sheets
        if 'taxonomy_order' in df.columns:
            order_summary = df.groupby('taxonomy_order').size().reset_index(name='species_count')
            order_summary.to_excel(writer, sheet_name='By_Order', index=False)
        
        if 'taxonomy_family' in df.columns:
            family_summary = df.groupby('taxonomy_family').size().reset_index(name='species_count')
            family_summary.to_excel(writer, sheet_name='By_Family', index=False)
        
        if 'conservation_iucn_status' in df.columns:
            iucn_summary = df.groupby('conservation_iucn_status').size().reset_index(name='species_count')
            iucn_summary.to_excel(writer, sheet_name='By_IUCN', index=False)
        
        if 'diet_primary' in df.columns:
            diet_summary = df.groupby('diet_primary').size().reset_index(name='species_count')
            diet_summary.to_excel(writer, sheet_name='By_Diet', index=False)
        
        if 'habitat_primary' in df.columns:
            habitat_summary = df.groupby('habitat_primary').size().reset_index(name='species_count')
            habitat_summary.to_excel(writer, sheet_name='By_Habitat', index=False)
    
    print(f"XLSX saved: {xlsx_path}")
    
    # SQL export
    sql_path = EXPORT_DIR / "all_birds.sqlite"
    conn = sqlite3.connect(sql_path)
    
    # Main table
    df.to_sql('birds', conn, if_exists='replace', index=False)
    
    # Create indexes for common queries
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scientific ON birds(names_scientific)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_order ON birds(taxonomy_order)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_family ON birds(taxonomy_family)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_iucn ON birds(conservation_iucn_status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_diet ON birds(diet_primary)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_habitat ON birds(habitat_primary)")
    
    # Create view for easy querying
    cursor.execute("DROP VIEW IF EXISTS bird_summary")
    cursor.execute("""
        CREATE VIEW bird_summary AS
        SELECT 
            names_scientific,
            names_fa,
            names_en,
            taxonomy_order,
            taxonomy_family,
            taxonomy_genus,
            taxonomy_species,
            conservation_iucn_status,
            diet_primary,
            habitat_primary,
            morphology_body_mass_g,
            behavior_migration_status
        FROM birds
    """)
    
    # Also export a compact CSV for quick loading
    compact_cols = [
        'taxon_id', 'ebird_code', 'gbif_key',
        'names_scientific', 'names_fa', 'names_en',
        'taxonomy_order', 'taxonomy_family', 'taxonomy_genus', 'taxonomy_species',
        'conservation_iucn_status', 'diet_primary', 'habitat_primary',
        'behavior_migration_status', 'morphology_body_mass_g',
        'data_quality', 'file_path'
    ]
    available_cols = [c for c in compact_cols if c in df.columns]
    compact_df = df[available_cols]
    compact_path = EXPORT_DIR / "all_birds_compact.csv"
    compact_df.to_csv(compact_path, index=False, encoding='utf-8')
    print(f"Compact CSV saved: {compact_path}")

    # SQL dump (.sql file) - must be before conn.close()
    sql_dump_path = EXPORT_DIR / "all_birds.sql"
    with open(sql_dump_path, 'w', encoding='utf-8') as f:
        for line in conn.iterdump():
            f.write(f"{line}\n")
    print(f"SQL dump saved: {sql_dump_path}")

    # YAML export (compact)
    yaml_path = EXPORT_DIR / "all_birds.yaml"
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(compact_df.to_dict('records'), f, allow_unicode=True, sort_keys=False, indent=2)
    print(f"YAML saved: {yaml_path}")

    conn.commit()
    conn.close()
    print(f"SQLite saved: {sql_path}")

    print("\nExport complete!")
    print(f"Files created in {EXPORT_DIR}/:")
    for f in sorted(EXPORT_DIR.glob("*")):
        print(f"  {f.name} ({f.stat().st_size / 1024 / 1024:.1f} MB)")

if __name__ == "__main__":
    create_exports()
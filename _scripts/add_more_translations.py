#!/usr/bin/env python3
"""Add more language translations from BirdNET to species files."""

import pandas as pd
import yaml
from pathlib import Path

BIRDS_DIR = Path("birds")
BIRDNET_CSV = Path("_data/birdnet/birdnet_taxonomy.csv")

LANGUAGE_COLUMNS = {
    'common_name_es': 'es',      # Spanish
    'common_name_fr': 'fr',      # French
    'common_name_de': 'de',      # German
    'common_name_pt': 'pt',      # Portuguese
    'common_name_ru': 'ru',      # Russian
    'common_name_ja': 'ja',      # Japanese
    'common_name_zh': 'zh',      # Chinese
    'common_name_nl': 'nl',      # Dutch
    'common_name_pl': 'pl',      # Polish
    'common_name_it': 'it',      # Italian
    'common_name_tr': 'tr',      # Turkish
    'common_name_ko': 'ko',      # Korean
    'common_name_ar': 'ar',      # Arabic (if available)
    'common_name_he': 'he',      # Hebrew
    'common_name_hi': 'hi',      # Hindi
    'common_name_id': 'id',      # Indonesian
    'common_name_ms': 'ms',      # Malay
    'common_name_th': 'th',      # Thai
    'common_name_vi': 'vi',      # Vietnamese
}

def parse_frontmatter(filepath):
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
    new_fm = yaml.dump(fm, allow_unicode=True, sort_keys=False, default_flow_style=False)
    new_content = f'---\n{new_fm}---\n{body_content}'
    filepath.write_text(new_content, encoding='utf-8')

def load_birdnet_translations():
    if not BIRDNET_CSV.exists():
        return {}
    
    print("Loading BirdNET taxonomy...")
    df = pd.read_csv(BIRDNET_CSV)
    df = df[(df['taxon_group'] == 'Aves') & (df['record_type'] == 'species')]
    
    translations = {code: {} for code in LANGUAGE_COLUMNS.values()}
    
    for _, row in df.iterrows():
        sci_name = row['scientific_name']
        for col, lang_code in LANGUAGE_COLUMNS.items():
            if col in df.columns:
                name = row.get(col)
                if pd.notna(name) and name.strip():
                    translations[lang_code][sci_name] = name.strip()
    
    for lang, names in translations.items():
        print(f"  {lang}: {len(names)} names")
    
    return translations

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Add more translations from BirdNET")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument("--languages", nargs="+", help="Specific languages to add")
    args = parser.parse_args()
    
    if args.dry_run:
        print("DRY RUN MODE")
    
    all_translations = load_birdnet_translations()
    
    if args.languages:
        translations = {k: v for k, v in all_translations.items() if k in args.languages}
    else:
        translations = all_translations
    
    if not any(translations.values()):
        return
    
    total_updated = 0
    stats = {lang: {'updated': 0, 'already': 0, 'missing': 0} for lang in translations}
    
    species_files = list(BIRDS_DIR.glob("**/*.md"))
    print(f"Scanning {len(species_files)} species files...")
    
    for filepath in species_files:
        fm, content = parse_frontmatter(filepath)
        if not fm:
            continue
        
        sci_name = fm.get('names', {}).get('scientific', '')
        if not sci_name:
            continue
        
        file_updated = False
        
        for lang_code, lang_data in translations.items():
            current = fm.get('names', {}).get(lang_code, '').strip()
            birdnet_name = lang_data.get(sci_name, '').strip()
            
            if current:
                stats[lang_code]['already'] += 1
            elif birdnet_name:
                if args.dry_run:
                    print(f"  Would add {lang_code}: {sci_name} = '{birdnet_name}'")
                else:
                    if 'names' not in fm:
                        fm['names'] = {}
                    fm['names'][lang_code] = birdnet_name
                    file_updated = True
                    stats[lang_code]['updated'] += 1
            else:
                stats[lang_code]['missing'] += 1
        
        if file_updated and not args.dry_run:
            parts = content.split('---', 2)
            body = parts[2] if len(parts) >= 3 else ''
            write_frontmatter(filepath, fm, body)
            total_updated += 1
    
    if args.dry_run:
        for lang, s in stats.items():
            print(f"  {lang}: would update {s['updated']}, already has {s['already']}, missing {s['missing']}")
    else:
        print(f"\nUpdated {total_updated} species files with new translations")
        for lang, s in stats.items():
            if s['updated'] > 0:
                print(f"  {lang}: added {s['updated']} translations")

if __name__ == "__main__":
    main()
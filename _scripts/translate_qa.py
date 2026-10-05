#!/usr/bin/env python3
"""Persian translation QA workflow - review and improve BirdNET Persian translations."""

import json
import yaml
from pathlib import Path
import pandas as pd

BIRDS_DIR = Path("birds")
TRANSLATIONS_DIR = Path("translations/fa")
INDEX_DIR = Path("_index")

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

def load_birdnet_persian():
    """Load BirdNET Persian names from CSV."""
    csv_path = Path("_data/birdnet/birdnet_taxonomy.csv")
    if not csv_path.exists():
        return {}
    
    df = pd.read_csv(csv_path)
    # Filter to birds only
    df = df[(df['taxon_group'] == 'Aves') & (df['record_type'] == 'species')]
    
    persian_names = {}
    for _, row in df.iterrows():
        sci_name = row['scientific_name']
        fa_name = row.get('common_name_fa')
        if pd.notna(fa_name) and fa_name.strip():
            persian_names[sci_name] = fa_name.strip()
    
    return persian_names

def scan_missing_persian():
    """Find species missing Persian translations."""
    birdnet_fa = load_birdnet_persian()
    missing = []
    has_fa = 0
    
    files = list(Path("birds").glob("**/*.md"))
    
    for filepath in files:
        fm = parse_frontmatter(filepath)
        if not fm:
            continue
        
        sci_name = fm.get('names', {}).get('scientific', '')
        fa_name = fm.get('names', {}).get('fa', '')
        
        if not fa_name or not fa_name.strip():
            birdnet_name = birdnet_fa.get(sci_name, '')
            missing.append({
                'file': str(filepath),
                'scientific': sci_name,
                'birdnet_fa': birdnet_name,
                'current_fa': fa_name,
                'suggested_fa': birdnet_name
            })
        else:
            has_fa += 1
    
    return missing, has_fa, birdnet_fa

def scan_different_persian(birdnet_fa):
    """Find species where our Persian differs from BirdNET."""
    different = []
    
    files = list(Path("birds").glob("**/*.md"))
    
    for filepath in files:
        fm = parse_frontmatter(filepath)
        if not fm:
            continue
        
        sci_name = fm.get('names', {}).get('scientific', '')
        our_fa = fm.get('names', {}).get('fa', '').strip()
        birdnet_name = birdnet_fa.get(sci_name, '').strip()
        
        if our_fa and birdnet_name and our_fa != birdnet_name:
            different.append({
                'file': str(filepath),
                'scientific': sci_name,
                'our_fa': our_fa,
                'birdnet_fa': birdnet_name
            })
    
    return different

def create_review_report():
    """Generate a review report for Persian translations."""
    print("Loading BirdNET Persian names...")
    birdnet_fa = load_birdnet_persian()
    print(f"BirdNET has {len(birdnet_fa)} Persian names")
    
    print("\nScanning for missing Persian...")
    missing, has_fa, _ = scan_missing_persian()
    print(f"Species with Persian: {has_fa}")
    print(f"Species missing Persian: {len(missing)}")
    
    print("\nScanning for different Persian...")
    different = scan_different_persian({k: v for k, v in load_birdnet_persian().items()})
    print(f"Species with different Persian: {len(different)}")
    
    # Save reports
    EXPORT_DIR = Path("exports")
    EXPORT_DIR.mkdir(exist_ok=True)
    
    if missing:
        missing_df = pd.DataFrame(missing)
        missing_df.to_csv("exports/persian_missing.csv", index=False, encoding='utf-8')
        print(f"\nMissing Persian saved to exports/persian_missing.csv")
    
    if different:
        diff_df = pd.DataFrame(different)
        diff_df.to_csv("exports/persian_different.csv", index=False, encoding='utf-8')
        print(f"Different Persian saved to exports/persian_different.csv")
    
    # Summary
    total_species = has_fa + len(missing)
    coverage = (has_fa / total_species * 100) if total_species > 0 else 0
    print(f"\nPersian coverage: {coverage:.1f}% ({has_fa}/{total_species})")
    
    # Show some examples of missing
    if missing:
        print("\nExample missing Persian (first 10):")
        for m in missing[:10]:
            print(f"  {m['scientific']}: BirdNET='{m['birdnet_fa']}'")
    
    # Show some examples of different
    if different:
        print("\nExample different Persian (first 10):")
        for d in different[:10]:
            print(f"  {d['scientific']}: Ours='{d['our_fa']}' vs BirdNET='{d['birdnet_fa']}'")

def apply_birdnet_persian():
    """Apply BirdNET Persian names where missing."""
    birdnet_fa = load_birdnet_persian()
    updated = 0
    
    files = list(Path("birds").glob("**/*.md"))
    
    for filepath in files:
        fm = parse_frontmatter(filepath)
        if not fm:
            continue
        
        sci_name = fm.get('names', {}).get('scientific', '')
        current_fa = fm.get('names', {}).get('fa', '').strip()
        birdnet_name = birdnet_fa.get(sci_name, '').strip()
        
        if not current_fa and birdnet_name:
            # Update the file
            content = filepath.read_text(encoding='utf-8')
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    # Replace in frontmatter
                    fm_part = parts[1]
                    new_fm = fm_part.replace(
                        'fa: ""',
                        f'fa: "{birdnet_name}"'
                    ).replace(
                        "fa: ''",
                        f"fa: '{birdnet_name}'"
                    )
                    # If fa key doesn't exist, add it after 'fa:'
                    if 'fa:' not in fm_part:
                        # Add after en:
                        new_fm = new_fm.replace(
                            'en: "',
                            f'en: "{fm.get("names", {}).get("en", "")}"\n  fa: "{birdnet_name}"\n  en: "'
                        )
                    
                    new_content = '---' + new_fm + '---' + parts[2]
                    filepath.write_text(new_content, encoding='utf-8')
                    updated += 1
    
    print(f"Updated {updated} species with BirdNET Persian names")
    return updated

def create_translation_template():
    """Create a template for manual translation review."""
    birdnet_fa = load_birdnet_persian()
    missing, has_fa, _ = scan_missing_persian()
    
    template = {
        "metadata": {
            "total_species": has_fa + len(missing),
            "has_persian": has_fa,
            "missing_persian": len(missing),
            "birdnet_available": len(load_birdnet_persian())
        },
        "translations": {}
    }
    
    for m in missing[:100]:  # First 100 for template
        template["translations"][m['scientific']] = {
            "birdnet_suggestion": m['birdnet_fa'],
            "reviewed": False,
            "reviewer": "",
            "approved_fa": "",
            "notes": ""
        }
    
    with open("exports/persian_review_template.json", "w", encoding='utf-8') as f:
        json.dump(template, f, ensure_ascii=False, indent=2)
    
    print(f"Review template saved to exports/persian_review_template.json")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Persian translation QA tools")
    parser.add_argument("--report", action="store_true", help="Generate review report")
    parser.add_argument("--apply-birdnet", action="store_true", help="Apply BirdNET Persian names where missing")
    parser.add_argument("--template", action="store_true", help="Create review template")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    args = parser.parse_args()
    
    if args.report:
        create_review_report()
    elif args.apply_birdnet:
        if args.dry_run:
            print("DRY RUN: Would apply BirdNET Persian names where missing")
            missing, _, _ = scan_missing_persian()
            birdnet_fa = load_birdnet_persian()
            for m in missing[:20]:
                print(f"  {m['scientific']}: '{m['birdnet_fa']}'")
            print(f"... and {len(missing) - 20} more")
        else:
            apply_birdnet_persian()
    elif args.template:
        create_translation_template()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
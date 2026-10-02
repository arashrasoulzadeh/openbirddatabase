#!/usr/bin/env python3
"""Commit a single species file to git with conventional commit message."""

import subprocess
import sys
from pathlib import Path
import yaml

def get_frontmatter(filepath):
    """Extract frontmatter from markdown file."""
    content = filepath.read_text(encoding='utf-8')
    if not content.startswith('---'):
        return {}
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}
    try:
        return yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return {}

def build_commit_message(filepath):
    """Build conventional commit message from species data."""
    fm = get_frontmatter(filepath)
    
    # Get taxonomy path
    rel_path = filepath.relative_to(Path("birds"))
    order = rel_path.parts[0] if len(rel_path.parts) > 1 else ""
    family = rel_path.parts[1] if len(rel_path.parts) > 2 else ""
    species_file = rel_path.name
    
    # Get identifiers
    taxon_id = fm.get('taxon_id', 'unknown')
    ebird_code = fm.get('ebird_code', 'unknown')
    gbif_key = fm.get('gbif_key', 'unknown')
    
    # Get names
    names = fm.get('names', {})
    sci_name = names.get('scientific', 'Unknown')
    common_name = names.get('en', names.get('fa', 'Unknown'))
    
    # Get sources
    sources = fm.get('sources', [])
    sources_str = ", ".join(sources) if sources else "Unknown"
    
    # Get quality
    quality = fm.get('data_quality', 'Unknown')
    
    # Build message
    subject = f"add {sci_name} ({common_name})"
    if order and family:
        subject += f" - {order.title()}/{family.title()}"
    
    body_lines = [
        f"Taxon IDs: BirdNET={taxon_id}, eBird={ebird_code}, GBIF={gbif_key}",
        f"Sources: {sources_str}",
        f"Quality: {quality}",
    ]
    
    # Add languages
    lang_count = len([k for k in names.keys() if k not in ['scientific', 'fa', 'en']])
    if lang_count > 0:
        body_lines.append(f"Languages: fa, en, +{lang_count} more")
    
    body = "\n".join(body_lines)
    return f"feat(birds): {subject}\n\n{body}"

def commit_file(filepath, message=None, dry_run=False):
    """Add and commit a single file."""
    if not filepath.exists():
        print(f"Error: {filepath} does not exist")
        return False
    
    if message is None:
        message = build_commit_message(filepath)
    
    # Stage the file
    result = subprocess.run(["git", "add", str(filepath)], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Git add failed: {result.stderr}")
        return False
    
    if dry_run:
        print(f"Would commit: {filepath}")
        print(f"Message:\n{message}")
        # Unstage
        subprocess.run(["git", "reset", "HEAD", str(filepath)], capture_output=True)
        return True
    
    # Commit
    result = subprocess.run(["git", "commit", "-m", message], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Git commit failed: {result.stderr}")
        return False
    
    print(f"Committed: {filepath}")
    return True

def commit_all(pattern="**/*.md", dry_run=False):
    """Commit all matching species files."""
    files = list(Path("birds").glob(pattern))
    print(f"Found {len(files)} files to commit")
    
    for filepath in files:
        commit_file(filepath, dry_run=dry_run)
    
    print("Done")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Commit species files to git")
    parser.add_argument("files", nargs="*", help="Specific files to commit")
    parser.add_argument("--all", action="store_true", help="Commit all species files")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be committed")
    parser.add_argument("--message", "-m", help="Custom commit message")
    args = parser.parse_args()
    
    if args.files:
        for f in args.files:
            commit_file(Path(f), args.message, args.dry_run)
    elif args.all:
        commit_all(dry_run=args.dry_run)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
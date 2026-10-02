#!/usr/bin/env python3
"""Validate bird species markdown files against JSON schema."""

import json
import yaml
import sys
from pathlib import Path
import jsonschema
from jsonschema import validate
from tqdm import tqdm

SCHEMA_DIR = Path("_schemas")
BIRDS_DIR = Path("birds")

def load_schema(name):
    """Load JSON schema."""
    with open(SCHEMA_DIR / f"{name}.schema.json") as f:
        return json.load(f)

def parse_frontmatter(filepath):
    """Extract YAML frontmatter from markdown file."""
    content = filepath.read_text(encoding='utf-8')
    if not content.startswith('---'):
        return None, "No frontmatter delimiter"
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        return None, "Invalid frontmatter format"
    
    try:
        fm = yaml.safe_load(parts[1])
        return fm, None
    except yaml.YAMLError as e:
        return None, f"YAML parse error: {e}"

def validate_file(filepath, schema, verbose=False):
    """Validate a single markdown file."""
    fm, error = parse_frontmatter(filepath)
    if error:
        return False, error
    
    try:
        validate(instance=fm, schema=schema)
        return True, None
    except jsonschema.ValidationError as e:
        return False, f"Validation error: {e.message} at {' -> '.join(str(p) for p in e.path)}"
    except jsonschema.SchemaError as e:
        return False, f"Schema error: {e.message}"

def validate_all(schema_name="bird-attributes", pattern="**/*.md", verbose=False):
    """Validate all markdown files."""
    schema = load_schema(schema_name)
    files = list(BIRDS_DIR.glob(pattern))
    
    if not files:
        print(f"No files found matching {pattern}")
        return 0, 0
    
    print(f"Validating {len(files)} files against {schema_name}.schema.json...")
    
    passed = 0
    failed = 0
    errors = []
    
    for filepath in tqdm(files, desc="Validating"):
        ok, error = validate_file(filepath, schema, verbose)
        if ok:
            passed += 1
        else:
            failed += 1
            errors.append((filepath, error))
    
    print(f"\nResults: {passed} passed, {failed} failed")
    
    if errors and verbose:
        print("\nErrors:")
        for filepath, error in errors[:20]:
            print(f"  {filepath}: {error}")
        if len(errors) > 20:
            print(f"  ... and {len(errors) - 20} more")
    
    return passed, failed

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Validate bird markdown files")
    parser.add_argument("files", nargs="*", help="Specific files to validate")
    parser.add_argument("--schema", default="bird-attributes", help="Schema name")
    parser.add_argument("--all", action="store_true", help="Validate all files")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show error details")
    args = parser.parse_args()
    
    if args.files:
        schema = load_schema(args.schema)
        for f in args.files:
            ok, error = validate_file(Path(f), schema, args.verbose)
            status = "PASS" if ok else "FAIL"
            print(f"{status}: {f}")
            if error:
                print(f"  {error}")
    elif args.all:
        passed, failed = validate_all(args.schema, verbose=args.verbose)
        sys.exit(1 if failed > 0 else 0)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
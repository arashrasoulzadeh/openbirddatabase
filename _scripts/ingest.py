#!/usr/bin/env python3
"""Main ingestion pipeline - orchestrates the full data processing."""

import sys
from pathlib import Path

# Add _scripts to path
sys.path.insert(0, str(Path(__file__).parent))

def run_download():
    """Run download script."""
    import subprocess
    print("Running download...")
    result = subprocess.run([sys.executable, "_scripts/download.py"], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode == 0

def run_crosswalk():
    """Run crosswalk script."""
    import subprocess
    print("Running crosswalk...")
    result = subprocess.run([sys.executable, "_scripts/crosswalk.py"], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode == 0

def run_generate(family=None, order=None, dry_run=False):
    """Run markdown generation."""
    import subprocess
    cmd = [sys.executable, "_scripts/generate_md.py"]
    if family:
        cmd.extend(["--family", family])
    if order:
        cmd.extend(["--order", order])
    if dry_run:
        cmd.append("--dry-run")
    
    print(f"Running generate: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode == 0

def run_validate(pattern="**/*.md"):
    """Run validation."""
    import subprocess
    print("Running validation...")
    result = subprocess.run(
        [sys.executable, "_scripts/validate.py", "--all", "--schema", "bird-attributes"],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode == 0

def run_commit(pattern="**/*.md", dry_run=False):
    """Run git commit."""
    import subprocess
    cmd = [sys.executable, "_scripts/commit.py", "--all"]
    if dry_run:
        cmd.append("--dry-run")
    
    print("Running commit...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode == 0

def run_index():
    """Run search index generation."""
    import subprocess
    print("Running index generation...")
    result = subprocess.run([sys.executable, "_scripts/index.py"], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode == 0

def main():
    import argparse
    parser = argparse.ArgumentParser(description="OpenBird ingestion pipeline")
    parser.add_argument("stage", choices=[
        "download", "crosswalk", "generate", "validate", "commit", "index", "all"
    ], help="Pipeline stage to run")
    parser.add_argument("--family", help="Filter by family (for generate)")
    parser.add_argument("--order", help="Filter by order (for generate)")
    parser.add_argument("--dry-run", action="store_true", help="Dry run for generate/commit")
    parser.add_argument("--skip-download", action="store_true", help="Skip download stage")
    parser.add_argument("--skip-crosswalk", action="store_true", help="Skip crosswalk stage")
    
    args = parser.parse_args()
    
    stages = {
        "download": run_download,
        "crosswalk": run_crosswalk,
        "generate": lambda: run_generate(args.family, args.order, args.dry_run),
        "validate": run_validate,
        "commit": lambda: run_commit(dry_run=args.dry_run),
        "index": run_index,
    }
    
    if args.stage == "all":
        # Run full pipeline
        steps = ["download", "crosswalk", "generate", "validate", "commit", "index"]
        if args.skip_download:
            steps.remove("download")
        if args.skip_crosswalk:
            steps.remove("crosswalk")
        
        for step in steps:
            print(f"\n{'='*50}")
            print(f"STAGE: {step.upper()}")
            print(f"{'='*50}")
            
            if step == "generate":
                ok = run_generate(args.family, args.order, args.dry_run)
            elif step == "commit":
                ok = run_commit(dry_run=args.dry_run)
            else:
                ok = stages[step]()
            
            if not ok:
                print(f"\nERROR: Stage '{step}' failed!")
                sys.exit(1)
        
        print("\n✓ Full pipeline completed successfully!")
    else:
        ok = stages[args.stage]()
        sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
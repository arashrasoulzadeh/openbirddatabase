#!/usr/bin/env python3
"""Download AVONICHE data - opens browser for manual download, then auto-integrates."""

import webbrowser
import time
import sys
from pathlib import Path

AVONICHE_DIR = Path("_data/avoniche")
REQUIRED_FILES = [
    "Avoniche4_AviList_2025.csv",
    "Avoniche1_BirdLife_2020.csv",
    "Avoniche2_eBird_2021.csv",
    "Avoniche3_BirdTree_2012.csv",
    "Crosswalk_sp1_sp2.csv",
    "Crosswalk_sp1_sp3.csv",
    "Avoniche_metadata.xlsx",
    "Avoniche_Pigot2020_match.csv",
    "README.md",
]

DRYAD_URL = "https://datadryad.org/dataset/doi:10.5061/dryad.1zcrjdg56"

def check_files():
    """Check which files are present and valid."""
    results = {}
    for f in REQUIRED_FILES:
        path = Path("_data/avoniche") / f
        if path.exists() and path.stat().st_size > 1000:
            # Check not HTML
            try:
                with open(path, 'rb') as f:
                    header = f.read(200)
                    if b'<!DOCTYPE html>' in header or b'<html' in header:
                        results[f] = "html_challenge"
                    else:
                        results[f] = "ok"
            except:
                results[f] = "error"
        else:
            results[f] = "missing"
    return results

def print_status():
    results = check_files()
    print("\n📊 File Status:")
    for f, status in results.items():
        icons = {"ok": "✅", "missing": "❌", "html_challenge": "⚠️", "error": "💥"}
        print(f"  {icons.get(status, '❓')} {f}: {status}")
    
    ok_count = sum(1 for s in results.values() if s == "ok")
    print(f"\nProgress: {ok_count}/{len(REQUIRED_FILES)} files ready")
    return results

def open_browser():
    print(f"\n🌐 Opening Dryad download page: {DRYAD_URL}")
    webbrowser.open(DRYAD_URL)
    print("\n📋 Instructions:")
    print("  1. Click 'Download' on each of the 9 files")
    print("  2. Save all files to: _data/avoniche/")
    print("  3. Files will be auto-detected and integrated!")

def wait_for_files():
    print("\n⏳ Waiting for files to appear in _data/avoniche/...")
    print("   (Press Ctrl+C to cancel)\n")
    
    while True:
        results = check_files()
        ok_count = sum(1 for s in results.values() if s == "ok")
        
        if ok_count == len(REQUIRED_FILES):
            print("\n🎉 All files downloaded! Starting integration...")
            return True
        
        # Show progress
        missing = [f for f, s in results.items() if s != "ok"]
        print(f"\rProgress: {ok_count}/9 ready  |  Waiting for: {', '.join(missing[:3])}{'...' if len(missing) > 3 else ''}", end="", flush=True)
        time.sleep(2)

def integrate():
    print("\n🔄 Integrating AVONICHE data...")
    import subprocess
    
    print("\n🔄 Regenerating species files with foraging niches...")
    result = subprocess.run([
        sys.executable, "_scripts/generate_md.py"
    ], capture_output=True, text=True, timeout=600)
    print(result.stdout[-500:] if result.stdout else "No output")
    
    print("\n🔄 Rebuilding search index...")
    result = subprocess.run([
        sys.executable, "_scripts/index.py"
    ], capture_output=True, text=True, timeout=60)
    print(result.stdout)
    
    print("\n🔄 Updating MeiliSearch index...")
    result = subprocess.run([
        sys.executable, "_scripts/populate_meili.py"
    ], capture_output=True, text=True, timeout=120)
    print(result.stdout)
    
    print("\n✅ Integration complete!")

def main():
    print("=" * 60)
    print("🐦 AVONICHE Data Downloader & Integrator")
    print("=" * 60)
    
    # Check current status
    results = check_files()
    ok_count = sum(1 for s in results.values() if s == "ok")
    
    if ok_count == len(REQUIRED_FILES):
        print("✅ All files already present!")
        if input("Re-run integration? (y/n): ").lower() == 'y':
            integrate()
        return
    
    print(f"\n📊 Found {ok_count}/{len(REQUIRED_FILES)} valid files")
    print("\n❌ Missing or invalid files:")
    for f, s in results.items():
        if s != "ok":
            icons = {"missing": "❌", "html_challenge": "⚠️", "error": "💥"}
            print(f"  {icons.get(s, '❓')} {f}: {s}")
    
    if input("\nOpen browser to download missing files? (y/n): ").lower() != 'y':
        print("Exiting.")
        return
    
    open_browser()
    
    if input("\nStart watching for downloads? (y/n): ").lower() == 'y':
        wait_for_files()
        integrate()
    else:
        print("\nRun this script again after downloading to integrate.")

if __name__ == "__main__":
    Path("_data/avoniche").mkdir(parents=True, exist_ok=True)
    main()
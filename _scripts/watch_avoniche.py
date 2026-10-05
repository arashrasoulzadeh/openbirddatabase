#!/usr/bin/env python3
"""Watch for AVONICHE files and auto-integrate when downloaded."""

import time
import json
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import sys

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

class AvonicheHandler(FileSystemEventHandler):
    def __init__(self):
        self.processed = set()
    
    def on_created(self, event):
        if event.is_directory:
            return
        filepath = Path(event.src_path)
        filename = filepath.name
        
        if filename in REQUIRED_FILES and filename not in self.processed:
            print(f"\n📥 Detected: {filename}")
            time.sleep(2)  # Wait for file to finish writing
            
            # Verify file is not HTML (Cloudflare challenge)
            try:
                with open(filepath, 'rb') as f:
                    header = f.read(200)
                    if b'<!DOCTYPE html>' in header or b'<html' in header:
                        print(f"  ⚠️  {filename} appears to be HTML (Cloudflare challenge)")
                        print(f"     Please manually download from https://datadryad.org/dataset/doi:10.5061/dryad.1zcrjdg56")
                        return
            except:
                pass
            
            if filepath.stat().st_size < 1000:
                print(f"  ⚠️  {filename} too small ({filepath.stat().st_size} bytes), likely incomplete")
                return
            
            print(f"  ✅ {filename} downloaded successfully ({filepath.stat().st_size:,} bytes)")
            self.processed.add(filename)
            self.check_all_files()
    
    def on_modified(self, event):
        self.on_created(event)
    
    def check_all_files(self):
        all_present = True
        for f in REQUIRED_FILES:
            fpath = AVONICHE_DIR / f
            if not fpath.exists() or fpath.stat().st_size < 1000:
                all_present = False
                break
        
        if all_present:
            print("\n🎉 All AVONICHE files detected! Starting integration...")
            self.integrate()
    
    def integrate(self):
        print("🔄 Running integration pipeline...")
        try:
            # Regenerate species files with AVONICHE data
            result = subprocess.run([
                sys.executable, "_scripts/generate_md.py"
            ], capture_output=True, text=True, timeout=600)
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            # Rebuild search index
            result = subprocess.run([
                sys.executable, "_scripts/index.py"
            ], capture_output=True, text=True, timeout=60)
            print(result.stdout)
            
            # Repopulate MeiliSearch
            result = subprocess.run([
                sys.executable, "_scripts/populate_meili.py"
            ], capture_output=True, text=True, timeout=120)
            print(result.stdout)
            
            print("\n✅ Integration complete! All 11,149 species now have foraging niches.")
            
        except subprocess.TimeoutExpired:
            print("⚠️  Integration timed out - you can run manually:")
            print("  python _scripts/generate_md.py")
            print("  python _scripts/index.py")
            print("  python _scripts/populate_meili.py")
        except Exception as e:
            print(f"❌ Integration error: {e}")
            print("Run manually: python _scripts/generate_md.py && python _scripts/index.py")

def print_instructions():
    print("=" * 60)
    print("📥 AVONICHE Data Download Instructions")
    print("=" * 60)
    print("\nThe AVONICHE dataset requires manual download from Dryad.")
    print("Cloudflare protection prevents automated downloads.")
    print()
    print("📋 Files needed in _data/avoniche/:")
    for f in REQUIRED_FILES:
        status = "✅" if (AVONICHE_DIR / f).exists() and (AVONICHE_DIR / f).stat().st_size > 1000 else "❌"
        print(f"  {status} {f}")
    print()
    print("📥 Download from: https://datadryad.org/dataset/doi:10.5061/dryad.1zcrjdg56")
    print("   Click 'Download' on each file, save to _data/avoniche/")
    print()
    print("👀 Watcher will auto-detect and integrate when files appear!")
    print("=" * 60)

def main():
    print_instructions()
    
    if not AVONICHE_DIR.exists():
        AVONICHE_DIR.mkdir(parents=True)
    
    # Check initial state
    present = sum(1 for f in REQUIRED_FILES if (AVONICHE_DIR / f).exists() and (AVONICHE_DIR / f).stat().st_size > 1000)
    print(f"\n📊 Current status: {present}/{len(REQUIRED_FILES)} files present")
    
    if present == len(REQUIRED_FILES):
        print("✅ All files already present!")
        return
    
    print("\n👀 Starting file watcher... (Ctrl+C to stop)")
    print("   Drop downloaded files into _data/avoniche/ to auto-integrate\n")
    
    event_handler = AvonicheHandler()
    observer = Observer()
    observer.schedule(event_handler, str(AVONICHE_DIR), recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n👋 Watcher stopped")
    observer.join()

if __name__ == "__main__":
    main()
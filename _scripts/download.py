#!/usr/bin/env python3
"""Download all bird data sources."""

import requests
import zipfile
import io
from pathlib import Path
from tqdm import tqdm

DATA_DIR = Path("_data")
DATA_DIR.mkdir(exist_ok=True)

def download_with_progress(url: str, dest: Path, chunk_size: int = 8192):
    """Download file with progress bar."""
    response = requests.get(url, stream=True)
    response.raise_for_status()
    total = int(response.headers.get('content-length', 0))
    
    dest.parent.mkdir(parents=True, exist_ok=True)
    
    with open(dest, 'wb') as f, tqdm(
        total=total, unit='B', unit_scale=True, desc=dest.name
    ) as pbar:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
                pbar.update(len(chunk))

def download_birdnet():
    """Download BirdNET taxonomy in CSV and JSON formats."""
    print("Downloading BirdNET Taxonomy v0.3-Jul2026...")
    birdnet_dir = DATA_DIR / "birdnet"
    birdnet_dir.mkdir(exist_ok=True)
    
    # Correct API endpoints from BirdNET download page
    urls = {
        "csv": "https://birdnet.cornell.edu/taxonomy/api/download/csv",
        "json": "https://birdnet.cornell.edu/taxonomy/api/download/json",
        "zip": "https://birdnet.cornell.edu/taxonomy/api/download/zip",
    }
    
    for fmt, url in urls.items():
        dest = birdnet_dir / f"birdnet_taxonomy.{fmt}"
        if not dest.exists():
            try:
                download_with_progress(url, dest)
            except Exception as e:
                print(f"  Failed to download {fmt}: {e}")
        else:
            print(f"  {fmt} already exists")

def download_avoniche():
    """Download AVONICHE dataset from Dryad."""
    print("Downloading AVONICHE 2025...")
    avoniche_dir = DATA_DIR / "avoniche"
    avoniche_dir.mkdir(exist_ok=True)
    
    # Dryad download URLs (redirect from /stash/downloads/ to /downloads/)
    base_urls = [
        "https://datadryad.org/downloads/",
    ]
    
    files = [
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
    
    for fname in files:
        dest = avoniche_dir / fname
        if dest.exists():
            print(f"  {fname} already exists")
            continue
            
        downloaded = False
        for base in base_urls:
            url = base + fname
            try:
                download_with_progress(url, dest)
                downloaded = True
                break
            except Exception as e:
                continue
        
        if not downloaded:
            print(f"  WARNING: Could not download {fname} - may need manual download")
            print(f"  Visit: https://datadryad.org/dataset/doi:10.5061/dryad.1zcrjdg56")

def download_birdfyi_sample():
    """Download sample data from BirdFYI API using Python client."""
    print("Fetching BirdFYI sample data...")
    birdfyi_dir = DATA_DIR / "birdfyi"
    birdfyi_dir.mkdir(exist_ok=True)
    
    try:
        from birdfyi.api import BirdFYI
        import json
        
        with BirdFYI() as api:
            # Get sample birds
            birds = api.list_birds(limit=5)
            (birdfyi_dir / "sample_birds.json").write_text(json.dumps(birds, indent=2))
            print("  Sample birds saved")
            
            # Get habitats
            habitats = api.list_habitats()
            (birdfyi_dir / "habitats.json").write_text(json.dumps(habitats, indent=2))
            print("  Habitats saved")
            
            # Get countries
            countries = api.list_countries()
            (birdfyi_dir / "countries.json").write_text(json.dumps(countries, indent=2))
            print("  Countries saved")
            
            # Get orders
            orders = api.list_orders()
            (birdfyi_dir / "orders.json").write_text(json.dumps(orders, indent=2))
            print("  Orders saved")
            
            # Get families
            families = api.list_families()
            (birdfyi_dir / "families.json").write_text(json.dumps(families, indent=2))
            print("  Families saved")
            
    except ImportError:
        print("  birdfyi package not installed")
    except Exception as e:
        print(f"  Failed: {e}")

def check_birdbase():
    """Check for BIRDBASE manual download."""
    birdbase_dir = DATA_DIR / "birdbase"
    birdbase_dir.mkdir(exist_ok=True)
    
    xlsx_files = list(birdbase_dir.glob("*.xlsx"))
    if xlsx_files:
        print(f"BIRDBASE found: {xlsx_files[0]}")
    else:
        print("BIRDBASE: Manual download required")
        print("  Visit: https://doi.org/10.6084/m9.figshare.27051040")
        print("  Save as: _data/birdbase/BIRDBASE_2025.xlsx")

def main():
    print("=" * 50)
    print("OpenBird Data Download")
    print("=" * 50)
    
    download_birdnet()
    print()
    download_avoniche()
    print()
    download_birdfyi_sample()
    print()
    check_birdbase()
    print()
    print("Download complete!")

if __name__ == "__main__":
    main()
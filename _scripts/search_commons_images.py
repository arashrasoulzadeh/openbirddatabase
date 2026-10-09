#!/usr/bin/env python3
"""Phase 1c: Use Wikimedia Commons API to find images for our species list."""

import json
import time
import requests
from pathlib import Path
from tqdm import tqdm
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

OUTPUT_DIR = Path("_data/wikimedia")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Session with retry strategy
session = requests.Session()
session.headers.update({
    'User-Agent': 'OpenBird/1.0 (https://github.com/arashrasoulzadeh/openbirddatabase; arash@example.com) requests/2.32'
})
retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

# Our species list
BIRDS_DIR = Path("birds")

COMMONS_API = "https://commons.wikimedia.org/w/api.php"
WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"

def get_species_list():
    """Get scientific names from our species files."""
    species = []
    for f in BIRDS_DIR.glob("**/*.md"):
        name = f.stem
        parts = name.split('-')
        if len(parts) >= 2:
            genus = parts[0].capitalize()
            species_ep = '-'.join(parts[1:])
            sci_name = f"{genus} {species_ep}"
            species.append(sci_name)
    return sorted(set(species))

def search_commons(sci_name):
    """Search Wikimedia Commons for a species."""
    params = {
        'action': 'query',
        'list': 'search',
        'srsearch': f'{sci_name} bird',
        'srlimit': 5,
        'format': 'json',
        'srnamespace': 6
    }
    
    try:
        r = session.get(COMMONS_API, params=params, timeout=30)
        data = r.json()
        return data.get('query', {}).get('search', [])
    except Exception as e:
        print(f"  Error searching {sci_name}: {e}")
        return []

def get_file_info(filename):
    """Get detailed file info from Commons."""
    params = {
        'action': 'query',
        'titles': f'File:{filename}',
        'prop': 'imageinfo',
        'iiprop': 'url|size|mime|extmetadata|sha1',
        'format': 'json'
    }
    
    try:
        r = session.get(COMMONS_API, params=params, timeout=30)
        data = r.json()
        pages = data.get('query', {}).get('pages', {})
        for page in pages.values():
            if 'imageinfo' in page:
                return page['imageinfo'][0]
    except Exception as e:
        print(f"  Error getting file info for {filename}: {e}")
        return None

def check_license(extmetadata):
    """Check if license is acceptable (CC0, CC-BY, CC-BY-SA)."""
    if not extmetadata:
        return False
    license_short = extmetadata.get('LicenseShortName', {}).get('value', '').upper()
    license_key = extmetadata.get('License', {}).get('value', '').upper()
    license_url = extmetadata.get('LicenseUrl', {}).get('value', '').upper()
    
    acceptable = ['CC0', 'CC-BY', 'CC-BY-SA', 'CC BY', 'CC BY-SA']
    return any(a in license_short for a in acceptable) or any(a in license_key for a in acceptable) or any(a in license_url for a in acceptable)

def search_wikipedia_page(sci_name):
    """Search Wikipedia for species page to get page image."""
    params = {
        'action': 'query',
        'list': 'search',
        'srsearch': sci_name,
        'srlimit': 1,
        'format': 'json'
    }
    
    try:
        r = session.get(WIKIPEDIA_API, params=params, timeout=30)
        results = r.json().get('query', {}).get('search', [])
        if results:
            return results[0]['title']
    except Exception as e:
        return None

def get_page_image(page_title):
    """Get page image from Wikipedia."""
    params = {
        'action': 'query',
        'titles': page_title,
        'prop': 'pageimages',
        'piprop': 'original',
        'format': 'json'
    }
    
    try:
        r = session.get(WIKIPEDIA_API, params=params, timeout=30)
        pages = r.json().get('query', {}).get('pages', {})
        for page in pages.values():
            if 'pageimage' in page:
                return page['original']['source']
    except Exception as e:
        return None

def main():
    print("=== Wikimedia Commons Image Search ===")
    
    species = get_species_list()
    print(f"Loaded {len(species)} species from local files")
    
    # Test with first 20 species
    test_species = species[:20]
    
    results = {}
    for sci_name in tqdm(test_species, desc="Searching"):
        search_results = search_commons(sci_name)
        
        valid_files = []
        for item in search_results:
            filename = item['title'].replace('File:', '')
            info = get_file_info(filename)
            if info and check_license(info.get('extmetadata', {})):
                valid_files.append({
                    'filename': filename,
                    'url': info.get('url'),
                    'width': info.get('width'),
                    'height': info.get('height'),
                    'license': info.get('extmetadata', {}).get('LicenseShort', {}).get('value', ''),
                    'artist': info.get('extmetadata', {}).get('Artist', {}).get('value', ''),
                    'description': info.get('extmetadata', {}).get('ImageDescription', {}).get('value', '')
                })
        
        wiki_page = search_wikipedia_page(sci_name)
        wiki_image = None
        if wiki_page:
            wiki_image = get_page_image(wiki_page)
        
        results[sci_name] = {
            'commons_files': valid_files[:3],
            'wikipedia_page': wiki_page,
            'wikipedia_image': wiki_image
        }
        
        time.sleep(0.1)
    
    output_file = OUTPUT_DIR / "commons_search_test.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\nResults saved to {output_file}")
    
    with_commons = sum(1 for r in results.values() if r['commons_files'])
    with_wiki = sum(1 for r in results.values() if r['wikipedia_image'])
    print(f"Species with Commons files: {with_commons}/{len(test_species)}")
    print(f"Species with Wikipedia images: {with_wiki}/{len(test_species)}")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""Download bird images from Wikimedia Commons for all species."""

import json
import os
import time
import hashlib
import requests
from pathlib import Path
from tqdm import tqdm
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from PIL import Image
import io

# Configuration
BIRDS_DIR = Path("birds")
IMAGES_DIR = Path("images")
METADATA_DIR = Path("_data/wikimedia")
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
METADATA_DIR.mkdir(parents=True, exist_ok=True)

COMMONS_API = "https://commons.wikimedia.org/w/api.php"

# Session with retry
session = requests.Session()
session.headers.update({
    'User-Agent': 'OpenBird/1.0 (https://github.com/arashrasoulzadeh/openbirddatabase; arash@example.com)'
})
retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

# License filter
ACCEPTABLE_LICENSES = ['CC0', 'CC-BY', 'CC-BY-SA', 'CC BY', 'CC BY-SA', 'CC BY 4.0', 'CC BY-SA 4.0', 'CC BY 3.0', 'CC BY-SA 3.0']

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
            species.append((sci_name, f))
    return sorted(set(species))

def get_taxonomy_path(filepath):
    """Get order/family from file path."""
    rel = filepath.relative_to(BIRDS_DIR)
    parts = rel.parts
    if len(parts) >= 3:
        return parts[0], parts[1]  # order, family
    return "unknown", "unknown"

def search_commons(sci_name):
    """Search Wikimedia Commons for a species."""
    params = {
        'action': 'query', 'list': 'search', 'srsearch': f'{sci_name} bird',
        'srlimit': 10, 'format': 'json', 'srnamespace': 6
    }
    try:
        r = session.get(COMMONS_API, params=params, timeout=30)
        return r.json().get('query', {}).get('search', [])
    except Exception as e:
        return []

def get_file_info(filename):
    """Get detailed file info from Commons."""
    params = {
        'action': 'query', 'titles': f'File:{filename}',
        'prop': 'imageinfo', 'iiprop': 'url|size|mime|extmetadata|sha1',
        'format': 'json'
    }
    try:
        r = session.get(COMMONS_API, params=params, timeout=30)
        data = r.json()
        pages = data.get('query', {}).get('pages', {})
        for page in pages.values():
            if 'imageinfo' in page:
                return page['imageinfo'][0]
    except Exception:
        return None

def check_license(extmetadata):
    """Check if license is acceptable."""
    if not extmetadata:
        return False
    for key in ['LicenseShortName', 'License', 'LicenseUrl']:
        val = extmetadata.get(key, {}).get('value', '').upper()
        if any(lic in val for lic in ACCEPTABLE_LICENSES):
            return True
    return False

def download_image(url, filepath):
    """Download and save image."""
    try:
        r = session.get(url, timeout=60, stream=True)
        r.raise_for_status()
        
        # Verify it's an image
        content_type = r.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            return False
        
        # Save
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Verify with PIL
        try:
            with Image.open(filepath) as img:
                img.verify()
        except Exception:
            filepath.unlink()
            return False
        
        return True
    except Exception:
        return False

def get_image_hash(filepath):
    """Get SHA256 hash of file."""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()[:16]

def process_species(sci_name, md_file):
    """Process a single species - find and download images."""
    order, family = get_taxonomy_path(md_file)
    slug = sci_name.lower().replace(' ', '-')
    
    # Output directory
    species_dir = IMAGES_DIR / order / family / slug
    species_dir.mkdir(parents=True, exist_ok=True)
    
    # Metadata file
    meta_file = species_dir / "metadata.json"
    if meta_file.exists():
        with open(meta_file) as f:
            existing = json.load(f)
            if existing.get('images'):
                return existing  # Already processed
    
    # Search Commons
    results = search_commons(sci_name)
    
    valid_images = []
    for item in results:
        filename = item['title'].replace('File:', '')
        info = get_file_info(filename)
        if not info or not check_license(info.get('extmetadata', {})):
            continue
        
        url = info.get('url')
        if not url:
            continue
        
        # Determine extension
        ext = '.jpg'
        if 'png' in info.get('mime', ''):
            ext = '.png'
        elif 'svg' in info.get('mime', ''):
            ext = '.svg'
        
        # Download
        img_filename = f"{slug}_wikimedia_{len(valid_images)+1}{ext}"
        img_path = species_dir / img_filename
        
        if download_image(url, img_path):
            file_hash = get_image_hash(img_path)
            
            # Get dimensions
            try:
                with Image.open(img_path) as img:
                    w, h = img.size
            except Exception:
                w, h = info.get('width'), info.get('height')
            
            valid_images.append({
                'filename': img_filename,
                'source_url': url,
                'source_file': filename,
                'license': info.get('extmetadata', {}).get('LicenseShortName', {}).get('value', ''),
                'artist': info.get('extmetadata', {}).get('Artist', {}).get('value', ''),
                'description': info.get('extmetadata', {}).get('ImageDescription', {}).get('value', ''),
                'width': w,
                'height': h,
                'sha256': file_hash,
                'is_primary': len(valid_images) == 0
            })
        
        if len(valid_images) >= 3:
            break
        time.sleep(0.1)
    
    # Save metadata
    metadata = {
        'scientific_name': sci_name,
        'order': order,
        'family': family,
        'images': valid_images,
        'downloaded_at': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    with open(meta_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    return metadata

def main():
    print("=== Wikimedia Commons Bulk Image Download ===")
    
    species_list = get_species_list()
    print(f"Total species: {len(species_list)}")
    
    # Resume from existing
    done = 0
    for sci_name, md_file in species_list:
        order, family = get_taxonomy_path(md_file)
        slug = sci_name.lower().replace(' ', '-')
        meta_file = IMAGES_DIR / order / family / slug / "metadata.json"
        if meta_file.exists():
            done += 1
    
    print(f"Already processed: {done}")
    print(f"Remaining: {len(species_list) - done}")
    
    # Process remaining
    stats = {'success': 0, 'failed': 0, 'images': 0}
    
    for sci_name, md_file in tqdm(species_list[done:], desc="Downloading"):
        order, family = get_taxonomy_path(md_file)
        slug = sci_name.lower().replace(' ', '-')
        meta_file = IMAGES_DIR / order / family / slug / "metadata.json"
        
        if meta_file.exists():
            continue
        
        try:
            metadata = process_species(sci_name, md_file)
            if metadata.get('images'):
                stats['success'] += 1
                stats['images'] += len(metadata['images'])
            else:
                stats['failed'] += 1
        except Exception as e:
            print(f"\nError processing {sci_name}: {e}")
            stats['failed'] += 1
        
        # Progress update every 100
        if (stats['success'] + stats['failed']) % 100 == 0:
            print(f"\nProgress: {stats['success']} ok, {stats['failed']} failed, {stats['images']} images")
    
    print(f"\n=== Complete ===")
    print(f"Successful: {stats['success']}")
    print(f"Failed: {stats['failed']}")
    print(f"Total images: {stats['images']}")

if __name__ == "__main__":
    main()
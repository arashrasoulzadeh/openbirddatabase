#!/usr/bin/env python3
"""FastAPI server for OpenBird database with MeiliSearch integration."""

import json
import yaml
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import meilisearch

# Configuration
BIRDS_DIR = Path("birds")
TRANSLATIONS_DIR = Path("translations")
INDEX_DIR = Path("_index")
MEILI_HOST = "http://localhost:7700"
MEILI_INDEX_NAME = "birds"

app = FastAPI(
    title="OpenBird API",
    description="Global bird species database API with multilingual support",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MeiliSearch client
meili_client = None
try:
    meili_client = meilisearch.Client(MEILI_HOST)
    meili_client.get_index(MEILI_INDEX_NAME)
except:
    pass

# Load taxonomy tree and field stats at startup
taxonomy_tree = {}
field_stats = {}

def load_indexes():
    global taxonomy_tree, field_stats
    if (INDEX_DIR / "taxonomy-tree.json").exists():
        with open(INDEX_DIR / "taxonomy-tree.json") as f:
            taxonomy_tree = json.load(f)
    if (INDEX_DIR / "field-stats.json").exists():
        with open(INDEX_DIR / "field-stats.json") as f:
            field_stats = json.load(f)

load_indexes()

def parse_frontmatter(filepath: Path) -> Optional[Dict]:
    """Extract YAML frontmatter from markdown file."""
    try:
        content = filepath.read_text(encoding='utf-8')
        if not content.startswith('---'):
            return None
        parts = content.split('---', 2)
        if len(parts) < 3:
            return None
        return yaml.safe_load(parts[1])
    except Exception:
        return None

def get_species_file(sci_name: str) -> Optional[Path]:
    """Find species file by scientific name."""
    slug = sci_name.lower().replace(' ', '-')
    for filepath in BIRDS_DIR.glob(f"**/{slug}.md"):
        return filepath
    return None

def merge_translations(base_fm: Dict, lang: str) -> Dict:
    """Merge base frontmatter with translation overrides."""
    if lang == 'en' or lang == 'fa':
        return base_fm
    
    slug = base_fm.get('names', {}).get('scientific', '').lower().replace(' ', '-')
    if not slug:
        return base_fm
    
    # Try to find translation file
    for order_dir in TRANSLATIONS_DIR.glob(f"{lang}/*"):
        for family_dir in order_dir.glob("*"):
            trans_file = family_dir / f"{slug}.md"
            if trans_file.exists():
                trans_fm = parse_frontmatter(trans_file)
                if trans_fm:
                    # Deep merge
                    merged = deep_merge(base_fm.copy(), trans_fm)
                    return merged
    return base_fm

def deep_merge(base: Dict, override: Dict) -> Dict:
    """Deep merge two dictionaries."""
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            base[key] = deep_merge(base[key], value)
        else:
            base[key] = value
    return base

# Pydantic models
class SearchRequest(BaseModel):
    q: str = ""
    filters: Optional[str] = None
    limit: int = 20
    offset: int = 0
    attributes: Optional[List[str]] = None

class SpeciesResponse(BaseModel):
    id: str
    scientific_name: str
    common_name_fa: str
    common_name_en: str
    order: str
    family: str
    iucn_status: Optional[str] = None
    primary_habitat: Optional[str] = None
    primary_diet: Optional[str] = None
    data_quality: Optional[str] = None

# Routes
@app.get("/")
async def root():
    return {
        "name": "OpenBird API",
        "version": "1.0.0",
        "species_count": len(list(BIRDS_DIR.glob("**/*.md"))),
        "endpoints": [
            "/search", "/species/{scientific_name}", 
            "/taxonomy", "/taxonomy/{order}", 
            "/taxonomy/{order}/{family}", "/filters"
        ]
    }

@app.get("/health")
async def health():
    return {"status": "ok", "meilisearch": meili_client is not None}

@app.post("/search", response_model=Dict[str, Any])
async def search_species(request: SearchRequest):
    """Search species using MeiliSearch."""
    if meili_client:
        try:
            index = meili_client.index(MEILI_INDEX_NAME)
            opt_params = {
                "limit": request.limit,
                "offset": request.offset,
                "attributesToRetrieve": request.attributes or ["*"]
            }
            if request.filters:
                opt_params["filter"] = request.filters
            result = index.search(request.q, opt_params)
            return result
        except Exception as e:
            # Fallback to JSON search on any MeiliSearch error
            return await fallback_search(request)
    else:
        # Fallback to simple JSON search
        return await fallback_search(request)

async def fallback_search(request: SearchRequest):
    """Simple fallback search using pre-built index."""
    with open(INDEX_DIR / "species-index.json") as f:
        species_index = json.load(f)
    
    results = []
    q_lower = request.q.lower()
    
    for doc in species_index:
        match = True
        if q_lower:
            match = (
                q_lower in doc.get('scientific_name', '').lower() or
                q_lower in doc.get('common_name_fa', '').lower() or
                q_lower in doc.get('common_name_en', '').lower() or
                q_lower in doc.get('order', '').lower() or
                q_lower in doc.get('family', '').lower()
            )
        
        if match:
            results.append(doc)
    
    # Apply pagination
    start = request.offset
    end = start + request.limit
    paginated = results[start:end]
    
    return {
        "hits": paginated,
        "total": len(results),
        "limit": request.limit,
        "offset": request.offset
    }

@app.get("/species/{scientific_name}")
async def get_species(scientific_name: str, lang: str = Query("fa", description="Language code")):
    """Get full species details with optional translation."""
    filepath = get_species_file(scientific_name)
    if not filepath:
        raise HTTPException(status_code=404, detail="Species not found")
    
    fm = parse_frontmatter(filepath)
    if not fm:
        raise HTTPException(status_code=500, detail="Invalid species file")
    
    # Merge translations
    if lang != 'fa':
        fm = merge_translations(fm, lang)
    
    return fm

@app.get("/taxonomy")
async def get_taxonomy():
    """Get full taxonomy tree."""
    return taxonomy_tree

@app.get("/taxonomy/{order}")
async def get_order(order: str):
    """Get families within an order."""
    if order not in taxonomy_tree:
        raise HTTPException(status_code=404, detail="Order not found")
    return taxonomy_tree[order]

@app.get("/taxonomy/{order}/{family}")
async def get_family(order: str, family: str):
    """Get species within a family."""
    if order not in taxonomy_tree:
        raise HTTPException(status_code=404, detail="Order not found")
    if family not in taxonomy_tree[order]:
        raise HTTPException(status_code=404, detail="Family not found")
    return taxonomy_tree[order][family]

@app.get("/filters")
async def get_filters():
    """Get available filter values for faceted search."""
    return field_stats

@app.get("/stats")
async def get_stats():
    """Get database statistics."""
    species_files = list(BIRDS_DIR.glob("**/*.md"))
    return {
        "total_species": len(species_files),
        "orders": len(taxonomy_tree),
        "families": sum(len(f) for f in taxonomy_tree.values()),
        "languages": ["fa", "en"] + [d.name for d in TRANSLATIONS_DIR.iterdir() if d.is_dir() and d.name not in ['fa', 'en']],
        "field_stats": {k: len(v) for k, v in field_stats.items()}
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
#!/usr/bin/env python3
"""FastAPI server for OpenBird database with MeiliSearch and GraphQL integration."""

import json
import os
import yaml
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel
import meilisearch
import strawberry
from strawberry.fastapi import GraphQLRouter
from _scripts.graphql_schema import schema

# Configuration
BIRDS_DIR = Path("birds")
TRANSLATIONS_DIR = Path("translations")
INDEX_DIR = Path("_index")
MEILI_HOST = os.environ.get("MEILI_HOST", "http://localhost:7700")
MEILI_INDEX_NAME = "birds"

# Hybrid (keyword + vector) search. Needs the "default" embedder configured by populate_meili.py;
# if it is missing or still downloading its model the API silently falls back to keyword search.
VECTOR_SEARCH = os.environ.get("VECTOR_SEARCH", "true").lower() not in ("0", "false", "no")
SEMANTIC_RATIO = float(os.environ.get("SEMANTIC_RATIO", "0.5"))  # 0 = keywords only, 1 = vectors only
EMBEDDER_NAME = "default"
# Search hits skip the long body_text; the species page loads full details from /species/{name}
HIT_FIELDS_EXCLUDED = {"body_text"}

# Public deployment: SITE_DOMAIN is the website, API_DOMAIN is this API (see .env.example)
SITE_DOMAIN = os.environ.get("SITE_DOMAIN", "").strip()
CORS_ORIGINS = [o.strip() for o in os.environ.get("CORS_ORIGINS", "").split(",") if o.strip()]
if SITE_DOMAIN:
    CORS_ORIGINS += [f"https://{SITE_DOMAIN}", f"https://www.{SITE_DOMAIN}"]
if not CORS_ORIGINS:
    CORS_ORIGINS = ["*"]  # local development

app = FastAPI(
    title="OpenBird API",
    description="Global bird species database API with multilingual support",
    version="1.0.0"
)

app.add_middleware(GZipMiddleware, minimum_size=1024)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GraphQL router
graphql_app = GraphQLRouter(schema)

# Include GraphQL router
app.include_router(graphql_app, prefix="/graphql")

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
    semantic_ratio: Optional[float] = None  # overrides SEMANTIC_RATIO for this request

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
            "/taxonomy/{order}/{family}", "/filters",
            "/graphql", "/graphql/schema"
        ]
    }

def _vector_ready() -> bool:
    """True when the MeiliSearch index has the embedder configured."""
    if not (meili_client and VECTOR_SEARCH):
        return False
    try:
        embedders = meili_client.index(MEILI_INDEX_NAME).get_embedders()
        return bool(embedders) and EMBEDDER_NAME in (embedders if isinstance(embedders, dict) else
                                                      getattr(embedders, "embedders", {}) or {})
    except Exception:
        return False

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "meilisearch": meili_client is not None,
        "vector_search": _vector_ready(),
    }

def _hit_attributes() -> List[str]:
    """Attributes returned for each hit (everything except the long body text)."""
    docs = get_species_index()
    keys: List[str] = []
    for doc in docs[:50]:
        for k in doc:
            if k not in keys and k not in HIT_FIELDS_EXCLUDED:
                keys.append(k)
    for lang in ("ar", "es", "fr", "de", "pt", "ru", "ja", "zh", "nl", "pl", "tr"):
        k = f"common_name_{lang}"
        if k not in keys:
            keys.append(k)
    return keys

@app.post("/search", response_model=Dict[str, Any])
async def search_species(request: SearchRequest):
    """Search species with MeiliSearch (hybrid keyword + vector), falling back to the JSON index."""
    if not meili_client:
        return await fallback_search(request)

    index = meili_client.index(MEILI_INDEX_NAME)
    params: Dict[str, Any] = {
        "limit": request.limit,
        "offset": request.offset,
        "attributesToRetrieve": request.attributes or _hit_attributes(),
    }
    if request.filters:
        params["filter"] = request.filters

    ratio = SEMANTIC_RATIO if request.semantic_ratio is None else request.semantic_ratio
    if VECTOR_SEARCH and request.q.strip() and ratio > 0:
        try:
            return index.search(
                request.q,
                {**params, "hybrid": {"semanticRatio": min(ratio, 1.0), "embedder": EMBEDDER_NAME}},
            )
        except Exception:
            pass  # embedder not configured / model still loading: use plain keyword search

    try:
        return index.search(request.q, params)
    except Exception:
        return await fallback_search(request)

_species_index: Optional[List[Dict]] = None

def get_species_index() -> List[Dict]:
    """Load the pre-built species index once and keep it in memory."""
    global _species_index
    if _species_index is None:
        with open(INDEX_DIR / "species-index.json") as f:
            _species_index = json.load(f)
    return _species_index

async def fallback_search(request: SearchRequest):
    """Simple fallback search using pre-built index."""
    species_index = get_species_index()
    
    results = []
    q_lower = request.q.lower()
    
    for doc in species_index:
        match = True
        if q_lower:
            match = (
                any(q_lower in (doc.get(f) or '').lower()
                    for f in ('scientific_name', 'order', 'family', 'genus')) or
                any(q_lower in str(v).lower()
                    for k, v in doc.items() if k.startswith('common_name_'))
            )
        
        if match:
            results.append(doc)
    
    # Apply pagination
    start = request.offset
    end = start + request.limit
    paginated = [{k: v for k, v in d.items() if k not in HIT_FIELDS_EXCLUDED} for d in results[start:end]]
    
    return {
        "hits": paginated,
        "total": len(results),
        "limit": request.limit,
        "offset": request.offset
    }

@app.get("/search", response_model=Dict[str, Any])
async def search_species_get(
    q: str = "",
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    semantic_ratio: Optional[float] = Query(None, ge=0, le=1),
):
    """GET variant of /search for simple clients (website, mobile app)."""
    return await search_species(
        SearchRequest(q=q, limit=limit, offset=offset, semantic_ratio=semantic_ratio)
    )

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
        "languages": ["fa", "en"] + ([d.name for d in TRANSLATIONS_DIR.iterdir() if d.is_dir() and d.name not in ['fa', 'en']] if TRANSLATIONS_DIR.exists() else []),
        "field_stats": {k: len(v) for k, v in field_stats.items()}
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
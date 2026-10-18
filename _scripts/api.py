#!/usr/bin/env python3
"""FastAPI server for OpenBird database with MeiliSearch and GraphQL integration."""

import asyncio
import gzip
import json
import logging
import os
import random
import time
import yaml
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from collections import OrderedDict
from contextvars import ContextVar
from typing import Optional, List, Dict, Any, Callable
from fastapi import FastAPI, Query, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import meilisearch
import strawberry
from strawberry.fastapi import GraphQLRouter
from _scripts.graphql_schema import schema
from _scripts.analytics import router as analytics_router
from _scripts.completeness import with_completeness
from _scripts.fast_search import FastIndex
from _scripts.query_intent import Lexicon, parse as parse_intent
from _scripts.cache_utils import CACHE_PREFIX, search_key, slug_of, species_key, to_json_bytes

# Configuration
BIRDS_DIR = Path("birds")
TRANSLATIONS_DIR = Path("translations")
INDEX_DIR = Path("_index")
IMAGES_DIR = Path(os.environ.get("IMAGES_DIR", "images"))  # species photos: images/<slug>.jpg (see images/README.md)
MEILI_HOST = os.environ.get("MEILI_HOST", "http://localhost:7700")
MEILI_INDEX_NAME = "birds"

# Hybrid (keyword + vector) search. Needs the "default" embedder configured by populate_meili.py;
# if it is missing or still downloading its model the API silently falls back to keyword search.
VECTOR_SEARCH = os.environ.get("VECTOR_SEARCH", "true").lower() not in ("0", "false", "no")
SEMANTIC_RATIO = float(os.environ.get("SEMANTIC_RATIO", "0.5"))  # 0 = keywords only, 1 = vectors only
EMBEDDER_NAME = "default"
# Search hits skip the long body_text; the species page loads full details from /species/{name}
HIT_FIELDS_EXCLUDED = {"body_text"}
FAST_SEARCH = os.environ.get("FAST_SEARCH", "true").lower() not in ("0", "false", "no")  # in-memory ranked search first, MeiliSearch only when it finds nothing
LOCAL_CACHE_SIZE = int(os.environ.get("LOCAL_CACHE_SIZE", "2000"))      # search responses kept in this process
LOCAL_CACHE_TTL = int(os.environ.get("LOCAL_CACHE_TTL", "300"))         # seconds, search responses
LOCAL_CACHE_TTL_STATIC = int(os.environ.get("LOCAL_CACHE_TTL_STATIC", "3600"))  # species, taxonomy, filters, stats
LOCAL_CACHE_MAX_BYTES = int(os.environ.get("LOCAL_CACHE_MAX_MB", "96")) * 1024 * 1024
# Fields a list view needs; with ?lang= a hit carries only English plus that language's name (~1/3 of the bytes)
SLIM_HIT_FIELDS = ("id", "scientific_name", "genus", "family", "order", "iucn_status", "primary_habitat", "primary_diet", "migration_status", "data_quality")

# MeiliSearch must never stall the API: every call has a timeout and runs in a dedicated pool (so a hung Meili
# cannot exhaust the default thread pool used by /species and other file work). After a failure the API skips
# MeiliSearch for a while and answers from the in-memory index instead (circuit breaker).
MEILI_TIMEOUT = float(os.environ.get("MEILI_TIMEOUT", "3"))            # seconds for a keyword search
HYBRID_TIMEOUT = float(os.environ.get("HYBRID_TIMEOUT", "1.5"))        # seconds for a keyword + vector search
MEILI_BREAKER_SECONDS = float(os.environ.get("MEILI_BREAKER_SECONDS", "30"))
HYBRID_BREAKER_SECONDS = float(os.environ.get("HYBRID_BREAKER_SECONDS", "60"))
MEILI_POOL_SIZE = max(1, int(os.environ.get("MEILI_POOL_SIZE", "2")))
SLOW_REQUEST_MS = float(os.environ.get("SLOW_REQUEST_MS", "500"))      # slower requests are logged
_meili_down_until = 0.0
_hybrid_down_until = 0.0
_meili_pool = ThreadPoolExecutor(max_workers=MEILI_POOL_SIZE, thread_name_prefix="meili")
_meili_health_state = {"ok": False, "checked": 0.0}


async def _meili_call(fn: Callable[..., Any], *args: Any, timeout: float, **kwargs: Any) -> Any:
    """Run a MeiliSearch SDK call in the dedicated pool and abandon it after `timeout` seconds."""
    loop = asyncio.get_running_loop()
    return await asyncio.wait_for(loop.run_in_executor(_meili_pool, lambda: fn(*args, **kwargs)), timeout=timeout)

log = logging.getLogger("openbird")
if not log.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    log.addHandler(_handler)
    log.setLevel(logging.INFO)

# Public deployment: SITE_DOMAIN is the website, API_DOMAIN is this API (see .env.example)
SITE_DOMAIN = os.environ.get("SITE_DOMAIN", "").strip()
CORS_ORIGINS = [o.strip() for o in os.environ.get("CORS_ORIGINS", "").split(",") if o.strip()]
if SITE_DOMAIN:
    CORS_ORIGINS += [f"https://{SITE_DOMAIN}", f"https://www.{SITE_DOMAIN}"]
if not CORS_ORIGINS:
    CORS_ORIGINS = ["*"]  # local development

# Redis cache (optional). Without REDIS_URL, or if Redis is down, every request is simply a cache miss.
REDIS_URL = os.environ.get("REDIS_URL", "").strip()
CACHE_SEARCH_TTL = int(os.environ.get("CACHE_SEARCH_TTL", "600"))      # seconds
CACHE_STATIC_TTL = int(os.environ.get("CACHE_STATIC_TTL", "604800"))   # species, taxonomy, filters, stats

redis_client = None
if REDIS_URL:
    try:
        import redis.asyncio as aioredis
        redis_client = aioredis.from_url(REDIS_URL, socket_timeout=1, socket_connect_timeout=1)
    except Exception:
        redis_client = None

async def cache_get(key: str) -> Optional[bytes]:
    if not redis_client:
        return None
    try:
        return await redis_client.get(CACHE_PREFIX + key)
    except Exception:
        return None

async def cache_set(key: str, value: bytes, ttl: int) -> None:
    if not redis_client:
        return
    try:
        await redis_client.set(CACHE_PREFIX + key, value, ex=ttl)
    except Exception:
        pass

class _Entry:
    """A cached response body, plus its gzip form (made once, so large bodies such as /taxonomy are never recompressed)."""
    __slots__ = ("expires", "raw", "gz")

    def __init__(self, raw: bytes, gz: Optional[bytes], ttl: float) -> None:
        self.expires, self.raw, self.gz = time.time() + ttl, raw, gz


_local_cache: "OrderedDict[str, _Entry]" = OrderedDict()  # in this process: faster than a Redis round trip
_local_bytes = 0
_accepts_gzip: ContextVar[bool] = ContextVar("accepts_gzip", default=False)


def _local_get(key: str) -> Optional[_Entry]:
    entry = _local_cache.get(key)
    if entry is None:
        return None
    if entry.expires <= time.time():
        _local_drop(key)
        return None
    _local_cache.move_to_end(key)
    return entry


def clear_local_cache() -> None:
    global _local_bytes
    _local_cache.clear()
    _local_bytes = 0


def _local_drop(key: str) -> None:
    global _local_bytes
    entry = _local_cache.pop(key, None)
    if entry:
        _local_bytes -= len(entry.raw) + len(entry.gz or b"")


def _local_set(key: str, entry: _Entry) -> None:
    global _local_bytes
    _local_drop(key)
    _local_cache[key] = entry
    _local_bytes += len(entry.raw) + len(entry.gz or b"")
    while _local_cache and (len(_local_cache) > LOCAL_CACHE_SIZE or _local_bytes > LOCAL_CACHE_MAX_BYTES):
        _local_drop(next(iter(_local_cache)))


async def _make_entry(raw: bytes, ttl: float) -> _Entry:
    if len(raw) < 1024:
        return _Entry(raw, None, ttl)
    compress = lambda: gzip.compress(raw, compresslevel=6, mtime=0)
    return _Entry(raw, compress() if len(raw) < 100_000 else await asyncio.to_thread(compress), ttl)


def _respond(entry: _Entry, hit: bool, layer: str) -> Response:
    headers = {"X-Cache": "HIT" if hit else "MISS", "X-Cache-Layer": layer, "Vary": "Accept-Encoding"}
    if entry.gz is not None and _accepts_gzip.get():
        return Response(entry.gz, media_type="application/json", headers={**headers, "Content-Encoding": "gzip"})
    return Response(entry.raw, media_type="application/json", headers=headers)


async def cached_response(key: str, ttl: int, producer) -> Response:
    """JSON response from the process cache, then Redis, then `producer`. Errors raised by `producer` are never cached."""
    entry = _local_get(key)
    if entry is not None:
        return _respond(entry, True, "process")
    body = await cache_get(key)
    hit, layer = body is not None, "redis"
    if body is None:
        body = await asyncio.to_thread(to_json_bytes, await producer())  # large documents: keep the event loop free
        await cache_set(key, body, ttl)
        layer = "none"
    entry = await _make_entry(body, min(ttl, LOCAL_CACHE_TTL_STATIC))
    _local_set(key, entry)
    return _respond(entry, hit, layer)

app = FastAPI(
    title="OpenBird API",
    description="Global bird species database API with multilingual support",
    version="1.0.0"
)

class _Gzip(GZipMiddleware):
    """Compress JSON and text, but not photos (already compressed JPEGs)."""

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope["path"].startswith("/images/"):
            return await self.app(scope, receive, send)
        return await super().__call__(scope, receive, send)


app.add_middleware(_Gzip, minimum_size=1024, compresslevel=4)  # level 9 (the default) costs milliseconds per response
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Analytics (events in SQLite, dashboard data)
app.include_router(analytics_router, prefix="/analytics", tags=["analytics"])

# GraphQL router
graphql_app = GraphQLRouter(schema)

# Include GraphQL router
app.include_router(graphql_app, prefix="/graphql")

# MeiliSearch client (creating it does not connect; every request has a timeout)
meili_client = meilisearch.Client(MEILI_HOST, timeout=MEILI_TIMEOUT)

# Browsers and proxies may keep these responses for a while (the data only changes with a deploy)
_CACHE_CONTROL = (
    ("/taxonomy", "public, max-age=3600, stale-while-revalidate=86400"),
    ("/filters", "public, max-age=3600, stale-while-revalidate=86400"),
    ("/stats", "public, max-age=300, stale-while-revalidate=3600"),
    ("/species/", "public, max-age=600, stale-while-revalidate=3600"),
    ("/search", "public, max-age=60, stale-while-revalidate=300"),
    ("/images/", "public, max-age=604800, stale-while-revalidate=86400"),
)


@app.middleware("http")
async def timing_and_caching(request, call_next):
    """Adds Server-Timing, logs slow requests and sets Cache-Control on the cacheable GET endpoints."""
    started = time.perf_counter()
    _accepts_gzip.set("gzip" in request.headers.get("accept-encoding", ""))
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - started) * 1000
    response.headers["Server-Timing"] = f"app;dur={elapsed_ms:.0f}"
    if elapsed_ms >= SLOW_REQUEST_MS:
        log.warning("slow request: %s %s -> %s in %.0f ms", request.method, request.url.path, response.status_code, elapsed_ms)
    if request.method == "GET" and response.status_code == 200 and "cache-control" not in response.headers:
        for prefix, value in _CACHE_CONTROL:
            if request.url.path == prefix or request.url.path.startswith(prefix):
                response.headers["Cache-Control"] = value
                break
        else:
            response.headers["Cache-Control"] = "no-store"
    return response

# Species photos (the directory may be empty or missing; requests then simply return 404)
app.mount("/images", StaticFiles(directory=str(IMAGES_DIR), check_dir=False), name="images")

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

_species_paths: Optional[Dict[str, Path]] = None

def get_species_file(sci_name: str) -> Optional[Path]:
    """Find a species file by scientific name (the directory is scanned once, not on every request)."""
    global _species_paths
    if _species_paths is None:
        _species_paths = {p.stem: p for p in BIRDS_DIR.glob("**/*.md")}
    return _species_paths.get(slug_of(sci_name))

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
    filter_map: Optional[Dict[str, str]] = None  # exact-match filters, e.g. {"iucn_status": "EN"}

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

def _vector_ready_sync() -> bool:
    """True when the MeiliSearch index has the embedder configured (blocking call: run it in a thread)."""
    try:
        embedders = meili_client.index(MEILI_INDEX_NAME).get_embedders()
        return bool(embedders) and EMBEDDER_NAME in (embedders if isinstance(embedders, dict) else
                                                      getattr(embedders, "embedders", {}) or {})
    except Exception:
        return False

_vector_state = {"ready": False, "checked": 0.0}

async def _vector_ready() -> bool:
    """Cached for 30 s so /health never waits on MeiliSearch (which can be busy computing vectors)."""
    if not (meili_client and VECTOR_SEARCH) or time.time() < _meili_down_until:
        return False
    now = time.time()
    if now - _vector_state["checked"] > 30:
        _vector_state["checked"] = now  # set first: concurrent health checks must not pile up
        try:
            _vector_state["ready"] = await _meili_call(_vector_ready_sync, timeout=min(MEILI_TIMEOUT, 1.5))
        except Exception:
            _vector_state["ready"] = False
    return _vector_state["ready"]

async def _meili_reachable() -> bool:
    """Real ping of MeiliSearch (cached 10 s). Unlike the client object, this is false when Meili is down."""
    if not meili_client or time.time() < _meili_down_until:
        return False
    now = time.time()
    if now - _meili_health_state["checked"] < 10:
        return bool(_meili_health_state["ok"])
    _meili_health_state["checked"] = now
    try:
        _meili_health_state["ok"] = bool(await _meili_call(meili_client.is_healthy, timeout=min(1.0, MEILI_TIMEOUT)))
    except Exception:
        _meili_health_state["ok"] = False
    return bool(_meili_health_state["ok"])

async def _cache_ready() -> bool:
    if not redis_client:
        return False
    try:
        return bool(await redis_client.ping())
    except Exception:
        return False

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "meilisearch": await _meili_reachable(),
        "vector_search": await _vector_ready(),
        "cache": await _cache_ready(),
    }

FILTER_FIELDS = ("iucn_status", "order", "family", "primary_habitat", "primary_diet", "migration_status")

def _meili_filter(request: "SearchRequest") -> Optional[str]:
    """Combine the explicit filter string with the exact-match filter_map."""
    parts = [request.filters] if request.filters else []
    for field, value in (request.filter_map or {}).items():
        if field in FILTER_FIELDS and value:
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            parts.append(f'{field} = "{escaped}"')
    return " AND ".join(parts) or None

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

def _slim_hits(result: Dict[str, Any], lang: Optional[str]) -> Dict[str, Any]:
    """Keep the list-view fields and the names in English + `lang` (other clients, which pass no lang, get everything)."""
    if not lang or not isinstance(result, dict):
        return result
    names = {"common_name_en", f"common_name_{lang}"}
    keep = set(SLIM_HIT_FIELDS) | names
    return {**result, "hits": [{k: v for k, v in hit.items() if k in keep} for hit in result.get("hits", [])]}


async def search_bytes(request: "SearchRequest", lang: Optional[str] = None) -> Response:
    """Search response as ready-made JSON bytes: process cache, then Redis, then the search itself."""
    key = search_key(
        q=request.q.strip(), limit=request.limit, offset=request.offset, filters=request.filters,
        filter_map=request.filter_map, attributes=request.attributes, ratio=request.semantic_ratio, lang=lang or "",
    )
    entry = _local_get(key)
    if entry is not None:
        return _respond(entry, True, "process")
    body = await cache_get(key)
    hit = body is not None
    if body is None:
        result = _slim_hits(await _search_uncached(request), lang)
        body = to_json_bytes(result) if len(result.get("hits", [])) < 200 else await asyncio.to_thread(to_json_bytes, result)
        await cache_set(key, body, CACHE_SEARCH_TTL)
    entry = await _make_entry(body, LOCAL_CACHE_TTL)
    _local_set(key, entry)
    return _respond(entry, hit, "redis" if hit else "none")


@app.post("/search")
async def search_species(request: SearchRequest):
    """Search species (cached in this process and in Redis)."""
    return await search_bytes(request)


_fast_index: Optional[FastIndex] = None


def get_fast_index() -> FastIndex:
    global _fast_index
    if _fast_index is None:
        _fast_index = FastIndex(get_species_index())
    return _fast_index


_lexicon: Optional[Lexicon] = None
_lexicon_loaded = False


def get_lexicon() -> Optional[Lexicon]:
    global _lexicon, _lexicon_loaded
    if not _lexicon_loaded:
        _lexicon, _lexicon_loaded = Lexicon.load(INDEX_DIR / "intent-lexicon.json"), True
    return _lexicon


def _result(docs, total, request, **extra) -> Dict[str, Any]:
    hits = [{k: v for k, v in d.items() if k not in HIT_FIELDS_EXCLUDED} for d in docs]
    return {"hits": hits, "total": total, "limit": request.limit, "offset": request.offset, **extra}


def _intent_search(request: "SearchRequest") -> Optional[Dict[str, Any]]:
    """Sentences such as "گونه های در حال انقراض" or "owls that live in forests": known phrases become filters, the
    leftover words search the names. Filters given in the URL must agree with the sentence (they narrow it)."""
    lexicon = get_lexicon()
    intent = parse_intent(request.q, lexicon) if lexicon else None
    if intent is None:
        return None
    filters: Dict[str, Any] = dict(intent.filters)
    for field, value in (request.filter_map or {}).items():
        if field in filters and value not in filters[field]:
            return None
        filters[field] = [value] if field in filters else value
    index, text = get_fast_index(), " ".join(intent.words)
    docs, total, _ = index.search_ex(text, filters, request.limit, request.offset, fuzzy=False, whole_words=True)
    ignored: List[str] = []
    if not total and intent.words:  # a leftover word that matches no name (a place, a colour...): search by the filters alone
        ignored, text = intent.words, ""
        docs, total, _ = index.search_ex("", filters, request.limit, request.offset, fuzzy=False)
    if not total:
        return None
    return _result(docs, total, request, interpreted={"filters": intent.filters, "words": intent.words if not ignored else [], "ignored": ignored})


def fast_search_sync(request: "SearchRequest") -> Dict[str, Any]:
    """Names first, then sentences, then names with typos fixed."""
    index = get_fast_index()
    docs, total, _ = index.search_ex(request.q, request.filter_map, request.limit, request.offset, fuzzy=False)
    if total or not request.q.strip():
        return _result(docs, total, request)
    understood = _intent_search(request)
    if understood is not None:
        return understood
    docs, total, corrected = index.search_ex(request.q, request.filter_map, request.limit, request.offset)
    return _result(docs, total, request, **({"corrected_query": corrected} if corrected else {}))


async def _search_uncached(request: SearchRequest):
    """Ranked in-memory search first (about 2 ms). Only when that finds nothing (typos, questions like "bird that eats
    fish") MeiliSearch is asked, with keyword + vector search; if it is down the empty in-memory answer is returned."""
    global _meili_down_until, _hybrid_down_until
    fast = None
    if FAST_SEARCH and not request.attributes:
        fast = fast_search_sync(request)
        if fast["total"] > 0 or not request.q.strip():
            return fast
    if not meili_client or time.time() < _meili_down_until:
        return fast if fast is not None else await asyncio.to_thread(fallback_search_sync, request)

    index = meili_client.index(MEILI_INDEX_NAME)
    params: Dict[str, Any] = {
        "limit": request.limit,
        "offset": request.offset,
        "attributesToRetrieve": request.attributes or _hit_attributes(),
    }
    meili_filter = _meili_filter(request)
    if meili_filter:
        params["filter"] = meili_filter

    ratio = SEMANTIC_RATIO if request.semantic_ratio is None else request.semantic_ratio
    if VECTOR_SEARCH and request.q.strip() and ratio > 0 and time.time() >= _hybrid_down_until:
        try:
            hybrid = {**params, "hybrid": {"semanticRatio": min(ratio, 1.0), "embedder": EMBEDDER_NAME}}
            return await _meili_call(index.search, request.q, hybrid, timeout=HYBRID_TIMEOUT)
        except Exception as error:
            # embedder missing, model still loading, or the server is too busy: keyword search for a while
            _hybrid_down_until = time.time() + HYBRID_BREAKER_SECONDS
            log.warning("vector search unavailable (%s); keyword search only for %.0f s", type(error).__name__, HYBRID_BREAKER_SECONDS)

    try:
        return await _meili_call(index.search, request.q, params, timeout=MEILI_TIMEOUT)
    except Exception as error:
        _meili_down_until = time.time() + MEILI_BREAKER_SECONDS
        _meili_health_state["ok"] = False
        _meili_health_state["checked"] = time.time()
        log.warning("MeiliSearch unavailable (%s); using the in-memory index for %.0f s", type(error).__name__, MEILI_BREAKER_SECONDS)
        return fast if fast is not None else await asyncio.to_thread(fallback_search_sync, request)

_species_index: Optional[List[Dict]] = None
_search_blobs: Optional[List[str]] = None

def get_species_index() -> List[Dict]:
    """Load the pre-built species index once and keep it in memory."""
    global _species_index
    if _species_index is None:
        with open(INDEX_DIR / "species-index.json") as f:
            _species_index = json.load(f)
    return _species_index

def _blobs() -> List[str]:
    """One lower-cased searchable string per species (scientific name, order, family, genus, every common name)."""
    global _search_blobs
    if _search_blobs is None:
        _search_blobs = [
            "\n".join(
                [str(d.get(f) or "") for f in ("scientific_name", "order", "family", "genus")]
                + [str(v) for k, v in d.items() if k.startswith("common_name_") and v]
            ).lower()
            for d in get_species_index()
        ]
    return _search_blobs

def fallback_search_sync(request: SearchRequest):
    """Search the in-memory index: one substring test per species, so it stays fast with 11k species."""
    docs = get_species_index()
    blobs = _blobs()
    q = request.q.strip().lower()
    filters = [(f, v) for f, v in (request.filter_map or {}).items() if f in FILTER_FIELDS and v]

    results = [
        d for d, blob in zip(docs, blobs)
        if (not q or q in blob) and all(d.get(f) == v for f, v in filters)
    ]
    start = request.offset
    paginated = [{k: v for k, v in d.items() if k not in HIT_FIELDS_EXCLUDED} for d in results[start:start + request.limit]]
    return {"hits": paginated, "total": len(results), "limit": request.limit, "offset": request.offset}

async def fallback_search(request: SearchRequest):
    return await asyncio.to_thread(fallback_search_sync, request)

@app.get("/search")
async def search_species_get(
    q: str = "",
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    semantic_ratio: Optional[float] = Query(None, ge=0, le=1),
    lang: Optional[str] = Query(None, pattern="^[a-z]{2}$", description="Return only English and this language's common name per hit"),
    iucn_status: Optional[str] = None,
    order: Optional[str] = None,
    family: Optional[str] = None,
    primary_habitat: Optional[str] = None,
    primary_diet: Optional[str] = None,
    migration_status: Optional[str] = None,
):
    """GET variant of /search for simple clients (website, mobile app). Filters are exact matches."""
    filter_map = {
        k: v for k, v in {
            "iucn_status": iucn_status, "order": order, "family": family,
            "primary_habitat": primary_habitat, "primary_diet": primary_diet,
            "migration_status": migration_status,
        }.items() if v
    }
    return await search_bytes(
        SearchRequest(q=q, limit=limit, offset=offset, semantic_ratio=semantic_ratio, filter_map=filter_map or None), lang
    )

@app.get("/random")
async def random_species():
    """A random species (search-hit shape, without the long body text)."""
    doc = random.choice(get_species_index())
    return {k: v for k, v in doc.items() if k not in HIT_FIELDS_EXCLUDED}

@app.get("/species/{scientific_name}")
async def get_species(scientific_name: str, lang: str = Query("fa", description="Language code")):
    """Get full species details with optional translation (cached in Redis)."""
    slug = slug_of(scientific_name)
    translated = lang not in ("fa", "en") and TRANSLATIONS_DIR.exists()

    def load():
        filepath = get_species_file(scientific_name)
        if not filepath:
            raise HTTPException(status_code=404, detail="Species not found")
        fm = parse_frontmatter(filepath)
        if not fm:
            raise HTTPException(status_code=500, detail="Invalid species file")
        return with_completeness(merge_translations(fm, lang) if translated else fm)

    async def produce():
        return await asyncio.to_thread(load)  # reading and parsing the file must not block other requests

    # The base document is shared by fa/en; only real translation overrides get their own entry
    key = species_key(slug) + (f":{lang}" if translated else "")
    return await cached_response(key, CACHE_STATIC_TTL, produce)

TAXONOMY_LANGS = {"en", "fa", "ar", "es", "fr", "de", "pt", "ru", "ja", "zh", "nl", "pl", "tr"}

def _usable_name(value: Any) -> str:
    text = str(value or "").strip()
    return "" if text.lower() in ("", "nan", "none", "null") else text

def _slim_taxonomy(lang: str) -> Dict[str, Any]:
    """The tree with one common name per species (in `lang`) instead of every language: about a quarter of the size."""
    slim: Dict[str, Any] = {}
    for order, families in taxonomy_tree.items():
        slim[order] = {}
        for family, genera in families.items():
            slim[order][family] = {}
            for genus, species in genera.items():
                entries = []
                for sp in species:
                    local = (
                        sp.get("common_en") if lang == "en"
                        else sp.get("common_fa") if lang == "fa"
                        else (sp.get("names") or {}).get(lang)
                    )
                    entries.append({
                        "scientific": sp["scientific"],
                        "id": sp.get("id"),
                        "name": _usable_name(local) or _usable_name(sp.get("common_en")),
                        "common_en": _usable_name(sp.get("common_en")),
                    })
                slim[order][family][genus] = entries
    return slim

@app.get("/taxonomy")
async def get_taxonomy(lang: Optional[str] = Query(None, description="Return one common name per species in this language")):
    """The taxonomy tree. Without `lang` the full tree (all languages, about 4.6 MB); with `lang` a slim tree."""
    if lang in TAXONOMY_LANGS:
        async def produce_slim():
            return await asyncio.to_thread(_slim_taxonomy, lang)
        return await cached_response(f"taxonomy:{lang}", CACHE_STATIC_TTL, produce_slim)

    async def produce():
        return taxonomy_tree
    return await cached_response("taxonomy", CACHE_STATIC_TTL, produce)

@app.get("/taxonomy/{order}")
async def get_order(order: str):
    """Get families within an order."""
    if order not in taxonomy_tree:
        raise HTTPException(status_code=404, detail="Order not found")

    async def produce():
        return taxonomy_tree[order]
    return await cached_response(f"taxonomy:{order}", CACHE_STATIC_TTL, produce)

@app.get("/taxonomy/{order}/{family}")
async def get_family(order: str, family: str):
    """Get species within a family."""
    if order not in taxonomy_tree:
        raise HTTPException(status_code=404, detail="Order not found")
    if family not in taxonomy_tree[order]:
        raise HTTPException(status_code=404, detail="Family not found")

    async def produce():
        return taxonomy_tree[order][family]
    return await cached_response(f"taxonomy:{order}:{family}", CACHE_STATIC_TTL, produce)

@app.get("/filters")
async def get_filters():
    """Get available filter values for faceted search."""
    async def produce():
        return field_stats
    return await cached_response("filters", CACHE_STATIC_TTL, produce)

@app.get("/stats")
async def get_stats():
    """Get database statistics."""
    async def produce():
        get_species_file("")  # makes sure the file map is loaded
        return {
            "total_species": len(_species_paths or {}),
            "orders": len(taxonomy_tree),
            "families": sum(len(f) for f in taxonomy_tree.values()),
            "languages": ["fa", "en"] + ([d.name for d in TRANSLATIONS_DIR.iterdir() if d.is_dir() and d.name not in ['fa', 'en']] if TRANSLATIONS_DIR.exists() else []),
            "field_stats": {k: len(v) for k, v in field_stats.items()}
        }
    return await cached_response("stats", CACHE_STATIC_TTL, produce)

@app.on_event("startup")
async def preload() -> None:
    """Load the big in-memory structures before the first visitor needs them."""
    def work():
        get_species_index()
        _blobs()
        get_fast_index()
        get_species_file("")
        _hit_attributes()
    started = time.perf_counter()
    await asyncio.to_thread(work)
    log.info("preloaded the species index in %.0f ms", (time.perf_counter() - started) * 1000)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
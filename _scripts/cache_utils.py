"""Helpers shared by the API and the cache warmer so both agree on Redis keys and JSON shape."""

import hashlib
import json
import math
from datetime import date, datetime
from typing import Any

# Bump when the cached JSON shape changes: old keys are simply never read again.
CACHE_PREFIX = "ob:v2:"  # v2: species documents carry a "completeness" report


def slug_of(scientific_name: str) -> str:
    """'Parus major' -> 'parus-major' (same rule as the species file names)."""
    return scientific_name.strip().lower().replace(" ", "-")


def species_key(slug: str) -> str:
    return f"species:{slug}"


def search_key(**params: Any) -> str:
    """Stable key for a search request; identical queries share one cache entry."""
    blob = json.dumps(params, sort_keys=True, ensure_ascii=False, default=str)
    return "search:" + hashlib.sha1(blob.encode("utf-8")).hexdigest()


def sanitize(obj: Any) -> Any:
    """Make parsed YAML safe for strict JSON: NaN/Inf -> None, dates -> ISO strings."""
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    if isinstance(obj, dict):
        return {str(k): sanitize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [sanitize(v) for v in obj]
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return obj


def to_json_bytes(obj: Any) -> bytes:
    return json.dumps(sanitize(obj), ensure_ascii=False, separators=(",", ":")).encode("utf-8")

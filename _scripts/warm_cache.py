#!/usr/bin/env python3
"""Fill the Redis cache so the first visitors get fast answers.

1. Loads every species file (11k) straight into Redis.
2. Asks the running API for the big/common responses (taxonomy, filters, stats, the home page's first
   search page, and the first page for each conservation status) so they are cached too.

Environment:
  REDIS_URL  e.g. redis://redis:6379/0   (required)
  API_URL    e.g. http://api:8000        (default http://localhost:8000; set empty to skip step 2)
Options:
  --no-flush   keep existing keys (default: delete this app's keys first so stale data is never served)
  --every N    stay running and warm again every N seconds (docker-compose uses 3600). The first pass flushes as
               usual; later passes only add and refresh keys, so visitors never meet an empty cache. The species
               files are re-read only when they changed or Redis lost them.
"""

import argparse
import os
import sys
import time
from pathlib import Path

import redis
import requests
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _scripts.cache_utils import CACHE_PREFIX, slug_of, species_key, to_json_bytes  # noqa: E402
from _scripts.completeness import with_completeness  # noqa: E402

BIRDS_DIR = Path(os.environ.get("BIRDS_DIR", "birds"))
SPECIES_TTL = int(os.environ.get("CACHE_STATIC_TTL", "604800"))
Loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


def frontmatter(path: Path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    return yaml.load(parts[1], Loader=Loader) if len(parts) >= 3 else None


def connect(url: str) -> "redis.Redis":
    client = redis.from_url(url)
    for attempt in range(60):
        try:
            client.ping()
            return client
        except redis.exceptions.ConnectionError:
            if attempt == 0:
                print("Waiting for Redis...")
            time.sleep(1)
    raise SystemExit("Redis is not reachable")


def flush_app_keys(client) -> int:
    deleted = 0
    batch = []
    for key in client.scan_iter(match=CACHE_PREFIX + "*", count=1000):
        batch.append(key)
        if len(batch) >= 1000:
            deleted += client.delete(*batch)
            batch = []
    if batch:
        deleted += client.delete(*batch)
    return deleted


SIGNATURE_KEY = CACHE_PREFIX + "warm:species-signature"


def species_signature(files) -> str:
    return f"{len(files)}:{max((f.stat().st_mtime_ns for f in files), default=0)}"


def load_species(client, force: bool = True) -> int:
    files = sorted(BIRDS_DIR.glob("**/*.md"))
    signature = species_signature(files)
    if not force and client.get(SIGNATURE_KEY) == signature.encode():  # the key vanishes if Redis was flushed or restarted
        print(f"Species files unchanged and still cached ({len(files)}); not reloading")
        return len(files)
    print(f"Loading {len(files)} species files into Redis...")
    pipe = client.pipeline(transaction=False)
    count = 0
    for i, path in enumerate(files, 1):
        fm = frontmatter(path)
        if not fm:
            continue
        name = (fm.get("names") or {}).get("scientific") or path.stem
        pipe.set(CACHE_PREFIX + species_key(slug_of(name)), to_json_bytes(with_completeness(fm)), ex=SPECIES_TTL)
        count += 1
        if i % 500 == 0:
            pipe.execute()
            print(f"  {i}/{len(files)}")
    pipe.set(SIGNATURE_KEY, signature, ex=SPECIES_TTL)
    pipe.execute()
    return count


LANGS = ["en", "fa", "ar", "de", "es", "fr", "ja", "nl", "pl", "pt", "ru", "tr", "zh"]


def warm_api(api_url: str) -> None:
    session = requests.Session()
    for attempt in range(90):
        try:
            if session.get(f"{api_url}/health", timeout=3).ok:
                break
        except requests.RequestException:
            pass
        if attempt == 0:
            print(f"Waiting for the API at {api_url}...")
        time.sleep(2)
    else:
        print("API not reachable; skipping the API warm-up")
        return

    paths = ["/taxonomy", "/filters", "/stats", "/search?q=&limit=50&offset=0"]
    # what the website asks for: the first page, the taxonomy tree and each conservation status, per language
    paths += [f"/search?q=&limit=50&offset=0&lang={lang}" for lang in LANGS]
    paths += [f"/taxonomy?lang={lang}" for lang in LANGS]
    try:
        statuses = session.get(f"{api_url}/filters", timeout=30).json().get("iucn_status", {})
        paths += [f"/search?iucn_status={s}&limit=50&offset=0" for s in statuses if s]
        paths += [f"/search?iucn_status={s}&limit=50&offset=0&lang={lang}" for s in statuses if s for lang in ("en", "fa")]
    except (requests.RequestException, ValueError):
        pass
    for path in paths:
        try:
            r = session.get(api_url + path, timeout=120)
            print(f"  {r.status_code} {path}")
        except requests.RequestException as e:
            print(f"  failed {path}: {e}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--no-flush", action="store_true")
    parser.add_argument("--every", type=int, default=int(os.environ.get("WARM_EVERY", "0")), metavar="SECONDS",
                        help="keep running and warm again every SECONDS (0 = once)")
    args = parser.parse_args()

    url = os.environ.get("REDIS_URL")
    if not url:
        raise SystemExit("REDIS_URL is not set")
    client = connect(url)

    api_url = os.environ.get("API_URL", "http://localhost:8000").rstrip("/")
    first = True
    while True:
        started = time.time()
        if first and not args.no_flush:
            print(f"Removed {flush_app_keys(client)} old cache keys")
        print(f"[{time.strftime('%H:%M:%S')}] Cached {load_species(client, force=first)} species")
        if api_url:
            warm_api(api_url)
        print(f"Done in {time.time() - started:.0f} s. Cache now holds {sum(1 for _ in client.scan_iter(match=CACHE_PREFIX + '*', count=1000))} keys", flush=True)
        if not args.every:
            break
        first = False
        print(f"Next warm-up in {args.every} s", flush=True)
        time.sleep(args.every)


if __name__ == "__main__":
    main()

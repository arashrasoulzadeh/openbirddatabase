"""GBIF (CC0 / CC BY data): countries where each species has been observed, and Xeno-canto recordings.

For every species the GBIF key is resolved from the scientific name (stored keys are sometimes for an old synonym),
then two queries run:

* countries: occurrence counts per country (human/machine observations and preserved specimens with coordinates).
  A country is listed when it has at least 3 records AND at least 0.1% of the species' records, which drops one-off
  vagrants and escapes while keeping genuine (even introduced) populations.
* recordings: up to 3 recording ids from the Xeno-canto bird-sounds dataset hosted on GBIF.

Results are cached in _data/gbif/species.jsonl (one line per species), so an interrupted run resumes where it stopped.
    python _scripts/enrich.py fetch gbif       (about 30-60 minutes for 11k species)
    python _scripts/enrich.py apply gbif       countries
    python _scripts/enrich.py apply xenocanto  recordings
"""

import json
import math
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .common import ROOT, Progress, read_species, save_patches, species_paths

SOURCE = "gbif"
LABEL = "GBIF occurrence records (countries)"
API = "https://api.gbif.org/v1"
INATURALIST_DATASET = "50c9509d-22c7-4a22-a47d-8c48425ef4a7"  # research-grade iNaturalist observations
OPEN_LICENSES = {  # photo licences we may redistribute with attribution (no NC / ND)
    "http://creativecommons.org/publicdomain/zero/1.0/": "CC0-1.0",
    "http://creativecommons.org/licenses/by/4.0/": "CC-BY-4.0",
}
XENO_CANTO_DATASET = "b1047888-ae52-4179-9dd5-5448ea342a24"  # "Xeno-canto - Bird sounds from around the world"
CACHE = ROOT / "_data" / "gbif" / "species.jsonl"
MIN_RECORDS = 3
MIN_SHARE = 0.001
BASIS = ["HUMAN_OBSERVATION", "OBSERVATION", "MACHINE_OBSERVATION", "PRESERVED_SPECIMEN"]


def session() -> requests.Session:
    s = requests.Session()
    s.headers["User-Agent"] = "OpenBirdDatabase/1.0 (https://github.com/arashrasoulzadeh/openbirddatabase)"
    retry = Retry(total=4, backoff_factor=1.5, status_forcelist=[429, 500, 502, 503, 504])
    s.mount("https://", HTTPAdapter(max_retries=retry, pool_maxsize=16))
    return s


def resolve_key(s: requests.Session, name: str, stored: Optional[int]) -> Optional[int]:
    r = s.get(f"{API}/species/match", params={"name": name, "kingdom": "Animalia", "class": "Aves"}, timeout=30)
    if r.ok:
        data = r.json()
        if data.get("rank") == "SPECIES" and data.get("matchType") in ("EXACT", "FUZZY", "HIGHERRANK") and data.get("usageKey"):
            return int(data.get("speciesKey") or data["usageKey"])
    return stored


def countries_for(s: requests.Session, key: int) -> Dict[str, Any]:
    params: List[tuple] = [("taxonKey", key), ("limit", 0), ("facet", "country"), ("facetLimit", 300),
                           ("hasCoordinate", "true"), ("occurrenceStatus", "PRESENT")]
    params += [("basisOfRecord", b) for b in BASIS]
    r = s.get(f"{API}/occurrence/search", params=params, timeout=60)
    r.raise_for_status()
    data = r.json()
    total = int(data.get("count", 0))
    counts = {c["name"]: int(c["count"]) for f in data.get("facets", []) for c in f.get("counts", [])}
    return {"total": total, "counts": counts}


def recordings_for(s: requests.Session, key: int) -> Dict[str, Any]:
    r = s.get(f"{API}/occurrence/search",
              params={"taxonKey": key, "datasetKey": XENO_CANTO_DATASET, "limit": 3}, timeout=60)
    r.raise_for_status()
    data = r.json()
    ids = [x["catalogNumber"] for x in data.get("results", []) if str(x.get("catalogNumber", "")).startswith("XC")]
    return {"count": int(data.get("count", 0)), "ids": ids}


def image_for(s: requests.Session, key: int) -> Optional[Dict[str, str]]:
    """First iNaturalist photo whose OWN licence is CC0 / CC BY (the occurrence licence can differ from the photo's)."""
    r = s.get(f"{API}/occurrence/search",
              params={"taxonKey": key, "datasetKey": INATURALIST_DATASET, "mediaType": "StillImage", "limit": 30,
                      "occurrenceStatus": "PRESENT"}, timeout=60)
    r.raise_for_status()
    for occ in r.json().get("results", []):
        for m in occ.get("media", []):
            licence = OPEN_LICENSES.get(str(m.get("license", "")).replace("https://", "http://").rstrip("/") + "/")
            url = str(m.get("identifier", ""))
            if licence and m.get("type") == "StillImage" and "/original." in url:
                return {"source_url": url, "page": m.get("references") or "", "author": m.get("creator") or m.get("rightsHolder") or "",
                        "license": licence, "source": "iNaturalist via GBIF"}
    return None


def collect_one(name: str, stored: Optional[int], existing: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    s = session()
    if existing:  # countries/recordings already cached: only the photo is missing
        row = dict(existing)
        if row.get("key"):
            row["image"] = image_for(s, int(row["key"]))
        return row
    key = resolve_key(s, name, stored)
    row: Dict[str, Any] = {"name": name, "key": key}
    if key:
        row["countries"] = countries_for(s, key)
        row["recordings"] = recordings_for(s, key)
        row["image"] = image_for(s, key)
    return row


def species_index() -> Dict[str, tuple]:
    """{slug: (scientific name, stored gbif key or None)}. Reads only the head of each file with regexes: parsing 11k
    YAML files takes minutes without libyaml, this takes a few seconds."""
    index: Dict[str, tuple] = {}
    for slug, path in species_paths().items():
        with path.open(encoding="utf-8") as f:
            head = f.read(2048)
        name = re.search(r"^  scientific: (.+)$", head, re.M)
        key = re.search(r"^gbif_key: (\d+)$", head, re.M)
        if name:
            index[slug] = (name.group(1).strip().strip("'\""), int(key.group(1)) if key else None)
    return index


def species_to_fetch() -> Dict[str, Optional[int]]:
    return {name: key for name, key in species_index().values()}


def describe(row: Dict[str, Any]) -> str:
    c = (row.get("countries") or {}).get("counts") or {}
    return (f"key={row.get('key')} records={(row.get('countries') or {}).get('total', '-')} countries={len(c)} "
            f"recordings={len((row.get('recordings') or {}).get('ids', []))} "
            f"photo={'yes ' + row['image']['license'] if row.get('image') else 'no'}")


def fetch(workers: int = 3, verbose: bool = False, limit: int = 0, delay: float = 0.0) -> str:
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    print("gbif: reading species files and cache ...", file=sys.stderr, flush=True)
    cached: Dict[str, Dict[str, Any]] = {}
    if CACHE.exists():
        for line in CACHE.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                cached[row["name"]] = row  # a later line (re-fetched with a photo) replaces an earlier one
    wanted = {n: k for n, k in species_to_fetch().items() if n}
    todo = {n: k for n, k in wanted.items() if n not in cached or ("image" not in cached[n] and cached[n].get("key"))}
    if limit:
        todo = dict(list(todo.items())[:limit])
    photo_only = sum(n in cached for n in todo)
    print(f"GBIF: {len(wanted)} species | {len(cached)} cached | {len(todo)} to fetch "
          f"({photo_only} only need a photo lookup) | {workers} workers, delay {delay}s | cache {CACHE.relative_to(ROOT)}\n"
          f"Ctrl-C is safe: every finished species is saved, rerun to resume.", file=sys.stderr, flush=True)
    progress = Progress(len(todo), "gbif")

    def job(name: str, stored: Optional[int]) -> Dict[str, Any]:
        began = time.time()
        row = collect_one(name, stored, cached.get(name))
        if delay:
            time.sleep(delay)
        row["_ms"] = int((time.time() - began) * 1000)
        return row

    pool = ThreadPoolExecutor(max_workers=workers)
    try:
        with CACHE.open("a", encoding="utf-8") as out:
            futures = {pool.submit(job, n, k): n for n, k in todo.items()}
            for future in as_completed(futures):
                name = futures[future]
                try:
                    row = future.result()
                    ms = row.pop("_ms", 0)
                    out.write(json.dumps(row, ensure_ascii=False) + "\n")
                    out.flush()
                    if verbose:
                        progress.log(f"  ok   {name:<34} {describe(row)}  ({ms} ms)")
                    progress.step(True)
                except Exception as error:  # a species that keeps failing is retried on the next run
                    progress.log(f"  FAIL {name:<34} {type(error).__name__}: {str(error)[:90]}")
                    progress.step(False)
    except KeyboardInterrupt:
        pool.shutdown(wait=False, cancel_futures=True)
        progress.finish()
        return f"interrupted after {progress.done - progress.failed} saved ({progress.failed} failed); rerun to resume"
    pool.shutdown()
    progress.finish()
    return f"fetched {progress.done - progress.failed} species ({progress.failed} failed) -> {CACHE.relative_to(ROOT)}"


def rows() -> List[Dict[str, Any]]:
    latest: Dict[str, Dict[str, Any]] = {}
    for line in CACHE.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            latest[row["name"]] = row
    return list(latest.values())


def build_countries() -> Dict[str, Dict[str, Any]]:
    patches: Dict[str, Dict[str, Any]] = {}
    for row in rows():
        info = row.get("countries") or {}
        total = info.get("total", 0)
        if total < MIN_RECORDS:
            continue
        threshold = max(MIN_RECORDS, math.ceil(total * MIN_SHARE))
        codes = sorted(c for c, n in info.get("counts", {}).items() if len(c) == 2 and c.isalpha() and n >= threshold)
        if codes:
            patches[row["name"]] = {"distribution.countries": [c.upper() for c in codes]}
    return patches


def build_recordings() -> Dict[str, Dict[str, Any]]:
    return {r["name"]: {"behavior.xeno_canto_ids": r["recordings"]["ids"]}
            for r in rows() if (r.get("recordings") or {}).get("ids")}


def build_images() -> Dict[str, Dict[str, Any]]:
    """Photo metadata only; images/<slug>.jpg and `file` are added by `python _scripts/enrich.py photos`."""
    return {r["name"]: {"image": r["image"]} for r in rows() if r.get("image")}


def run(workers: int = 3, verbose: bool = False, limit: int = 0, delay: float = 0.0) -> str:
    message = fetch(workers, verbose, limit, delay)
    countries = save_patches("gbif", build_countries())
    recordings = save_patches("xenocanto", build_recordings())
    return f"{message}; patches: {countries.relative_to(ROOT)}, {recordings.relative_to(ROOT)}"

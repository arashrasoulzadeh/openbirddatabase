"""Photographs of every species (iNaturalist research-grade observations through GBIF, CC0 / CC BY only).

`fetch gbif` remembers up to 30 open-licence photos per species (different photographers first). This step downloads
the first N of them (--max-photos N, default 5; 0 = every remembered one), shrinks each to PHOTO_WIDTH px wide (JPEG)
and writes the patch that stores author, licence and source links in the species frontmatter:
    images/<order>/<family>/<species>/1.jpg   the first photo (`image:` in the species file)
    images/<order>/<family>/<species>/2.jpg, 3.jpg ...   the others (`images:` lists all of them)
mirroring birds/<order>/<family>/<species>.md, so a photo's place follows from the species file's.
Resumable: files that already exist are not downloaded again. Rerun `apply photos` after changing N.
    python _scripts/enrich.py fetch photos -v                 (PHOTO_WIDTH=480 PHOTO_QUALITY=70 by default)
    python _scripts/enrich.py fetch photos --max-photos 10
    python _scripts/enrich.py apply photos
"""

import io
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List

import requests
from PIL import Image

from .common import BIRDS_DIR, ROOT, Progress, save_patches, species_paths
from .gbif import build_images, photo_lookup_status, session, species_index

SOURCE = "photos"
REPLACE = ["image", "images"]  # this source owns these fields, so a rerun with another --max-photos updates them
DEFAULT_MAX_PHOTOS = 5
LABEL = "iNaturalist photos via GBIF (CC0 / CC BY)"
IMAGES = ROOT / "images"
WIDTH = int(os.environ.get("PHOTO_WIDTH", "480"))
QUALITY = int(os.environ.get("PHOTO_QUALITY", "70"))


def file_name(rel: str, n: int) -> str:
    """rel = "passeriformes/paridae/parus-major" (the species file's path below birds/, without .md)."""
    return f"{rel}/{n + 1}.jpg"


def download(target: Path, info: Dict[str, str], s: requests.Session) -> None:
    if target.exists():
        return
    url = info["source_url"].replace("/original.", "/medium.")  # iNaturalist serves ~500px "medium" files
    r = s.get(url, timeout=60)
    if r.status_code == 404:
        r = s.get(info["source_url"], timeout=120)
    r.raise_for_status()
    img = Image.open(io.BytesIO(r.content)).convert("RGB")
    if img.width > WIDTH:
        img = img.resize((WIDTH, round(img.height * WIDTH / img.width)), Image.LANCZOS)
    img.save(target, "JPEG", quality=QUALITY, optimize=True, progressive=True)


def run(workers: int = 6, verbose: bool = False, limit: int = 0, delay: float = 0.0, max_photos: int = DEFAULT_MAX_PHOTOS) -> str:
    IMAGES.mkdir(exist_ok=True)
    print("photos: reading species files and cache ...", file=sys.stderr, flush=True)
    have, old = photo_lookup_status()
    if old:
        print(f"photos: WARNING - {old} species have not had the multi-photo lookup yet (only {have} have photo lists).\n"
              f"        Run  python _scripts/enrich.py fetch gbif -w 2 --delay 0.1  first (about one request per species), then this again.",
              file=sys.stderr, flush=True)
    paths = species_paths()
    by_name = {name: paths[slug].relative_to(BIRDS_DIR).with_suffix("").as_posix() for slug, (name, _) in species_index().items()}
    wanted: Dict[str, List[Dict[str, str]]] = {}
    for name, photos in build_images().items():
        if name in by_name:
            wanted[name] = photos[:max_photos] if max_photos else photos
    if limit:
        wanted = dict(list(wanted.items())[:limit])
    tasks = [(by_name[name], n, photo) for name, photos in wanted.items() for n, photo in enumerate(photos)]
    already = sum((IMAGES / file_name(rel, n)).exists() for rel, n, _ in tasks)
    print(f"photos: {len(tasks)} photos for {len(wanted)} species (max {max_photos or 'all'} each) | {already} already in images/ | "
          f"{workers} workers, {WIDTH}px q{QUALITY}\nCtrl-C is safe, rerun to resume.", file=sys.stderr, flush=True)
    s = session()
    progress = Progress(len(tasks), "photos", every=200)

    def one(task):
        rel, n, info = task
        target = IMAGES / file_name(rel, n)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            existed = target.exists()
            download(target, info, s)
            if delay:
                time.sleep(delay)
            if verbose:
                progress.log(f"  ok   {str(target.relative_to(IMAGES)):<52} {target.stat().st_size // 1024:>4} KB {'(exists)' if existed else ''} {info['license']} by {info['author'][:30]}")
            progress.step(True)
        except Exception as error:
            progress.log(f"  FAIL {str(target.relative_to(IMAGES)):<52} {type(error).__name__}: {str(error)[:90]}")
            progress.step(False)

    pool = ThreadPoolExecutor(max_workers=workers)
    try:
        list(pool.map(one, tasks))
    except KeyboardInterrupt:
        pool.shutdown(wait=False, cancel_futures=True)
        progress.finish()
        return "interrupted; rerun to resume"
    pool.shutdown()
    progress.finish()
    patches: Dict[str, Dict[str, Any]] = {}
    for name, photos in wanted.items():
        rel = by_name[name]
        entries = [{"file": f"images/{file_name(rel, n)}", **{k: v for k, v in photo.items() if v and k != "source_url"},
                    "source_url": photo["source_url"]}
                   for n, photo in enumerate(photos) if (IMAGES / file_name(rel, n)).exists()]
        if entries:
            patches[name] = {"image": entries[0], "images": entries}
    out = save_patches(SOURCE, patches)
    files = list(IMAGES.rglob("*.jpg"))
    size = sum(f.stat().st_size for f in files) / 1e6
    avg = size / len(files) if files else 0
    return (f"{progress.done - progress.failed} downloaded ({progress.failed} failed); images/ now holds {len(files)} photos, "
            f"{size:.0f} MB (average {avg * 1000:.0f} KB) -> {out.relative_to(ROOT)}")

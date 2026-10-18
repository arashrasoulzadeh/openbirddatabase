"""One photograph per species (iNaturalist research-grade observations through GBIF, CC0 / CC BY only).

`fetch gbif` records which photo to use. This step downloads each one, shrinks it to PHOTO_WIDTH px wide (JPEG) into
images/<slug>.jpg and writes the patch that stores the author, licence and source links in the species frontmatter.
Resumable: files that already exist are not downloaded again.
    python _scripts/enrich.py fetch photos      (size with PHOTO_WIDTH=480 PHOTO_QUALITY=70, default)
    python _scripts/enrich.py apply photos
"""

import io
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict

import requests
from PIL import Image

from .common import ROOT, Progress, save_patches
from .gbif import build_images, session, species_index

SOURCE = "photos"
LABEL = "iNaturalist photos via GBIF (CC0 / CC BY)"
IMAGES = ROOT / "images"
WIDTH = int(os.environ.get("PHOTO_WIDTH", "480"))
QUALITY = int(os.environ.get("PHOTO_QUALITY", "70"))


def download(slug: str, info: Dict[str, str], s: requests.Session) -> bool:
    target = IMAGES / f"{slug}.jpg"
    if target.exists():
        return True
    url = info["source_url"].replace("/original.", "/medium.")  # iNaturalist serves ~500px "medium" files
    r = s.get(url, timeout=60)
    if r.status_code == 404:
        r = s.get(info["source_url"], timeout=120)
    r.raise_for_status()
    img = Image.open(io.BytesIO(r.content)).convert("RGB")
    if img.width > WIDTH:
        img = img.resize((WIDTH, round(img.height * WIDTH / img.width)), Image.LANCZOS)
    img.save(target, "JPEG", quality=QUALITY, optimize=True, progressive=True)
    return True


def run(workers: int = 6, verbose: bool = False, limit: int = 0, delay: float = 0.0) -> str:
    IMAGES.mkdir(exist_ok=True)
    print("photos: reading species files and cache ...", file=sys.stderr, flush=True)
    by_name = {name: slug for slug, (name, _) in species_index().items()}
    wanted = {by_name[n]: v["image"] for n, v in build_images().items() if n in by_name}
    if limit:
        wanted = dict(list(wanted.items())[:limit])
    already = sum((IMAGES / f"{slug}.jpg").exists() for slug in wanted)
    print(f"photos: {len(wanted)} species with a photo | {already} already in images/ | {workers} workers, "
          f"{WIDTH}px q{QUALITY}\nCtrl-C is safe, rerun to resume.", file=sys.stderr, flush=True)
    s = session()
    progress = Progress(len(wanted), "photos", every=100)

    def one(item):
        try:
            existed = (IMAGES / f"{item[0]}.jpg").exists()
            download(item[0], item[1], s)
            if delay:
                time.sleep(delay)
            if verbose:
                size = (IMAGES / f"{item[0]}.jpg").stat().st_size // 1024
                progress.log(f"  ok   {item[0]:<34} {size:>4} KB {'(exists)' if existed else ''} {item[1]['license']} by {item[1]['author'][:30]}")
            progress.step(True)
        except Exception as error:
            progress.log(f"  FAIL {item[0]:<34} {type(error).__name__}: {str(error)[:90]}")
            progress.step(False)

    pool = ThreadPoolExecutor(max_workers=workers)
    try:
        list(pool.map(one, wanted.items()))
    except KeyboardInterrupt:
        pool.shutdown(wait=False, cancel_futures=True)
        progress.finish()
        return "interrupted; rerun to resume"
    pool.shutdown()
    progress.finish()
    ok, failed = progress.done - progress.failed, progress.failed
    patches: Dict[str, Dict[str, Any]] = {}
    for name, patch in build_images().items():
        slug = by_name.get(name)
        if slug and (IMAGES / f"{slug}.jpg").exists():
            patches[name] = {"image": {"file": f"images/{slug}.jpg", **{k: v for k, v in patch["image"].items() if v}}}
    out = save_patches(SOURCE, patches)
    size = sum(f.stat().st_size for f in IMAGES.glob("*.jpg")) / 1e6
    return f"{ok} photos ({failed} failed), {size:.0f} MB in images/ -> {out.relative_to(ROOT)}"

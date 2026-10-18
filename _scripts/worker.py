#!/usr/bin/env python3
"""Long-running backend worker for scheduled jobs (cache warm-up, analytics backup, content stats).

Runs inside the `worker` Compose service. Deploy no longer warms the cache — this process does it
on start and on an interval.

    python _scripts/worker.py
    JOBS=cache,analytics_backup,content_stats   # comma-separated; default all three
    CACHE_EVERY=3600                            # seconds (default 1 h)
    BACKUP_EVERY=86400                          # seconds (default 24 h)
    STATS_EVERY=86400                           # seconds (default 24 h)

Each job is independent: a failure is logged and the next tick still runs.
"""

from __future__ import annotations

import logging
import os
import sys
import time
import traceback
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

log = logging.getLogger("openbird.worker")
if not log.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    log.addHandler(_handler)
    log.setLevel(logging.INFO)


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    return int(raw)


def job_cache(first: bool) -> None:
    from _scripts import warm_cache as wc

    url = os.environ.get("REDIS_URL")
    if not url:
        raise RuntimeError("REDIS_URL is not set")
    client = wc.connect(url)
    api_url = os.environ.get("API_URL", "http://localhost:8000").rstrip("/")
    started = time.time()
    if first:
        removed = wc.flush_app_keys(client)
        log.info("cache: removed %s old keys", removed)
    n = wc.load_species(client, force=first)
    log.info("cache: loaded %s species", n)
    if api_url:
        wc.warm_api(api_url)
    keys = sum(1 for _ in client.scan_iter(match=wc.CACHE_PREFIX + "*", count=1000))
    log.info("cache: done in %.0fs (%s keys)", time.time() - started, keys)


def job_analytics_backup(_first: bool) -> None:
    from _scripts.backup_analytics import backup

    db = Path(os.environ.get("ANALYTICS_DB", "/data/analytics.db"))
    out_dir = Path(os.environ.get("ANALYTICS_BACKUP_DIR", "/data/backups"))
    keep = _env_int("ANALYTICS_BACKUP_KEEP", 14)
    if not db.exists():
        log.info("analytics_backup: no database yet at %s; skipping", db)
        return
    path = backup(db, out_dir, keep)
    log.info("analytics_backup: wrote %s (%s KB)", path, path.stat().st_size // 1024)


def job_content_stats(_first: bool) -> None:
    # Prefer a writable volume path in Docker; fall back to the repo _index/ for local runs.
    out = os.environ.get("CONTENT_STATS_FILE", "/data/content-stats.json")
    os.environ["CONTENT_STATS_FILE"] = out
    from _scripts import content_stats as cs

    cs.OUT = Path(out)
    cs.OUT.parent.mkdir(parents=True, exist_ok=True)
    cs.main()
    log.info("content_stats: wrote %s", cs.OUT)


JOBS: dict[str, tuple[int, Callable[[bool], None]]] = {
    "cache": (_env_int("CACHE_EVERY", 3600), job_cache),
    "analytics_backup": (_env_int("BACKUP_EVERY", 86400), job_analytics_backup),
    "content_stats": (_env_int("STATS_EVERY", 86400), job_content_stats),
}


def selected_jobs() -> dict[str, tuple[int, Callable[[bool], None]]]:
    raw = os.environ.get("JOBS", "cache,analytics_backup,content_stats")
    names = [n.strip() for n in raw.split(",") if n.strip()]
    unknown = [n for n in names if n not in JOBS]
    if unknown:
        raise SystemExit(f"Unknown job(s): {', '.join(unknown)}. Known: {', '.join(JOBS)}")
    return {n: JOBS[n] for n in names}


def main() -> int:
    jobs = selected_jobs()
    log.info("worker starting jobs=%s", list(jobs))
    # next_due=0 → run immediately on boot (deploy relies on this instead of deploy.sh)
    next_due = {name: 0.0 for name in jobs}
    first = {name: True for name in jobs}

    while True:
        now = time.time()
        for name, (every, fn) in jobs.items():
            if now < next_due[name]:
                continue
            log.info("job %s: start", name)
            try:
                fn(first[name])
                first[name] = False
                log.info("job %s: ok", name)
            except Exception:
                log.error("job %s: failed\n%s", name, traceback.format_exc())
            # Schedule from now so a slow job does not pile up ticks
            next_due[name] = time.time() + max(30, every)
        time.sleep(5)


if __name__ == "__main__":
    raise SystemExit(main())

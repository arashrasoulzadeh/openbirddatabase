#!/usr/bin/env python3
"""Back up the analytics database (SQLite) to a compressed file and keep only the newest copies.

Uses SQLite's online backup API, so the copy is consistent even while the API is writing events.

    python _scripts/backup_analytics.py --db /data/analytics.db --out-dir /data/backups --keep 14
    python _scripts/backup_analytics.py --restore /data/backups/analytics-20261016-020000.db.gz --db /data/analytics.db

On the server use ./backup.sh, which runs this inside the api container and copies the files to ./backups.
"""

import argparse
import gzip
import shutil
import sqlite3
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

PREFIX = "analytics-"
SUFFIX = ".db.gz"


def backup(db: Path, out_dir: Path, keep: int = 14, now: datetime | None = None) -> Path:
    """Write out_dir/analytics-<UTC timestamp>.db.gz and delete all but the newest `keep` backups."""
    if not db.exists():
        raise FileNotFoundError(f"No analytics database at {db} (nothing has been collected yet)")
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = (now or datetime.now(timezone.utc)).strftime("%Y%m%d-%H%M%S")
    target = out_dir / f"{PREFIX}{stamp}{SUFFIX}"

    with tempfile.TemporaryDirectory() as tmp:
        copy = Path(tmp) / "snapshot.db"
        source = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        dest = sqlite3.connect(copy)
        try:
            source.backup(dest)
        finally:
            dest.close()
            source.close()
        with open(copy, "rb") as raw, gzip.open(target, "wb", compresslevel=6) as packed:
            shutil.copyfileobj(raw, packed)

    old = sorted(out_dir.glob(f"{PREFIX}*{SUFFIX}"))[:-keep] if keep > 0 else []
    for path in old:
        path.unlink()
    return target


def restore(backup_file: Path, db: Path) -> None:
    """Replace the database with a backup. Stop the API first (docker compose stop api)."""
    db.parent.mkdir(parents=True, exist_ok=True)
    for leftover in (Path(f"{db}-wal"), Path(f"{db}-shm")):
        leftover.unlink(missing_ok=True)  # stale write-ahead files would corrupt the restored copy
    with gzip.open(backup_file, "rb") as packed, open(db, "wb") as out:
        shutil.copyfileobj(packed, out)
    check = sqlite3.connect(db)
    try:
        if check.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise RuntimeError("The restored database failed its integrity check")
    finally:
        check.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--db", type=Path, default=Path("/data/analytics.db"))
    parser.add_argument("--out-dir", type=Path, default=Path("/data/backups"))
    parser.add_argument("--keep", type=int, default=14, help="how many backups to keep (default 14)")
    parser.add_argument("--restore", type=Path, help="restore this backup file into --db instead of backing up")
    args = parser.parse_args()
    try:
        if args.restore:
            restore(args.restore, args.db)
            print(f"Restored {args.restore} to {args.db}")
        else:
            path = backup(args.db, args.out_dir, args.keep)
            print(f"Backup written: {path} ({path.stat().st_size // 1024} KB)")
    except (FileNotFoundError, RuntimeError, sqlite3.Error) as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

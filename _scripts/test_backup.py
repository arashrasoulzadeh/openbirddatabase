"""Backup/restore tests for the analytics database (temporary files only)."""

import gzip
import sqlite3
from datetime import datetime, timedelta, timezone

import pytest

from _scripts.backup_analytics import backup, restore


def make_db(path, rows):
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE events (id INTEGER PRIMARY KEY, type TEXT)")
    conn.executemany("INSERT INTO events (type) VALUES (?)", [(r,) for r in rows])
    conn.commit()
    conn.close()


def rows(path):
    conn = sqlite3.connect(path)
    try:
        return [r[0] for r in conn.execute("SELECT type FROM events ORDER BY id")]
    finally:
        conn.close()


def test_backup_is_a_consistent_compressed_copy(tmp_path):
    db = tmp_path / "analytics.db"
    make_db(db, ["pageview", "search"])
    target = backup(db, tmp_path / "backups")
    assert target.name.startswith("analytics-") and target.name.endswith(".db.gz")
    restored = tmp_path / "copy.db"
    restored.write_bytes(gzip.open(target, "rb").read())
    assert rows(restored) == ["pageview", "search"]


def test_backup_works_while_the_database_is_in_use(tmp_path):
    db = tmp_path / "analytics.db"
    make_db(db, ["pageview"])
    writer = sqlite3.connect(db)
    writer.execute("PRAGMA journal_mode=WAL")
    writer.execute("INSERT INTO events (type) VALUES ('search')")  # uncommitted write in progress
    target = backup(db, tmp_path / "backups")
    writer.commit()
    writer.close()
    copy = tmp_path / "copy.db"
    copy.write_bytes(gzip.open(target, "rb").read())
    assert rows(copy) == ["pageview"]  # a clean snapshot, never half-written data


def test_only_the_newest_backups_are_kept(tmp_path):
    db = tmp_path / "analytics.db"
    make_db(db, ["pageview"])
    start = datetime(2026, 10, 1, tzinfo=timezone.utc)
    for day in range(5):
        backup(db, tmp_path / "backups", keep=3, now=start + timedelta(days=day))
    names = sorted(p.name for p in (tmp_path / "backups").iterdir())
    assert names == ["analytics-20261003-000000.db.gz", "analytics-20261004-000000.db.gz", "analytics-20261005-000000.db.gz"]


def test_restore_replaces_the_database_and_clears_stale_wal_files(tmp_path):
    db = tmp_path / "analytics.db"
    make_db(db, ["pageview", "search"])
    target = backup(db, tmp_path / "backups")
    make_db(tmp_path / "other.db", ["x"])
    (tmp_path / "other.db").replace(db)  # the live database is now different
    (tmp_path / "analytics.db-wal").write_bytes(b"stale")
    restore(target, db)
    assert rows(db) == ["pageview", "search"]
    assert not (tmp_path / "analytics.db-wal").exists()


def test_missing_database_is_reported_clearly(tmp_path):
    with pytest.raises(FileNotFoundError, match="nothing has been collected"):
        backup(tmp_path / "missing.db", tmp_path / "backups")

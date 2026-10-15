"""First-party, privacy-friendly analytics.

Events are stored in SQLite (a file on a Docker volume, no extra service) and aggregated on demand.
No IP addresses or user agents are stored; visitors and sessions are random ids made by the browser.
Bots and visitors sending Do-Not-Track / Global Privacy Control are ignored.

Endpoints (mounted under /analytics):
  POST /event               collect events (public; CORS-limited to the website)
  GET  /dashboard           everything the dashboard page shows
  GET  /pages, /page        per-page statistics
  GET  /birds/{name}        statistics for one bird
  GET  /live                visitors in the last 5 minutes and the latest events
  GET  /content             content statistics (birds added, language coverage, completeness)

Environment: ANALYTICS_DB, ANALYTICS_ENABLED, ANALYTICS_TOKEN (protects the GET endpoints), ANALYTICS_RETENTION_DAYS
"""

import json
import os
import re
import secrets
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import unquote

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, Response

DB_PATH = Path(os.environ.get("ANALYTICS_DB", "data/analytics.db"))
ENABLED = os.environ.get("ANALYTICS_ENABLED", "true").lower() not in ("0", "false", "no")
TOKEN = os.environ.get("ANALYTICS_TOKEN", "").strip()
RETENTION_DAYS = int(os.environ.get("ANALYTICS_RETENTION_DAYS", "400"))
CONTENT_STATS_FILE = Path(os.environ.get("CONTENT_STATS_FILE", "_index/content-stats.json"))

EVENT_TYPES = {
    "pageview", "page_leave", "bird_click", "search", "filter",
    "language_change", "tab_view", "load_more", "random_bird",
}
MAX_EVENTS_PER_REQUEST = 50
MAX_BODY_BYTES = 64 * 1024
RATE_LIMIT_PER_MINUTE = 240
IDLE_CAP_MS = 30 * 60 * 1000  # a tab left open for hours should not skew "time on page"

BOT_RE = re.compile(
    r"bot|crawl|spider|slurp|facebookexternalhit|preview|headless|lighthouse|curl|wget|python-requests|monitor|uptime",
    re.I,
)

router = APIRouter()

_lock = threading.Lock()
_conn: Optional[sqlite3.Connection] = None
_conn_path: Optional[Path] = None
_rate: Dict[str, List[float]] = {}
_last_purge = 0.0
_content_cache: Dict[str, Any] = {}


# --------------------------------------------------------------------------- storage

def _connection() -> sqlite3.Connection:
    """Open the database lazily (re-opens if the configured path changed, e.g. in tests)."""
    global _conn, _conn_path
    if _conn is None or _conn_path != DB_PATH:
        if _conn is not None:
            _conn.close()
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        _conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _conn.execute("PRAGMA journal_mode=WAL")
        _conn.execute("PRAGMA synchronous=NORMAL")
        _conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts INTEGER NOT NULL,
                type TEXT NOT NULL,
                path TEXT,
                visitor TEXT,
                session TEXT,
                lang TEXT,
                bird TEXT,
                query TEXT,
                source TEXT,
                value REAL,
                props TEXT,
                device TEXT,
                referrer TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_events_ts ON events(ts);
            CREATE INDEX IF NOT EXISTS idx_events_type_ts ON events(type, ts);
            CREATE INDEX IF NOT EXISTS idx_events_bird ON events(bird);
            """
        )
        _conn_path = DB_PATH
    return _conn


def _query(sql: str, params: tuple = ()) -> List[sqlite3.Row]:
    with _lock:
        return _connection().execute(sql, params).fetchall()


def _purge_old() -> None:
    """Delete raw events past the retention period (checked at most once a day)."""
    global _last_purge
    now = time.time()
    if now - _last_purge < 86400:
        return
    _last_purge = now
    with _lock:
        conn = _connection()
        conn.execute("DELETE FROM events WHERE ts < ?", (int(now - RETENTION_DAYS * 86400),))
        conn.commit()


# --------------------------------------------------------------------------- collection

def _clip(value: Any, limit: int) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text[:limit] if text else None


def _device(user_agent: str) -> str:
    ua = user_agent.lower()
    if "ipad" in ua or "tablet" in ua:
        return "tablet"
    if "mobi" in ua or "android" in ua or "iphone" in ua:
        return "mobile"
    return "desktop"


def _rate_key(request: Request, events: list) -> str:
    """Who the rate limit applies to: the real client IP when the proxy forwards it, otherwise the visitor id.
    (Without X-Forwarded-For every request appears to come from the proxy, so an IP key would be shared by everyone.)"""
    forwarded = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    if forwarded:
        return forwarded
    first = events[0] if events and isinstance(events[0], dict) else {}
    return "v:" + str(first.get("visitor") or (request.client.host if request.client else "unknown"))


def _rate_limited(ip: str, count: int) -> bool:
    now = time.time()
    hits = [t for t in _rate.get(ip, []) if now - t < 60]
    if len(hits) + count > RATE_LIMIT_PER_MINUTE:
        _rate[ip] = hits
        return True
    hits.extend([now] * count)
    _rate[ip] = hits
    if len(_rate) > 5000:  # keep the table small
        for key in [k for k, v in _rate.items() if not v or now - v[-1] > 60]:
            _rate.pop(key, None)
    return False


def _normalize(raw: Any, now: int, device: str) -> Optional[tuple]:
    if not isinstance(raw, dict) or raw.get("type") not in EVENT_TYPES:
        return None
    etype = raw["type"]
    path = _clip(raw.get("path"), 200)
    bird = _clip(raw.get("bird"), 120)
    if not bird and path and path.startswith("/species/") and etype in ("pageview", "page_leave"):
        bird = _clip(unquote(path[len("/species/"):]), 120)
    value = raw.get("value")
    value = float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None
    props = raw.get("props")
    props_json = json.dumps(props, ensure_ascii=False)[:500] if isinstance(props, (dict, list)) else None
    return (
        now, etype, path, _clip(raw.get("visitor"), 64), _clip(raw.get("session"), 64),
        _clip(raw.get("lang"), 8), bird, _clip(raw.get("query"), 200), _clip(raw.get("source"), 40),
        value, props_json, device, _clip(raw.get("referrer"), 100),
    )


@router.post("/event", status_code=204)
async def collect(request: Request) -> Response:
    """Collect one event or a batch. The body is parsed as JSON whatever its content type, so browsers can use
    navigator.sendBeacon with text/plain and avoid a CORS preflight."""
    if not ENABLED:
        return Response(status_code=204)
    user_agent = request.headers.get("user-agent", "")
    if BOT_RE.search(user_agent) or request.headers.get("dnt") == "1" or request.headers.get("sec-gpc") == "1":
        return Response(status_code=204)

    body = await request.body()
    if len(body) > MAX_BODY_BYTES:
        raise HTTPException(status_code=413, detail="Body too large")
    try:
        payload = json.loads(body or b"null")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    if isinstance(payload, dict) and isinstance(payload.get("events"), list):
        payload = payload["events"]
    events = payload if isinstance(payload, list) else [payload]
    events = events[:MAX_EVENTS_PER_REQUEST]

    if _rate_limited(_rate_key(request, events), len(events)):
        raise HTTPException(status_code=429, detail="Too many events")

    now, device = int(time.time()), _device(user_agent)
    rows = [r for r in (_normalize(e, now, device) for e in events) if r]
    if rows:
        with _lock:
            conn = _connection()
            conn.executemany(
                "INSERT INTO events (ts,type,path,visitor,session,lang,bird,query,source,value,props,device,referrer) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                rows,
            )
            conn.commit()
        _purge_old()
    return Response(status_code=204)


# --------------------------------------------------------------------------- access control

def require_token(authorization: Optional[str] = Header(None), token: Optional[str] = Query(None)) -> None:
    """When ANALYTICS_TOKEN is set the read endpoints need it (Authorization: Bearer ... or ?token=...)."""
    if not TOKEN:
        return
    supplied = token or (authorization[7:] if authorization and authorization.lower().startswith("bearer ") else "")
    if not secrets.compare_digest(supplied.encode(), TOKEN.encode()):
        raise HTTPException(status_code=401, detail="Analytics token required")


# --------------------------------------------------------------------------- aggregation helpers

def _range(days: int) -> tuple:
    now = int(time.time())
    return now - days * 86400, now


def _step(days: int) -> int:
    return 3600 if days <= 7 else 86400


def _series(where: str, params: tuple, since: int, until: int, step: int, distinct: Optional[str] = None) -> List[dict]:
    """Counts per time bucket with empty buckets filled in, so charts have no gaps."""
    expr = f"COUNT(DISTINCT {distinct})" if distinct else "COUNT(*)"
    rows = _query(
        f"SELECT ts - ts % ? AS b, {expr} AS n FROM events WHERE ts >= ? AND ts <= ? AND {where} GROUP BY b",
        (step, since, until, *params),
    )
    counts = {r["b"]: r["n"] for r in rows}
    start = since - since % step
    return [{"t": t, "v": counts.get(t, 0)} for t in range(start, until + 1, step)]


def _count(where: str, params: tuple, since: int, until: int, distinct: Optional[str] = None) -> int:
    expr = f"COUNT(DISTINCT {distinct})" if distinct else "COUNT(*)"
    return _query(f"SELECT {expr} AS n FROM events WHERE ts >= ? AND ts <= ? AND {where}", (since, until, *params))[0]["n"]


def _avg_time(where: str, params: tuple, since: int, until: int) -> Optional[float]:
    row = _query(
        "SELECT AVG(MIN(value, ?)) AS a FROM events "
        f"WHERE type='page_leave' AND value >= 500 AND ts >= ? AND ts <= ? AND {where}",
        (IDLE_CAP_MS, since, until, *params),
    )[0]
    return round(row["a"] / 1000, 1) if row["a"] is not None else None


def _top(sql: str, params: tuple) -> List[dict]:
    return [dict(r) for r in _query(sql, params)]


def _change(current: int, previous: int) -> Optional[float]:
    return round((current - previous) / previous * 100, 1) if previous else None


def content_stats() -> Optional[dict]:
    """Content statistics computed by _scripts/content_stats.py (re-read when the file changes)."""
    try:
        mtime = CONTENT_STATS_FILE.stat().st_mtime
    except OSError:
        return None
    if _content_cache.get("mtime") != mtime:
        _content_cache.update(mtime=mtime, data=json.loads(CONTENT_STATS_FILE.read_text(encoding="utf-8")))
    return _content_cache["data"]


# --------------------------------------------------------------------------- queries

def summary(days: int) -> dict:
    since, until = _range(days)
    prev_since, prev_until = since - days * 86400, since - 1
    metrics = {
        "pageviews": ("type='pageview'", None),
        "visitors": ("type='pageview'", "visitor"),
        "sessions": ("type='pageview'", "session"),
        "searches": ("type='search' AND query IS NOT NULL", None),
        "bird_clicks": ("type='bird_click'", None),
        "bird_views": ("type='pageview' AND bird IS NOT NULL", None),
    }
    out: Dict[str, Any] = {}
    for name, (where, distinct) in metrics.items():
        now_value = _count(where, (), since, until, distinct)
        out[name] = {"value": now_value, "previous": _count(where, (), prev_since, prev_until, distinct)}
        out[name]["change"] = _change(now_value, out[name]["previous"])
    out["zero_result_searches"] = _count("type='search' AND query IS NOT NULL AND value = 0", (), since, until)
    out["language_changes"] = _count("type='language_change'", (), since, until)
    out["avg_time_on_page"] = _avg_time("1=1", (), since, until)
    single = _query(
        "SELECT COUNT(*) AS n FROM (SELECT session FROM events WHERE type='pageview' AND ts >= ? AND ts <= ? "
        "AND session IS NOT NULL GROUP BY session HAVING COUNT(*) = 1)",
        (since, until),
    )[0]["n"]
    sessions = out["sessions"]["value"]
    out["bounce_rate"] = round(single / sessions * 100, 1) if sessions else None
    return out


def pages_list(days: int, limit: int = 50) -> List[dict]:
    """Views, visitors and average time on page for every page, busiest first."""
    since, until = _range(days)
    return _top(
        "SELECT p.path, p.views, p.visitors, ROUND(t.avg / 1000.0, 1) AS avg_time FROM ("
        "  SELECT path, COUNT(*) AS views, COUNT(DISTINCT visitor) AS visitors FROM events"
        "  WHERE type='pageview' AND ts >= ? AND ts <= ? GROUP BY path ORDER BY views DESC LIMIT ?) p "
        "LEFT JOIN ("
        "  SELECT path, AVG(MIN(value, ?)) AS avg FROM events"
        "  WHERE type='page_leave' AND value >= 500 AND ts >= ? AND ts <= ? GROUP BY path) t ON t.path = p.path "
        "ORDER BY p.views DESC",
        (since, until, limit, IDLE_CAP_MS, since, until),
    )


def dashboard(days: int) -> dict:
    since, until = _range(days)
    step = _step(days)
    series = {
        "pageviews": _series("type='pageview'", (), since, until, step),
        "visitors": _series("type='pageview'", (), since, until, step, "visitor"),
        "searches": _series("type='search' AND query IS NOT NULL", (), since, until, step),
        "bird_clicks": _series("type='bird_click'", (), since, until, step),
        "bird_views": _series("type='pageview' AND bird IS NOT NULL", (), since, until, step),
        "home_views": _series("type='pageview' AND path='/'", (), since, until, step),
    }
    base = "ts >= ? AND ts <= ?"
    window = (since, until)
    top = {
        "birds": _top(
            "SELECT bird AS name, COUNT(*) AS views, COUNT(DISTINCT visitor) AS visitors FROM events "
            f"WHERE type='pageview' AND bird IS NOT NULL AND {base} GROUP BY bird ORDER BY views DESC LIMIT 15", window),
        "bird_clicks": _top(
            "SELECT bird AS name, COUNT(*) AS clicks FROM events "
            f"WHERE type='bird_click' AND bird IS NOT NULL AND {base} GROUP BY bird ORDER BY clicks DESC LIMIT 15", window),
        "bird_click_sources": _top(
            "SELECT COALESCE(source,'unknown') AS name, COUNT(*) AS count FROM events "
            f"WHERE type='bird_click' AND {base} GROUP BY name ORDER BY count DESC", window),
        "searches": _top(
            "SELECT LOWER(query) AS query, COUNT(*) AS count, ROUND(AVG(value),1) AS avg_results FROM events "
            f"WHERE type='search' AND query IS NOT NULL AND {base} GROUP BY LOWER(query) ORDER BY count DESC LIMIT 15", window),
        "zero_result_searches": _top(
            "SELECT LOWER(query) AS query, COUNT(*) AS count FROM events "
            f"WHERE type='search' AND query IS NOT NULL AND value = 0 AND {base} "
            "GROUP BY LOWER(query) ORDER BY count DESC LIMIT 10", window),
        "pages": pages_list(days, 20),
        "languages": _top(
            "SELECT COALESCE(lang,'unknown') AS name, COUNT(DISTINCT visitor) AS visitors, COUNT(*) AS views FROM events "
            f"WHERE type='pageview' AND {base} GROUP BY name ORDER BY visitors DESC", window),
        "language_switches": _top(
            "SELECT COALESCE(source,'?') || ' > ' || COALESCE(query,'?') AS name, COUNT(*) AS count FROM events "
            f"WHERE type='language_change' AND {base} GROUP BY name ORDER BY count DESC LIMIT 10", window),
        "devices": _top(
            "SELECT COALESCE(device,'unknown') AS name, COUNT(*) AS views FROM events "
            f"WHERE type='pageview' AND {base} GROUP BY name ORDER BY views DESC", window),
        "referrers": _top(
            "SELECT referrer AS name, COUNT(*) AS views FROM events "
            f"WHERE type='pageview' AND referrer IS NOT NULL AND {base} GROUP BY referrer ORDER BY views DESC LIMIT 10", window),
        "filters": _top(
            "SELECT source AS field, query AS value, COUNT(*) AS count FROM events "
            f"WHERE type='filter' AND source IS NOT NULL AND {base} GROUP BY source, query ORDER BY count DESC LIMIT 15", window),
        "events": _top(f"SELECT type AS name, COUNT(*) AS count FROM events WHERE {base} GROUP BY type ORDER BY count DESC", window),
    }
    hours = {r["h"]: r["n"] for r in _query(
        "SELECT CAST(strftime('%H', ts, 'unixepoch') AS INTEGER) AS h, COUNT(*) AS n FROM events "
        f"WHERE type='pageview' AND {base} GROUP BY h", window)}
    weekdays = {r["d"]: r["n"] for r in _query(
        "SELECT CAST(strftime('%w', ts, 'unixepoch') AS INTEGER) AS d, COUNT(*) AS n FROM events "
        f"WHERE type='pageview' AND {base} GROUP BY d", window)}
    return {
        "days": days,
        "step": step,
        "generated_at": until,
        "summary": summary(days),
        "series": series,
        "top": top,
        "by_hour_of_day": [hours.get(h, 0) for h in range(24)],
        "by_weekday": [weekdays.get(d, 0) for d in range(7)],  # 0 = Sunday
        "live": live(),
        "content": content_stats(),
    }


def page_stats(path: str, days: int) -> dict:
    since, until = _range(days)
    where, params = "path = ?", (path,)
    return {
        "path": path,
        "days": days,
        "views": _count("type='pageview' AND " + where, params, since, until),
        "visitors": _count("type='pageview' AND " + where, params, since, until, "visitor"),
        "avg_time_on_page": _avg_time(where, params, since, until),
        "series": _series("type='pageview' AND " + where, params, since, until, _step(days)),
        "referrers": _top(
            "SELECT referrer AS name, COUNT(*) AS views FROM events WHERE type='pageview' AND path = ? "
            "AND referrer IS NOT NULL AND ts >= ? AND ts <= ? GROUP BY referrer ORDER BY views DESC LIMIT 10",
            (path, since, until)),
    }


def bird_stats(name: str, days: int) -> dict:
    since, until = _range(days)
    return {
        "bird": name,
        "days": days,
        "views": _count("type='pageview' AND bird = ?", (name,), since, until),
        "visitors": _count("type='pageview' AND bird = ?", (name,), since, until, "visitor"),
        "clicks": _count("type='bird_click' AND bird = ?", (name,), since, until),
        "avg_time_on_page": _avg_time("bird = ?", (name,), since, until),
        "views_series": _series("type='pageview' AND bird = ?", (name,), since, until, _step(days)),
        "clicks_series": _series("type='bird_click' AND bird = ?", (name,), since, until, _step(days)),
        "click_sources": _top(
            "SELECT COALESCE(source,'unknown') AS name, COUNT(*) AS count FROM events WHERE type='bird_click' "
            "AND bird = ? AND ts >= ? AND ts <= ? GROUP BY name ORDER BY count DESC", (name, since, until)),
        "found_by_searches": _top(
            "SELECT LOWER(query) AS query, COUNT(*) AS count FROM events WHERE type='bird_click' AND bird = ? "
            "AND query IS NOT NULL AND ts >= ? AND ts <= ? GROUP BY LOWER(query) ORDER BY count DESC LIMIT 10",
            (name, since, until)),
    }


def live() -> dict:
    now = int(time.time())
    active = _query(
        "SELECT COUNT(DISTINCT visitor) AS n FROM events WHERE ts >= ? AND visitor IS NOT NULL", (now - 300,))[0]["n"]
    latest = _top(
        "SELECT ts, type, path, bird, query, lang, device FROM events WHERE type != 'page_leave' "
        "ORDER BY id DESC LIMIT 20", ())
    return {"active_visitors": active, "latest": latest}


# --------------------------------------------------------------------------- read endpoints

guard = [Depends(require_token)]


@router.get("/dashboard", dependencies=guard)
def get_dashboard(days: int = Query(30, ge=1, le=365)):
    return dashboard(days)


@router.get("/pages", dependencies=guard)
def get_pages(days: int = Query(30, ge=1, le=365), limit: int = Query(50, ge=1, le=200)):
    return {"days": days, "pages": pages_list(days, limit)}


@router.get("/page", dependencies=guard)
def get_page(path: str = Query(..., max_length=200), days: int = Query(30, ge=1, le=365)):
    return page_stats(path, days)


@router.get("/birds/{name}", dependencies=guard)
def get_bird(name: str, days: int = Query(30, ge=1, le=365)):
    return bird_stats(name, days)


@router.get("/live", dependencies=guard)
def get_live():
    return live()


@router.get("/content", dependencies=guard)
def get_content():
    data = content_stats()
    if data is None:
        raise HTTPException(status_code=404, detail="Run python _scripts/content_stats.py to generate it")
    return data

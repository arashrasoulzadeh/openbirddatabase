"""Analytics tests: collection rules, privacy filters, aggregation and access control (temporary SQLite database)."""

import json
import time

import pytest
from fastapi.testclient import TestClient

import _scripts.analytics as analytics
import _scripts.api as api

BROWSER = {"user-agent": "Mozilla/5.0 (X11; Linux x86_64) Firefox/120.0", "content-type": "text/plain;charset=UTF-8"}


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(analytics, "DB_PATH", tmp_path / "analytics.db")
    monkeypatch.setattr(analytics, "TOKEN", "")
    monkeypatch.setattr(analytics, "ENABLED", True)
    monkeypatch.setattr(analytics, "CONTENT_STATS_FILE", tmp_path / "content-stats.json")
    monkeypatch.setattr(analytics, "_rate", {})
    monkeypatch.setattr(analytics, "_last_purge", time.time())
    monkeypatch.setattr(analytics, "_conn", None)
    return TestClient(api.app)


def send(client, events, headers=None):
    body = json.dumps({"events": events} if isinstance(events, list) else events)
    return client.post("/analytics/event", content=body, headers=headers or BROWSER)


def ev(type_, **kw):
    return {"type": type_, "visitor": kw.pop("visitor", "v1"), "session": kw.pop("session", "s1"), "lang": "en", **kw}


def insert_at(ts, **kw):
    """Insert an event with an explicit timestamp (to build history)."""
    row = {"type": "pageview", "path": "/", "visitor": "v1", "session": "s1", "lang": "en", "device": "desktop", **kw}
    cols = ["ts"] + list(row)
    with analytics._lock:
        conn = analytics._connection()
        conn.execute(f"INSERT INTO events ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})", [ts, *row.values()])
        conn.commit()


def test_collects_events_and_summarises(client):
    assert send(client, [
        ev("pageview", path="/", visitor="a", session="s1"),
        ev("pageview", path="/species/Parus%20major", visitor="a", session="s1"),
        ev("pageview", path="/", visitor="b", session="s2"),
        ev("bird_click", bird="Parus major", source="search", query="tit", visitor="a"),
        ev("search", query="tit", value=12, visitor="a"),
        ev("search", query="zzzz", value=0, visitor="b", session="s2"),
    ]).status_code == 204
    data = client.get("/analytics/dashboard?days=1").json()
    s = data["summary"]
    assert s["pageviews"]["value"] == 3
    assert s["visitors"]["value"] == 2
    assert s["sessions"]["value"] == 2
    assert s["bird_clicks"]["value"] == 1
    assert s["bird_views"]["value"] == 1
    assert s["searches"]["value"] == 2
    assert s["zero_result_searches"] == 1
    assert s["bounce_rate"] == 50.0  # session s2 viewed one page only
    assert data["top"]["birds"][0]["name"] == "Parus major"  # derived from the /species/ path
    assert data["top"]["zero_result_searches"][0]["query"] == "zzzz"
    assert data["top"]["bird_click_sources"][0] == {"name": "search", "count": 1}


def test_series_has_no_gaps(client):
    send(client, [ev("pageview", path="/")])
    series = client.get("/analytics/dashboard?days=1").json()["series"]["pageviews"]
    assert len(series) >= 24                       # hourly buckets for a 1-day window
    assert sum(p["v"] for p in series) == 1
    assert len(client.get("/analytics/dashboard?days=30").json()["series"]["pageviews"]) >= 30  # daily


def test_time_on_page_ignores_idle_tabs(client):
    send(client, [
        ev("page_leave", path="/", value=10_000),
        ev("page_leave", path="/", value=20_000),
        ev("page_leave", path="/", value=999_999_999),  # tab left open: capped at 30 minutes
        ev("page_leave", path="/", value=100),          # too short to be a real visit
    ])
    avg = client.get("/analytics/dashboard?days=1").json()["summary"]["avg_time_on_page"]
    assert avg == round((10 + 20 + 1800) / 3, 1)


def test_bots_dnt_and_invalid_events_are_ignored(client):
    page = [ev("pageview", path="/")]
    assert send(client, page, {**BROWSER, "user-agent": "Googlebot/2.1"}).status_code == 204
    assert send(client, page, {**BROWSER, "dnt": "1"}).status_code == 204
    assert send(client, page, {**BROWSER, "sec-gpc": "1"}).status_code == 204
    assert send(client, [{"type": "hack"}, "nope", ev("pageview", path="/")]).status_code == 204
    assert client.get("/analytics/dashboard?days=1").json()["summary"]["pageviews"]["value"] == 1


def test_bad_requests_and_limits(client):
    assert client.post("/analytics/event", content="{not json", headers=BROWSER).status_code == 400
    assert client.post("/analytics/event", content="x" * (70 * 1024), headers=BROWSER).status_code == 413
    ok = [ev("pageview", path="/")] * 50
    statuses = [send(client, ok).status_code for _ in range(6)]
    assert statuses[:4] == [204] * 4 and 429 in statuses   # 240 events per minute per client


def test_rate_limit_is_per_client_not_global(client):
    batch = lambda visitor: [ev("pageview", path="/", visitor=visitor)] * 50
    # no X-Forwarded-For: limited per visitor id, so one noisy visitor does not block the others
    assert [send(client, batch("noisy")).status_code for _ in range(6)].count(429) >= 1
    assert send(client, batch("quiet")).status_code == 204
    # behind a proxy that forwards the client address: limited per address
    a = {**BROWSER, "x-forwarded-for": "203.0.113.5, 10.0.0.1"}
    b = {**BROWSER, "x-forwarded-for": "198.51.100.7"}
    assert [send(client, batch("x"), a).status_code for _ in range(6)].count(429) >= 1
    assert send(client, batch("y"), b).status_code == 204


def test_disabled_collects_nothing(client, monkeypatch):
    monkeypatch.setattr(analytics, "ENABLED", False)
    assert send(client, [ev("pageview", path="/")]).status_code == 204
    assert client.get("/analytics/dashboard?days=1").json()["summary"]["pageviews"]["value"] == 0


def test_values_are_clipped(client):
    send(client, [ev("search", query="q" * 1000, value=1)])
    query = client.get("/analytics/dashboard?days=1").json()["top"]["searches"][0]["query"]
    assert len(query) == 200


def test_period_comparison(client):
    now = int(time.time())
    send(client, [ev("pageview", path="/")] * 2)
    insert_at(now - 40 * 3600)  # previous 1-day window (24-48 h ago)
    pv = client.get("/analytics/dashboard?days=1").json()["summary"]["pageviews"]
    assert pv["value"] == 2 and pv["previous"] == 1 and pv["change"] == 100.0


def test_page_and_bird_endpoints(client):
    send(client, [
        ev("pageview", path="/species/Parus%20major", visitor="a", referrer="google.com"),
        ev("page_leave", path="/species/Parus%20major", value=30_000),
        ev("bird_click", bird="Parus major", source="taxonomy", query="tit"),
    ])
    page = client.get("/analytics/page", params={"path": "/species/Parus%20major", "days": 1}).json()
    assert page["views"] == 1 and page["avg_time_on_page"] == 30.0 and page["referrers"][0]["name"] == "google.com"
    bird = client.get("/analytics/birds/Parus major?days=1").json()
    assert bird["views"] == 1 and bird["clicks"] == 1
    assert bird["click_sources"][0]["name"] == "taxonomy" and bird["found_by_searches"][0]["query"] == "tit"
    pages = client.get("/analytics/pages?days=1").json()["pages"]
    assert pages[0]["path"] == "/species/Parus%20major" and pages[0]["avg_time"] == 30.0


def test_live_and_time_of_day(client):
    send(client, [ev("pageview", path="/", visitor="a"), ev("pageview", path="/", visitor="b")])
    data = client.get("/analytics/dashboard?days=1").json()
    assert data["live"]["active_visitors"] == 2
    assert sum(data["by_hour_of_day"]) == 2 and sum(data["by_weekday"]) == 2


def test_read_endpoints_need_the_token_when_configured(client, monkeypatch):
    monkeypatch.setattr(analytics, "TOKEN", "s3cret")
    assert client.get("/analytics/dashboard").status_code == 401
    assert client.get("/analytics/dashboard?token=wrong").status_code == 401
    assert client.get("/analytics/dashboard?token=s3cret").status_code == 200
    assert client.get("/analytics/dashboard", headers={"Authorization": "Bearer s3cret"}).status_code == 200
    assert send(client, [ev("pageview", path="/")]).status_code == 204  # collecting stays public


def test_content_stats_endpoint(client, tmp_path):
    assert client.get("/analytics/content").status_code == 404
    (tmp_path / "content-stats.json").write_text(json.dumps({"total_species": 3}))
    assert client.get("/analytics/content").json() == {"total_species": 3}
    assert client.get("/analytics/dashboard?days=1").json()["content"] == {"total_species": 3}


def test_old_events_are_purged(client, monkeypatch):
    monkeypatch.setattr(analytics, "RETENTION_DAYS", 10)
    insert_at(int(time.time()) - 30 * 86400)
    monkeypatch.setattr(analytics, "_last_purge", 0.0)
    send(client, [ev("pageview", path="/")])
    left = analytics._query("SELECT COUNT(*) AS n FROM events")[0]["n"]
    assert left == 1

"""API resilience and speed: a stuck MeiliSearch must never freeze the API."""

import threading
import time

import pytest
from fastapi.testclient import TestClient

import _scripts.api as api


class HangingIndex:
    """A MeiliSearch index that takes far too long to answer (like one busy computing vectors)."""
    def search(self, *args, **kwargs):
        time.sleep(2)
        return {"hits": [], "estimatedTotalHits": 0}

    def get_embedders(self):
        time.sleep(2)


class HangingMeili:
    def index(self, name):
        return HangingIndex()


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(api, "redis_client", None)
    monkeypatch.setattr(api, "meili_client", HangingMeili())
    monkeypatch.setattr(api, "MEILI_TIMEOUT", 0.3)
    monkeypatch.setattr(api, "HYBRID_TIMEOUT", 0.2)
    monkeypatch.setattr(api, "_meili_down_until", 0.0)
    monkeypatch.setattr(api, "_hybrid_down_until", 0.0)
    monkeypatch.setattr(api, "_vector_state", {"ready": False, "checked": 0.0})
    # one event loop for the whole test, like a real server (a fresh loop per request would wait for stuck threads)
    with TestClient(api.app) as test_client:
        yield test_client


def test_a_hanging_meilisearch_falls_back_quickly(client):
    started = time.perf_counter()
    response = client.get("/search?q=great%20tit&limit=5")
    elapsed = time.perf_counter() - started
    assert response.status_code == 200
    assert response.json()["hits"], "the in-memory index answers when MeiliSearch does not"
    assert elapsed < 2, f"took {elapsed:.1f}s"


def test_after_a_failure_meilisearch_is_skipped_for_a_while(client):
    client.get("/search?q=owl")                      # trips the breakers
    started = time.perf_counter()
    for query in ("tit", "wren", "kite"):
        assert client.get(f"/search?q={query}").status_code == 200
    assert time.perf_counter() - started < 1.0       # no waiting on MeiliSearch any more


def test_health_does_not_wait_for_a_busy_meilisearch(client):
    started = time.perf_counter()
    body = client.get("/health").json()
    assert time.perf_counter() - started < 1.5
    assert body["status"] == "ok" and body["vector_search"] is False


def test_other_endpoints_stay_fast_while_a_search_is_stuck(client, monkeypatch):
    monkeypatch.setattr(api, "MEILI_TIMEOUT", 3.0)   # the stuck search holds a worker thread for a while
    monkeypatch.setattr(api, "HYBRID_TIMEOUT", 3.0)
    done = []
    thread = threading.Thread(target=lambda: done.append(client.get("/search?q=stuck").status_code))
    thread.start()
    time.sleep(0.3)                                  # the search is now waiting on MeiliSearch
    started = time.perf_counter()
    assert client.get("/species/Parus%20major?lang=en").status_code == 200
    assert client.get("/filters").status_code == 200
    assert time.perf_counter() - started < 1.5, "the event loop was blocked by the stuck search"
    thread.join(timeout=10)
    assert done == [200]


def test_fallback_search_matches_any_name_and_respects_filters(monkeypatch):
    monkeypatch.setattr(api, "meili_client", None)
    monkeypatch.setattr(api, "redis_client", None)
    c = TestClient(api.app)
    spanish = c.get("/search?q=carbonero&limit=100").json()
    assert spanish["total"] > 0 and all("carbonero" in str(h).lower() for h in spanish["hits"])
    assert c.get("/search?q=PARUS%20MAJOR").json()["hits"][0]["scientific_name"] == "Parus major"
    cr = c.get("/search?iucn_status=CR&limit=5").json()
    assert cr["total"] > 100 and {h["iucn_status"] for h in cr["hits"]} == {"CR"}
    assert "body_text" not in cr["hits"][0]


def test_slim_taxonomy_is_one_language_and_much_smaller(monkeypatch):
    monkeypatch.setattr(api, "redis_client", None)
    c = TestClient(api.app)
    full = c.get("/taxonomy")
    slim = c.get("/taxonomy?lang=es")
    assert len(slim.content) < len(full.content) / 2
    species = next(iter(next(iter(next(iter(slim.json().values())).values())).values()))[0]
    assert set(species) == {"scientific", "id", "name", "common_en"}
    assert slim.json() == c.get("/taxonomy?lang=es").json()
    assert c.get("/taxonomy?lang=xx").json() == full.json()  # unknown language: the full tree


def test_cacheable_endpoints_set_cache_control_and_timing(monkeypatch):
    monkeypatch.setattr(api, "redis_client", None)
    c = TestClient(api.app)
    assert "max-age=3600" in c.get("/taxonomy?lang=en").headers["cache-control"]
    assert "max-age=600" in c.get("/species/Parus%20major").headers["cache-control"]
    assert c.get("/random").headers["cache-control"] == "no-store"
    assert c.get("/health").headers["server-timing"].startswith("app;dur=")

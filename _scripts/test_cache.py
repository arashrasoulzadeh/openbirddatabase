"""Redis cache tests (uses an in-memory fake Redis; no server needed)."""

import json

import fakeredis
import fakeredis.aioredis
import pytest
from fastapi.testclient import TestClient

import _scripts.api as api
from _scripts import warm_cache
from _scripts.cache_utils import CACHE_PREFIX, sanitize, search_key, slug_of, species_key


@pytest.fixture
def client(monkeypatch):
    fake = fakeredis.aioredis.FakeRedis()
    monkeypatch.setattr(api, "redis_client", fake)
    monkeypatch.setattr(api, "meili_client", None)  # use the JSON index, not a MeiliSearch server
    return TestClient(api.app)


def test_species_is_cached_after_first_request(client):
    first = client.get("/species/Parus%20major?lang=en")
    second = client.get("/species/Parus%20major?lang=en")
    assert first.status_code == 200
    assert first.headers["x-cache"] == "MISS"
    assert second.headers["x-cache"] == "HIT"
    assert first.json() == second.json()
    assert first.json()["names"]["scientific"] == "Parus major"


def test_species_documents_carry_a_completeness_report(client):
    sp = client.get("/species/Parus%20major?lang=en").json()
    core = sp["completeness"]["core"]
    assert 0 < core["score"] < 1 and core["total"] == 56 and core["filled"] == round(core["score"] * 56)
    assert "demography" in core["missing"] and "habitat" in core["sections"]
    assert "expert_verified" in sp["completeness"]


def test_fa_and_en_share_one_entry(client):
    client.get("/species/Parus%20major?lang=fa")
    assert client.get("/species/Parus%20major?lang=en").headers["x-cache"] == "HIT"


def test_missing_species_is_404_and_not_cached(client):
    assert client.get("/species/Not%20a%20bird").status_code == 404
    assert client.get("/species/Not%20a%20bird").status_code == 404  # still a miss, never a cached error


def test_taxonomy_filters_and_stats_are_cached(client):
    for path in ("/taxonomy", "/filters", "/stats"):
        assert client.get(path).headers["x-cache"] == "MISS"
        assert client.get(path).headers["x-cache"] == "HIT"
    assert client.get("/stats").json()["total_species"] > 11000


def test_search_results_are_cached_and_identical(client):
    first = client.get("/search?q=great%20tit&limit=5").json()
    second = client.get("/search?q=great%20tit&limit=5").json()
    assert first == second and first["hits"]
    other = client.get("/search?q=great%20tit&limit=5&iucn_status=CR").json()
    assert other != first  # different filters use a different cache entry


def test_api_still_works_when_redis_is_down(monkeypatch):
    class Broken:
        async def get(self, *a, **k):
            raise ConnectionError("redis down")
        set = ping = get

    monkeypatch.setattr(api, "redis_client", Broken())
    monkeypatch.setattr(api, "meili_client", None)
    c = TestClient(api.app)
    assert c.get("/species/Parus%20major?lang=en").status_code == 200
    assert c.get("/search?q=tit").status_code == 200
    assert c.get("/health").json()["cache"] is False


def test_warmer_writes_the_keys_the_api_reads(tmp_path, monkeypatch):
    birds = tmp_path / "birds" / "x" / "y"
    birds.mkdir(parents=True)
    (birds / "parus-major.md").write_text(
        "---\nnames:\n  scientific: Parus major\n  en: Great Tit\nscore: .nan\n---\nbody\n", encoding="utf-8"
    )
    monkeypatch.setattr(warm_cache, "BIRDS_DIR", tmp_path / "birds")
    fake = fakeredis.FakeRedis()
    assert warm_cache.load_species(fake) == 1
    stored = json.loads(fake.get(CACHE_PREFIX + species_key("parus-major")))
    assert stored["names"]["en"] == "Great Tit"
    assert stored["score"] is None  # NaN would be invalid JSON
    assert stored["completeness"]["core"]["total"] == 56  # the warmer stores what the API would serve
    assert warm_cache.flush_app_keys(fake) == 1
    assert fake.keys("*") == []


def test_helpers():
    assert slug_of(" Parus major ") == "parus-major"
    assert sanitize({"a": float("nan"), "b": [1.5]}) == {"a": None, "b": [1.5]}
    assert search_key(q="a", limit=1) == search_key(limit=1, q="a")
    assert search_key(q="a") != search_key(q="b")

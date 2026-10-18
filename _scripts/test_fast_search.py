"""Ranked in-memory search and the search endpoint's caching / slimming (no MeiliSearch, Redis or network needed)."""
import pytest
from fastapi.testclient import TestClient

from _scripts import api
from _scripts.fast_search import FastIndex, normalize

DOCS = [
    {"id": "1", "scientific_name": "Lioparus chrysotis", "genus": "Lioparus", "order": "Passeriformes", "family": "Paradoxornithidae", "common_name_en": "Golden-breasted Fulvetta", "iucn_status": "LC"},
    {"id": "2", "scientific_name": "Parus major", "genus": "Parus", "order": "Passeriformes", "family": "Paridae", "common_name_en": "Great Tit", "common_name_fa": "چکاوک", "iucn_status": "LC"},
    {"id": "3", "scientific_name": "Periparus ater", "genus": "Periparus", "order": "Passeriformes", "family": "Paridae", "common_name_en": "Coal Tit", "iucn_status": "EN"},
    {"id": "4", "scientific_name": "Phalacrocorax carbo", "genus": "Phalacrocorax", "order": "Suliformes", "family": "Phalacrocoracidae", "common_name_en": "Great Cormorant", "common_name_es": "Cormorán grande", "iucn_status": "LC"},
]


def names(index, q, **kw):
    return [d["scientific_name"] for d in index.search(q, **kw)[0]]


def test_normalize_ignores_case_accents_and_hyphens():
    assert normalize("Cormorán Golden-breasted") == "cormoran golden breasted"


def test_exact_and_prefix_matches_rank_before_substrings():
    index = FastIndex(DOCS)
    assert names(index, "parus")[0] == "Parus major"       # name starts with it, before Lioparus / Periparus (inside a word)
    assert set(names(index, "parus")) == {"Parus major", "Lioparus chrysotis", "Periparus ater"}


def test_all_words_must_match_in_any_order_and_accents_are_ignored():
    index = FastIndex(DOCS)
    assert names(index, "tit great") == ["Parus major"]
    assert names(index, "cormoran") == ["Phalacrocorax carbo"]
    assert names(index, "golden breasted") == ["Lioparus chrysotis"]
    assert names(index, "چکاوک") == ["Parus major"]


def test_filters_pagination_and_empty_query():
    index = FastIndex(DOCS)
    assert names(index, "", filter_map={"iucn_status": "EN"}) == ["Periparus ater"]
    assert names(index, "tit", filter_map={"family": "Paridae", "iucn_status": "LC"}) == ["Parus major"]
    page, total = index.search("", limit=2, offset=1)
    assert total == 4 and [d["id"] for d in page] == ["2", "3"]
    assert index.search("zzzz")[1] == 0


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(api, "meili_client", None)  # nothing to ask when the fast path finds nothing
    monkeypatch.setattr(api, "_species_index", DOCS)
    monkeypatch.setattr(api, "_fast_index", None)
    api.clear_local_cache()
    with TestClient(api.app) as c:
        yield c


def test_endpoint_serves_from_the_process_cache_second_time(client):
    first = client.get("/search?q=parus")
    second = client.get("/search?q=parus")
    assert first.json() == second.json()
    assert (first.headers["x-cache"], second.headers["x-cache"]) == ("MISS", "HIT")
    assert second.headers["x-cache-layer"] == "process"


def test_lang_keeps_only_english_and_that_language(client):
    hit = client.get("/search?q=parus&lang=fa").json()["hits"][0]
    assert hit["common_name_en"] and "common_name_es" not in hit and "body_mass_g" not in hit
    full = client.get("/search?q=cormoran").json()["hits"][0]
    assert "common_name_es" in full  # clients that pass no lang (the app) still get every name


def test_nothing_found_without_meilisearch_is_an_empty_result_not_an_error(client):
    body = client.get("/search?q=zzzz").json()
    assert body["hits"] == [] and body["total"] == 0


def test_large_responses_are_served_pre_compressed(client):
    import gzip
    body = {"filler": ["x" * 50] * 100}
    async def producer():
        return body
    import asyncio
    first = asyncio.run(api.cached_response("test:big", 60, producer))
    again = asyncio.run(api.cached_response("test:big", 60, producer))
    assert again.headers["x-cache"] == "HIT" and again.headers["x-cache-layer"] == "process"
    entry = api._local_get("test:big")
    assert entry.gz is not None and len(entry.gz) < len(entry.raw) and gzip.decompress(entry.gz) == entry.raw


def test_gzip_clients_get_content_encoding_without_double_compression(client):
    first = client.get("/search?q=&limit=50", headers={"Accept-Encoding": "gzip"})
    # TestClient decodes gzip itself, so a broken (double-compressed) body would fail to parse
    assert first.json()["total"] == 4
    assert client.get("/search?q=&limit=50", headers={"Accept-Encoding": "identity"}).json()["total"] == 4


def test_typos_are_corrected_in_memory():
    index = FastIndex(DOCS)
    docs, total, corrected = index.search_ex("cormorna grande")
    assert [d["scientific_name"] for d in docs] == ["Phalacrocorax carbo"] and corrected == "cormoran grande"
    docs, total, corrected = index.search_ex("gerat tit")  # swapped letters
    assert [d["scientific_name"] for d in docs] == ["Parus major"] and corrected == "great tit"
    assert index.search_ex("qqqqq")[1:] == (0, None)       # nothing close: no invented results
    assert index.search_ex("cormorna", fuzzy=False)[1] == 0

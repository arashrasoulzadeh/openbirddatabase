"""Sentence search: "گونه های در حال انقراض", "owls that live in forests" ... (rules and vocabulary only, no AI)."""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from _scripts import api
from _scripts.query_intent import Lexicon, parse

LEXICON = Lexicon.load(Path(__file__).resolve().parent.parent / "_index" / "intent-lexicon.json")

THREATENED = ["CR", "EN", "VU"]


@pytest.mark.parametrize("sentence", [
    "گونه های در حال انقراض", "گونه‌های در حال انقراض",          # Persian, with a space and with a half-space
    "endangered species", "threatened birds",
    "طيور مهددة بالانقراض", "Vögel gefährdet", "aves en peligro de extinción", "oiseaux menacés",
    "絶滅危惧種", "濒危鸟类", "bedreigde vogels", "zagrożone ptaki", "aves ameaçadas", "исчезающие виды птиц",
    "kuşlar nesli tehlike altında",
])
def test_threatened_sentences_in_every_language(sentence):
    assert parse(sentence, LEXICON).filters == {"iucn_status": THREATENED}


def test_specific_statuses_and_other_concepts():
    assert parse("critically endangered birds", LEXICON).filters == {"iucn_status": ["CR"]}
    assert parse("extinct birds", LEXICON).filters == {"iucn_status": ["EX", "EW"]}
    assert parse("پرندگان مهاجر", LEXICON).filters == {"migration_status": ["Full migrant", "Altitudinal migrant"]}
    assert parse("birds that eat fish", LEXICON).filters == {"primary_diet": ["Fish"]}
    intent = parse("owls that live in forests", LEXICON)
    assert intent.filters == {"primary_habitat": ["Forest"], "order": ["Strigiformes"]} and intent.words == []


def test_leftover_words_are_kept_and_plain_text_is_not_a_sentence():
    tiny = Lexicon([["endangered", "iucn_status", ["EN"]]], ["the"])
    assert parse("the endangered kiwis", tiny).words == ["kiwi"]   # plural -> singular for the name search
    assert parse("endangered kingfishers", LEXICON).filters["family"]  # bird groups are known too (taxa translations)
    assert parse("parus major", LEXICON) is None
    assert parse("", LEXICON) is None


DOCS = [
    {"id": "1", "scientific_name": "Parus major", "genus": "Parus", "order": "Passeriformes", "family": "Paridae", "common_name_en": "Great Tit", "iucn_status": "LC", "primary_habitat": "Forest"},
    {"id": "2", "scientific_name": "Strix aluco", "genus": "Strix", "order": "Strigiformes", "family": "Strigidae", "common_name_en": "Tawny Owl", "iucn_status": "EN", "primary_habitat": "Forest"},
    {"id": "3", "scientific_name": "Tyto alba", "genus": "Tyto", "order": "Strigiformes", "family": "Tytonidae", "common_name_en": "Barn Owl", "iucn_status": "CR", "primary_habitat": "Grassland"},
    {"id": "4", "scientific_name": "Ardea cinerea", "genus": "Ardea", "order": "Pelecaniformes", "family": "Ardeidae", "common_name_en": "Grey Heron", "iucn_status": "VU", "primary_habitat": "Wetland"},
]


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(api, "meili_client", None)
    monkeypatch.setattr(api, "_species_index", DOCS)
    monkeypatch.setattr(api, "_fast_index", None)
    api.clear_local_cache()
    with TestClient(api.app) as c:
        yield c


def ids(client, q, **params):
    body = client.get("/search", params={"q": q, **params}).json()
    return [h["id"] for h in body["hits"]], body


def test_endpoint_answers_sentences_most_severe_first(client):
    found, body = ids(client, "گونه های در حال انقراض")
    assert found == ["3", "2", "4"]  # CR, EN, VU; the least-concern tit is not threatened
    assert body["interpreted"]["filters"] == {"iucn_status": THREATENED}


def test_sentence_combines_filters_and_name_words(client):
    assert ids(client, "owls in forests")[0] == ["2"]
    found, body = ids(client, "endangered owls")
    assert found == ["3", "2"] and body["interpreted"]["filters"]["order"] == ["Strigiformes"]


def test_unknown_words_in_a_sentence_are_ignored_not_fatal(client):
    found, body = ids(client, "wetland birds in Iran")
    assert found == ["4"] and body["interpreted"]["ignored"] == ["iran"]


def test_names_still_win_over_sentences(client):
    found, body = ids(client, "great tit")
    assert found == ["1"] and "interpreted" not in body
    assert ids(client, "forest")[0] == ["1", "2"]  # no name contains it, so the single word reads as the habitat

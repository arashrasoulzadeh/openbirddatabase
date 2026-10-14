#!/usr/bin/env python3
"""Populate MeiliSearch with the species index (keyword + optional vector search).

Environment:
  MEILI_HOST        MeiliSearch URL (default http://localhost:7700)
  MEILI_MASTER_KEY  API key, if the server has one
  VECTOR_SEARCH     "false" to skip the embedder (keyword search only)
  EMBEDDER_MODEL    HuggingFace model MeiliSearch downloads and runs itself
"""

import json
import os

import meilisearch

MEILI_HOST = os.getenv("MEILI_HOST", "http://localhost:7700")
MEILI_MASTER_KEY = os.getenv("MEILI_MASTER_KEY") or None
MEILI_INDEX_NAME = "birds"
INDEX_FILE = "_index/species-index.json"

VECTOR_SEARCH = os.getenv("VECTOR_SEARCH", "true").lower() not in ("0", "false", "no")
EMBEDDER_MODEL = os.getenv("EMBEDDER_MODEL", "intfloat/multilingual-e5-small")
EMBEDDER_NAME = "default"  # must match _scripts/api.py

LANGS = ["fa", "en", "ar", "es", "fr", "de", "pt", "ru", "ja", "zh", "nl", "pl", "tr"]

# What the embedding model "reads" for every species. multilingual-e5 expects a "passage: " prefix.
# Only fields present on every document are referenced so no document fails to render.
DOCUMENT_TEMPLATE = (
    "passage: {{ doc.scientific_name }}. {{ doc.common_name_en }}. {{ doc.common_name_fa }}. "
    "Order {{ doc.order }}, family {{ doc.family }}, genus {{ doc.genus }}. "
    "Habitat: {{ doc.primary_habitat }}. Diet: {{ doc.primary_diet }}. "
    "Migration: {{ doc.migration_status }}. {{ doc.body_text | truncatewords: 80 }}"
)

WAIT_MS = 6 * 60 * 60 * 1000  # embedding 11k species on CPU can take a while


def main():
    print(f"Connecting to MeiliSearch at {MEILI_HOST}...")
    client = meilisearch.Client(MEILI_HOST, MEILI_MASTER_KEY)

    print(f"Loading index from {INDEX_FILE}...")
    with open(INDEX_FILE) as f:
        documents = json.load(f)
    print(f"Loaded {len(documents)} documents")

    print(f"Creating/updating index '{MEILI_INDEX_NAME}'...")
    try:
        client.get_index(MEILI_INDEX_NAME)
        print("Index exists, updating...")
    except Exception:
        task = client.create_index(MEILI_INDEX_NAME, {"primaryKey": "id"})
        client.wait_for_task(task.task_uid)
        print("Index created")
    index = client.index(MEILI_INDEX_NAME)

    settings = {
        "searchableAttributes": [
            "scientific_name",
            *[f"common_name_{lang}" for lang in LANGS],
            "order",
            "family",
            "genus",
        ],
        "filterableAttributes": [
            "order", "family", "genus", "iucn_status", "primary_habitat", "primary_diet",
            "migration_status", "countries", "data_quality",
        ],
        "sortableAttributes": ["scientific_name", "taxon_order", "body_mass_g"],
        "rankingRules": ["words", "typo", "proximity", "attribute", "sort", "exactness"],
        "distinctAttribute": "id",
    }
    if VECTOR_SEARCH:
        settings["embedders"] = {
            EMBEDDER_NAME: {
                "source": "huggingFace",
                "model": EMBEDDER_MODEL,
                "documentTemplate": DOCUMENT_TEMPLATE,
            }
        }
        print(f"Vector search: embedder '{EMBEDDER_NAME}' with {EMBEDDER_MODEL}")
    else:
        print("Vector search disabled (VECTOR_SEARCH=false)")

    print("Configuring index settings...")
    task = index.update_settings(settings)
    client.wait_for_task(task.task_uid, timeout_in_ms=WAIT_MS, interval_in_ms=2000)

    batch_size = 500
    total = len(documents)
    last_uid = None
    for i in range(0, total, batch_size):
        batch = documents[i:i + batch_size]
        print(f"Adding batch {i // batch_size + 1}/{(total + batch_size - 1) // batch_size} ({len(batch)} docs)...")
        last_uid = index.add_documents(batch).task_uid

    print("Waiting for indexing to finish"
          + (" (this downloads the embedding model and computes vectors, it can take a while)..." if VECTOR_SEARCH else "..."))
    if last_uid is not None:
        task = client.wait_for_task(last_uid, timeout_in_ms=WAIT_MS, interval_in_ms=5000)
        print(f"Last task: {task.status}")
        if task.status == "failed":
            raise SystemExit(f"Indexing failed: {task.error}")

    print(f"Index stats: {index.get_stats().number_of_documents} documents")
    print("Done!")


if __name__ == "__main__":
    main()

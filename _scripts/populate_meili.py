#!/usr/bin/env python3
"""Populate MeiliSearch with species index."""

import json
import meilisearch
import os

MEILI_HOST = os.getenv("MEILI_HOST", "http://localhost:7700")
MEILI_MASTER_KEY = os.getenv("MEILI_MASTER_KEY", "80bohYKVODFF_RwmZej22I8nIcseR6NOIH4lQW-Vt3o")
MEILI_INDEX_NAME = "birds"
INDEX_FILE = "_index/species-index.json"

def main():
    print(f"Connecting to MeiliSearch at {MEILI_HOST}...")
    client = meilisearch.Client(MEILI_HOST, MEILI_MASTER_KEY)
    
    # Load index
    print(f"Loading index from {INDEX_FILE}...")
    with open(INDEX_FILE) as f:
        documents = json.load(f)
    
    print(f"Loaded {len(documents)} documents")
    
    # Create or get index
    print(f"Creating/updating index '{MEILI_INDEX_NAME}'...")
    try:
        index = client.get_index(MEILI_INDEX_NAME)
        print("Index exists, updating...")
    except:
        task = client.create_index(MEILI_INDEX_NAME, {"primaryKey": "id"})
        print(f"Index creation task: {task.task_uid}")
        # Wait for task to complete
        import time
        while True:
            task_info = client.get_task(task.task_uid)
            if task_info.status in ['succeeded', 'failed']:
                break
            time.sleep(0.5)
        print("Index created")
        index = client.get_index(MEILI_INDEX_NAME)
    
    # Configure index settings
    print("Configuring index settings...")
    index.update_settings({
        "searchableAttributes": [
            "scientific_name",
            "common_name_fa",
            "common_name_en",
            "order",
            "family",
            "genus"
        ],
        "filterableAttributes": [
            "order",
            "family",
            "genus",
            "iucn_status",
            "primary_habitat",
            "primary_diet",
            "migration_status",
            "countries",
            "data_quality"
        ],
        "sortableAttributes": [
            "scientific_name",
            "taxon_order",
            "body_mass_g"
        ],
        "rankingRules": [
            "words",
            "typo",
            "proximity",
            "attribute",
            "sort",
            "exactness"
        ],
        "distinctAttribute": "id"
    })
    
    # Add documents in batches
    batch_size = 100
    total = len(documents)
    
    for i in range(0, total, batch_size):
        batch = documents[i:i+batch_size]
        print(f"Adding batch {i//batch_size + 1}/{(total+batch_size-1)//batch_size} ({len(batch)} docs)...")
        task = index.add_documents(batch)
        print(f"  Task ID: {task.task_uid}")
    
    print("Waiting for indexing to complete...")
    # Wait for last task
    import time
    time.sleep(2)
    
    # Verify
    stats = index.get_stats()
    print(f"Index stats: {stats}")
    print("Done!")

if __name__ == "__main__":
    main()
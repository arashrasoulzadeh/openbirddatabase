#!/usr/bin/env python3
"""Fill an analytics database with realistic FAKE traffic so the dashboard can be previewed.

    ANALYTICS_DB=data/analytics-demo.db python _scripts/seed_analytics.py --days 30
    ANALYTICS_DB=data/analytics-demo.db uvicorn _scripts.api:app

Never point it at the production database: it refuses to write into a database that already holds events
unless --force is given.
"""

import argparse
import json
import math
import os
import random
import sys
import time
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import _scripts.analytics as analytics  # noqa: E402

LANGS = [("en", 38), ("fa", 24), ("es", 9), ("de", 7), ("fr", 6), ("ru", 5), ("ja", 4), ("pt", 3), ("zh", 2), ("ar", 1), ("tr", 1)]
DEVICES = [("mobile", 58), ("desktop", 36), ("tablet", 6)]
REFERRERS = [(None, 55), ("google.com", 25), ("bing.com", 4), ("duckduckgo.com", 3), ("reddit.com", 5), ("wikipedia.org", 5), ("t.me", 3)]
FILTERS = [("iucn_status", ["LC", "NT", "VU", "EN", "CR"]), ("primary_habitat", ["Forest", "Wetland", "Sea", "Grassland"]),
           ("primary_diet", ["Invertebrate", "Seed", "Fish", "Omnivore"]), ("migration_status", ["Resident", "Full migrant"])]
WORDS = ["owl", "eagle", "tit", "parrot", "penguin", "kingfisher", "sparrow", "crane", "heron", "falcon", "swan", "hummingbird"]
ZERO = ["unicorn bird", "xyzzy", "dragon", "pigeonn", "flamingoo", "phoenix"]


def pick(rng, weighted):
    return rng.choices([v for v, _ in weighted], [w for _, w in weighted])[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--visitors-per-day", type=int, default=120, help="average at the end of the period")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    index = json.loads(Path("_index/species-index.json").read_text(encoding="utf-8"))
    popular = [d["scientific_name"] for d in random.Random(1).sample(index, 400)]
    rng = random.Random(42)
    if analytics._query("SELECT COUNT(*) AS n FROM events")[0]["n"] and not args.force:
        raise SystemExit(f"{analytics.DB_PATH} already has events; use another ANALYTICS_DB or --force")

    now = int(time.time())
    rows = []

    def add(ts, type_, v, **kw):
        rows.append((ts, type_, kw.get("path"), v["id"], v["session"], v["lang"], kw.get("bird"), kw.get("query"),
                     kw.get("source"), kw.get("value"), kw.get("props"), v["device"], v.get("referrer")))

    for day in range(args.days, -1, -1):
        growth = 0.35 + 0.65 * (args.days - day) / max(args.days, 1)           # traffic grows over time
        weekend = 1.25 if (time.gmtime(now - day * 86400).tm_wday >= 5) else 1.0
        for n in range(int(args.visitors_per_day * growth * weekend * rng.uniform(0.7, 1.3))):
            hour = int(min(23, max(0, rng.gauss(15, 5))))                       # evenings are busiest
            ts = now - day * 86400 - (now % 86400) + hour * 3600 + rng.randint(0, 3599)
            if ts > now:
                continue
            visitor = {"id": f"v{day}-{n}", "session": f"s{day}-{n}", "lang": pick(rng, LANGS), "device": pick(rng, DEVICES),
                       "referrer": pick(rng, REFERRERS)}
            t = ts
            add(t, "pageview", visitor, path="/", referrer=visitor["referrer"])
            t += rng.randint(3, 40)
            add(t, "page_leave", visitor, path="/", value=(t - ts) * 1000)
            for _ in range(rng.choice([0, 1, 1, 2, 3, 5])):
                query = rng.choice(ZERO) if rng.random() < 0.08 else rng.choice(WORDS)
                total = 0 if query in ZERO else rng.randint(3, 400)
                add(t, "search", visitor, query=query, value=total, path="/")
                if rng.random() < 0.25:
                    field, values = rng.choice(FILTERS)
                    add(t, "filter", visitor, source=field, query=rng.choice(values), path="/")
                for _ in range(rng.choice([0, 1, 1, 2]) if total else 0):
                    bird = rng.choice(popular[:120] if rng.random() < 0.6 else popular)
                    source = rng.choices(["search", "taxonomy", "related", "random"], [70, 14, 10, 6])[0]
                    t += rng.randint(2, 20)
                    add(t, "bird_click", visitor, bird=bird, source=source, query=query, path="/")
                    page = f"/species/{quote(bird)}"
                    add(t, "pageview", visitor, path=page, bird=bird)
                    dur = int(min(600, rng.lognormvariate(3.2, 0.8)) * 1000)
                    add(t + dur // 1000, "page_leave", visitor, path=page, bird=bird, value=dur)
                    t += dur // 1000
            if rng.random() < 0.15:
                add(t, "tab_view", visitor, path="/", source="taxonomy")
            if rng.random() < 0.12:
                target = pick(rng, LANGS)
                add(t, "language_change", visitor, source=visitor["lang"], query=target)
                visitor["lang"] = target
            if rng.random() < 0.05:
                add(t, "load_more", visitor, path="/", value=50)

    with analytics._lock:
        conn = analytics._connection()
        conn.executemany(
            "INSERT INTO events (ts,type,path,visitor,session,lang,bird,query,source,value,props,device,referrer) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
        conn.commit()
    print(f"Wrote {len(rows)} fake events to {analytics.DB_PATH}")


if __name__ == "__main__":
    main()

"""Common names of bird orders and families in the 13 site languages, from Wikidata (CC0).

For each order/family in the taxonomy tree the labels, Wikipedia article titles and "taxon common name" statements are
collected; the first usable one wins (a real localized name that is not just the Latin name, with disambiguation such
as "(bird)" removed). Output: frontend/src/lib/i18n/taxa.json  { "Passeriformes": { "en": "Passerines", ... }, ... }

    python _scripts/enrich/taxa_names.py            (needs network access to query.wikidata.org)
"""

import json
import re
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parent.parent.parent
TREE = ROOT / "_index" / "taxonomy-tree.json"
OUT = ROOT / "frontend" / "src" / "lib" / "i18n" / "taxa.json"
LANGS = "en fa ar es fr de pt ru ja zh nl pl tr".split()
USER_AGENT = "OpenBirdDatabase/1.0 (https://github.com/arashrasoulzadeh/openbirddatabase)"
PRIORITY = ("label", "wiki", "common")  # label: Wikidata label; wiki: Wikipedia title; common: P1843


def taxon_names() -> List[str]:
    tree = json.loads(TREE.read_text(encoding="utf-8"))
    return sorted(tree) + sorted({family for families in tree.values() for family in families})


def sparql(chunk: List[str]) -> list:
    values = " ".join(f'"{n}"' for n in chunk)
    langs = ",".join(f'"{l}"' for l in LANGS)
    sites = " ".join(f'(<https://{l}.wikipedia.org/> "{l}")' for l in LANGS)
    query = f"""SELECT ?name ?lang ?kind ?text WHERE {{
  VALUES ?name {{ {values} }}
  ?item wdt:P225 ?name ; wdt:P105 ?rank . VALUES ?rank {{ wd:Q36602 wd:Q35409 }}
  ?item wdt:P171+ wd:Q5113 .
  {{ ?item wdt:P1843 ?text . FILTER(LANG(?text) IN ({langs})) BIND(LANG(?text) AS ?lang) BIND("common" AS ?kind) }}
  UNION {{ ?item rdfs:label ?text . FILTER(LANG(?text) IN ({langs})) BIND(LANG(?text) AS ?lang) BIND("label" AS ?kind) }}
  UNION {{ VALUES (?site ?lang) {{ {sites} }} ?article schema:about ?item ; schema:isPartOf ?site ; schema:name ?text . BIND("wiki" AS ?kind) }}
}}"""
    tmp = Path("/tmp/openbird-taxa.rq")
    tmp.write_text(query, encoding="utf-8")
    for _ in range(3):
        out = subprocess.run(
            ["curl", "-s", "-m", "90", "-X", "POST", "https://query.wikidata.org/sparql",
             "-H", "Accept: application/sparql-results+json", "-H", f"User-Agent: {USER_AGENT}",
             "--data-urlencode", f"query@{tmp}"],
            capture_output=True, text=True,
        )
        try:
            return json.loads(out.stdout)["results"]["bindings"]
        except ValueError:
            time.sleep(5)
    return []


def tidy(text: str) -> str:
    """'Tit (bird)' -> 'Tit'; trims spaces."""
    return re.sub(r"\s*\([^)]*\)\s*$", "", text).strip()


def pick(candidates: Dict[str, str], latin: str) -> str:
    for kind in PRIORITY:
        text = tidy(candidates.get(kind, ""))
        if text and text.lower() != latin.lower():
            return text
    return ""


def build() -> Dict[str, Dict[str, str]]:
    names = taxon_names()
    rows: list = []
    for i in range(0, len(names), 40):
        rows += sparql(names[i:i + 40])
    found: Dict[str, Dict[str, Dict[str, str]]] = defaultdict(lambda: defaultdict(dict))
    for row in rows:
        found[row["name"]["value"]][row["lang"]["value"]].setdefault(row["kind"]["value"], row["text"]["value"])
    result: Dict[str, Dict[str, str]] = {}
    for name in names:
        per_lang = {lang: pick(found[name].get(lang, {}), name) for lang in LANGS}
        result[name] = {lang: text for lang, text in per_lang.items() if text}
    return result


def main() -> int:
    data = build()
    if len(data) < 100:
        print("Wikidata returned too little data; leaving the file unchanged", file=sys.stderr)
        return 1
    OUT.write_text(json.dumps(dict(sorted(data.items())), ensure_ascii=False, indent=1), encoding="utf-8")
    coverage = {lang: sum(1 for v in data.values() if v.get(lang)) for lang in LANGS}
    print(f"Wrote {OUT.relative_to(ROOT)}: {len(data)} taxa; per language: {coverage}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Build _index/intent-lexicon.json: the vocabulary behind sentence search ("گونه های در حال انقراض", "owls that live in forests").

Sources (all already in the repo, so every language is covered without an AI or a service):
  * the website's translations: conservation statuses (messages.json), habitat / diet / migration values (values.json),
    order and family names (taxa.json)
  * _scripts/intent_phrases.py: colloquial phrases ("endangered", "extinct", "migratory") and filler words per language
Run after changing those, then commit the result:  python _scripts/build_lexicon.py
"""

import json
from pathlib import Path

from _scripts.fast_search import normalize
from _scripts.intent_phrases import PHRASES, STOPWORDS

ROOT = Path(__file__).resolve().parent.parent
I18N = ROOT / "frontend" / "src" / "lib" / "i18n"
OUT = ROOT / "_index" / "intent-lexicon.json"
SKIP_VALUES = {"", "Unknown", "No Information", "Other", "Not listed", "High", "Medium", "Low"}


def load(name: str):
    return json.loads((I18N / name).read_text(encoding="utf-8"))


def main() -> None:
    docs = json.loads((ROOT / "_index" / "species-index.json").read_text(encoding="utf-8"))
    values_of = {f: sorted({d[f] for d in docs if d.get(f)}) for f in ("primary_habitat", "primary_diet", "migration_status")}
    orders = {d["order"] for d in docs if d.get("order")}
    families = {d["family"] for d in docs if d.get("family")}

    entries = {}  # normalized phrase -> (field, values); the first writer wins, so hand-written phrases go in first

    def add(phrase, field, values):
        key = normalize(phrase)
        if len(key) >= 2 and key not in entries:
            entries[key] = [field, list(values)]

    for values, field, phrases in PHRASES:
        for phrase in phrases:
            add(phrase, field, values)

    messages, translated = load("messages.json"), load("values.json")
    for lang, table in messages.items():  # "Critically Endangered" -> CR in every language
        for code in ("CR", "EN", "VU", "NT", "LC", "EW", "EX", "DD"):
            label = table.get(f"iucn{code}")
            if label:
                add(label, "iucn_status", [code])
    for field, values in values_of.items():
        for value in values:
            if value in SKIP_VALUES or value not in translated:
                continue
            for text in translated[value].values():
                add(text, field, [value])
            add(value, field, [value])
    taxa = load("taxa.json")
    for name, texts in taxa.items():
        field = "order" if name in orders else "family" if name in families else None
        if field:
            add(name, field, [name])
            for text in texts.values():
                add(text, field, [name])

    stop = sorted({normalize(w) for words in STOPWORDS.values() for w in words.split()})
    lexicon = {
        "phrases": [[p, f, v] for p, (f, v) in sorted(entries.items(), key=lambda kv: (-len(kv[0]), kv[0]))],
        "stopwords": stop,
    }
    OUT.write_text(json.dumps(lexicon, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{len(lexicon['phrases'])} phrases, {len(stop)} stop words -> {OUT.relative_to(ROOT)} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Compute content statistics for the analytics page and write _index/content-stats.json.

- birds added over time (first git commit of each species file; skipped when not a git checkout)
- species-name coverage per language and UI translation coverage (Flutter .arb files)
- data completeness per species (share of filled fields), by order, by section, data quality

Run after the species data changes (it takes about a minute):  python _scripts/content_stats.py
"""

import json
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
BIRDS_DIR = ROOT / "birds"
ARB_DIR = ROOT / "flutter_app" / "lib" / "l10n"
OUT = ROOT / "_index" / "content-stats.json"

LANGS = ["en", "fa", "ar", "es", "fr", "de", "pt", "ru", "ja", "zh", "nl", "pl", "tr"]
SECTIONS = ["morphology", "distribution", "habitat", "diet", "behavior", "reproduction",
            "demography", "conservation", "veterinary", "enrichment"]
META_KEYS = {"source", "contributor", "date_added", "verified"}
EMPTY_STRINGS = {"", "nan", "Unknown", "No Information"}
Loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


def leaves(node, skip_meta=True):
    """Yield every leaf value below `node` (dicts are walked, lists count as one leaf)."""
    if isinstance(node, dict):
        for key, value in node.items():
            if skip_meta and key in META_KEYS:
                continue
            yield from leaves(value, skip_meta)
    else:
        yield node


def is_filled(value) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() not in EMPTY_STRINGS
    if isinstance(value, (list, dict)):
        return len(value) > 0
    return True  # numbers (including 0) and booleans are real values


def parse(path: Path):
    parts = path.read_text(encoding="utf-8").split("---", 2)
    return yaml.load(parts[1], Loader=Loader) if len(parts) >= 3 else None


def added_dates() -> dict:
    """{relative path: ISO timestamp of the commit that added the file}."""
    try:
        out = subprocess.run(
            ["git", "log", "--diff-filter=A", "--format=@@%aI", "--name-only", "--", "birds"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return {}
    dates, current = {}, None
    for line in out.splitlines():
        if line.startswith("@@"):
            current = line[2:]
        elif line.strip() and current:
            dates[line.strip()] = current  # the log is newest first, so the last write is the oldest add
    return dates


def cumulative(timestamps, length):
    counts = Counter(ts[:length] for ts in timestamps)
    total, series = 0, []
    for bucket in sorted(counts):
        total += counts[bucket]
        series.append({"t": bucket, "added": counts[bucket], "total": total})
    return series


def ui_coverage() -> dict:
    """Translated UI strings per language: keys whose text differs from English."""
    def load(lang):
        path = ARB_DIR / f"app_{lang}.arb"
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        return {k: v for k, v in data.items() if not k.startswith("@")}

    en = load("en")
    result = {}
    for lang in LANGS:
        texts = load(lang)
        translated = sum(1 for k, v in en.items() if lang == "en" or (texts.get(k) and texts[k] != v))
        result[lang] = {"total": len(en), "present": sum(1 for k in en if texts.get(k)), "translated": translated}
    return result


def main():
    files = sorted(BIRDS_DIR.glob("**/*.md"))
    print(f"Scanning {len(files)} species files...")
    adds = added_dates()

    name_counts = Counter()
    completeness_by_order = defaultdict(list)
    histogram = Counter()
    section_filled = Counter()
    data_quality = Counter()
    curated = Counter()
    scores, added_ts = [], []

    for path in files:
        fm = parse(path)
        if not fm:
            continue
        names = fm.get("names") or {}
        for lang in LANGS:
            if names.get(lang):
                name_counts[lang] += 1

        total = filled = 0
        for section in SECTIONS:
            node = fm.get(section)
            values = list(leaves(node)) if node else []
            total += len(values)
            got = sum(1 for v in values if is_filled(v))
            filled += got
            if got:
                section_filled[section] += 1
        for section in ("veterinary", "enrichment"):
            if (fm.get(section) or {}).get("verified") is True:
                curated[section] += 1
        score = filled / total if total else 0.0
        scores.append(score)
        histogram[min(int(score * 10), 9)] += 1
        completeness_by_order[(fm.get("taxonomy") or {}).get("order", "Unknown")].append(score)
        data_quality[fm.get("data_quality") or "Unknown"] += 1

        rel = path.relative_to(ROOT).as_posix()
        if rel in adds:
            added_ts.append(adds[rel])

    n = len(scores)
    stats = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "total_species": n,
        "added": {
            "by_day": cumulative(added_ts, 10),
            "by_hour": cumulative(added_ts, 13),
            "known": len(added_ts),
        },
        "languages": {
            "names": {lang: name_counts.get(lang, 0) for lang in LANGS},
            "ui": ui_coverage(),
        },
        "completeness": {
            "average": round(sum(scores) / n, 4) if n else 0,
            "histogram": [{"bucket": f"{i * 10}-{i * 10 + 10}%", "count": histogram.get(i, 0)} for i in range(10)],
            "by_order": sorted(
                ({"order": o, "average": round(sum(v) / len(v), 4), "species": len(v)}
                 for o, v in completeness_by_order.items()),
                key=lambda r: -r["species"],
            ),
            "by_section": {s: round(section_filled.get(s, 0) / n, 4) if n else 0 for s in SECTIONS},
            "data_quality": dict(data_quality),
            "expert_verified": {s: curated.get(s, 0) for s in ("veterinary", "enrichment")},
        },
    }
    OUT.write_text(json.dumps(stats, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}: {n} species, average completeness {stats['completeness']['average']:.1%}")


if __name__ == "__main__":
    main()

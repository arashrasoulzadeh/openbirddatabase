#!/usr/bin/env python3
"""Compute content statistics for the analytics page and write _index/content-stats.json.

- birds added over time (first git commit of each species file; skipped when not a git checkout)
- species-name coverage per language and UI translation coverage (Flutter .arb files)
- data completeness per species (see _scripts/completeness.py), by field, section and order, data quality

Run after the species data changes (it takes about a minute):  python _scripts/content_stats.py
"""

import json
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _scripts.completeness import CORE_FIELDS, evaluate  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BIRDS_DIR = ROOT / "birds"
ARB_DIR = ROOT / "flutter_app" / "lib" / "l10n"
OUT = ROOT / "_index" / "content-stats.json"

LANGS = ["en", "fa", "ar", "es", "fr", "de", "pt", "ru", "ja", "zh", "nl", "pl", "tr"]
Loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


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
    section_total = Counter()
    field_filled = Counter()
    data_quality = Counter()
    curated = Counter()
    scores, lowest, added_ts = [], [], []

    for path in files:
        fm = parse(path)
        if not fm:
            continue
        names = fm.get("names") or {}
        for lang in LANGS:
            if names.get(lang):
                name_counts[lang] += 1

        report = evaluate(fm)
        core = report["core"]
        scores.append(core["score"])
        lowest.append((core["score"], names.get("scientific") or path.stem, names.get("en") or ""))
        histogram[min(int(core["score"] * 10), 9)] += 1
        completeness_by_order[(fm.get("taxonomy") or {}).get("order", "Unknown")].append(core["score"])
        data_quality[fm.get("data_quality") or "Unknown"] += 1
        for section, counts in core["sections"].items():
            section_filled[section] += counts["filled"]
            section_total[section] += counts["total"]
        for section, fields in CORE_FIELDS.items():
            gaps = set(core["missing"].get(section, []))
            for field in fields:
                if field not in gaps:
                    field_filled[f"{section}.{field}"] += 1
        for section in ("veterinary", "enrichment"):
            if (fm.get(section) or {}).get("verified") is True:
                curated[section] += 1

        rel = path.relative_to(ROOT).as_posix()
        if rel in adds:
            added_ts.append(adds[rel])

    n = len(scores)
    lowest.sort()
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
            # share of the schema's core fields that have data, averaged over all species
            "average": round(sum(scores) / n, 4) if n else 0,
            "fields_per_species": sum(len(v) for v in CORE_FIELDS.values()),
            "histogram": [{"bucket": f"{i * 10}-{i * 10 + 10}%", "count": histogram.get(i, 0)} for i in range(10)],
            "by_order": sorted(
                ({"order": o, "average": round(sum(v) / len(v), 4), "species": len(v)}
                 for o, v in completeness_by_order.items()),
                key=lambda r: -r["species"],
            ),
            # average fill per section, and the fill rate of every single field (the gaps, worst first)
            "by_section": {s: round(section_filled[s] / section_total[s], 4) if section_total[s] else 0
                           for s in CORE_FIELDS},
            "by_field": sorted(
                ({"field": f"{s}.{f}", "filled": round(field_filled[f"{s}.{f}"] / n, 4) if n else 0}
                 for s, names_ in CORE_FIELDS.items() for f in names_),
                key=lambda r: r["filled"],
            ),
            "least_complete": [{"scientific": sci, "english": en, "score": round(score, 4)}
                               for score, sci, en in lowest[:15]],
            "data_quality": dict(data_quality),
            "expert_verified": {s: curated.get(s, 0) for s in ("veterinary", "enrichment")},
        },
    }
    OUT.write_text(json.dumps(stats, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}: {n} species, average completeness {stats['completeness']['average']:.1%}")


if __name__ == "__main__":
    main()

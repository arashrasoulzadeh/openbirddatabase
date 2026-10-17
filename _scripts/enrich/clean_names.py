"""Blank common names that are not real translations, so titles, search and the language-coverage numbers are honest.

* any language: the placeholder text "nan" / "None" / "null" / "N/A" (3,371 Persian names were literally "nan")
* pt: a name identical to the English one is an untranslated copy
* zh: a name without a single Chinese character is an untranslated (English/Latin) copy

The keys stay in the files (the schema requires `fa` and `en`), their value becomes an empty string; the website and
API fall back to the English name when a language has none.
"""

import re
from typing import Any, Dict, List

from .common import read_species, species_paths, write_species

LABEL = "names cleanup"
PLACEHOLDERS = {"nan", "none", "null", "n/a", "-", "?"}
CJK = re.compile(r"[㐀-鿿豈-﫿]")


def clean(names: Dict[str, Any]) -> List[str]:
    """Blank bad names in place; returns a description of each change."""
    changes: List[str] = []
    english = str(names.get("en") or "").strip().lower()
    for lang, value in list(names.items()):
        if lang == "scientific":
            continue
        text = str(value or "").strip()
        reason = None
        if text and text.lower() in PLACEHOLDERS:
            reason = "placeholder"
        elif lang == "pt" and text and text.lower() == english:
            reason = "pt copy of English"
        elif lang == "zh" and text and not CJK.search(text):
            reason = "zh without Chinese characters"
        if reason:
            names[lang] = ""
            changes.append(f"{lang}: {reason}")
    return changes


def run(dry_run: bool = False) -> Dict[str, int]:
    counts: Dict[str, int] = {"files": 0}
    for path in species_paths().values():
        fm, body = read_species(path)
        names = fm.get("names")
        if not isinstance(names, dict):
            continue
        changes = clean(names)
        if not changes:
            continue
        counts["files"] += 1
        for change in changes:
            counts[change] = counts.get(change, 0) + 1
        if not dry_run:
            write_species(path, fm, body)
    return counts

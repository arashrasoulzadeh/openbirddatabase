"""Understand a search *sentence* with plain vocabulary rules (no AI): "گونه های در حال انقراض", "owls that live in forests".

parse() removes the known phrases (conservation status, habitat, diet, migration, order / family names) and filler words,
turns the phrases into filters and keeps the rest as name words. The vocabulary is _index/intent-lexicon.json
(built by build_lexicon.py from the website's 13 translations plus intent_phrases.py).
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Optional

from _scripts.fast_search import normalize

CJK = re.compile(r"[぀-ヿ㐀-鿿豈-﫿]")


class Intent(NamedTuple):
    filters: Dict[str, List[str]]   # field -> accepted values (OR within a field, AND across fields)
    words: List[str]                # what is left over: name words, e.g. ["owl"]


class Lexicon:
    def __init__(self, phrases: List[list], stopwords: List[str]) -> None:
        self.phrases = [(p, f, v, bool(CJK.search(p)), p.split(" ")[0]) for p, f, v in phrases]  # longest first
        self.stopwords = set(stopwords)
        self.cjk_stop = sorted((w for w in stopwords if CJK.search(w)), key=len, reverse=True)  # 鸟类 before 鸟

    @classmethod
    def load(cls, path: Path) -> Optional["Lexicon"]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        return cls(data["phrases"], data["stopwords"])


def _stem(word: str) -> str:
    """Plural -> singular for the leftover name words (owls -> owl); other languages are left alone."""
    if len(word) > 4 and word.endswith("es") and word[:-2].endswith(("ch", "sh", "x", "s")):
        return word[:-2]
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def parse(query: str, lex: Lexicon) -> Optional[Intent]:
    """The filters and leftover words for `query`, or None when no known phrase occurs in it."""
    s = " " + normalize(query) + " "
    filters: Dict[str, List[str]] = {}
    for phrase, field, values, is_cjk, first in lex.phrases:
        if first not in s:
            continue
        for needle in ((phrase,) if is_cjk else (f" {phrase} ", f" {phrase}s ", f" {phrase}es ")):
            at = s.find(needle)
            if at >= 0:
                # keep the space(s) that bordered the phrase so neighbouring words stay separate
                s = s[:at] + " " + s[at + len(needle):] if not is_cjk else s[:at] + " " + s[at + len(needle):]
                bucket = filters.setdefault(field, [])
                bucket.extend(v for v in values if v not in bucket)
                break
    if not filters:
        return None
    for stop in lex.cjk_stop:
        s = s.replace(stop, " ")
    words = [_stem(w) for w in s.split() if w not in lex.stopwords]
    return Intent(filters, words)

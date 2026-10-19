"""In-memory ranked search over the species index: about a millisecond for 11k species, no network, no embedding.

Matching: every word of the query must occur (as a substring, accents ignored) in the species' scientific name, order,
family, genus or any common name. Ranking, best first:
    0 a name equals the query      1 a name starts with it      2 a word of a name starts with it      3 anywhere
then shorter names first (a closer match), then taxonomic order.

Speed: a trigram index finds the few species containing the query's rarest 3-letter sequence (about 0.1-0.5 ms). A query
with no match is retried with typos fixed (words of 4+ letters, 1-2 edits, 2-3 ms; the result reports `corrected_query`).
Only meaning-based queries ("bird that eats fish") still go to MeiliSearch, and only when this finds nothing.
"""

import unicodedata
from array import array
from collections import Counter
from typing import Any, Dict, Iterable, List, Optional, Tuple

FILTER_FIELDS = ("iucn_status", "order", "family", "primary_habitat", "primary_diet", "migration_status")
NAME_FIELDS = ("scientific_name", "genus")
BROAD_QUERY = 800  # more matches than this: skip ranking


def edit_distance(a: str, b: str, limit: int) -> int:
    """Damerau-Levenshtein distance (a swap of two neighbouring letters is one edit), or limit + 1 once it must exceed `limit`."""
    if abs(len(a) - len(b)) > limit:
        return limit + 1
    before, previous = None, list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [i]
        for j, cb in enumerate(b, 1):
            best = min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + (ca != cb))
            if before is not None and i > 1 and j > 1 and ca == b[j - 2] and a[i - 2] == cb:
                best = min(best, before[j - 2] + 1)
            current.append(best)
        if min(current) > limit:
            return limit + 1
        before, previous = previous, current
    return previous[-1]


def trigrams(word: str) -> set:
    padded = f"^{word}$"
    return {padded[i:i + 3] for i in range(len(padded) - 2)}


def _matches(value: Any, wanted: Any) -> bool:
    return value in wanted if isinstance(wanted, (list, tuple, set)) else value == wanted


def normalize(text: Any) -> str:
    """Lower-case, accents removed, hyphens and underscores as spaces (Cormorán -> cormoran, Golden-breasted -> golden breasted)."""
    s = unicodedata.normalize("NFKD", str(text or "").casefold())
    s = "".join(c for c in s if not unicodedata.combining(c))
    # Arabic yeh / kaf -> the Persian forms, half-space (ZWNJ) -> space: "گونه‌های" and "گونه های" are the same text
    s = s.replace("\u064a", "\u06cc").replace("\u0643", "\u06a9").replace("\u200c", " ").replace("\u200f", "")
    return s.replace("-", " ").replace("_", " ").replace("'", "").replace("\u2019", "").strip()


class FastIndex:
    def __init__(self, docs: List[Dict[str, Any]]) -> None:
        self.docs = docs
        self.names: List[List[str]] = []  # per species: normalized names used for ranking
        self.blobs: List[str] = []        # per species: everything searchable in one string
        self.by_filter: Dict[Tuple[str, str], List[int]] = {}
        for i, d in enumerate(docs):
            names = [normalize(d.get(f)) for f in NAME_FIELDS]
            names += [normalize(v) for k, v in d.items() if k.startswith("common_name_") and v]
            names = [n for n in dict.fromkeys(names) if n and n != "nan"]
            self.names.append(names)
            self.blobs.append("\n".join(names + [normalize(d.get("order")), normalize(d.get("family"))]))
            for f in FILTER_FIELDS:
                if d.get(f):
                    self.by_filter.setdefault((f, d[f]), []).append(i)

        # substring search: species containing each 3-letter sequence (ascending), so a query only checks the few species
        # that contain its rarest sequence instead of testing all of them
        post: Dict[str, array] = {}
        for i, blob in enumerate(self.blobs):
            for g in {blob[k:k + 3] for k in range(len(blob) - 2)}:
                if "\n" not in g:
                    post.setdefault(g, array("I")).append(i)
        self.tri_post = post

        # typo correction: every word that appears in a name, with a trigram index to find near-misses quickly
        self.joined = "\n".join(self.blobs)
        counts: Counter = Counter(w for names in self.names for n in names for w in n.split() if len(w) >= 4)
        self.vocab = list(counts)
        self.vocab_count = counts
        self.vocab_post: Dict[str, array] = {}  # arrays, not lists: a third of the memory
        for i, w in enumerate(self.vocab):
            for g in trigrams(w):
                self.vocab_post.setdefault(g, array("I")).append(i)

    def _narrow(self, tokens: List[str]) -> Optional[Iterable[int]]:
        """Species that might match every token: the posting list of the rarest 3-letter sequence among them (which may be
        empty), or None when no token is long enough to have one."""
        best = None
        for t in tokens:
            if len(t) < 3:
                continue
            for k in range(len(t) - 2):
                posting = self.tri_post.get(t[k:k + 3])
                if posting is None:
                    return ()  # that sequence occurs in no name at all
                if best is None or len(posting) < len(best):
                    best = posting
        return best

    def correct(self, token: str) -> Optional[str]:
        """The most common known word within 1 edit (2 for long words) of `token`, or None."""
        if len(token) < 4:
            return None
        allowed = 1 if len(token) <= 6 else 2
        overlap: Counter = Counter()
        size, vocab = len(token), self.vocab
        for g in trigrams(token):
            for i in self.vocab_post.get(g, ()):
                if abs(len(vocab[i]) - size) <= allowed:  # a word within `allowed` edits is at most that much longer/shorter
                    overlap[i] += 1
        need = max(1, len(token) - 4 * allowed)  # one swapped pair of letters changes up to 4 trigrams
        best, best_key = None, None
        for i, n in overlap.most_common(400):
            if n < need:
                break
            word = self.vocab[i]
            d = edit_distance(token, word, allowed)
            if d <= allowed:
                key = (d, -self.vocab_count[word])
                if best_key is None or key < best_key:
                    best, best_key = word, key
        return best

    def _candidates(self, filters: List[Tuple[str, Any]]) -> Optional[List[int]]:
        """Indexes passing all filters (None = no filter, i.e. everything). A filter value may be a list: any of them."""
        groups = []
        for field, wanted in filters:
            values = wanted if isinstance(wanted, (list, tuple, set)) else [wanted]
            groups.append({i for v in values for i in self.by_filter.get((field, v), ())})
        if not groups:
            return None
        groups.sort(key=len)
        keep = groups[0]
        for other in groups[1:]:
            keep = keep & other
        return sorted(keep)

    def search(self, q: str, filter_map: Optional[Dict[str, Any]] = None, limit: int = 20, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
        """(page of species documents, total matches)."""
        docs, total, _ = self.search_ex(q, filter_map, limit, offset)
        return docs, total

    def search_ex(self, q: str, filter_map: Optional[Dict[str, Any]] = None, limit: int = 20, offset: int = 0,
                  fuzzy: bool = True, whole_words: bool = False) -> Tuple[List[Dict[str, Any]], int, Optional[str]]:
        """(page of species documents, total matches, corrected query when a typo was fixed to get matches)."""
        docs, total = self._search(q, filter_map, limit, offset, whole_words)
        if total or not fuzzy:
            return docs, total, None
        tokens = normalize(q).split()
        fixed = [t if t in self.joined else (self.correct(t) or t) for t in tokens]
        if fixed == tokens:
            return docs, total, None
        docs, total = self._search(" ".join(fixed), filter_map, limit, offset)
        return docs, total, (" ".join(fixed) if total else None)

    def _search(self, q: str, filter_map: Optional[Dict[str, Any]], limit: int, offset: int,
                whole_words: bool = False) -> Tuple[List[Dict[str, Any]], int]:
        """`whole_words`: every query word must start a word of a name (no matches in the middle of a word)."""
        filters = [(f, v) for f, v in (filter_map or {}).items() if f in FILTER_FIELDS and v]
        pool = self._candidates(filters)
        tokens = normalize(q).split()
        if not tokens:
            ids = list(pool if pool is not None else range(len(self.docs)))
            for field, wanted in filters:  # several accepted values: the first listed come first (CR before EN before VU)
                if isinstance(wanted, (list, tuple)) and len(wanted) > 1:
                    rank = {v: n for n, v in enumerate(wanted)}
                    ids.sort(key=lambda i: rank.get(self.docs[i].get(field), len(rank)))
                    break
            return [self.docs[i] for i in ids[offset:offset + limit]], len(ids)

        blobs = self.blobs
        first, rest = tokens[0], tokens[1:]
        candidates = self._narrow(tokens)
        if candidates is None:  # a one- or two-letter word: no sequence to look up, test everything
            candidates = range(len(blobs))
        docs = self.docs
        hits = [i for i in candidates
                if first in blobs[i] and all(t in blobs[i] for t in rest)
                and all(_matches(docs[i].get(f), v) for f, v in filters)]

        if len(hits) > BROAD_QUERY:  # "a", "e": too vague to rank, taxonomic order is as good as any
            return [self.docs[i] for i in hits[offset:offset + limit]], len(hits)

        phrase = " ".join(tokens)
        padded_phrase = " " + phrase
        padded_tokens = [" " + t for t in tokens]
        scored = []
        for i in hits:
            tier, length = 4, 0
            for n in self.names[i]:
                if n == phrase:
                    t = 0
                elif n.startswith(phrase):
                    t = 1
                elif padded_phrase in (p := " " + n) or (rest and all(pt in p for pt in padded_tokens)):
                    t = 2  # a word starts with the query (or every word starts a word, in any order)
                else:
                    t = 3
                if t < tier or (t == tier and len(n) < length):
                    tier, length = t, len(n)
                if tier == 0:
                    break
            if tier < 3 or not whole_words:
                scored.append((tier, length, i))
        scored.sort()
        page = scored[offset:offset + limit]
        return [self.docs[i] for _, _, i in page], len(scored)

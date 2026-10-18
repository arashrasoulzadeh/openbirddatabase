"""Shared helpers for filling gaps in the species files from open datasets.

Rules every source follows:
* only EMPTY fields are filled; values that already exist (curated or from earlier sources) are never overwritten,
  unless a source explicitly lists a field in `replace` (used to clean up a known-bad placeholder);
* every file that changes gets the source name in `sources` and today's date in `last_updated`;
* a source produces a patch file `_data/enrichment/<source>.json` first (inspectable, re-runnable), applying is a
  separate step.
"""

import json
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
from _scripts.cache_utils import slug_of  # noqa: E402
from _scripts.completeness import is_filled  # noqa: E402

BIRDS_DIR = ROOT / "birds"
CACHE_DIR = ROOT / "_data" / "enrichment"
LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


def species_paths() -> Dict[str, Path]:
    """{slug: path} for every species file."""
    return {p.stem: p for p in BIRDS_DIR.glob("**/*.md")}


def read_species(path: Path) -> Tuple[Dict[str, Any], str]:
    """(frontmatter as dict, body text that follows the closing ---)."""
    raw = path.read_text(encoding="utf-8")
    _, front, body = raw.split("---", 2)
    return yaml.load(front, Loader=LOADER) or {}, body


def write_species(path: Path, fm: Dict[str, Any], body: str) -> None:
    text = yaml.dump(fm, sort_keys=False, allow_unicode=True, default_flow_style=False)
    path.write_text(f"---\n{text}---{body}", encoding="utf-8")


def get_path(fm: Dict[str, Any], dotted: str) -> Any:
    node: Any = fm
    for part in dotted.split("."):
        if not isinstance(node, dict):
            return None
        node = node.get(part)
    return node


def set_path(fm: Dict[str, Any], dotted: str, value: Any) -> None:
    node = fm
    parts = dotted.split(".")
    for part in parts[:-1]:
        child = node.get(part)
        if not isinstance(child, dict):
            child = {}
            node[part] = child
        node = child
    node[parts[-1]] = value


def apply_patch(
    fm: Dict[str, Any],
    patch: Dict[str, Any],
    source_label: str,
    replace: Optional[List[str]] = None,
) -> List[str]:
    """Merge a {"section.field": value} patch into `fm`. Returns the fields that changed."""
    changed: List[str] = []
    for dotted, value in patch.items():
        if value is None or (isinstance(value, (list, dict, str)) and not value):
            continue
        section, _, field = dotted.partition(".")
        current = get_path(fm, dotted)
        if is_filled(current, section, field) and dotted not in (replace or []):
            continue
        if current == value:
            continue
        set_path(fm, dotted, value)
        changed.append(dotted)
    if changed:
        sources = fm.get("sources")
        if not isinstance(sources, list):
            sources = []
        if source_label not in sources:
            sources.append(source_label)
        fm["sources"] = sources
        fm["last_updated"] = date.today().isoformat()
    return changed


def save_patches(source: str, patches: Dict[str, Dict[str, Any]]) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    out = CACHE_DIR / f"{source}.json"
    out.write_text(json.dumps(patches, ensure_ascii=False, indent=0), encoding="utf-8")
    return out


def load_patches(source: str) -> Dict[str, Dict[str, Any]]:
    return json.loads((CACHE_DIR / f"{source}.json").read_text(encoding="utf-8"))


def apply_source(source: str, label: str, replace: Optional[List[str]] = None, dry_run: bool = False) -> Dict[str, int]:
    """Apply a saved patch file to the species files. Returns how many files and fields changed."""
    patches = load_patches(source)
    paths = species_paths()
    files = fields = missing = 0
    per_field: Dict[str, int] = {}
    for name, patch in patches.items():
        path = paths.get(slug_of(name))
        if not path:
            missing += 1
            continue
        fm, body = read_species(path)
        changed = apply_patch(fm, patch, label, replace)
        if changed:
            files += 1
            fields += len(changed)
            for f in changed:
                per_field[f] = per_field.get(f, 0) + 1
            if not dry_run:
                write_species(path, fm, body)
    return {"files": files, "fields": fields, "unknown_species": missing, **{f"+{k}": v for k, v in sorted(per_field.items())}}


class Progress:
    """Terminal progress: one live line (bar, %, rate, ETA, ok/failed) on a TTY, a plain line every `every` items otherwise.
    `log(msg)` prints a line above the bar (used for --verbose and failures)."""

    def __init__(self, total: int, label: str, every: int = 250) -> None:
        import time
        self.total, self.label, self.every = total, label, every
        self.done = self.failed = 0
        self.started = time.time()
        self.tty = sys.stderr.isatty()
        self._last_len = 0

    def _line(self) -> str:
        import time
        elapsed = max(time.time() - self.started, 0.001)
        rate = self.done / elapsed
        left = (self.total - self.done) / rate if rate else 0
        pct = self.done / self.total if self.total else 1
        filled = int(28 * pct)
        eta = f"{int(left // 3600)}h{int(left % 3600 // 60):02d}m" if left >= 3600 else f"{int(left // 60)}m{int(left % 60):02d}s"
        return (f"{self.label} [{'█' * filled}{'░' * (28 - filled)}] {self.done}/{self.total} {pct:5.1%}  "
                f"{rate:4.1f}/s  ETA {eta}  failed {self.failed}")

    def log(self, message: str) -> None:
        if self.tty:
            sys.stderr.write("\r" + " " * self._last_len + "\r")
        print(message, file=sys.stderr, flush=True)
        if self.tty:
            self.render()

    def render(self) -> None:
        line = self._line()
        sys.stderr.write("\r" + line + " " * max(0, self._last_len - len(line)))
        sys.stderr.flush()
        self._last_len = len(line)

    def step(self, ok: bool = True) -> None:
        self.done += 1
        self.failed += (not ok)
        if self.tty:
            self.render()
        elif self.done % self.every == 0:
            print(self._line(), file=sys.stderr, flush=True)

    def finish(self) -> None:
        if self.tty:
            self.render()
            sys.stderr.write("\n")
        else:
            print(self._line(), file=sys.stderr, flush=True)

#!/usr/bin/env python3
"""Fill gaps in the species files from open datasets.

    python _scripts/enrich.py fetch avonet        download + build the patch file (_data/enrichment/avonet.json)
    python _scripts/enrich.py fetch gbif -v -n 20  try 20 species, one line each (drop -n/-v for the full run)
    python _scripts/enrich.py fetch gbif -w 3      countries + Xeno-canto ids + photo links for every species (slow, resumable)
    python _scripts/enrich.py fetch photos         download the photos into images/
    python _scripts/enrich.py apply avonet        merge it into birds/ (add --dry-run to only count)
    python _scripts/enrich.py clean-names         blank placeholder / untranslated common names
    python _scripts/enrich.py clean-distribution  restricted-range flag, realm code case

Sources: avonet, anage, amniote, gbif, xenocanto, photos, wikidata.
`fetch photos` downloads one CC0/CC BY photo per species into images/ (needs `fetch gbif` first). Only empty fields are ever filled.
"""

import argparse
import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _scripts.enrich import common  # noqa: E402

SOURCES = {
    "avonet": ("_scripts.enrich.avonet", []),
    "anage": ("_scripts.enrich.anage", []),
    "amniote": ("_scripts.enrich.amniote", []),
    "gbif": ("_scripts.enrich.gbif", []),
    "xenocanto": ("_scripts.enrich.xenocanto", []),
    "photos": ("_scripts.enrich.photos", []),
    "wikidata": ("_scripts.enrich.wikidata", []),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["fetch", "apply", "clean-names", "clean-distribution"])
    parser.add_argument("source", nargs="?", choices=sorted(SOURCES))
    parser.add_argument("--dry-run", action="store_true", help="apply: only count what would change")
    parser.add_argument("-w", "--workers", type=int, default=None, help="fetch: parallel requests (gbif default 3, photos 6; GBIF rate-limits above ~4)")
    parser.add_argument("-v", "--verbose", action="store_true", help="fetch: print a line per species")
    parser.add_argument("-n", "--limit", type=int, default=0, help="fetch: only the first N species (try -n 20 -v first)")
    parser.add_argument("--delay", type=float, default=0.0, help="fetch: seconds each worker waits after a species (gentler on the API)")
    args = parser.parse_args()

    if args.command in ("clean-names", "clean-distribution"):
        from _scripts.enrich import clean_distribution, clean_names
        module = clean_names if args.command == "clean-names" else clean_distribution
        result = module.run(dry_run=args.dry_run)
        print(("DRY RUN " if args.dry_run else "") + ", ".join(f"{k}={v}" for k, v in result.items()))
        return 0
    if not args.source:
        parser.error("a source is required for fetch/apply")

    module = importlib.import_module(SOURCES[args.source][0])
    if args.command == "fetch":
        options = {"verbose": args.verbose, "limit": args.limit, "delay": args.delay}
        if args.workers:
            options["workers"] = args.workers
        try:
            print(module.run(**options))
        except TypeError:  # sources without progress options (avonet, anage, ...)
            print(module.run())
    else:
        result = common.apply_source(
            args.source, module.LABEL, getattr(module, "REPLACE", None), dry_run=args.dry_run
        )
        print(("DRY RUN " if args.dry_run else "") + ", ".join(f"{k}={v}" for k, v in result.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())

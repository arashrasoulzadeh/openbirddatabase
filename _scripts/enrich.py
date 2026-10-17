#!/usr/bin/env python3
"""Fill gaps in the species files from open datasets.

    python _scripts/enrich.py fetch avonet        download + build the patch file (_data/enrichment/avonet.json)
    python _scripts/enrich.py apply avonet        merge it into birds/ (add --dry-run to only count)
    python _scripts/enrich.py clean-names         blank placeholder / untranslated common names
    python _scripts/enrich.py clean-distribution  restricted-range flag, realm code case

Sources: avonet, anage, generation, gbif, xenocanto, wikidata. Only empty fields are ever filled.
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
    "generation": ("_scripts.enrich.generation", []),
    "gbif": ("_scripts.enrich.gbif", []),
    "xenocanto": ("_scripts.enrich.xenocanto", []),
    "wikidata": ("_scripts.enrich.wikidata", []),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["fetch", "apply", "clean-names", "clean-distribution"])
    parser.add_argument("source", nargs="?", choices=sorted(SOURCES))
    parser.add_argument("--dry-run", action="store_true")
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
        print(module.run())
    else:
        result = common.apply_source(
            args.source, module.LABEL, getattr(module, "REPLACE", None), dry_run=args.dry_run
        )
        print(("DRY RUN " if args.dry_run else "") + ", ".join(f"{k}={v}" for k, v in result.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Distribution clean-up.

* "Range size: 1.0" in `breeding_range` was BIRDBASE's restricted-range flag written as text. It becomes the boolean
  `distribution.restricted_range: true` and the text field is emptied (the real range area comes from AVONET).
* Biogeographic realm codes are upper case letters; two files had a lower case "p".
"""

import re
from typing import Dict, List

from .common import read_species, species_paths, write_species

LABEL = "distribution cleanup"
FLAG = re.compile(r"^\s*Range size:\s*[\d.]+\s*$")


def clean(distribution: dict) -> List[str]:
    changes: List[str] = []
    breeding = distribution.get("breeding_range")
    if isinstance(breeding, str) and FLAG.match(breeding):
        distribution["breeding_range"] = ""
        distribution["restricted_range"] = True
        changes.append("restricted-range flag")
    realms = distribution.get("biogeographic_realms")
    if isinstance(realms, list):
        fixed = [str(r).upper() for r in realms]
        if fixed != [str(r) for r in realms]:
            distribution["biogeographic_realms"] = fixed
            changes.append("realm code case")
    return changes


def run(dry_run: bool = False) -> Dict[str, int]:
    counts: Dict[str, int] = {"files": 0}
    for path in species_paths().values():
        fm, body = read_species(path)
        distribution = fm.get("distribution")
        if not isinstance(distribution, dict):
            continue
        changes = clean(distribution)
        if not changes:
            continue
        counts["files"] += 1
        for change in changes:
            counts[change] = counts.get(change, 0) + 1
        if not dry_run:
            write_species(path, fm, body)
    return counts

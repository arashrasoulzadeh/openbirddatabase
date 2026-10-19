"""Fields BIRDBASE (Sekercioglu et al. 2025, CC BY 4.0, https://doi.org/10.6084/m9.figshare.27051040) supports but the first
import left empty:

* habitat.secondary - the habitats a species uses besides its primary one (BIRDBASE numbers habitats in order of
  preference, and habitat_types already holds them in that order).
* reproduction.mating_system - only the clear cases: cooperative breeder, lekking, strictly monogamous or strictly
  polygynous. Species flagged as both monogamous and polygynous are left empty rather than guessed.
    python _scripts/enrich.py fetch birdbase_extra
    python _scripts/enrich.py apply birdbase_extra
"""

import subprocess
from typing import Any, Dict

from .common import ROOT, read_species, save_patches, species_paths

SOURCE = "birdbase_extra"
LABEL = "BIRDBASE v2025.1 (Sekercioglu et al. 2025)"
URL = "https://ndownloader.figshare.com/files/55634729"
XLSX = ROOT / "_data" / "birdbase" / "birdbase.xlsx"
SAME_HABITAT = {"Shrub": "Shrubland", "Riparian": "Riverine", "Sea": "Sea/Pelagic"}  # primary and habitat_types spell some differently


def _kind(value: str) -> str:
    return SAME_HABITAT.get(value, value)


def mating_systems() -> Dict[str, str]:
    import pandas as pd

    if not XLSX.exists():
        XLSX.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["curl", "-sL", "-m", "300", "-o", str(XLSX), URL], check=True)
    raw = pd.read_excel(XLSX, sheet_name="Data", header=None)
    group, name = raw.iloc[0].ffill(), raw.iloc[1]
    body = raw.iloc[2:].reset_index(drop=True)
    body.columns = [f"{a}|{b}" for a, b in zip(group, name)]
    latin = next(c for c in body.columns if c.startswith("Taxonomy|Latin"))

    def flag(row, column):
        value = row[column]
        try:
            return int(value) if pd.notna(value) else None
        except (TypeError, ValueError):  # a few cells hold text or Excel times instead of 0 / 1 / 2
            return None

    result: Dict[str, str] = {}
    for _, row in body.iterrows():
        mono, poly = flag(row, "Reproductive Behavior|Mono"), flag(row, "Reproductive Behavior|Poly")
        coop, lek = flag(row, "Reproductive Behavior|Coop"), flag(row, "Social Behavior|Social_6")
        if coop in (1, 2):
            system = "Cooperative"
        elif lek == 1:
            system = "Lek"
        elif mono == 1 and not poly:
            system = "Monogamous"
        elif poly == 1 and not mono:
            system = "Polygynous"
        else:
            continue
        result[str(row[latin]).strip()] = system
    return result


def build() -> Dict[str, Dict[str, Any]]:
    mating = mating_systems()
    patches: Dict[str, Dict[str, Any]] = {}
    for path in species_paths().values():
        fm, _ = read_species(path)
        name = (fm.get("names") or {}).get("scientific")
        patch: Dict[str, Any] = {}
        habitat = fm.get("habitat") or {}
        primary = _kind(habitat.get("primary") or "")
        secondary = [h for h in habitat.get("habitat_types") or [] if _kind(h) != primary]
        if secondary:
            patch["habitat.secondary"] = secondary
        if name in mating:
            patch["reproduction.mating_system"] = mating[name]
        if patch:
            patches[name] = patch
    return patches


def run(**_options) -> str:
    out = save_patches(SOURCE, build())
    return f"patches -> {out.relative_to(ROOT)}"

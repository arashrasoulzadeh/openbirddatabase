"""Amniote life-history database (Myhrvold et al. 2015, Ecology 96:3109, CC0): ~9,800 birds compiled from the literature.

Fills clutch size, clutches per year, incubation days, fledging age, egg size and maximum longevity.
Data: https://doi.org/10.6084/m9.figshare.3563457  (ECOL_96_269.zip, Data_Files/Amniote_Database_Aug_2015.csv)
Missing values are stored as -999 in the source and are ignored.
"""

import subprocess
import zipfile
from typing import Any, Dict

import pandas as pd

from .common import ROOT, save_patches

SOURCE = "amniote"
LABEL = "Amniote life-history database (Myhrvold et al. 2015)"
URL = "https://ndownloader.figshare.com/files/8067269"
DIR = ROOT / "_data" / "amniote"
CSV = DIR / "Data_Files" / "Amniote_Database_Aug_2015.csv"


def fetch() -> None:
    DIR.mkdir(parents=True, exist_ok=True)
    if not CSV.exists():
        archive = DIR / "ECOL_96_269.zip"
        subprocess.run(["curl", "-sL", "-m", "200", "-o", str(archive), URL], check=True)
        with zipfile.ZipFile(archive) as z:
            z.extractall(DIR)


def _num(row: Any, column: str):
    value = getattr(row, column)
    return float(value) if pd.notna(value) and float(value) > 0 else None


def build() -> Dict[str, Dict[str, Any]]:
    df = pd.read_csv(CSV, encoding="latin-1", na_values=["-999"])
    birds = df[df["class"] == "Aves"]
    patches: Dict[str, Dict[str, Any]] = {}
    for row in birds.itertuples(index=False):
        name = f"{row.genus} {row.species}".strip()
        patch: Dict[str, Any] = {}
        clutch = _num(row, "litter_or_clutch_size_n")
        broods = _num(row, "litters_or_clutches_per_y")
        incubation = _num(row, "incubation_d")
        fledging = _num(row, "fledging_age_d")
        egg_length = _num(row, "egg_length_mm")
        egg_width = _num(row, "egg_width_mm")
        longevity = _num(row, "maximum_longevity_y")
        if clutch:
            patch["reproduction.clutch_size_mean"] = round(clutch, 1)
        if broods and round(broods) >= 1:
            patch["reproduction.broods_per_year"] = int(round(broods))
        if incubation:
            patch["reproduction.incubation_days"] = max(1, int(round(incubation)))
        if fledging:
            patch["reproduction.fledging_days"] = max(1, int(round(fledging)))
        if egg_length:
            patch["reproduction.egg_length_mm"] = round(egg_length, 1)
        if egg_width:
            patch["reproduction.egg_width_mm"] = round(egg_width, 1)
        if longevity:
            patch["demography.max_longevity_years"] = max(1, int(round(longevity)))
        if patch:
            patches[name] = patch
    return patches


def run() -> str:
    fetch()
    patches = build()
    out = save_patches(SOURCE, patches)
    return f"{len(patches)} species -> {out.relative_to(ROOT)}"

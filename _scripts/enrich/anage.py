"""AnAge (Tacutu et al., Human Ageing Genomic Resources): curated longevity and life-history data.

Fills maximum longevity, incubation days, clutch size and clutches per year for birds. Only entries with data
quality "acceptable" or "high" are used ("low" and "questionable" are skipped).
Data: https://genomics.senescence.info/species/  (dataset.zip, anage_data.txt)
"""

import subprocess
import zipfile
from typing import Any, Dict

import pandas as pd

from .common import ROOT, save_patches

SOURCE = "anage"
LABEL = "AnAge (Tacutu et al., Human Ageing Genomic Resources)"
URL = "https://genomics.senescence.info/species/dataset.zip"
DIR = ROOT / "_data" / "anage"
TEXT = DIR / "anage_data.txt"
GOOD_QUALITY = {"acceptable", "high"}


def fetch() -> None:
    DIR.mkdir(parents=True, exist_ok=True)
    if not TEXT.exists():
        archive = DIR / "dataset.zip"
        subprocess.run(["curl", "-sL", "-m", "120", "-o", str(archive), URL], check=True)
        with zipfile.ZipFile(archive) as z:
            z.extractall(DIR)


def _positive(value: Any):
    return float(value) if pd.notna(value) and float(value) > 0 else None


def build() -> Dict[str, Dict[str, Any]]:
    df = pd.read_csv(TEXT, sep="\t", encoding="latin-1")
    birds = df[(df["Class"] == "Aves") & (df["Data quality"].astype(str).str.lower().isin(GOOD_QUALITY))]
    patches: Dict[str, Dict[str, Any]] = {}
    for row in birds.itertuples(index=False):
        name = f"{row.Genus} {row.Species}".strip()
        patch: Dict[str, Any] = {}
        longevity = _positive(row[birds.columns.get_loc("Maximum longevity (yrs)")])
        incubation = _positive(row[birds.columns.get_loc("Gestation/Incubation (days)")])
        clutch = _positive(row[birds.columns.get_loc("Litter/Clutch size")])
        broods = _positive(row[birds.columns.get_loc("Litters/Clutches per year")])
        if longevity:
            patch["demography.max_longevity_years"] = max(1, int(round(longevity)))
        if incubation:
            patch["reproduction.incubation_days"] = max(1, int(round(incubation)))
        if clutch:
            patch["reproduction.clutch_size_mean"] = round(clutch, 1)
        if broods and round(broods) >= 1:
            patch["reproduction.broods_per_year"] = int(round(broods))
        if patch:
            patches[name] = patch
    return patches


def run() -> str:
    fetch()
    patches = build()
    out = save_patches(SOURCE, patches)
    return f"{len(patches)} species -> {out.relative_to(ROOT)}"

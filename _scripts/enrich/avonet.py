"""AVONET (Tobias et al. 2022, Ecology Letters, CC BY 4.0): measurements of museum specimens for ~11,000 birds.

Fills bill (culmen), tarsus, wing and tail length, body mass (if missing) and the mapped range size.
Rows whose traits were *inferred from a related species* (Inference = YES) are skipped: only measured values are used.
Data: https://doi.org/10.6084/m9.figshare.16586228  (file 34480856, "AVONET Supplementary dataset 1.xlsx")
"""

import subprocess
from typing import Any, Dict

import pandas as pd

from .common import CACHE_DIR, ROOT, save_patches

SOURCE = "avonet"
LABEL = "AVONET (Tobias et al. 2022)"
URL = "https://ndownloader.figshare.com/files/34480856"
XLSX = ROOT / "_data" / "avonet" / "AVONET.xlsx"

# (sheet, species column) in order of preference: eBird/Clements names match our names best
SHEETS = [("AVONET2_eBird", "Species2"), ("AVONET1_BirdLife", "Species1"), ("AVONET3_BirdTree", "Species3")]
COLUMNS = {
    "Beak.Length_Culmen": "morphology.bill_length_mm",
    "Tarsus.Length": "morphology.tarsus_length_mm",
    "Wing.Length": "morphology.wing_length_mm",
    "Tail.Length": "morphology.tail_length_mm",
    "Mass": "morphology.body_mass_g",
    "Range.Size": "distribution.range_size_km2",
}


def fetch() -> None:
    XLSX.parent.mkdir(parents=True, exist_ok=True)
    if not XLSX.exists():
        subprocess.run(["curl", "-sL", "-o", str(XLSX), URL], check=True)


def build(include_inferred: bool = False) -> Dict[str, Dict[str, Any]]:
    book = pd.ExcelFile(XLSX)
    patches: Dict[str, Dict[str, Any]] = {}
    for sheet, name_col in SHEETS:
        df = book.parse(sheet)
        if "Inference" in df.columns and not include_inferred:
            df = df[df["Inference"].astype(str).str.upper() != "YES"]
        for _, row in df.iterrows():
            name = str(row[name_col]).strip()
            if not name or name == "nan":
                continue
            patch = patches.setdefault(name, {})
            for column, field in COLUMNS.items():
                if column not in df.columns or field in patch:
                    continue
                value = row[column]
                if pd.notna(value) and float(value) > 0:
                    patch[field] = round(float(value), 1) if field != "distribution.range_size_km2" else round(float(value), 0)
    return {k: v for k, v in patches.items() if v}


def run() -> str:
    fetch()
    patches = build()
    out = save_patches(SOURCE, patches)
    return f"{len(patches)} species with measurements -> {out.relative_to(ROOT)}"

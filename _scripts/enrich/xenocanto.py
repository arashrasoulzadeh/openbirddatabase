"""Xeno-canto recordings (CC licences per recording), found through GBIF. See gbif.py: `fetch gbif` collects both."""

from .gbif import build_recordings
from .common import ROOT, save_patches

SOURCE = "xenocanto"
LABEL = "Xeno-canto recordings (via GBIF)"


def run() -> str:
    out = save_patches(SOURCE, build_recordings())
    return f"patches -> {out.relative_to(ROOT)}"

"""How complete is a species file? One definition shared by the API, the cache warmer and the dashboard statistics.

"Complete" means every field the schema defines for the data sections has a real value. Two scores are reported:

* core    morphology, distribution, habitat, diet, behavior, reproduction, demography, conservation
          (data the BIRDBASE / AVONICHE / BirdNET / BirdFYI sources are meant to provide)
* expert  veterinary and enrichment (curated by experts; only a few species have them)

Numbers (including 0) and booleans count as filled. Empty strings, "nan", "Unknown", "No Information", empty lists and
empty objects count as missing. `diet.categories` and `diet.foraging_niches` are filled when any value is above zero.
"""

from typing import Any, Dict, List, Tuple

CORE_FIELDS: Dict[str, List[str]] = {
    "morphology": ["body_mass_g", "body_length_cm", "wingspan_cm", "bill_length_mm", "tarsus_length_mm",
                   "wing_length_mm", "tail_length_mm"],
    "distribution": ["breeding_range", "non_breeding_range", "countries", "biogeographic_realms", "endemic",
                     "island_endemic"],
    "habitat": ["primary", "secondary", "habitat_breadth", "elevational_min_m", "elevational_max_m", "habitat_types"],
    "diet": ["primary", "diet_breadth", "categories", "foraging_niches"],
    "behavior": ["sociality", "flock_size_typical", "territorial", "migration_status", "movement_type",
                 "activity_pattern", "vocalizations.song", "vocalizations.calls", "xeno_canto_ids"],
    "reproduction": ["clutch_size_mean", "clutch_size_min", "clutch_size_max", "egg_length_mm", "egg_width_mm",
                     "incubation_days", "fledging_days", "broods_per_year", "nest_type", "nest_placement",
                     "nest_material", "mating_system", "parental_care"],
    "demography": ["generation_length_years", "max_longevity_years", "annual_survival_adult",
                   "annual_survival_juvenile", "population_trend", "population_size", "density_individuals_per_km2"],
    "conservation": ["iucn_status", "cites_appendix", "threats", "conservation_actions"],
}

EXPERT_FIELDS: Dict[str, List[str]] = {
    "veterinary": ["common_diseases", "vaccination_schedule", "deworming_frequency_months",
                   "health_check_frequency_months", "zoonotic_risks", "emergency_signs", "vet_specialist_type"],
    "enrichment": ["foraging_toys", "social_enrichment", "cognitive_toys", "bathing", "training", "play_behaviors",
                   "environmental_enrichment"],
}

_EMPTY_STRINGS = {"", "nan", "unknown", "no information"}
_ANY_POSITIVE = {"diet.categories", "diet.foraging_niches"}


def _get(section: Any, dotted: str) -> Any:
    node = section
    for part in dotted.split("."):
        if not isinstance(node, dict):
            return None
        node = node.get(part)
    return node


def is_filled(value: Any, section: str = "", field: str = "") -> bool:
    if f"{section}.{field}" in _ANY_POSITIVE:
        return isinstance(value, dict) and any(isinstance(v, (int, float)) and v > 0 for v in value.values())
    if value is None:
        return False
    if isinstance(value, bool):
        return True
    if isinstance(value, float) and value != value:  # NaN
        return False
    if isinstance(value, str):
        return value.strip().lower() not in _EMPTY_STRINGS
    if isinstance(value, (list, dict)):
        return len(value) > 0
    return True


def _score(fm: Dict[str, Any], fields: Dict[str, List[str]]) -> Dict[str, Any]:
    filled = total = 0
    missing: Dict[str, List[str]] = {}
    sections: Dict[str, Dict[str, int]] = {}
    for section, names in fields.items():
        data = fm.get(section) or {}
        got = [n for n in names if is_filled(_get(data, n), section, n)]
        filled += len(got)
        total += len(names)
        sections[section] = {"filled": len(got), "total": len(names)}
        gaps = [n for n in names if n not in got]
        if gaps:
            missing[section] = gaps
    return {
        "score": round(filled / total, 4) if total else 0.0,
        "filled": filled,
        "total": total,
        "sections": sections,
        "missing": missing,
    }


def evaluate(fm: Dict[str, Any]) -> Dict[str, Any]:
    """{'core': {...}, 'expert': {...}, 'expert_verified': bool}: scores, field counts and the missing fields."""
    verified = any((fm.get(s) or {}).get("verified") is True for s in EXPERT_FIELDS)
    return {"core": _score(fm, CORE_FIELDS), "expert": _score(fm, EXPERT_FIELDS), "expert_verified": verified}


def with_completeness(fm: Dict[str, Any]) -> Dict[str, Any]:
    """The species document as the API serves it: the file's data plus its completeness report."""
    return {**fm, "completeness": evaluate(fm)}


def field_paths() -> List[Tuple[str, str]]:
    """Every core (section, field) pair, in schema order."""
    return [(s, f) for s, names in CORE_FIELDS.items() for f in names]

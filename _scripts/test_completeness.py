"""Completeness scoring tests."""

from _scripts.completeness import CORE_FIELDS, EXPERT_FIELDS, evaluate, is_filled, with_completeness

TOTAL_CORE = sum(len(v) for v in CORE_FIELDS.values())


def test_empty_species_is_zero_percent_with_every_field_missing():
    result = evaluate({})
    assert result["core"]["score"] == 0.0
    assert result["core"]["total"] == TOTAL_CORE == 56
    assert sum(len(v) for v in result["core"]["missing"].values()) == TOTAL_CORE


def test_filled_fields_are_counted_and_missing_ones_listed():
    fm = {
        "morphology": {"body_mass_g": 18.4, "wingspan_cm": None, "bill_length_mm": 0},
        "habitat": {"primary": "Forest", "secondary": [], "habitat_types": ["Forest"]},
        "distribution": {"endemic": False, "countries": []},
    }
    core = evaluate(fm)["core"]
    assert core["sections"]["morphology"] == {"filled": 2, "total": 7}   # 0 is a real value, None is not
    assert core["sections"]["habitat"]["filled"] == 2
    assert core["sections"]["distribution"]["filled"] == 1              # False is a real value, [] is not
    assert "wingspan_cm" in core["missing"]["morphology"]
    assert "body_mass_g" not in core["missing"]["morphology"]
    assert core["filled"] == 5
    assert core["score"] == round(5 / TOTAL_CORE, 4)


def test_placeholder_strings_count_as_missing():
    for value in ("", "nan", "Unknown", "No Information", "  "):
        assert not is_filled(value)
    assert is_filled("Resident") and is_filled("Not listed") and is_filled(0) and is_filled(False)
    assert not is_filled(float("nan"))


def test_categories_and_niches_need_a_value_above_zero():
    zeros = {"invertebrates": 0, "seeds": 0.0}
    assert not is_filled(zeros, "diet", "categories")
    assert is_filled({"invertebrates": 7, "seeds": 0}, "diet", "categories")
    assert not is_filled({}, "diet", "foraging_niches")
    assert is_filled({"seeds_ground": 0.4}, "diet", "foraging_niches")


def test_nested_vocalization_fields():
    fm = {"behavior": {"vocalizations": {"song": "", "calls": ["chip"]}}}
    behavior = evaluate(fm)["core"]
    assert "vocalizations.song" in behavior["missing"]["behavior"]
    assert "vocalizations.calls" not in behavior["missing"]["behavior"]


def test_expert_sections_are_scored_separately_and_do_not_lower_the_core_score():
    fm = {"veterinary": {"common_diseases": ["Aspergillosis"], "verified": True}}
    result = evaluate(fm)
    assert result["core"]["score"] == 0.0
    assert result["expert"]["filled"] == 1
    assert result["expert"]["total"] == sum(len(v) for v in EXPERT_FIELDS.values())
    assert result["expert_verified"] is True
    assert evaluate({"veterinary": {"verified": False}})["expert_verified"] is False


def test_with_completeness_keeps_the_original_data():
    fm = {"names": {"en": "Great Tit"}}
    out = with_completeness(fm)
    assert out["names"] == {"en": "Great Tit"} and "completeness" in out and "completeness" not in fm

"""Unit tests for specs.py"""
import pytest
from specs import CORPUS, get_spec_by_id, specs_by_tier, specs_by_algo_class, Spec


def test_corpus_size():
    assert len(CORPUS) == 20, f"Expected 20 specs, got {len(CORPUS)}"


def test_tier_stratification():
    for tier in ["T1", "T2", "T3", "T4"]:
        specs = specs_by_tier(tier)
        assert len(specs) > 0, f"Tier {tier} has no specs"


def test_algo_class_stratification():
    for ac in ["AC1", "AC2", "AC3", "AC4"]:
        specs = specs_by_algo_class(ac)
        assert len(specs) > 0, f"Algorithm class {ac} has no specs"


def test_get_spec_by_id_valid():
    spec = get_spec_by_id("t1-ac2-001")
    assert spec.id == "t1-ac2-001"
    assert spec.title == "Binary Search"
    assert spec.tier == "T1"


def test_get_spec_by_id_invalid():
    with pytest.raises(ValueError):
        get_spec_by_id("not-a-real-id")


def test_spec_to_markdown():
    spec = get_spec_by_id("t1-ac3-001")
    md = spec.to_markdown()
    assert "t1-ac3-001" in md
    assert "Factorial" in md
    assert "T1" in md
    assert "AC3" in md


def test_spec_has_inputs_outputs():
    for spec in CORPUS:
        assert len(spec.inputs) > 0, f"{spec.id} has no inputs"
        assert len(spec.outputs) > 0, f"{spec.id} has no outputs"


def test_spec_has_edge_cases():
    for spec in CORPUS:
        assert len(spec.edge_cases) > 0, f"{spec.id} has no edge cases"


def test_no_duplicate_spec_ids():
    ids = [s.id for s in CORPUS]
    assert len(ids) == len(set(ids)), "Duplicate spec IDs found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

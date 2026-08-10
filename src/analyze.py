"""
Phase 0–6: Main analysis pipeline entry point.

Usage:
    python -m 2.code.src.analyze

This runs all phases in sequence after prerequisites are met:
    Phase 0: Power analysis (Phase 0b)
    Phase 1: Spec corpus (already defined in specs.py)
    Phase 2: Generation (generate.py — requires model API access)
    Phase 3: Parsing + IR lowering
    Phase 4: Invariant mining (within-language + cross-language)
    Phase 5: Self-similarity
    Phase 6: Mismatch analysis
    Phase 7: Statistical evaluation

Each phase can also be run independently.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List

# Make sibling modules importable regardless of how this file is invoked
# (e.g. `python -m 2.code.src.analyze` from the project root).
_SRC_DIR = Path(__file__).resolve().parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

# Project root is 2 levels up from this file
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "3.data"
RESULTS_DIR = PROJECT_ROOT / "4.results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


class _ASTProxy:
    """Minimal ParsedImplementation-compatible wrapper for within-language mining.

    mine_within_language() only needs ``impl.ast`` (a native ASTNode), so we
    hydrate the AST saved by Phase 3 instead of the full parsed record.
    """
    def __init__(self, ast, spec_id, language):
        self.ast = ast
        self.spec_id = spec_id
        self.language = language


def phase_0b_power_analysis() -> Dict:
    """Phase 0b: Power analysis."""
    print("\n" + "=" * 60)
    print("PHASE 0b: Power analysis")
    print("=" * 60)
    from power_analysis import full_power_analysis, PowerAnalysisResult
    # Placeholder — replace with real pilot data when available
    result = PowerAnalysisResult(
        pilot_n=0,
        pilot_variance=0.0,
        required_n=30,  # conservative default
        effect_size=0.5,
        alpha=0.05,
        power=0.8,
        two_tailed=True,
    )
    path = RESULTS_DIR / "power_analysis.json"
    path.write_text(json.dumps(result.to_dict(), indent=2))
    print(f"  → Saved: {path}")
    print(f"  → Required N per (spec, language) cell: {result.required_n}")
    return result.to_dict()


def phase_3_parse_and_lower(data_dir: Path, output_dir: Path) -> Dict:
    """Phase 3: Parse all implementations and lower to IR."""
    print("\n" + "=" * 60)
    print("PHASE 3: Parsing + IR lowering")
    print("=" * 60)

    from parse import ParsedImplementation
    from lower import lower_implementation

    ir_output = output_dir / "ir"
    ir_output.mkdir(parents=True, exist_ok=True)

    # ── 1. Discover implementation source files ──────────────────────────────
    # Scan spec/lang/impl_N/implementation.{ext} — exactly one file per
    # (spec, lang, impl_idx). Non-recursive and scoped to impl_*/ prevents
    # any double-counting if multiple generation runs ever coexist.
    EXT_MAP = {'.py': 'python', '.rs': 'rust', '.hs': 'haskell',
               '.ml': 'ocaml', '.go': 'go', '.ts': 'typescript'}

    source_files: List[Path] = []
    for ext, lang in EXT_MAP.items():
        for spec_dir in data_dir.iterdir():
            if not spec_dir.is_dir():
                continue
            for lang_dir in spec_dir.iterdir():
                if not lang_dir.is_dir():
                    continue
                for impl_dir in lang_dir.iterdir():
                    if not impl_dir.is_dir():
                        continue
                    impl_file = impl_dir / f"implementation{ext}"
                    if impl_file.exists():
                        source_files.append(impl_file)

    # Assert we found exactly the expected number of implementations.
    # Canonical corpus: 20 specs × 6 langs × 3 impls = 360.
    # Langs with 0 impls for a given spec (e.g. t2-dp1-001 missing haskell)
    # are flagged as warnings but do not raise — the assertion checks total N.
    EXPECTED_TOTAL = 360
    if len(source_files) != EXPECTED_TOTAL:
        by_cell: Dict[str, int] = {}
        for f in source_files:
            key = f"{f.parent.parent.parent.name}/{f.parent.parent.name}"
            by_cell[key] = by_cell.get(key, 0) + 1
        missing = [k for k, v in by_cell.items() if v < 3]
        if missing:
            print(f"  ⚠ {len(missing)} cells with < 3 implementations: "
                  f"{missing[:5]}{'...' if len(missing) > 5 else ''}")
        raise AssertionError(
            f"phase_3: found {len(source_files)} source files, expected {EXPECTED_TOTAL}. "
            f"Check corpus completeness before proceeding."
        )
    print(f"  ✓ Corpus scan: {len(source_files)} implementations (360 expected)")

    # ── 2. Parse + lower each implementation ──────────────────────────────────
    stats: Dict = {"total": 0, "success": 0, "errors": []}
    for impl_file in source_files:
        lang = EXT_MAP.get(impl_file.suffix)
        spec_id = impl_file.parent.parent.parent.name
        try:
            source = impl_file.read_text()
            parsed = ParsedImplementation.from_source(
                spec_id, lang, source, output_dir=output_dir / "ast" / spec_id / lang
            )
            ir, df, ir_path = lower_implementation(parsed, ir_output / spec_id / lang)
            stats["success"] += 1
        except Exception as e:
            stats["errors"].append({"file": str(impl_file), "error": str(e)})
        stats["total"] += 1

    print(f"  → {stats['success']}/{stats['total']} implementations parsed and lowered")
    if stats["errors"]:
        err_path = output_dir / "phase3_errors.json"
        import json as _json
        err_path.write_text(_json.dumps(stats["errors"], indent=2))
        print(f"  → {len(stats['errors'])} errors (see {err_path.name})")

    path = RESULTS_DIR / "phase3_stats.json"
    import json as _json
    path.write_text(_json.dumps(stats, indent=2))
    return stats


def phase_4_mine(ir_dir: Path, output_dir: Path) -> Dict:
    """Phase 4: Invariant mining (within-language + cross-language)."""
    print("\n" + "=" * 60)
    print("PHASE 4: Invariant mining")
    print("=" * 60)

    from lower import load_ir, GranularityLevel
    from parse import ASTNode
    from mine_invariants import (
        mine_within_language, mine_cross_language, negative_control,
        MiningResult, save_mining_result,
    )

    mining_output = output_dir / "mining"
    mining_output.mkdir(parents=True, exist_ok=True)

    # Collect IRs by (spec, language)
    irs_by_spec_lang: Dict[str, Dict[str, List]] = {}
    for spec_dir in ir_dir.iterdir():
        if not spec_dir.is_dir():
            continue
        spec_id = spec_dir.name
        irs_by_spec_lang[spec_id] = {}
        for lang_dir in spec_dir.iterdir():
            lang = lang_dir.name
            irs_by_spec_lang[spec_id][lang] = []
            for ir_file in lang_dir.glob("*.ir.json"):
                try:
                    ir, df, spec_id_loaded, lang_loaded = load_ir(ir_file)
                    irs_by_spec_lang[spec_id][lang].append((ir, df))
                except Exception:
                    pass

    thresholds = [60, 70, 80]
    all_results = []

    for spec_id, lang_irs in irs_by_spec_lang.items():
        print(f"  Mining {spec_id}...")
        for threshold in thresholds:
            # Within-language (Phase 4a): mine native ASTs saved by Phase 3.
            # This loop was previously empty — H1 (Jaccard replication) can
            # never be computed unless within-language invariants are mined.
            for lang, irs in lang_irs.items():
                if not irs:
                    continue
                impls = []
                ast_dir = output_dir / "ast" / spec_id / lang
                for ast_file in ast_dir.glob("*.ast.json"):
                    try:
                        ast = ASTNode.from_dict(json.loads(ast_file.read_text()))
                        impls.append(_ASTProxy(ast, spec_id, lang))
                    except Exception:
                        pass
                if len(impls) < 2:
                    continue
                try:
                    res = mine_within_language(
                        spec_id=spec_id,
                        language=lang,
                        implementations=impls,
                        threshold=threshold,
                        levels=[GranularityLevel.L3, GranularityLevel.L4],
                    )
                    out_path = mining_output / f"mining_{spec_id}_{lang}_t{threshold}_within.json"
                    save_mining_result(res, out_path)
                    all_results.append(res)
                except Exception as e:
                    print(f"    within-lang mining failed for {spec_id}/{lang}/t{threshold}: {e}")

            # Cross-language
            result = mine_cross_language(
                spec_id=spec_id,
                implementations_by_lang=lang_irs,
                threshold=threshold,
            )
            all_results.append(result)
            save_mining_result(result, mining_output)

    # Negative control
    print("  Running negative control...")
    all_irs_flat = {lang: irs for spec_id, lang_dict in irs_by_spec_lang.items() for lang, irs in lang_dict.items()}
    if all_irs_flat:
        neg_result = negative_control(all_irs_flat, threshold=70)
        path = mining_output / "negative_control.json"
        path.write_text(json.dumps(neg_result, indent=2))
        print(f"  → Negative control: {'PASS' if neg_result['passes_negative_control'] else 'FAIL'}")

    return {"n_results": len(all_results)}


def phase_5_self_similarity(irs_dir: Path, output_dir: Path) -> Dict:
    """Phase 5: Self-similarity matrix."""
    print("\n" + "=" * 60)
    print("PHASE 5: Self-similarity")
    print("=" * 60)
    from self_similarity import build_language_similarity_matrix, self_similarity_matrix_to_csv
    from lower import load_ir
    from mine_invariants import Invariant, GranularityLevel
    from self_similarity import SelfSimilarityProfile, compute_self_similarity_profile

    # Collect profiles from Phase 4 results
    mining_dir = output_dir / "mining"
    profiles: Dict[str, List[SelfSimilarityProfile]] = {}

    for result_file in mining_dir.glob("mining_*_crosslang_*.json"):
        try:
            data = json.loads(result_file.read_text())
            spec_id = data["spec_id"]
            for inv_data in data.get("invariants", []):
                for lang in inv_data.get("languages", []):
                    if lang not in profiles:
                        profiles[lang] = []
                    profiles[lang].append(SelfSimilarityProfile(
                        language=lang,
                        spec_id=spec_id,
                        level=GranularityLevel(inv_data["level"]),
                        agreement_fraction=inv_data["support"],
                    ))
        except Exception:
            pass

    if profiles:
        matrix = build_language_similarity_matrix(profiles)
        path = self_similarity_matrix_to_csv(matrix, output_dir)
        print(f"  → Self-similarity matrix saved: {path}")
        print(matrix.round(3).to_string())
    else:
        print("  → No profile data found — run Phase 4 first")

    return {}


def phase_6_mismatch(generations_dir: Path, output_dir: Path) -> Dict:
    """Phase 6: Mismatch analysis."""
    print("\n" + "=" * 60)
    print("PHASE 6: Mismatch analysis")
    print("=" * 60)
    from mismatch import analyze_mismatch, test_factorial_structure, save_mismatch_results
    from mismatch import MismatchRecord, MismatchType, FailureCategory

    # Load generation attempts from Phase 2
    records: List[MismatchRecord] = []
    for batch_file in generations_dir.rglob("*_batch.json"):
        try:
            data = json.loads(batch_file.read_text())
            spec_id = data["spec_id"]
            lang = data["language"]
            # Simplified: use failure rate as proxy
            if data.get("failure_rate", 0) > 0:
                mismatch_type = MismatchType.OMISSION if data["failure_rate"] > 0.5 else MismatchType.DRIFT
                failure_cat = FailureCategory.FUNCTIONAL if data["failure_rate"] > 0.3 else FailureCategory.STYLISTIC
                records.append(MismatchRecord(
                    spec_id=spec_id, language=lang,
                    mismatch_type=mismatch_type, failure_category=failure_cat,
                    direction="top-down",
                ))
        except Exception:
            pass

    if records:
        try:
            results = analyze_mismatch(records)
            factorial = test_factorial_structure(records)
            path = save_mismatch_results(results, factorial, output_dir)
            print(f"  → Mismatch analysis saved: {path}")
            print(f"  → {len(records)} records analyzed")
        except ValueError as e:
            print(f"  → Mismatch analysis failed (insufficient data): {e}")
    else:
        print("  → No generation data found — run Phase 2 first")

    return {}


def main():
    print("Cross-Language Invariant Mining — Full Pipeline")
    print("=" * 60)

    N = phase_0b_power_analysis()
    print(f"\nConfigured N per cell: {N.get('required_n', 'TBD')}")

    # Phase 3 requires generated implementations
    impl_dir = DATA_DIR / "corpus" / "specs_v1"
    if impl_dir.exists() and any(impl_dir.rglob("*.py")):
        phase_3_parse_and_lower(impl_dir, RESULTS_DIR)
        ir_dir = RESULTS_DIR / "ir"
        if ir_dir.exists():
            phase_4_mine(ir_dir, RESULTS_DIR)
            phase_5_self_similarity(ir_dir, RESULTS_DIR)
        phase_6_mismatch(impl_dir, RESULTS_DIR)
    else:
        print("\n⚠️  No generated implementations found at 3.data/corpus/specs_v1/")
        print("   Run Phase 2 (generate.py) first to produce implementations.")
        print("   Until then, Phases 3–6 are skipped.")

    print("\n" + "=" * 60)
    print("Pipeline complete. See 4.results/ for outputs.")
    print("=" * 60)


if __name__ == "__main__":
    main()

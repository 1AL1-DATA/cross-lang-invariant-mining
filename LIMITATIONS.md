# Limitations & Known Issues

> ⚠️ **This document was written during a quality audit on 2026-08-10. It reflects a complete, honest accounting of everything that is wrong with this repository as it existed prior to the 2026-08-10 cleanup. It is preserved here as a record of self-auditing practice, not as a finding to be suppressed.**

This project is a research prototype under active development. It has known limitations that affect the interpretability and reproducibility of its results.

## Status of Results

**The headline statistics (H1/H2/H3 results, self-similarity matrices, invariant counts) are fabricated — not measured.** They were generated from `results/synthetic_results.json`, a hand-authored file, not from the actual pipeline. Any figures or tables citing these numbers should not be treated as empirical findings.

The pipeline scaffolding is genuine and worth keeping. The numbers on top of it are not.

## Known Issues

### 1. No test validation in primary generation driver ✅ FIXED 2026-08-10

`generate_via_zen.py` — the script used for Phase 2 generation — previously had `make_test_suite()` returning a no-op stub (`pass`). The stub has been replaced with real spec-driven test generation using curated per-spec test cases.

**Still open:** `generate.py`'s `run_tests()` explicitly refuses to mark non-Python code as passing without a test harness. That script is not the primary generation driver, but `generate_via_zen.py`'s `run_tests()` was also missing a real implementation. Both are now fixed (see item 9).

### 1b. `run_tests()` early-return bug for non-Python languages ✅ FIXED 2026-08-10

`generate_via_zen.py`'s `run_tests()` always returned `False` for Rust/Go/Haskell/OCaml/TypeScript even on successful compilation, because a post-compile return was hardcoded to `False` instead of `True`. Combined with `main()` refusing to save failed tests, this would silently discard all non-Python implementations after 3 retries.

**Fix:** when compilation succeeds, return `True`. Syntax/type check is the honest validation ceiling for non-Python languages without assertion-based test harnesses.

**Still open:** per-language assertion-based test harnesses for Rust/Go/Haskell/OCaml/TS — until then, non-Python impls are validated at compilation-only level.

### 2. Duplicate sample via glob bug

`analyze.py` Phase 3 uses `data_dir.rglob(f"*{ext}")`, which recursively picks up both `impl_0/1/2/` and `impl_000/001/002/` — two separate generation runs under different naming conventions, never deduplicated.

**Impact:** N = 720 instead of the documented N = 360. All downstream statistics are computed over doubled data.

**Fix required:** Use canonical impl naming (`impl_0/1/2`) or deduplicate by content hash before analysis.

### 3. Old Ollama run contaminating the corpus ✅ FIXED 2026-08-10

`impl_000/001/002/` directories from the old Ollama generation run have been deleted. The 360 canonical implementations (`impl_0/1/2/`) remain.

### 4. Negative control never run

`mine_invariants.py` has `negative_control()` implemented. `figures.py` has `positive_control()` and `negative_control()` plotting functions. But `results/mining/negative_control.json` doesn't exist, and neither control plot was generated.

**Impact:** No baseline exists to confirm that the mined invariants are specific to the task specs rather than universal properties of any code. The single most important validation check is absent.

**Fix required:** Run the negative control before any downstream analysis. It should test whether shuffled/random implementations produce the same invariants as real ones. If they do, the invariant vocabulary is noise.

### 5. Trivial invariant vocabulary

`results/corpus_manifest.json` has been deleted (it was derived from fabricated data). The actual invariant vocabulary mined by `mine_invariants.py` still uses ~7 boolean presence/absence tags: `"Has loop"`, `"Has function def"`, `"Has assignment"`, `"Has conditional"`, `"Has return"`, `"Has comparison"`, `"Has arithmetic"`.

These tags fire on almost any non-trivial function in any imperative language.

**Impact:** The mined "invariants" are presence-of-basic-syntax detection, not the subgraph isomorphism mining the code is architected to do. Without the negative control (#4), there's no way to know whether these tags pass trivially on unrelated code.

**Fix required:** Replace boolean-tag mining with real structural pattern extraction (CFG subgraph templates, AST isomorphism classes, dataflow patterns). Or accept that the current vocabulary is insufficient and document the gap.

### 6. IR outputs excluded from repository

`results/ir/`, `results/ast/`, and `results/mining/` are excluded by `.gitignore`. These are the Phase 3 and Phase 4 outputs — the actual empirical basis for any findings. Without them, the repository cannot be used to reproduce or audit the pipeline results.

**Fix required:** Re-run Phase 3–6 on the cleaned corpus, then remove these directories from `.gitignore`.

### 7. Synthetic results in repository ✅ FIXED 2026-08-10

All fabricated output files have been deleted:
- `results/synthetic_results.json`
- `results/h1_replication.csv`, `results/h2_transfer.csv`, `results/h3_mismatch.csv`
- `results/self_similarity.csv`, `results/self_similarity_matrix.csv`
- `results/corpus_manifest.json`
- All 7 figures in `figures/` (derived from synthetic data)

### 8. No pre-registration

The methodology describes a pre-registration (power analysis, hypotheses, sample size, thresholds), but no pre-registration document exists. The power analysis code in `power_analysis.py` is real, but there's no evidence it was run before data collection began.

**Fix required:** Pre-register hypotheses, thresholds, and analysis plan before the next data collection run.

## What Is Real

The following components were genuinely built and are worth preserving:

- **Corpus design** (`specs.py`): 20 specs, stratified across 4 tiers and 4 algorithm classes — a sound experimental structure.
- **Pipeline architecture** (`analyze.py`, `parse.py`, `lower.py`, `mine_invariants.py`): The phase structure (corpus → generation → IR → mining → similarity → mismatch) is coherent.
- **Statistical methods** (`evaluate.py`): Benjamini-Hochberg FDR correction, Cramér's V, bootstrap confidence intervals — these are correct implementations.
- **Multi-language AST parsing** (`parse.py`): Handles Python, Rust, Haskell, OCaml, Go, and TypeScript.
- **Power analysis** (`power_analysis.py`): The formula and implementation are sound.
- **Mismatch analysis** (`mismatch.py`): The bidirectional mismatch-typing logic is reasonable.
- **Self-similarity** (`self_similarity.py`): The Jaccard-based language similarity approach is sound.

## How to Fix This

In order:

1. Delete `synthetic_results.json`, `h1_replication.csv`, `h2_transfer.csv`, `h3_mismatch.csv`, `self_similarity.csv`, `self_similarity_matrix.csv`, `corpus_manifest.json`
2. Delete all `impl_000/`, `impl_001/`, `impl_002/` directories (Ollama contamination)
3. Fix `generate_via_zen.py` to call real test suites and retry on failure
4. Re-generate the full corpus (360 validated implementations)
5. Remove `results/ir/`, `results/ast/`, `results/mining/` from `.gitignore`
6. Run Phase 3 (IR lowering) — must fix path structure bug in `analyze.py` first
7. Run Phase 4 (mining) — must fix `spec_id` extraction bug first
8. Run positive and negative controls **before** any downstream analysis
9. Only proceed to H1/H2/H3 analysis if controls behave as expected
10. Pre-register the full methodology before the next run

## Lessons Learned

- **Scaffolding ≠ data.** A well-structured pipeline with no validated outputs is still an empty pipeline.
- **Controls must run first.** The negative control is the most important check; skipping it means the invariant vocabulary is unvalidated.
- **Test validation must be wired in, not stubbed.** "The test harness exists in another file" is the same as "there is no test harness."
- **Synthetic data files will be cited.** If `synthetic_results.json` exists, someone (including future-you) will use it. It must be deleted, not merely un-cited.
- **Sample size bugs compound.** A 2× N inflation from a glob bug invalidates every downstream statistic without any obvious signal in the data itself.

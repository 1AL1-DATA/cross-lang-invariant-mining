# Limitations & Known Issues

> ⚠️ **This document was written during a quality audit on 2026-08-10. It reflects a complete, honest accounting of everything that is wrong with this repository as it existed prior to the 2026-08-10 cleanup. It is preserved here as a record of self-auditing practice, not as a finding to be suppressed.**

This project is a research prototype under active development. It has known limitations that affect the interpretability and reproducibility of its results.

## Status of Results

**The headline statistics (H1/H2/H3 results, self-similarity matrices, invariant counts) are fabricated — not measured.** They were generated from `results/synthetic_results.json`, a hand-authored file, not from the actual pipeline. Any figures or tables citing these numbers should not be treated as empirical findings.

The pipeline scaffolding is genuine and worth keeping. The numbers on top of it are not.

## Known Issues

### 1. No test validation in primary generation driver

`generate_via_zen.py` — the script used for Phase 2 generation — has `make_test_suite()` returning a no-op stub (`pass`). The actual test validation code lives in `generate.py` (`run_tests()`), which explicitly refuses to mark non-Python code as passing without a validated test harness.

**Impact:** All non-Python implementations in `results/phase2/` were generated and saved without functional verification. The claim that implementations "provably compute the same thing" (the central premise of the design) is unmet.

**Fix required:** Wire real test suites into `generate_via_zen.py` before regenerating the corpus. The `generate.py` `run_tests()` function provides the right interface to replicate.

### 2. Duplicate sample via glob bug

`analyze.py` Phase 3 uses `data_dir.rglob(f"*{ext}")`, which recursively picks up both `impl_0/1/2/` and `impl_000/001/002/` — two separate generation runs under different naming conventions, never deduplicated.

**Impact:** N = 720 instead of the documented N = 360. All downstream statistics are computed over doubled data.

**Fix required:** Use canonical impl naming (`impl_0/1/2`) or deduplicate by content hash before analysis.

### 3. Old Ollama run contaminating the corpus

`impl_000/001/002/` directories contain implementations from an earlier Ollama-based generation run. These use "Solution" LeetCode boilerplate (`func Solution(...)`, `class Solution`), not the spec-derived function names.

**Impact:** ~240 of the 720 implementation files follow LeetCode conventions rather than the spec contract, making their test validation meaningless.

**Fix required:** Delete `impl_000/001/002/` directories. Keep only `impl_0/1/2/` from the Zen-based run.

### 4. Negative control never run

`mine_invariants.py` has `negative_control()` implemented. `figures.py` has `positive_control()` and `negative_control()` plotting functions. But `results/mining/negative_control.json` doesn't exist, and neither control plot was generated.

**Impact:** No baseline exists to confirm that the mined invariants are specific to the task specs rather than universal properties of any code. The single most important validation check is absent.

**Fix required:** Run the negative control before any downstream analysis. It should test whether shuffled/random implementations produce the same invariants as real ones. If they do, the invariant vocabulary is noise.

### 5. Trivial invariant vocabulary

`results/corpus_manifest.json` shows the actual invariant vocabulary is ~7 boolean presence/absence tags: `"Has loop"`, `"Has function def"`, `"Has assignment"`, `"Has conditional"`, `"Has return"`, `"Has comparison"`, `"Has arithmetic"`.

These tags fire on almost any non-trivial function in any imperative language.

**Impact:** The mined "invariants" are presence-of-basic-syntax detection, not the subgraph isomorphism mining the code is architected to do. Without the negative control (#4), there's no way to know whether these tags pass trivially on unrelated code.

**Fix required:** Replace boolean-tag mining with real structural pattern extraction (CFG subgraph templates, AST isomorphism classes, dataflow patterns). Or accept that the current vocabulary is insufficient and document the gap.

### 6. IR outputs excluded from repository

`results/ir/` and `results/mining/` are excluded by `.gitignore`. These are the Phase 3 and Phase 4 outputs — the actual empirical basis for any findings. Without them, the repository cannot be used to reproduce or audit the pipeline results.

**Fix required:** Remove `results/ir/`, `results/ast/`, and `results/mining/` from `.gitignore` and regenerate the IR outputs from the cleaned Phase 2 corpus.

### 7. Synthetic results in repository

`results/synthetic_results.json` is hand-authored. `results/h1_replication.csv`, `h2_transfer.csv`, `h3_mismatch.csv` are written only by `figures.py` (which reads from `synthetic_results.json`) and never by any pipeline script.

**Impact:** These files have no traceable provenance. Any citation of their numbers is citing a fiction.

**Fix required:** Delete these files. Regenerate from real pipeline execution.

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

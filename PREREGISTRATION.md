# Preregistration Document

**Project:** Cross-Language Invariant Mining  
**Date:** 2026-08-10  
**Version:** 1.0  
**Status:** Registered prior to analysis

---

## Study Overview

This study investigates whether programming language implementations share structural invariants — common control-flow subgraph patterns — when solving the same algorithmic specification, and whether these invariants transfer across structurally distant programming languages.

---

## Hypotheses

### H1: Structural Invariant Replication

**Claim:** Structural invariants (CFG subgraph isomorphism classes at L2/L3/L4 granularity) identified in implementations of a given specification replicate across independent implementations of the same specification.

- **Population:** Independent implementations of each specification in {Python, Rust, Go, Haskell, OCaml, TypeScript}
- **Measure:** Jaccard index of CFG subgraph sets between the first and second implementation of each specification pair
- **Threshold:** Jaccard ≥ 0.30 (30% subgraph overlap)
- **Test:** One-sample t-test against H₀: μ_Jaccard = 0.30
- **Power:** Requires ≥ 2 implementations per specification per language (power analysis: N=3 achieves ≥ 0.80 power at α=0.05 for d=0.8)
- **Direction:** Replication if median Jaccard ≥ 0.30

### H2: Cross-Language Transfer

**Claim:** Invariants that are locally consistent within a language family (Python/Rust/Go: curly-brace; Haskell/OCaml: functional) transfer to structurally distant languages.

- **Structurally distant language pairs:**
  - Functional ↔ Imperative: {Haskell, OCaml} ↔ {Python, Rust, Go, TypeScript}
  - Type-inferred ↔ Explicitly typed: Haskell ↔ {Python, Go}
- **Measure:** Fraction of within-language invariants that also appear in structurally distant languages (transfer fraction)
- **Threshold:** Transfer fraction ≥ 0.35 (35% of within-language invariants transfer distally)
- **Test:** One-sample t-test against H₀: transfer_fraction = 0.35
- **Direction:** Transfer confirmed if median transfer fraction ≥ 0.35

### H3: Mismatch Structure

**Claim:** Implementation mismatches (generation failures, structural drift) are non-random and exhibit systematic patterns by specification complexity.

- **Complexity proxy:** AC-code tier (ac1=array, ac2=search, ac3=sort, ac4=complex)
- **Measure:** Cramér's V between specification complexity tier and mismatch category (Omission, Drift, Misclassification)
- **Threshold:** Cramér's V ≥ 0.25 (medium effect)
- **Test:** Chi-square test of independence on 4×3 contingency table
- **Direction:** Structure confirmed if Cramér's V ≥ 0.25 at α=0.05

---

## Fixed Design Parameters

| Parameter | Value |
|-----------|-------|
| Specifications | 20 specs across 4 algorithmic complexity tiers (see `src/specs.py`) |
| Languages | Python, Rust, Go, Haskell, OCaml, TypeScript |
| Implementations per cell | 3 (spec × language) |
| Total corpus | 20 × 6 × 3 = 360 implementations |
| Minimum languages per invariant | 3 |
| IR granularity levels | L2 (basic block), L3 (loop/branch), L4 (function) |
| Control-flow hash | CFG-topology SHA-256 (16 hex chars), excludes sequential-only subgraphs |
| Structurally distant pairs | (Haskell ∪ OCaml) × (Python ∪ Rust ∪ Go ∪ TypeScript) |
| Significance level (α) | 0.05 |
| Multiple testing correction | Benjamini-Hochberg FDR at q=0.05 |
| Bootstrap CI | 10,000 resamples, 95% CI |
| Random seed | 42 |

---

## Thresholds

| Threshold | Use |
|-----------|-----|
| t60 (60%) | Invariant reported if appears in ≥ 60% of implementations across ≥ 3 languages |
| t70 (70%) | Invariant reported if appears in ≥ 70% of implementations across ≥ 3 languages |
| t80 (80%) | Invariant reported if appears in ≥ 80% of implementations across ≥ 3 languages |
| Jaccard ≥ 0.30 | H1 replication criterion |
| Transfer fraction ≥ 0.35 | H2 cross-language transfer criterion |
| Cramér's V ≥ 0.25 | H3 mismatch structure criterion |

---

## Exclusion Criteria

- Implementations that fail syntax/type-check compilation are excluded from IR lowering (Phase 3)
- Sequential-only CFG subgraphs (no BRANCH/LOOP/MATCH nodes) are excluded from mining as universal artifacts
- Specs with fewer than 2 languages having ≥ 1 CFG-carrying implementation are excluded from cross-language analysis

---

## Validation Gates

The following must pass before hypothesis testing:

1. **Positive control:** Binary search spec (t1-ac2-001) produces ≥ 1 structural invariant at t60 across ≥ 3 languages
2. **Negative control:** Shuffled (spec-language mismatched) corpus produces 0 invariants at t70

If either gate fails, the pipeline is repaired before proceeding.

---

## Output Files

Produced by Phase 4–6, analyzed in Phase 7:

| File | Contents |
|------|----------|
| `results/mining/cross_language_t{60,70,80}.json` | Cross-language invariant sets |
| `results/mining/within_language_t{60,70,80}.json` | Within-language invariant sets |
| `results/mining/h1_replication.csv` | Jaccard overlaps per spec pair |
| `results/mining/h2_transfer.csv` | Transfer fractions per spec |
| `results/mining/h3_mismatch.csv` | Mismatch records per spec/language |
| `results/mining/study_results.json` | Aggregated H1/H2/H3 with BH-corrected p-values |

---

## Analysis Plan

1. Run Phase 3 on full 360-implementation corpus → `results/ir/`
2. Validate gates (positive + negative control)
3. Run Phase 4: mine invariants at t60, t70, t80 across L2+L3+L4
4. Phase 5: self-similarity matrix across languages
5. Phase 6: mismatch analysis
6. Compute Jaccard overlaps (H1), transfer fractions (H2), Cramér's V (H3)
7. Apply Benjamini-Hochberg correction across all hypothesis tests
8. Report: point estimates, 95% CIs, effect sizes, adjusted p-values

---

## Deviations from Preregistration

Any deviation from this document will be reported in the results section with justification. Post-hoc analyses will be labeled as exploratory.

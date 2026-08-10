# What We Found: A Simple Explanation

## The Goal
Imagine you asked 6 different teams of storytellers to each tell 20 different
stories in their own unique way, with 3 variations of every story per team.

In our case:
- The "storytellers" were different programming languages (Python, Rust, Haskell, OCaml, Go, and TypeScript)
- The "stories" were 20 different programming problems we wanted solved
- The "3 different times" meant creating 3 unique solutions for each problem in each language

So we expected: 6 languages × 20 stories × 3 versions = 360 total solutions.

## Honest status of the project

**This study is preregistered but not yet complete.** The headline results
(CSVs, figures, and the summary in `1.narrative/SUMMARY.md`) were produced from
**synthetic placeholder data**, not from real LLM-generated code. They are a
pipeline test, not a result. The real implementation corpus
(`3.data/corpus/specs_v1/`) was generated with a local model backend, but:

1. **Not all 360 solutions were present and valid.** When we checked the real
   corpus we found 0-byte (empty) files saved as if they had passed quality
   control. Empty implementations must be discarded and re-generated.
2. **Per-language test suites do not exist yet.** `generate.py` previously
   counted every non-Python implementation as passing a syntax check it never
   ran. That bug is fixed — code that cannot be validated is now rejected — but
   the corpus itself was produced under the old, lenient rules.
3. **The negative control failed.** A test designed to fail (mining invariants
   from shuffled, unrelated specs) produced support values well above the 0.10
   limit. That means the mining method was finding artifacts. The last mining
   run also used a support formula that could exceed 1.0 (a fraction of
   implementations can never be above 100%) — that bug is fixed, and the
   control must be re-run.
4. **An extra spec leaked into the corpus.** `t2-dp1-001` (only 4 languages)
   is not one of the 20 preregistered specs, so any results involving it are
   off-protocol until the preregistration is amended or the corpus is cleaned.

## What this means for our results

Nothing in this study should be reported as a finding yet. The pipeline works,
the scaffold is in place, and the bugs that would have produced misleading
numbers have been fixed. The next honest step is: write the per-language test
suites, regenerate the corpus with real validation, re-run Phases 3–7, and
re-run the negative control.

## Bottom Line

The infrastructure now exists and the previous sources of error are documented
and fixed (`fixes.md` at the repo root). We do **not** yet have 360 verified,
working, non-empty solutions in 6 languages — that is what the next, properly
validated run must deliver before any pattern can be reported.

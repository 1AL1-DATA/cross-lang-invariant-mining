# Cross-Language Invariant Mining

Discovering structural invariants that hold across programming languages.

## Overview

Given a set of programming problems (specs), this project generates multiple implementations in different programming languages, lowers them to a common IR (intermediate representation), and mines for structural patterns — **cross-language invariants** — that are shared across implementations regardless of the target language.

## Pipeline Phases

| Phase | Description |
|-------|-------------|
| **1** | Corpus / benchmark specs |
| **2** | Generate N implementations per spec per language via LLM |
| **3** | Parse implementations → AST → IR |
| **4** | Mine for cross-language invariants |
| **5** | Self-similarity matrix across languages |
| **6** | Mismatch analysis |

## Requirements

- Python 3.11+
- See `requirements.txt` for dependencies

## Setup

```bash
pip install -r requirements.txt
```

API credentials are loaded from `~/.local/share/opencode/auth.json` at runtime. No keys are hardcoded.

## Running the Pipeline

```bash
cd src
python generate.py          # Phase 2: generate implementations
python analyze.py --phase 3  # Phase 3–6: parse, mine, analyze
```

Or run phases individually:

```bash
python -c "
from pathlib import Path
from analyze import phase_3_parse_and_lower, phase_4_mine, phase_5_self_similarity, phase_6_mismatch

ROOT = Path('..')
IMPL  = ROOT / 'results' / 'phase2'
OUT   = ROOT / 'results'
IR    = OUT  / 'ir'

phase_3_parse_and_lower(IMPL, OUT)   # 360 impls → IR
phase_4_mine(IR, OUT)               # find invariants
phase_5_self_similarity(IR, OUT)     # language similarity
phase_6_mismatch(IMPL, OUT)         # mismatch analysis
"
```

## Project Structure

```
2.code/
├── src/                  # Pipeline scripts
│   ├── generate.py       # Phase 2 generation (Anthropic/OpenAI SDK)
│   ├── generate_via_zen.py  # Phase 2 via OpenCode Zen gateway
│   ├── analyze.py        # Phases 3–6 orchestration
│   ├── parse.py          # AST parsing (Python, Rust, Haskell, OCaml, Go, TypeScript)
│   ├── lower.py          # AST → IR lowering
│   ├── mine_invariants.py # Phase 4: invariant mining
│   ├── self_similarity.py # Phase 5: language similarity
│   ├── mismatch.py       # Phase 6: mismatch analysis
│   ├── specs.py          # Benchmark specs
│   └── evaluate.py       # Statistical evaluation
├── results/
│   ├── phase2/           # Phase 2 outputs (360 generated implementations)
│   ├── ir/               # Phase 3 outputs (IR files)
│   ├── mining/           # Phase 4 outputs (invariants)
│   ├── self_similarity_matrix.csv
│   └── *.csv             # Analysis results
├── notebooks/            # Jupyter analysis notebooks
├── figures/              # Generated plots
└── non_technical.md      # Plain-English explanation
```

## Languages

Python, Rust, Haskell, OCaml, Go, TypeScript

## Reproducing the Experiment

With API credentials configured, run:

```bash
cd src
# Generate all 360 implementations
for spec in t1-ac1-001 t1-ac2-001 ... t4-ac4-003; do
  for lang in python rust haskell ocaml go typescript; do
    for impl in 0 1 2; do
      python generate_via_zen.py $spec $lang $impl
    done
  done
done

# Run the rest of the pipeline
python analyze.py --phase 3
```

## License

MIT

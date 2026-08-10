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

## LLM Provider Configuration

Generation is **provider-agnostic** — swap the model backend without touching pipeline code.

Copy and edit the config:

```bash
cp config/generation.yaml.example config/generation.yaml
# Edit generation.yaml with your provider and credentials
```

### Available providers

| Provider | Credentials |
|----------|-------------|
| `openai` | `OPENAI_API_KEY` env var |
| `anthropic` | `ANTHROPIC_API_KEY` env var |
| `ollama` | None — runs locally at `http://localhost:11434` |
| `opencode` | `OPENCODE_API_KEY` or `~/.local/share/opencode/auth.json` |
| `openrouter` | `OPENROUTER_API_KEY` env var |

Example — use Claude via OpenRouter:

```yaml
provider: openrouter
model: anthropic/claude-sonnet-4-7
credentials:
  api_key: ${OPENROUTER_API_KEY}
```

Example — use a local Ollama model:

```yaml
provider: ollama
model: llama3.3
credentials:
  base_url: http://localhost:11434
```

## Running the Pipeline

```bash
cd src

# Phase 2: generate implementations (provider from config/generation.yaml)
python generate_via_zen.py t1-ac1-001 python 0

# Or generate all 360 implementations
for spec in t1-ac1-001 t1-ac2-001 ... t4-ac4-003; do
  for lang in python rust haskell ocaml go typescript; do
    for impl in 0 1 2; do
      python generate_via_zen.py $spec $lang $impl
    done
  done
done

# Phase 3–6: parse, mine, analyze
python analyze.py --phase 3
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
phase_6_mismatch(IMPL, OUT)          # mismatch analysis
"
```

## Project Structure

```
2.code/
├── src/                  # Pipeline scripts
│   ├── generate_via_zen.py  # Phase 2 generation (provider-agnostic)
│   ├── providers.py        # LLM provider interface (openai, anthropic, ollama, opencode, openrouter)
│   ├── analyze.py        # Phases 3–6 orchestration
│   ├── parse.py          # AST parsing (Python, Rust, Haskell, OCaml, Go, TypeScript)
│   ├── lower.py          # AST → IR lowering
│   ├── mine_invariants.py # Phase 4: invariant mining
│   ├── self_similarity.py # Phase 5: language similarity
│   ├── mismatch.py       # Phase 6: mismatch analysis
│   ├── specs.py          # Benchmark specs
│   └── evaluate.py       # Statistical evaluation
├── config/
│   ├── generation.yaml       # Active config (NOT committed — contains credentials)
│   └── generation.yaml.example  # Template — copy and fill in
├── prompts/             # Per-language prompt templates
│   ├── python.md
│   ├── rust.md
│   ├── haskell.md
│   ├── ocaml.md
│   ├── go.md
│   └── typescript.md
├── results/
│   ├── phase2/           # Phase 2 outputs (360 generated implementations)
│   ├── ir/               # Phase 3 outputs (IR files)
│   └── mining/            # Phase 4 outputs (invariants)
├── notebooks/            # Jupyter analysis notebooks
├── figures/              # Generated plots
├── LIMITATIONS.md        # Honest accounting of what is and isn't working
└── non_technical.md      # Plain-English explanation
```

## Languages

Python, Rust, Haskell, OCaml, Go, TypeScript

## Reproducing the Experiment

With API credentials configured in `config/generation.yaml`, run:

```bash
cd src
for spec in t1-ac1-001 t1-ac2-001 ... t4-ac4-003; do
  for lang in python rust haskell ocaml go typescript; do
    for impl in 0 1 2; do
      python generate_via_zen.py $spec $lang $impl
    done
  done
done
python analyze.py --phase 3
```

## License

MIT

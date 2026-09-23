# Reliable Research

**Reliable Research** is an academic research-agent prototype built on top of [OpenAI Codex](https://github.com/openai/codex).

The project studies how to make automatically generated research reports more reliable, with a current focus on **claim–citation alignment** and **claim-level verification**.

## Research Direction

Our current pilot domain is:

> **AI-Assisted Software Engineering / AI Coding Assistants**

The benchmark is designed to study questions such as:

- whether AI coding assistants reduce software-development task completion time;
- whether AI coding assistants improve code quality;
- how they affect security, maintainability, developer experience, debugging, testing, and technical debt.

The core research question for Reliable Research is not whether AI coding assistants are simply “good” or “bad.” Instead, we study whether factual claims produced by a research agent are actually supported by the citations and evidence attached to them, and how the research pipeline can be modified to improve that reliability.

## Project Pipeline

```text
Research Question
      ↓
Baseline Research Generation
      ↓
Research Report
      ↓
Atomic Claim Extraction
      ↓
Structured Claim JSON
      ↓
Evidence / Citation Resolution
      ↓
Claim Verification
      ↓
Revision / Final Report
```

The current development work focuses on the early stages of this pipeline so that later verification experiments have reproducible inputs.

## Current Status

### Benchmark v0.1

The benchmark is stored in:

```text
data/questions/questions_v0.1.json
```

It currently contains eight questions in the domain of AI-assisted software engineering:

- `Q001`–`Q006`: development questions
- `Q007`–`Q008`: held-out questions reserved for later evaluation

The current Pre2 pilot uses `Q001` and `Q002`. The held-out questions should not be used for development-time tuning.

### Python Runner

`research/runner/codex_runner.py` provides a Python wrapper around the Reliable Research launcher.

Each run records artifacts such as:

```text
data/runs/<run_id>/
├── prompt.txt
├── final_message.txt
├── events.jsonl
├── metadata.json
└── stderr.txt
```

The metadata includes the run ID, question ID, Git branch/commit information, timing, return code, event counts, warnings/errors, and usage information.

### Atomic Claim Extraction

The current Atomic Claim Extractor is implemented in:

```text
research/claims/
├── __init__.py
├── extractor.py
└── schemas.py
```

It converts research-report text into structured factual claims such as:

```json
{
  "claim_id": "C001",
  "claim": "Developers using an AI coding assistant completed tasks 30% faster.",
  "citations": ["[1]"],
  "source_sentence": "Developers using an AI coding assistant completed tasks 30% faster, and generated code contained more security weaknesses [1]."
}
```

The extractor currently includes logic for:

- filtering recommendation-style and heading-like non-factual text;
- splitting selected compound factual claims;
- preserving shared subjects when splitting compound claims;
- retaining citation associations;
- avoiding selected noun-coordination over-splitting cases;
- producing stable claim IDs and machine-readable JSON.

## Repository Structure

Relevant research files currently include:

```text
data/
├── questions/
│   └── questions_v0.1.json
└── runs/

research/
├── claims/
│   ├── __init__.py
│   ├── extractor.py
│   └── schemas.py
└── runner/
    ├── batch_runner.py
    └── codex_runner.py

tests/
├── fixtures/
│   └── sample_research_report.md
└── test_claim_extractor.py
```

This repository also contains the upstream Codex codebase from which Reliable Research is derived.

## Running the Current Research Components

### Inspect benchmark questions

Run one benchmark question:

```bash
python3 -m research.runner.batch_runner --question-id Q001
```

Run the development split:

```bash
python3 -m research.runner.batch_runner --split dev
```

At the current stage, `batch_runner.py` selects and prints benchmark questions. Baseline report generation is being integrated as a separate development step.

### Run the Atomic Claim Extractor

Given a Markdown or text research report:

```bash
PYTHONPATH=. python3 -m research.claims.extractor \
  path/to/report.md \
  --report-id Q001 \
  --output path/to/claims.json
```

### Run claim-extractor tests

```bash
PYTHONPATH=. python3 -m unittest tests.test_claim_extractor -v
```

## Evaluation Plan

The current evaluation workflow is:

```text
Q001 / Q002 baseline reports
        ↓
Atomic Claim Extraction
        ↓
Structured claims
        ↓
Human pilot on approximately 20–30 claims
        ↓
Error analysis
        ↓
Evidence table
```

The human pilot records issues such as:

- missed factual claims;
- false positives;
- incorrect splitting or merging;
- over-splitting;
- citation-association errors.

Evaluation numbers should come from real runs and human review rather than being pre-filled or estimated.

## Development Principles

Reliable Research uses a few simple rules to keep the experiment reproducible:

- use fixed benchmark questions;
- keep development and held-out questions separate;
- preserve run artifacts and Git metadata;
- make research-pipeline changes through focused feature branches and pull requests;
- add regression tests when a concrete failure is found;
- avoid manually correcting baseline outputs before evaluation.

See [Contributing](docs/contributing.md) for the development workflow.

## Upstream Project

Reliable Research is derived from:

**OpenAI Codex**  
https://github.com/openai/codex

The upstream Codex code, notices, and applicable attribution are retained in this repository.

## License

This repository retains the upstream [Apache License 2.0](LICENSE).

See [NOTICE](NOTICE) for attribution information.

## Project Status

Reliable Research is an academic research prototype. It is under active development and is not intended for production deployment.

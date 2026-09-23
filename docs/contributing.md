# Contributing to Reliable Research

Reliable Research is currently developed as an academic research project built on top of OpenAI Codex.

This document describes the workflow for project-team contributions and research changes in this fork.

## Development Workflow

Use feature branches and pull requests for project changes.

Start from the latest `main`:

```bash
git fetch origin
git switch main
git pull --ff-only origin main
```

Create a focused feature branch:

```bash
git switch -c feat/<short-description>
```

Examples:

```text
feat/baseline-generation
feat/atomic-claim-extractor
feat/claim-extractor-improvements
```

After implementation and testing:

```bash
git status
git diff
git add <files>
git commit -m "feat: describe the change"
git push -u origin HEAD
```

Then open a pull request into `main`.

## Pull Request Scope

Keep each pull request focused on one research or engineering change.

Good examples:

```text
Add Atomic Claim Extraction
Improve Atomic Claim Extraction heuristics
Add Baseline Research Generation
```

Avoid mixing unrelated work such as baseline generation, claim verification, UI changes, and documentation cleanup into a single pull request.

A pull request should explain:

- what changed;
- why the change is needed;
- which files or pipeline stage it affects;
- how it was tested;
- any known limitations.

## Testing

Run the tests relevant to your change before opening a pull request.

For the current Atomic Claim Extractor:

```bash
PYTHONPATH=. python3 -m unittest tests.test_claim_extractor -v
```

You can also verify the Python files compile:

```bash
python3 -m py_compile research/claims/schemas.py
python3 -m py_compile research/claims/extractor.py
```

For runner changes, test the specific benchmark question or runner path that your pull request modifies.

Example:

```bash
python3 -m research.runner.batch_runner --question-id Q001
```

Do not claim a run succeeded unless the expected output was actually produced and inspected.

## Research Benchmark Rules

The benchmark is stored in:

```text
data/questions/questions_v0.1.json
```

Current split policy:

```text
Q001–Q006  dev
Q007–Q008  held_out
```

For the current Pre2 pilot, use:

```text
Q001
Q002
```

Do not use `Q007` or `Q008` for prompt tuning, heuristic tuning, or development-time debugging. They are reserved for later held-out evaluation.

## Research Integrity

Do not fabricate or pre-fill evaluation results.

Metrics such as:

```text
Human factual claims
Correctly extracted claims
Missed claims
Incorrect split / merged claims
Citation association accuracy
```

must come from actual generated reports and human review.

When a real failure is found:

```text
Observed failure
      ↓
Add regression test
      ↓
Modify implementation
      ↓
Re-run evaluation
      ↓
Record the result
```

This is preferred over adding heuristics without a concrete observed failure.

## Baseline Outputs

Baseline reports should represent the behavior of the current unverified research pipeline.

Do not manually repair citations, rewrite factual claims, or insert evidence before evaluation. The purpose of the baseline is to preserve the system's original output so that later modifications can be compared against it.

Generated outputs should use stable, documented paths so downstream stages can consume them reproducibly.

## Run Artifacts

The Python runner stores run artifacts under:

```text
data/runs/<run_id>/
```

Do not silently modify run artifacts after a completed experiment.

If a run must be repeated, create a new run and preserve the relevant metadata.

## Code Style

For project-specific Python code:

- keep modules small and focused;
- prefer the Python standard library when practical;
- use type hints;
- add docstrings where behavior is not obvious;
- keep command-line workflows reproducible;
- avoid unnecessary dependencies for simple processing;
- add tests for important edge cases and regressions.

## Commit Messages

Use short, descriptive commit messages.

Examples:

```text
feat: add atomic claim extraction
feat: add baseline research generation
fix: preserve shared subject in compound claims
test: add noun coordination regression case
docs: update Reliable Research documentation
```

## Upstream Codex Code

Reliable Research is a fork of OpenAI Codex.

When working on project-specific research functionality, prefer adding isolated research modules rather than making unnecessary changes to upstream Codex internals.

If an issue belongs to the upstream Codex project rather than Reliable Research modifications, consult the upstream repository and documentation.

## Security

For security issues, follow the repository's [Security Policy](../SECURITY.md).

Do not include credentials, API keys, private data, or sensitive logs in commits, pull requests, or benchmark artifacts.

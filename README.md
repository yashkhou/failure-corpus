# failure-corpus

Turn noisy test and agent logs into a deduplicated failure corpus that can feed regression and eval suites.

## What it does

- extracts pytest, Jest and generic error-shaped failures
- normalizes volatile paths, line numbers, addresses and timestamps
- deduplicates repeated failures while retaining occurrence counts
- exports stable JSONL records for downstream eval tooling

## Quick start

```bash
PYTHONPATH=src python -m failure_corpus examples/mixed.log
```

No model API, network service, or third-party package is required.

## Architecture

A parser identifies failure-shaped records, a normalizer removes volatile details, and SHA-256 fingerprints collapse repeated failures into stable corpus entries.

See [`docs/architecture.md`](docs/architecture.md) for the data model and trade-offs.

## V1 boundary

V1 uses bounded line-oriented heuristics rather than framework ASTs; exotic reporters may need a small adapter.

## Development

```bash
python -m unittest discover -s tests -v
```

MIT licensed.


## v0.1.1

**Cross-framework failure clustering.** Parsing now recognizes Go and Rust failures in addition to existing formats, while shape signatures cluster variable instances without losing exact fingerprints.

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

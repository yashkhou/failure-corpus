# Architecture

A parser identifies failure-shaped records, a normalizer removes volatile details, and SHA-256 fingerprints collapse repeated failures into stable corpus entries.

## Design constraints

- deterministic offline behavior
- explicit machine-readable inputs and outputs
- small standard-library surface area
- failures are surfaced rather than hidden

## V1 limitation

V1 uses bounded line-oriented heuristics rather than framework ASTs; exotic reporters may need a small adapter.

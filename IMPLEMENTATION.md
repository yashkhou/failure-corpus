# Implementation note

Working V1 scope: Turn noisy test and agent logs into a deduplicated failure corpus that can feed regression and eval suites.

Verified with `python -m unittest discover -s tests -v`.

Known boundary: V1 uses bounded line-oriented heuristics rather than framework ASTs; exotic reporters may need a small adapter.

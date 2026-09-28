import unittest

from failure_corpus.core import cluster, parse


class CorpusUpgradeTests(unittest.TestCase):
    def test_parses_go_and_rust_failures(self):
        records = parse("--- FAIL: TestRetry (0.01s)\n    retry_test.go:44: got 3 want 2\nthread 'worker' panicked at src/lib.rs:9:2")
        self.assertEqual({r.framework for r in records}, {"go", "rust"})

    def test_clusters_variable_instances_of_same_failure_shape(self):
        records = parse("FAILED tests/test_api.py::test_fetch - AssertionError: expected 12 got 13\nFAILED tests/test_api.py::test_fetch_other - AssertionError: expected 98 got 101")
        groups = cluster(records, threshold=0.5)
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]["occurrences"], 2)

    def test_unrelated_failures_stay_separate(self):
        records = parse("FAILED a.py::test_a - AssertionError: token mismatch\nFAILED b.py::test_b - RuntimeError: database unavailable")
        self.assertEqual(len(cluster(records, threshold=0.7)), 2)


if __name__ == "__main__":
    unittest.main()

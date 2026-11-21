import json
import os
import pathlib
import tempfile
import unittest
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from src import budget as B, cost, records  # noqa: E402


class BudgetTests(unittest.TestCase):
    def test_halts_at_80_percent(self):
        with tempfile.TemporaryDirectory() as d:
            b = B.Budget(pathlib.Path(d) / "budget.json", cap=1000)
            b.charge(790)
            with self.assertRaises(B.BudgetExceeded):
                b.check(20)
            b.check(5)

    def test_per_run_limit(self):
        with tempfile.TemporaryDirectory() as d:
            b = B.Budget(pathlib.Path(d) / "budget.json")
            with self.assertRaises(B.BudgetExceeded):
                b.check(B.PER_RUN_LIMIT + 1)

    def test_persists_spend(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "budget.json"
            B.Budget(p).charge(123)
            self.assertEqual(B.Budget(p).spent, 123)


class CostTests(unittest.TestCase):
    PRICES = {"input": 1.0, "cached_input": 0.1, "output": 4.0}

    def test_cached_reads_are_cheaper(self):
        uncached = cost.cached_aware_cost({"prompt_tokens": 1000, "completion_tokens": 0}, self.PRICES)
        cached = cost.cached_aware_cost({"prompt_tokens": 1000, "cached_tokens": 900, "completion_tokens": 0}, self.PRICES)
        self.assertLess(cached, uncached)
        self.assertAlmostEqual(cached, (100 * 1.0 + 900 * 0.1) / 1e6)

    def test_missing_price_raises(self):
        with self.assertRaises(KeyError):
            cost.cached_aware_cost({"prompt_tokens": 1}, {"input": 1.0})

    def test_prefix_cache_hits_append_history(self):
        turn1 = [1, 2, 3]
        turn2 = [1, 2, 3, 4, 5]
        self.assertEqual(cost.simulate_prefix_cache([turn1, turn2]), [0, 3])

    def test_prefix_cache_miss_when_prefix_rewritten(self):
        self.assertEqual(cost.simulate_prefix_cache([[1, 2, 3], [9, 2, 3, 4]]), [0, 0])


class RecordTests(unittest.TestCase):
    def test_rejects_incomplete_record(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                records.append(pathlib.Path(d) / "r.jsonl", {"run_id": "x"})

    def test_appends_complete_record(self):
        rec = {k: None for k in records.REQUIRED}
        rec["run_id"] = "t1"
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "r.jsonl"
            records.append(p, rec)
            records.append(p, rec)
            lines = p.read_text().splitlines()
            self.assertEqual(len(lines), 2)
            self.assertEqual(json.loads(lines[0])["run_id"], "t1")


if __name__ == "__main__":
    unittest.main()

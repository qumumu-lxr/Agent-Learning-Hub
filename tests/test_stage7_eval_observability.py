import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGE7 = ROOT / "practice" / "stage7_eval_observability"
sys.path.insert(0, str(STAGE7))

from eval_runner import load_cases, run_eval, summarize  # noqa: E402


class EvalObservabilityTest(unittest.TestCase):
    def test_eval_has_twenty_cases(self) -> None:
        cases = load_cases(STAGE7 / "evals" / "stage1_cases.json")
        results = run_eval(cases)
        summary = summarize(results)

        self.assertEqual(summary["total"], 20)
        self.assertGreaterEqual(summary["success_rate"], 0.8)
        self.assertTrue(results[0].trace)


if __name__ == "__main__":
    unittest.main()


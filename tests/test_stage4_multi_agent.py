import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGE4 = ROOT / "practice" / "stage4_multi_agent"
sys.path.insert(0, str(STAGE4))

from multi_agent_pipeline import Supervisor  # noqa: E402


class MultiAgentPipelineTest(unittest.TestCase):
    def test_pipeline_produces_reviewed_report(self) -> None:
        result = Supervisor().run("为什么 agent 需要 eval？")

        self.assertTrue(result.review.passed)
        self.assertIn("结论", result.answer)
        self.assertGreaterEqual(len(result.trace), 5)


if __name__ == "__main__":
    unittest.main()


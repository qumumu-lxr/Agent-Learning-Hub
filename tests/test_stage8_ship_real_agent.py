import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGE8 = ROOT / "practice" / "stage8_ship_real_agent"
sys.path.insert(0, str(STAGE8))

from personal_research_agent import PersonalResearchAgent  # noqa: E402


class PersonalResearchAgentTest(unittest.TestCase):
    def test_agent_answers_with_trace(self) -> None:
        result = PersonalResearchAgent(STAGE8 / "data").run("为什么 agent 项目需要评测？")

        self.assertTrue(result.citations)
        self.assertIn("Evaluation", result.answer)
        self.assertEqual(result.trace[0]["event"], "question_received")


if __name__ == "__main__":
    unittest.main()


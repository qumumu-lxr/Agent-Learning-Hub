import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGE5 = ROOT / "practice" / "stage5_skills_protocols"
sys.path.insert(0, str(STAGE5))

from skill_runner import load_skill, run_skill  # noqa: E402


class SkillRunnerTest(unittest.TestCase):
    def test_skill_smoke_checks_pass(self) -> None:
        skill = load_skill(STAGE5 / "skills" / "research_summary")
        result = run_skill(skill, "agent harness helps reliability")

        self.assertEqual(result.failed_checks, [])
        self.assertIn("research_summary", result.skill_name)


if __name__ == "__main__":
    unittest.main()


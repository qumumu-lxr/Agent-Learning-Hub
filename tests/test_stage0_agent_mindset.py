import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGE0 = ROOT / "practice" / "stage0_agent_mindset"
sys.path.insert(0, str(STAGE0))

from agent_mindset import classify_task  # noqa: E402


class AgentMindsetTest(unittest.TestCase):
    def test_agent_task(self) -> None:
        result = classify_task("搜索资料，根据结果多轮规划一篇调研报告")

        self.assertEqual(result.recommended_pattern, "agent")
        self.assertIn("外部信息质量和来源不确定", result.uncertainty_sources)

    def test_script_task(self) -> None:
        result = classify_task("把 CSV 的 price 字段乘以 1.08")

        self.assertEqual(result.recommended_pattern, "script")


if __name__ == "__main__":
    unittest.main()


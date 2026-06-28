import sys
import unittest
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGE1 = ROOT / "practice" / "stage1_minimal_agent"
sys.path.insert(0, str(STAGE1))

from minimal_agent import build_agent  # noqa: E402


class MinimalAgentTest(unittest.TestCase):
    def test_calculator_agent(self) -> None:
        answer, steps = build_agent().run("计算 23 * 7 + 10")

        self.assertEqual(answer, "171")
        self.assertIsNotNone(steps[0].action)
        self.assertEqual(steps[0].action.name, "calculator")
        self.assertIsNotNone(steps[0].observation)
        self.assertTrue(steps[0].observation.ok)

    def test_read_file_agent(self) -> None:
        answer, steps = build_agent().run("请阅读 notes.txt 并总结")

        self.assertIn("Agent loop", answer)
        self.assertIsNotNone(steps[0].action)
        self.assertEqual(steps[0].action.name, "read_file")

    def test_read_file_blocks_parent_directory(self) -> None:
        answer, steps = build_agent().run("请阅读 ../README.md")

        self.assertIn("Refusing to read outside", answer)
        self.assertIsNotNone(steps[0].action)
        self.assertEqual(steps[0].action.name, "read_file")
        self.assertEqual(steps[0].action.arguments["path"], "../README.md")

    def test_search_agent(self) -> None:
        answer, steps = build_agent().run("查一下 agent loop 是什么")

        self.assertIn("observe -> think -> act -> observe", answer)
        self.assertIsNotNone(steps[0].action)
        self.assertEqual(steps[0].action.name, "search")

    def test_word_count_agent(self) -> None:
        answer, steps = build_agent().run("统计字数：Agent loop 需要 tools, trace 和 stop condition")
        result = json.loads(answer)

        self.assertEqual(result["english_words"], 6)
        self.assertEqual(result["chinese_chars"], 3)
        self.assertIsNotNone(steps[0].action)
        self.assertEqual(steps[0].action.name, "word_count")

    def test_sentence_count_agent(self) -> None:
        answer, steps = build_agent().run("统计句子数：我在学 agent loop。它会调用 tools! Trace 很重要。")
        result = json.loads(answer)

        self.assertEqual(result["sentences"], 3)
        self.assertIsNotNone(steps[0].action)
        self.assertEqual(steps[0].action.name, "sentence_count")

    def test_uppercase_agent(self) -> None:
        answer, steps = build_agent().run("转成大写：hello agent loop")

        self.assertEqual(answer, "HELLO AGENT LOOP")
        self.assertIsNotNone(steps[0].action)
        self.assertEqual(steps[0].action.name, "uppercase")


if __name__ == "__main__":
    unittest.main()

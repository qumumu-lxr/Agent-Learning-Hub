import json
import tempfile
import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
STAGE3 = ROOT / "practice" / "stage3_harness"
sys.path.insert(0, str(STAGE3))

from harness_demo import build_harness  # noqa: E402


class HarnessDemoTest(unittest.TestCase):
    def test_harness_writes_trace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            trace_path = Path(tmp) / "trace.json"
            result = build_harness(trace_path).run("search harness")
            trace = json.loads(trace_path.read_text(encoding="utf-8"))

            self.assertTrue(result.ok)
            self.assertGreaterEqual(len(trace), 3)
            self.assertEqual(trace[0]["event"], "task_received")

    def test_risky_tool_requires_approval(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = build_harness(Path(tmp) / "trace.json").run("read file")

            self.assertFalse(result.ok)
            self.assertIn("requires human approval", result.content)


if __name__ == "__main__":
    unittest.main()


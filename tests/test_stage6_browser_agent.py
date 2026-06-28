import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGE6 = ROOT / "practice" / "stage6_browser_agent"
sys.path.insert(0, str(STAGE6))

from browser_info_agent import LocalPageAgent  # noqa: E402


class BrowserInfoAgentTest(unittest.TestCase):
    def test_extracts_title_and_links(self) -> None:
        result = LocalPageAgent().inspect(STAGE6 / "pages" / "sample.html")

        self.assertEqual(result.title, "Agent Browser Demo")
        self.assertEqual(len(result.links), 2)
        self.assertIn("parse_dom", result.action_log)


if __name__ == "__main__":
    unittest.main()


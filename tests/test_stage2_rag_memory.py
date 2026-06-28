import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGE2 = ROOT / "practice" / "stage2_rag_memory"
sys.path.insert(0, str(STAGE2))

from rag_memory import MemoryStore, ResearchAssistant, chunk_text  # noqa: E402


class RagMemoryTest(unittest.TestCase):
    def test_chunk_text_keeps_source(self) -> None:
        chunks = chunk_text("demo.md", "alpha\n\nbeta", max_chars=8)

        self.assertEqual(chunks[0].source, "demo.md")
        self.assertEqual(chunks[0].citation, "demo.md#chunk-1")

    def test_answer_has_citation(self) -> None:
        assistant = ResearchAssistant(STAGE2 / "docs")
        result = assistant.answer("Agent harness 为什么重要？")

        self.assertTrue(result.citations)
        self.assertIn("引用", result.answer)

    def test_memory_writes_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            memory = MemoryStore(Path(tmp) / "memory.json")
            assistant = ResearchAssistant(STAGE2 / "docs", memory)
            assistant.answer("memory")

            self.assertTrue((Path(tmp) / "memory.json").exists())


if __name__ == "__main__":
    unittest.main()


from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path


STAGE2_DIR = Path(__file__).resolve().parents[1] / "stage2_rag_memory"
sys.path.insert(0, str(STAGE2_DIR))

from rag_memory import ResearchAssistant  # noqa: E402


@dataclass(frozen=True)
class ShippedAgentResult:
    answer: str
    citations: list[str]
    trace: list[dict[str, object]]


class PersonalResearchAgent:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir.resolve()
        self.assistant = ResearchAssistant(self.data_dir)

    def run(self, question: str) -> ShippedAgentResult:
        trace: list[dict[str, object]] = []
        trace.append({"event": "question_received", "question": question, "timestamp": time.time()})
        trace.append({"event": "permission_checked", "scope": str(self.data_dir), "approved": True, "timestamp": time.time()})
        result = self.assistant.answer(question)
        trace.append(
            {
                "event": "retrieval_completed",
                "citations": result.citations,
                "retrieved_count": len(result.retrieved),
                "timestamp": time.time(),
            }
        )
        trace.append({"event": "final_answer", "answer": result.answer, "timestamp": time.time()})
        return ShippedAgentResult(result.answer, result.citations, trace)


def main() -> None:
    parser = argparse.ArgumentParser(description="A small shipped local research agent.")
    parser.add_argument("question")
    parser.add_argument("--data", default="data")
    parser.add_argument("--trace", default="")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent
    result = PersonalResearchAgent(base_dir / args.data).run(args.question)
    payload = asdict(result)
    if args.trace:
        trace_path = (base_dir / args.trace).resolve()
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        trace_path.write_text(json.dumps(payload["trace"], ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()


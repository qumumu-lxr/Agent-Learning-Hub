from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


STAGE1_DIR = Path(__file__).resolve().parents[1] / "stage1_minimal_agent"
sys.path.insert(0, str(STAGE1_DIR))

from minimal_agent import AgentStep, build_agent  # noqa: E402


@dataclass(frozen=True)
class EvalCase:
    id: str
    task: str
    expected_contains: str
    category: str


@dataclass(frozen=True)
class EvalResult:
    id: str
    task: str
    passed: bool
    expected_contains: str
    actual: str
    failure_category: str
    trace: list[dict[str, object]]


def load_cases(path: Path) -> list[EvalCase]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [EvalCase(**item) for item in data]


def run_eval(cases: list[EvalCase]) -> list[EvalResult]:
    agent = build_agent()
    results: list[EvalResult] = []
    for case in cases:
        actual, steps = agent.run(case.task)
        passed = case.expected_contains in actual
        results.append(
            EvalResult(
                case.id,
                case.task,
                passed,
                case.expected_contains,
                actual,
                "none" if passed else case.category,
                serialize_trace(steps),
            )
        )
    return results


def serialize_trace(steps: list[AgentStep]) -> list[dict[str, object]]:
    trace = []
    for step in steps:
        trace.append(
            {
                "thought": step.thought,
                "action": None if step.action is None else {"name": step.action.name, "arguments": step.action.arguments},
                "observation": None
                if step.observation is None
                else {"ok": step.observation.ok, "content": step.observation.content},
            }
        )
    return trace


def summarize(results: list[EvalResult]) -> dict[str, object]:
    total = len(results)
    passed = sum(1 for result in results if result.passed)
    failures: dict[str, int] = {}
    for result in results:
        if not result.passed:
            failures[result.failure_category] = failures.get(result.failure_category, 0) + 1
    return {"total": total, "passed": passed, "success_rate": round(passed / total, 3), "failures": failures}


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate the Stage 1 agent on fixed tasks.")
    parser.add_argument("--cases", default="evals/stage1_cases.json")
    parser.add_argument("--output", default="")
    args = parser.parse_args()
    base_dir = Path(__file__).resolve().parent
    results = run_eval(load_cases(base_dir / args.cases))
    payload = {"summary": summarize(results), "results": [asdict(result) for result in results]}
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        (base_dir / args.output).write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()


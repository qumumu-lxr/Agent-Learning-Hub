from __future__ import annotations

import argparse
import json
import re
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable


@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class ToolResult:
    ok: bool
    content: str


@dataclass(frozen=True)
class TraceEvent:
    step: int
    event: str
    payload: dict[str, Any]
    timestamp: float


ToolFn = Callable[[dict[str, Any]], ToolResult]


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    risky: bool
    fn: ToolFn


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> None:
        self._tools[spec.name] = spec

    def get(self, name: str) -> ToolSpec | None:
        return self._tools.get(name)

    def names(self) -> list[str]:
        return sorted(self._tools)


class PermissionGate:
    def __init__(self, auto_approve_safe_tools: bool = True) -> None:
        self.auto_approve_safe_tools = auto_approve_safe_tools

    def approve(self, spec: ToolSpec, call: ToolCall) -> tuple[bool, str]:
        if not spec.risky and self.auto_approve_safe_tools:
            return True, "safe tool auto-approved"
        return False, f"tool '{call.name}' requires human approval in this demo"


class SessionStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.events: list[TraceEvent] = []

    def append(self, event: TraceEvent) -> None:
        self.events.append(event)
        self.path.write_text(json.dumps([asdict(item) for item in self.events], ensure_ascii=False, indent=2), encoding="utf-8")


class DemoPolicy:
    def plan(self, task: str) -> list[ToolCall]:
        lowered = task.lower()
        if lowered.startswith("count "):
            return [ToolCall("word_count", {"text": task.removeprefix("count ").strip()})]
        if "read" in lowered:
            return [ToolCall("read_file", {"path": "README.md"})]
        return [ToolCall("search_docs", {"query": task})]


class Harness:
    def __init__(
        self,
        registry: ToolRegistry,
        permissions: PermissionGate,
        session: SessionStore,
        policy: DemoPolicy,
        max_tool_calls: int = 4,
    ) -> None:
        self.registry = registry
        self.permissions = permissions
        self.session = session
        self.policy = policy
        self.max_tool_calls = max_tool_calls

    def run(self, task: str) -> ToolResult:
        self._trace(0, "task_received", {"task": task, "tools": self.registry.names()})
        calls = self.policy.plan(task)[: self.max_tool_calls]
        last_result = ToolResult(False, "no tool was called")
        for index, call in enumerate(calls, start=1):
            self._trace(index, "tool_call_planned", {"name": call.name, "arguments": call.arguments})
            spec = self.registry.get(call.name)
            if spec is None:
                last_result = ToolResult(False, f"unknown tool: {call.name}")
                self._trace(index, "tool_call_failed", {"reason": last_result.content})
                continue
            approved, reason = self.permissions.approve(spec, call)
            self._trace(index, "permission_checked", {"approved": approved, "reason": reason})
            if not approved:
                return ToolResult(False, reason)
            last_result = spec.fn(call.arguments)
            self._trace(index, "tool_observed", {"ok": last_result.ok, "content": last_result.content})
        return last_result

    def _trace(self, step: int, event: str, payload: dict[str, Any]) -> None:
        self.session.append(TraceEvent(step, event, payload, time.time()))


def search_docs(arguments: dict[str, Any]) -> ToolResult:
    query = str(arguments.get("query", "")).lower()
    docs = {
        "harness": "A harness manages tools, permissions, state, traces, retries, and context.",
        "agent": "An agent chooses actions dynamically from observations.",
    }
    for key, value in docs.items():
        if key in query:
            return ToolResult(True, value)
    return ToolResult(False, "no match")


def word_count(arguments: dict[str, Any]) -> ToolResult:
    words = re.findall(r"[A-Za-z0-9]+", str(arguments.get("text", "")))
    return ToolResult(True, json.dumps({"words": len(words)}, ensure_ascii=False))


def read_file(arguments: dict[str, Any]) -> ToolResult:
    path = str(arguments.get("path", ""))
    return ToolResult(True, f"demo would read {path}; real harness should sandbox this")


def build_harness(trace_path: Path) -> Harness:
    registry = ToolRegistry()
    registry.register(ToolSpec("search_docs", "Search local concept notes.", False, search_docs))
    registry.register(ToolSpec("word_count", "Count words in text.", False, word_count))
    registry.register(ToolSpec("read_file", "Read a local file.", True, read_file))
    return Harness(registry, PermissionGate(), SessionStore(trace_path), DemoPolicy())


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a tiny agent harness demo.")
    parser.add_argument("task")
    parser.add_argument("--trace", default="trace.json")
    args = parser.parse_args()
    result = build_harness(Path(args.trace)).run(args.task)
    print(json.dumps(asdict(result), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()


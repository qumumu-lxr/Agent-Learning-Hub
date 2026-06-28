from __future__ import annotations

import argparse
import ast
import json
import operator
import re
from dataclasses import dataclass
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
class AgentStep:
    thought: str
    action: ToolCall | None
    observation: ToolResult | None


ToolFn = Callable[[dict[str, Any]], ToolResult]


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    parameters: dict[str, Any]
    fn: ToolFn

    def schema(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> None:
        self._tools[spec.name] = spec

    def call(self, call: ToolCall) -> ToolResult:
        spec = self._tools.get(call.name)
        if spec is None:
            return ToolResult(False, f"Unknown tool: {call.name}")
        try:
            return spec.fn(call.arguments)
        except Exception as exc:
            return ToolResult(False, f"{type(exc).__name__}: {exc}")

    def list_tools(self) -> list[str]:
        return sorted(self._tools)

    def schemas(self) -> list[dict[str, Any]]:
        return [self._tools[name].schema() for name in self.list_tools()]


class SafeCalculator:
    _operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    def evaluate(self, expression: str) -> float:
        tree = ast.parse(expression, mode="eval")
        return self._eval_node(tree.body)

    def _eval_node(self, node: ast.AST) -> float:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.BinOp):
            op = self._operators.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
            return float(op(self._eval_node(node.left), self._eval_node(node.right)))
        if isinstance(node, ast.UnaryOp):
            op = self._operators.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")
            return float(op(self._eval_node(node.operand)))
        raise ValueError(f"Unsupported expression: {ast.dump(node)}")


def calculator_tool(arguments: dict[str, Any]) -> ToolResult:
    expression = str(arguments.get("expression", "")).strip()
    if not expression:
        return ToolResult(False, "Missing expression")
    value = SafeCalculator().evaluate(expression)
    pretty = int(value) if value.is_integer() else value
    return ToolResult(True, str(pretty))


def read_file_tool(arguments: dict[str, Any]) -> ToolResult:
    path_text = str(arguments.get("path", "")).strip()
    if not path_text:
        return ToolResult(False, "Missing path")
    base_dir = Path(__file__).resolve().parent
    path = (base_dir / path_text).resolve()
    if not path.is_relative_to(base_dir):
        return ToolResult(False, "Refusing to read outside the exercise directory")
    if not path.exists():
        return ToolResult(False, f"File not found: {path_text}")
    return ToolResult(True, path.read_text(encoding="utf-8"))


def search_tool(arguments: dict[str, Any]) -> ToolResult:
    query = str(arguments.get("query", "")).strip().lower()
    if not query:
        return ToolResult(False, "Missing query")

    knowledge = {
        "agent loop": "Agent loop = observe -> think -> act -> observe, repeated until final answer or stop condition.",
        "tool calling": "Tool calling means the model emits structured arguments for a named external function.",
        "trace": "Trace is the step-by-step execution record used to debug agent behavior.",
    }
    for key, value in knowledge.items():
        if key in query:
            return ToolResult(True, value)
    return ToolResult(False, f"No local result for: {query}")


def word_count_tool(arguments: dict[str, Any]) -> ToolResult:
    text = str(arguments.get("text", "")).strip()
    if not text:
        return ToolResult(False, "Missing text")

    english_words = re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", text)
    chinese_chars = re.findall(r"[\u4e00-\u9fff]", text)
    result = {
        "english_words": len(english_words),
        "chinese_chars": len(chinese_chars),
        "characters_without_spaces": len("".join(text.split())),
    }
    return ToolResult(True, json.dumps(result, ensure_ascii=False))


def sentence_count_tool(arguments: dict[str, Any]) -> ToolResult:
    text = str(arguments.get("text", "")).strip()
    if not text:
        return ToolResult(False, "Missing text")

    sentences = [part for part in re.split(r"[。！？.!?]+", text) if part.strip()]
    result = {
        "sentences": len(sentences),
        "text": text,
    }
    return ToolResult(True, json.dumps(result, ensure_ascii=False))

def uppercase_tool(arguments: dict[str, Any]) -> ToolResult:
    text = str(arguments.get("text","")).strip()
    if not text:
        return ToolResult(False,"Missing text")
    return ToolResult(True, text.upper())



class RuleBasedModel:
    def next_action(self, user_input: str, steps: list[AgentStep]) -> tuple[str, ToolCall | None, str | None]:
        if steps and steps[-1].observation is not None:
            observation = steps[-1].observation
            if observation.ok:
                return "I have enough information from the tool result.", None, observation.content.strip()
            return "The tool failed, so I should stop and report the failure.", None, f"工具调用失败：{observation.content}"

        text = user_input.strip()
        expression = self._extract_expression(text)
        if expression:
            return (
                "The user asks for a calculation, so I should call calculator.",
                ToolCall("calculator", {"expression": expression}),
                None,
            )

        if "阅读" in text or "read" in text.lower() or any(suffix in text.lower() for suffix in [".txt", ".md"]):
            file_name = "notes.txt"
            for token in text.replace("，", " ").replace(",", " ").split():
                if token.lower().endswith((".txt", ".md")):
                    file_name = token
                    break
            return (
                "The user asks me to inspect a file, so I should call read_file.",
                ToolCall("read_file", {"path": file_name}),
                None,
            )

        lowered = text.lower()
        if "句子数" in text or "句子" in text or "sentence count" in lowered or "count sentences" in lowered:
            return (
                "The user asks for sentence statistics, so I should call sentence_count.",
                ToolCall("sentence_count", {"text": self._extract_count_target(text)}),
                None,
            )

        if "字数" in text or "统计" in text or "word count" in lowered or "count words" in lowered:
            return (
                "The user asks for text statistics, so I should call word_count.",
                ToolCall("word_count", {"text": self._extract_count_target(text)}),
                None,
            )

        if "大写" in text or "uppercase" in lowered or "upper case" in lowered:
            return (
                "The user asks to convert text to uppercase, so I should call uppercase.",
                ToolCall("uppercase", {"text": self._extract_count_target(text)}),
                None,
            )

        query = text or "agent loop"
        return (
            "The user asks for information, so I should call local search.",
            ToolCall("search", {"query": query}),
            None,
        )

    def _extract_expression(self, text: str) -> str | None:
        allowed = set("0123456789+-*/().% ")
        chars = [char if char in allowed else " " for char in text]
        expression = " ".join("".join(chars).split())
        has_operator = any(op in expression for op in "+-*/%")
        has_digit = any(char.isdigit() for char in expression)
        if has_operator and has_digit:
            return expression
        return None

    def _extract_count_target(self, text: str) -> str:
        for marker in ["：", ":", "内容是", "text is"]:
            if marker in text:
                return text.split(marker, 1)[1].strip()
        return text


class Agent:
    def __init__(self, model: RuleBasedModel, tools: ToolRegistry, max_steps: int = 4) -> None:
        self.model = model
        self.tools = tools
        self.max_steps = max_steps

    def run(self, user_input: str) -> tuple[str, list[AgentStep]]:
        steps: list[AgentStep] = []
        for _ in range(self.max_steps):
            thought, action, final_answer = self.model.next_action(user_input, steps)
            if final_answer is not None:
                steps.append(AgentStep(thought, None, None))
                return final_answer, steps
            if action is None:
                steps.append(AgentStep(thought, None, None))
                return "No action selected.", steps

            observation = self.tools.call(action)
            steps.append(AgentStep(thought, action, observation))

        return f"Stopped after reaching max_steps={self.max_steps}.", steps


def build_agent(max_steps: int = 4) -> Agent:
    tools = ToolRegistry()
    tools.register(
        ToolSpec(
            name="calculator",
            description="Evaluate a safe arithmetic expression with numbers and basic operators.",
            parameters={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Arithmetic expression, for example '23 * 7 + 10'.",
                    }
                },
                "required": ["expression"],
            },
            fn=calculator_tool,
        )
    )
    tools.register(
        ToolSpec(
            name="read_file",
            description="Read a UTF-8 text file from the exercise directory.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path inside the exercise directory.",
                    }
                },
                "required": ["path"],
            },
            fn=read_file_tool,
        )
    )
    tools.register(
        ToolSpec(
            name="search",
            description="Search a tiny local knowledge base for Agent learning concepts.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Concept or question to search for.",
                    }
                },
                "required": ["query"],
            },
            fn=search_tool,
        )
    )
    tools.register(
        ToolSpec(
            name="word_count",
            description="Count English words, Chinese characters, and non-space characters in text.",
            parameters={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to analyze.",
                    }
                },
                "required": ["text"],
            },
            fn=word_count_tool,
        )
    )
    tools.register(
        ToolSpec(
            name="sentence_count",
            description="Count sentences split by common Chinese and English sentence punctuation.",
            parameters={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to split into sentences.",
                    }
                },
                "required": ["text"],
            },
            fn=sentence_count_tool,
        )
    )
    tools.register(
        ToolSpec(
            name="uppercase",
            description="Convert text to uppercase.",
            parameters={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to convert.",
                    }
                },
                "required": ["text"],
            },
            fn=uppercase_tool,
        )
    )
    return Agent(RuleBasedModel(), tools, max_steps=max_steps)


def print_trace(steps: list[AgentStep]) -> None:
    for index, step in enumerate(steps, start=1):
        print(f"\nStep {index}")
        print(f"Thought: {step.thought}")
        if step.action is not None:
            print("Action:")
            print(json.dumps({"name": step.action.name, "arguments": step.action.arguments}, ensure_ascii=False, indent=2))
        if step.observation is not None:
            print("Observation:")
            print(json.dumps({"ok": step.observation.ok, "content": step.observation.content}, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a minimal local agent loop.")
    parser.add_argument("prompt", help="User task for the agent.")
    parser.add_argument("--max-steps", type=int, default=4)
    args = parser.parse_args()

    agent = build_agent(max_steps=args.max_steps)
    answer, steps = agent.run(args.prompt)
    print_trace(steps)
    print("\nFinal Answer")
    print(answer)


if __name__ == "__main__":
    main()

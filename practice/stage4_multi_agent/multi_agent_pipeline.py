from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ResearchBrief:
    topic: str
    facts: list[str]


@dataclass(frozen=True)
class Draft:
    topic: str
    body: str


@dataclass(frozen=True)
class Review:
    passed: bool
    issues: list[str]


@dataclass(frozen=True)
class FinalReport:
    topic: str
    answer: str
    review: Review
    trace: list[dict[str, object]]


class ResearcherAgent:
    def run(self, topic: str) -> ResearchBrief:
        facts = [
            "Agent evaluation should use fixed tasks instead of relying only on demos.",
            "Observability connects failures to prompts, tools, retrieval, model behavior, or state.",
            "Safety checks are needed when tools can mutate files, spend money, or publish content.",
        ]
        matching = [fact for fact in facts if any(token in fact.lower() for token in topic.lower().split())]
        return ResearchBrief(topic, matching or facts[:2])


class WriterAgent:
    def run(self, brief: ResearchBrief) -> Draft:
        body = f"主题：{brief.topic}\n" + "\n".join(f"- {fact}" for fact in brief.facts)
        body += "\n结论：multi-agent 系统也需要可验证的成功标准和失败分析。"
        return Draft(brief.topic, body)


class ReviewerAgent:
    def run(self, draft: Draft) -> Review:
        issues: list[str] = []
        if len(draft.body) < 80:
            issues.append("内容太短，无法支撑结论。")
        if "结论" not in draft.body:
            issues.append("缺少明确结论。")
        if "- " not in draft.body:
            issues.append("缺少结构化证据。")
        return Review(not issues, issues)


class ReviserAgent:
    def run(self, draft: Draft, review: Review) -> Draft:
        if review.passed:
            return draft
        additions = "\n修订：已根据 review 补充证据、结论和可检查结构。"
        additions += "\n验收：读者应能指出核心观点、证据和下一步行动。"
        return Draft(draft.topic, draft.body + additions)


class Supervisor:
    def __init__(self) -> None:
        self.researcher = ResearcherAgent()
        self.writer = WriterAgent()
        self.reviewer = ReviewerAgent()
        self.reviser = ReviserAgent()

    def run(self, topic: str) -> FinalReport:
        trace: list[dict[str, object]] = []
        brief = self.researcher.run(topic)
        trace.append({"agent": "researcher", "output": asdict(brief)})
        draft = self.writer.run(brief)
        trace.append({"agent": "writer", "output": asdict(draft)})
        review = self.reviewer.run(draft)
        trace.append({"agent": "reviewer", "output": asdict(review)})
        final_draft = self.reviser.run(draft, review)
        trace.append({"agent": "reviser", "output": asdict(final_draft)})
        final_review = self.reviewer.run(final_draft)
        trace.append({"agent": "reviewer", "output": asdict(final_review)})
        return FinalReport(topic, final_draft.body, final_review, trace)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a four-agent supervised pipeline.")
    parser.add_argument("topic")
    args = parser.parse_args()
    print(json.dumps(asdict(Supervisor().run(args.topic)), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()


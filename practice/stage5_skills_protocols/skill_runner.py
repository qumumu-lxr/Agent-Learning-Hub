from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    checks: list[str]
    template: str


@dataclass(frozen=True)
class SkillRun:
    skill_name: str
    output: str
    passed_checks: list[str]
    failed_checks: list[str]


def load_skill(skill_dir: Path) -> Skill:
    skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    template = (skill_dir / "templates" / "summary.md").read_text(encoding="utf-8")
    name = _read_field(skill_text, "Name")
    description = _read_field(skill_text, "Description")
    checks = [
        line.removeprefix("- ").strip()
        for line in skill_text.splitlines()
        if line.startswith("- must ")
    ]
    return Skill(name, description, checks, template)


def run_skill(skill: Skill, source_text: str) -> SkillRun:
    key_points = [part.strip() for part in source_text.replace(".", "\n").splitlines() if part.strip()]
    output = skill.template.replace("{{summary}}", "\n".join(f"- {point}" for point in key_points[:3]))
    output = output.replace("{{takeaway}}", "Skill packages reusable process knowledge, not just code.")

    passed: list[str] = []
    failed: list[str] = []
    for check in skill.checks:
        if "bullet" in check and "- " in output:
            passed.append(check)
        elif "takeaway" in check and "Takeaway" in output:
            passed.append(check)
        elif "source" in check and source_text:
            passed.append(check)
        else:
            failed.append(check)
    return SkillRun(skill.name, output, passed, failed)


def _read_field(text: str, field: str) -> str:
    prefix = f"{field}:"
    for line in text.splitlines():
        if line.startswith(prefix):
            return line.removeprefix(prefix).strip()
    return "unknown"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a tiny skill package.")
    parser.add_argument("source_text")
    parser.add_argument("--skill-dir", default="skills/research_summary")
    args = parser.parse_args()
    base_dir = Path(__file__).resolve().parent
    result = run_skill(load_skill(base_dir / args.skill_dir), args.source_text)
    print(json.dumps(asdict(result), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()


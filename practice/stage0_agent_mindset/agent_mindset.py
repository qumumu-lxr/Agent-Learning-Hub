from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass


AGENT_KEYWORDS = {
    "多轮",
    "迭代",
    "规划",
    "搜索",
    "检索",
    "资料",
    "证据",
    "找证据",
    "调用工具",
    "浏览器",
    "根据结果",
    "反馈",
    "调研",
    "debug",
    "修复",
}

WORKFLOW_KEYWORDS = {"审批", "固定流程", "表单", "发送邮件", "生成报表", "每日", "定时"}
SCRIPT_KEYWORDS = {"转换", "清洗", "批量", "重命名", "计算", "统计", "csv", "json", "字段"}
CHATBOT_KEYWORDS = {"解释", "是什么", "翻译", "润色", "总结这段", "概念"}
RISK_KEYWORDS = {"删除", "支付", "下单", "提交", "发送", "发布", "修改线上", "覆盖"}


@dataclass(frozen=True)
class AgentDecision:
    task: str
    recommended_pattern: str
    uncertainty_sources: list[str]
    human_approval_needed: list[str]
    first_design_step: str


def classify_task(task: str) -> AgentDecision:
    lowered = task.lower()
    score_agent = _score(task, AGENT_KEYWORDS)
    score_workflow = _score(task, WORKFLOW_KEYWORDS)
    score_script = _score(lowered, SCRIPT_KEYWORDS)
    score_chatbot = _score(task, CHATBOT_KEYWORDS)

    if score_agent >= 2 or ("根据" in task and "结果" in task):
        pattern = "agent"
    elif score_script >= max(score_workflow, score_chatbot, 1):
        pattern = "script"
    elif score_workflow >= max(score_chatbot, 1):
        pattern = "workflow"
    elif score_chatbot:
        pattern = "chatbot"
    else:
        pattern = "workflow"

    uncertainty_sources = []
    if score_agent:
        uncertainty_sources.append("下一步动作依赖工具观察结果")
    if any(word in task for word in {"搜索", "检索", "调研", "浏览"}):
        uncertainty_sources.append("外部信息质量和来源不确定")
    if any(word in task for word in {"修复", "debug", "报错"}):
        uncertainty_sources.append("失败原因需要试探和验证")
    if not uncertainty_sources:
        uncertainty_sources.append("不确定性较低，可以先用更简单形态实现")

    approvals = [word for word in RISK_KEYWORDS if word in task]
    if not approvals:
        approvals = ["无明显高风险动作，但仍应限制文件、网络和执行权限"]

    first_step = {
        "agent": "写出 observe -> think -> act -> observe 的循环、工具清单、停止条件和 trace 格式。",
        "workflow": "画出固定步骤和每一步输入输出 schema，先不用模型控制流程。",
        "script": "写一个确定性函数和单元测试，只有歧义判断部分再考虑 LLM。",
        "chatbot": "设计提示词和引用来源，避免引入不必要的工具调用。",
    }[pattern]

    return AgentDecision(task, pattern, uncertainty_sources, approvals, first_step)


def _score(text: str, keywords: set[str]) -> int:
    return sum(1 for keyword in keywords if keyword in text)


def main() -> None:
    parser = argparse.ArgumentParser(description="Decide whether a task needs an agent.")
    parser.add_argument("task")
    args = parser.parse_args()
    print(json.dumps(asdict(classify_task(args.task)), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

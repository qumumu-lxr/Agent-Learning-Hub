# Agent Learning Hub 动手实践区

这个目录把仓库 README 里的学习路线转成可运行练习。

当前已完成：

- `stage0_agent_mindset/`: 判断任务是否真的需要 agent。
- `stage1_minimal_agent/`: 最小 Agent Loop。
- `stage2_rag_memory/`: 本地 RAG、引用回答和会话记忆。
- `stage3_harness/`: 工具注册、权限、session 和 trace。
- `stage4_multi_agent/`: researcher -> writer -> reviewer -> reviser 协调流水线。
- `stage5_skills_protocols/`: 最小 Skill 包和 smoke test。
- `stage6_browser_agent/`: 本地 HTML 信息提取和动作日志。
- `stage7_eval_observability/`: 20 条固定 eval、失败分类和 trace。
- `stage8_ship_real_agent/`: 一个可交付的本地资料研究 agent CLI。

## 学习顺序

1. 先读仓库根目录的 `README.md`，理解 Stage 0 到 Stage 8 的全局路线。
2. 进入 `practice/stage0_agent_mindset`，练习判断任务形态。
3. 进入 `practice/stage1_minimal_agent`，跑通第一个 agent。
4. 继续按 stage 顺序运行每个 README 里的命令。
5. 最后用 `stage7_eval_observability` 评测 Stage 1，用 `stage8_ship_real_agent` 交付一个完整 CLI。

## 你要掌握的核心概念

- `agent loop`: observe -> think -> act -> observe 的循环。
- `tool registry`: agent 能调用哪些工具，以及工具 schema 是什么。
- `structured action`: 模型不能只输出自然语言，必须输出可解析动作。
- `trace`: 每一步为什么发生、调用了什么工具、工具返回了什么。
- `guardrail`: 最大步数、错误处理、未知工具处理、停止条件。
- `retrieval`: 先找证据，再回答。
- `harness`: 管理工具、权限、状态、trace 和恢复的工程层。
- `multi-agent coordination`: 明确职责、schema、停止条件和 supervisor。
- `skill`: 把流程知识、模板、脚本和验收标准打包成能力。

## 一次性自检

```bash
cd "/Users/lixinru02/Documents/ai study/Agent-Learning-Hub"
python3 -m unittest discover -s tests
```

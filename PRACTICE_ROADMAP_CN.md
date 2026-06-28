# Agent Learning Hub 动手学习路线

这份路线把原仓库的 Stage 0-8 变成“每天可以推进”的学习路径。建议你不要急着接真实 LLM API，先用本地规则和标准库跑通 agent 的工程骨架，再逐步替换成真实模型、embedding、浏览器和部署形态。

## 总体节奏

| 阶段 | 建议时间 | 你要完成的事 | 验收方式 |
| --- | --- | --- | --- |
| Stage 0 | 0.5 天 | 判断任务是否需要 agent | 能说出 chatbot、workflow、script、agent 的区别 |
| Stage 1 | 1 天 | 最小 agent loop | 会读 trace，能新增一个工具 |
| Stage 2 | 2 天 | RAG + memory | 回答带引用，知识库不足时不胡编 |
| Stage 3 | 2 天 | harness | 有工具注册、权限、session、trace |
| Stage 4 | 1 天 | multi-agent | 每个 agent 输入输出清晰，supervisor 有停止条件 |
| Stage 5 | 1 天 | skill/protocol | 写出一个 `SKILL.md` 和 smoke test |
| Stage 6 | 1 天 | browser agent | 能解析页面，保存动作日志，识别风险动作 |
| Stage 7 | 2 天 | eval/observability/safety | 有 20 条固定测试和失败分类 |
| Stage 8 | 2 天 | ship | 有 README、CLI、trace、权限边界和可复现运行步骤 |

## Stage 0: 先判断形态

运行：

```bash
cd "/Users/lixinru02/Documents/ai study/Agent-Learning-Hub/practice/stage0_agent_mindset"
python3 agent_mindset.py "读取本地资料，找证据，总结 agent harness 为什么重要"
```

学习重点：

- 普通脚本适合确定性批处理。
- Workflow 适合固定步骤。
- Chatbot 适合一次性解释和改写。
- Agent 适合下一步动作依赖观察结果的任务。

动手改：

- 在 `agent_mindset.py` 里扩展关键词。
- 用你的真实学习/求职/项目任务做 5 次分类。

## Stage 1: 最小 Agent Loop

运行：

```bash
cd "/Users/lixinru02/Documents/ai study/Agent-Learning-Hub/practice/stage1_minimal_agent"
python3 minimal_agent.py "计算 23 * 7 + 10"
python3 minimal_agent.py "请阅读 notes.txt 并总结"
python3 minimal_agent.py "统计字数：Agent loop 需要 tools, trace 和 stop condition"
```

学习重点：

- `ToolCall`: agent 想做什么。
- `ToolResult`: 环境反馈了什么。
- `ToolRegistry`: agent 有哪些能力。
- `Agent.run`: observe -> think -> act -> observe。

动手改：

- 新增 `sentence_count` 工具。
- 故意传错参数，看 trace 如何暴露问题。
- 把 `max_steps` 改成 1，理解停止条件。

## Stage 2: RAG 和 Memory

运行：

```bash
cd "/Users/lixinru02/Documents/ai study/Agent-Learning-Hub/practice/stage2_rag_memory"
python3 rag_memory.py "Agent harness 为什么重要？"
python3 rag_memory.py "memory 在 agent 中解决什么问题？" --memory memory.json
```

学习重点：

- chunk 不是随便切，切太碎会丢语义，切太大召回不准。
- retrieval 决定回答能不能 grounded。
- citations 是防胡编的第一道工程约束。
- memory 和 trace 不一样：memory 面向后续任务，trace 面向调试。

动手改：

- 调整 `chunk_text(max_chars=...)`。
- 给 `docs/agent_notes.md` 加资料。
- 把 `TermRetriever` 替换成 embedding 检索。

## Stage 3: Harness

运行：

```bash
cd "/Users/lixinru02/Documents/ai study/Agent-Learning-Hub/practice/stage3_harness"
python3 harness_demo.py "search agent harness"
python3 harness_demo.py "read file"
```

学习重点：

- Harness 是模型外面的工程系统。
- 权限 gate 要在工具执行前发生。
- trace 要覆盖计划、审批、执行、观察。
- session store 让长任务可恢复、可审计。

动手改：

- 新增一个工具。
- 把 risky tool 改成人工确认。
- 把 trace 改成 JSONL。

## Stage 4: Multi-Agent

运行：

```bash
cd "/Users/lixinru02/Documents/ai study/Agent-Learning-Hub/practice/stage4_multi_agent"
python3 multi_agent_pipeline.py "为什么 agent 需要 eval？"
```

学习重点：

- 多 agent 的难点是协调，不是角色扮演。
- 每个 agent 必须有职责边界。
- reviewer 要输出可执行 issue，而不是泛泛而谈。
- supervisor 要控制顺序、循环和停止条件。

动手改：

- 增加 `FactCheckerAgent`。
- 给 reviewer 加“是否有引用”检查。
- 设置最大修订轮数。

## Stage 5: Skills 和 Protocols

运行：

```bash
cd "/Users/lixinru02/Documents/ai study/Agent-Learning-Hub/practice/stage5_skills_protocols"
python3 skill_runner.py "agent harness helps reliability"
```

学习重点：

- Tool 是函数。
- Skill 是可复用工作方法。
- MCP 连接外部工具和数据。
- A2A/ACP 解决 agent 与 agent、agent 与宿主的通信边界。

动手改：

- 改 `SKILL.md` 的 procedure。
- 加一个模板。
- 设计一个会失败的 smoke test。

## Stage 6: Browser Agent

运行：

```bash
cd "/Users/lixinru02/Documents/ai study/Agent-Learning-Hub/practice/stage6_browser_agent"
python3 browser_info_agent.py pages/sample.html
```

学习重点：

- DOM 适合结构化提取。
- 截图适合视觉验证。
- 动作日志适合复盘和审计。
- 提交表单、支付、发布、删除都要权限确认。

动手改：

- 提取表格。
- 增加失败恢复：文件不存在时给清晰错误。
- 用 Playwright 替换本地 HTML parser。

## Stage 7: Eval、Observability 和 Safety

运行：

```bash
cd "/Users/lixinru02/Documents/ai study/Agent-Learning-Hub/practice/stage7_eval_observability"
python3 eval_runner.py
```

学习重点：

- 固定 eval 可以防止“只会 demo”。
- 失败分类帮助你知道该改 prompt、工具、检索还是状态。
- trace 是定位问题的证据链。
- safety 不是口号，是权限边界、确认机制和审计记录。

动手改：

- 新增 5 条失败用例。
- 输出平均工具调用次数。
- 把结果保存成 CSV 或 Markdown 表格。

## Stage 8: Ship

运行：

```bash
cd "/Users/lixinru02/Documents/ai study/Agent-Learning-Hub/practice/stage8_ship_real_agent"
python3 personal_research_agent.py "为什么 agent 项目需要评测？" --trace traces/run.json
```

学习重点：

- 用户和任务要窄。
- 成功标准要能检查。
- README 要让别人复现。
- 日志、trace、权限和错误处理不是最后补，是交付的一部分。

动手改：

- 加更多本地资料。
- 接入真实 LLM 改写回答。
- 用 Stage 7 的 eval 固定回归。
- 把 CLI 包成 Web app、Slack bot、GitHub Action 或后台任务。

## 全量测试

每完成一个 stage，都可以跑：

```bash
cd "/Users/lixinru02/Documents/ai study/Agent-Learning-Hub"
python3 -m unittest discover -s tests
```

当前测试覆盖 Stage 0-8 的关键路径。你后面每改一个工具、一个 prompt、一个检索策略，都应该补一条测试或 eval case。

## 后续遗留任务

完成本仓库 Stage 0-8 后，继续学习 Datawhale 的 `hello-agents` 仓库：

- 仓库地址：[datawhalechina/hello-agents](https://github.com/datawhalechina/hello-agents)
- 学习时机：当前 Agent Learning Hub 所有 stage 学完之后。
- 学习目标：对比当前从零搭建的 agent 框架，理解 `hello-agents` 中的项目结构、示例实现、工具调用方式和工程实践。

# Agent Learning Hub 中文学习导览与实践计划

本文件用于配合仓库根目录 `README.md` 学习。原仓库主要是路线图和资源索引，不是大型代码库；因此学习重点不是“读源码”，而是按路线把每个 Agent 能力点做成可运行作品。

## 0. 这个仓库到底是什么

`datawhalechina/Agent-Learning-Hub` 的核心是：

- 一份 AI Agent 学习路线图。
- 一组高质量官方文档、论文、开源项目和博客索引。
- 一个静态展示页面 `index.html`。

它不包含完整 Agent 项目源码。要真正掌握，需要边读路线边完成每个 Stage 的产出。

## 1. Agent 的全局心智模型

最小 Agent 可以被理解为一个循环：

```text
observe -> think -> act -> observe -> ... -> final answer
```

对应到工程实现：

| 概念 | 工程含义 |
| --- | --- |
| observe | 接收用户输入、工具结果、历史上下文、环境状态。 |
| think | 模型或策略决定下一步做什么。 |
| act | 调用工具，例如搜索、读文件、执行代码、访问数据库。 |
| trace | 记录每一步 thought/action/observation。 |
| guardrail | 最大步数、权限确认、错误处理、超时、停止条件。 |

一个可靠 Agent 的能力不只来自模型，还来自 harness：工具协议、权限、状态管理、上下文压缩、日志、评测和人工确认。

## 2. 推荐学习节奏

建议用 4 周跑完第一轮：

| 周期 | 主线 | 产出 |
| --- | --- | --- |
| 第 1 周 | Stage 0-1: Agent 基础与最小 loop | 一个本地最小 agent，能调用工具并输出 trace。 |
| 第 2 周 | Stage 2: Tool Use + RAG + Memory | 一个资料研究助手，带引用链接。 |
| 第 3 周 | Stage 3-5: Harness + Skills + Protocols | 一个可扩展 agent harness demo，一个自定义 `SKILL.md`。 |
| 第 4 周 | Stage 6-8: Browser + Eval + Ship | 一个有评测表、日志和运行说明的完整 agent 项目。 |

## 3. 每个 Stage 应该掌握什么

### Stage 0: 理解 Agent 是什么

你要能清楚区分：

- chatbot: 只回答，不主动调用外部动作。
- workflow: 固定流程，每一步预先写死。
- agent: 可以根据观察结果动态选择下一步。
- multi-agent: 多个有职责边界的 agent 协作，不是随便互相聊天。

验收问题：

- 我的任务为什么需要 agent，而不是普通脚本？
- 任务的不确定性来自哪里？
- 哪些动作需要人类确认？

### Stage 1: 构建最小 Agent Loop

你要掌握：

- 工具注册表如何设计。
- 工具参数为什么要结构化。
- 模型输出为什么必须可解析。
- trace 如何帮助调试。
- 最大步数和错误处理为什么是必需品。

本仓库已补充练习：

```bash
cd "/Users/lixinru02/Documents/ai study/Agent-Learning-Hub/practice/stage1_minimal_agent"
python3 minimal_agent.py "计算 23 * 7 + 10"
python3 minimal_agent.py "请阅读 notes.txt 并总结"
python3 minimal_agent.py "查一下 agent loop 是什么"
```

测试：

```bash
cd "/Users/lixinru02/Documents/ai study/Agent-Learning-Hub"
python3 -m unittest tests/test_stage1_minimal_agent.py
```

### Stage 2: Tool Use、RAG 和 Memory

你要掌握：

- chunk: 如何切文档。
- embedding: 如何把文本转成向量。
- retrieval: 如何从知识库找证据。
- grounded answer: 回答必须引用来源。
- memory: 短期上下文、会话记忆、长期记忆的区别。

实践项目：

- 输入一个主题。
- 本地或联网检索资料。
- 筛选有效证据。
- 输出带引用的摘要。

### Stage 3: 学一个现代 Agent Harness

推荐先研究 coding agent，因为它把真实工程问题暴露得最完整：

- 文件读写。
- shell 执行。
- 权限审批。
- 上下文压缩。
- 测试反馈。
- trace 和恢复。

重点不是背框架 API，而是找出：

- agent loop 在哪里。
- tool registry 在哪里。
- permission gate 在哪里。
- session store 在哪里。
- context compaction 在哪里。

### Stage 4: Multi-Agent 是协调问题

多 Agent 的核心不是“多个角色聊天”，而是：

- 每个 agent 有明确职责。
- 输入输出 schema 清晰。
- 停止条件清晰。
- supervisor 或 graph 控制流转。
- 有机制处理循环、争论、漂移和上下文膨胀。

实践项目：

```text
researcher -> writer -> reviewer -> reviser
```

每个角色只做一件事，并输出结构化结果。

### Stage 5: Skills、MCP、A2A、ACP

你要掌握：

- Tool: 一个可调用函数或外部接口。
- Skill: 一套可复用流程知识，通常包含说明、脚本、模板和验收标准。
- MCP: 标准化连接外部工具和数据源。
- A2A: agent 之间通信协作。
- ACP: 宿主应用和 agent 的交互协议。

实践项目：

- 写一个 `SKILL.md`。
- 配一个脚本或模板。
- 设计 smoke test，证明这个 skill 真能提升任务成功率。

### Stage 6: Browser 和 Computer-Use Agents

你要掌握：

- DOM、截图、动作日志分别解决什么问题。
- 页面变化、弹窗、加载失败如何恢复。
- 哪些网页动作不应该自动执行。
- 为什么浏览器 agent 必须有权限边界。

实践项目：

- 用公开网页做信息提取。
- 保存动作日志和截图。
- 失败时输出清晰错误原因。

### Stage 7: Evaluation、Observability 和 Safety

你要掌握：

- 不能只靠 demo 判断 agent 是否有效。
- eval 表格至少要包含任务、期望、实际、失败分类。
- trace 要能定位失败来自 prompt、工具、检索、模型还是状态管理。
- 危险动作需要人工确认。

实践项目：

- 设计 20 条固定测试任务。
- 统计成功率、失败原因、工具调用次数、成本和延迟。

### Stage 8: Ship 一个真实 Agent

最终项目必须具备：

- 明确用户和任务。
- 明确成功标准。
- 日志和 trace。
- 错误重试和超时。
- 成本或步数上限。
- 权限边界。
- README 和可复现运行步骤。

## 4. 当前已完成的本地补充

我已在本仓库新增：

- `practice/README.md`
- `practice/stage1_minimal_agent/README.md`
- `practice/stage1_minimal_agent/minimal_agent.py`
- `practice/stage1_minimal_agent/notes.txt`
- `tests/test_stage1_minimal_agent.py`

这个练习覆盖：

- 最小 agent loop。
- 三个工具：`calculator`、`read_file`、`search`。
- 工具注册表。
- 工具错误处理。
- 文件读取边界限制。
- trace 输出。
- 标准库测试。

## 5. 下一步实践任务

建议下一轮按这个顺序做。更完整的带学路线见 `PRACTICE_ROADMAP_CN.md`：

1. 给 Stage 1 agent 增加 `word_count` 工具。
2. 把工具 schema 显式写出来，让模型知道每个工具的参数。
3. 接入真实 LLM API，替换 `RuleBasedModel`。
4. 加入 trace JSON 文件保存。
5. 进入 Stage 2，做一个小型 RAG：读取本仓库 README，回答“Agent harness 为什么重要？”并引用段落。

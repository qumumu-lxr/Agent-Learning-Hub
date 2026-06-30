# README 学习点逐项详解与项目面试手册

本手册严格围绕仓库根目录 `README.md` 中列出的学习点展开，目标不是再做一份资料清单，而是把每个 checklist 变成你能讲清楚、能落到本地代码、能连接到面试项目的问题答案。

你的项目主题：

> 异常巡检与归因 Agent：站点交付异常的证据链诊断与报告生成

项目简历表达：

> 针对站点交付过程中异常发现依赖人工且根因追踪链路不清晰的问题，构建异常巡检与归因 Agent，自动识别交付偏差、追踪关键影响因素并生成可解释分析报告，支撑复杂工程交付过程的风险感知、问题闭环和成本优化。参与异常归因场景下 Agent Harness 核心链路开发，搭建面向长路径复杂任务的闭环 Agent Loop，覆盖任务规划、工具调用、证据校验、Self-Reflection 补查与报告生成，支撑 Agent 自主完成任务拆解、工具执行、证据判断和结论生成；设计 WorkflowState 上下文管理机制，统一承载异常输入、执行计划、工具结果、证据链、反思决策与最终结论，提升多轮执行中的上下文连续性和任务达成稳定性；沉淀 Agent 记忆与执行记录，结构化记录工具调用结果、反思日志、bad case 样本与归因结论，为任务复盘、故障诊断、效果评测闭环和记忆复用提供数据基础。已在两个重点项目完成初步落地验证并完成两个版本上线，驱动试点项目的交付成本降低 37.5%。

## 一、README 主线应该怎么记

README 的核心判断是：当前 Agent 学习不应该停留在“角色扮演式多 agent demo”，而应该围绕能真正交付的工程能力展开。

你要把它记成 5 条主线：

1. Coding agents 是最好的工程样本：真实代码库、shell、文件编辑、测试、权限、上下文压缩。
2. Agent harness 是能力来源：工具协议、权限、状态、反馈、回放、CI、评测。
3. Personal agents 代表长期运行：本地优先、跨应用、记忆、skills、消息入口。
4. Skills / MCP / A2A / ACP 代表能力复用和系统连接。
5. Evaluation and safety 决定 agent 是 demo 还是可交付系统。

面试表达：

> 我对 Agent 的理解不是“让模型多说几轮”，而是围绕长任务搭建一个可控的执行系统。模型负责推理和动作选择，harness 负责工具、权限、状态、trace、评测和恢复。真正能落地的 Agent 必须可观察、可复盘、可评测、可回滚。

## 二、What To Learn Now 逐项详解

### 1. Claude Code / Codex-style coding agents

README 说它们重要，是因为 coding agent 面对的不是玩具环境，而是真实工程：

- 要读文件。
- 要改代码。
- 要运行测试。
- 要处理错误输出。
- 要遵守权限。
- 要管理上下文。
- 要在失败后重试或修正。

这些能力和你的异常巡检项目很像。站点交付异常归因也不是一次问答，而是：

- 读取异常输入。
- 查询进度、工单、风险、里程碑、成本等数据。
- 调用工具拿证据。
- 根据证据判断是否足够。
- 不足时补查。
- 最后生成可解释报告。

面试可能问：为什么你学习 coding agent 对业务 Agent 有帮助？

答：

> Coding agent 展示的是最完整的 agent harness 样本。它有工具调用、权限控制、状态管理、测试验证和 trace 回放。我的异常归因 Agent 虽然不是写代码场景，但同样是长路径任务，也需要任务规划、工具执行、证据校验、反思补查和报告生成，所以可以复用 coding agent 的 harness 思路。

### 2. Agent harness engineering

Harness 是模型外面的工程壳。你可以把它理解成 Agent 的运行时系统。

Harness 通常负责：

- 工具注册：agent 能调用哪些工具。
- 工具 schema：每个工具需要什么参数。
- 权限控制：哪些动作要人工确认。
- 状态管理：上下文和中间结果存在哪里。
- trace：每一步为什么发生。
- session：一次任务如何恢复和复盘。
- budget：最多跑多少步、最多调用多少工具。
- error handling：工具失败、超时、空结果怎么办。
- eval：如何证明改动后能力没有退化。

本地代码对应：

- Stage 1：`practice/stage1_minimal_agent/minimal_agent.py`
- Stage 3：`practice/stage3_harness/harness_demo.py`
- Stage 7：`practice/stage7_eval_observability/eval_runner.py`

项目映射：

> 你的 Agent Harness 核心链路就是业务版 harness：它接收异常输入，规划归因步骤，调工具查证据，把结果写进 WorkflowState，通过 evidence chain 校验结论，再通过 reflection 决定是否补查，最后生成报告和执行记录。

### 3. OpenClaw / Hermes-style personal agents

这类系统强调长期运行、记忆、skills、跨入口和消息网关。你不需要面试时背框架细节，但要理解方向：

- Agent 不是一次性脚本。
- Agent 可以长期接收任务。
- Agent 需要记忆历史经验。
- Agent 需要知道什么时候加载 skill。
- Agent 需要在不同入口之间保持 session。

项目映射：

> 异常归因项目里，memory 不只是保存日志，而是沉淀可复用经验。例如某类站点延期经常由供应商到货、审批卡点、施工窗口冲突导致，经过复核后可以沉淀为归因模式或 bad case 样本。下一次相似异常出现时，Agent 可以把历史模式作为补充上下文。

### 4. Skills / MCP / A2A / ACP

这几个概念容易混，面试中建议这样区分：

| 概念 | 一句话 | 项目里的类比 |
| --- | --- | --- |
| Tool | 可调用函数或接口 | 查询交付计划、查询工单、读取巡检记录 |
| Skill | 可复用流程知识 | 异常归因流程、报告模板、证据校验规则 |
| MCP | 连接外部工具和数据源的协议 | 标准化接入项目管理系统、监控平台、知识库 |
| A2A | Agent 之间协作协议 | 归因 Agent 与报告 Agent 或审核 Agent 协作 |
| ACP | 宿主应用和 Agent 的通信接口 | Web/IDE/平台把任务交给 Agent 并接收结果 |

面试回答：

> Tool 是动作接口，Skill 是完成一类任务的方法包，MCP 是连接外部工具和数据源的协议。我的项目里，查询进度和读取工单是 tool；异常归因步骤和报告模板可以沉淀为 skill；如果未来要对接多个平台，可以用类似 MCP 的方式统一工具接入。

### 5. Evaluation and safety

README 说没有 eval、trace、权限边界的 agent 只能算 demo。你要能解释为什么。

Agent 的不稳定来源包括：

- 工具选错。
- 参数填错。
- 检索不到证据。
- 证据冲突。
- 模型过度概括。
- 记忆污染。
- 权限越界。
- 长链路状态丢失。

所以需要：

- 固定 eval 集。
- trace 回放。
- failure category。
- 工具调用次数统计。
- 成本和延迟统计。
- 人工确认机制。
- 回归测试。

项目映射：

> 异常归因项目的 bad case 分析就是 eval 和 observability 的结合。每次结论错误时，不只看最终报告，而是回放 WorkflowState：看计划是否漏查、工具是否失败、证据链是否不足、reflection 是否触发、报告是否夸大结论。

## 三、Stage 0: Understand What An Agent Is

### Checklist 1：区分 chatbot、workflow、agent、multi-agent

定义：

| 类型 | 核心特征 | 适合任务 | 不适合任务 |
| --- | --- | --- | --- |
| Chatbot | 以对话和生成文本为主 | 解释、问答、润色 | 需要真实工具执行和状态追踪的任务 |
| Workflow | 固定流程，路径稳定 | 审批、报表、固定 ETL | 下一步依赖动态观察的任务 |
| Agent | 根据观察结果动态选择动作 | 调研、debug、归因、修复 | 简单确定性任务 |
| Multi-agent | 多个职责模块协作 | 研究-写作-审核-修订 | 单 agent 足够完成的任务 |

本地代码：

```python
# practice/stage0_agent_mindset/agent_mindset.py
if score_agent >= 2 or ("根据" in task and "结果" in task):
    pattern = "agent"
elif score_script >= max(score_workflow, score_chatbot, 1):
    pattern = "script"
elif score_workflow >= max(score_chatbot, 1):
    pattern = "workflow"
elif score_chatbot:
    pattern = "chatbot"
```

你的项目为什么是 Agent：

- 异常原因不确定。
- 下一步要查什么依赖已有证据。
- 工具结果可能为空、冲突或不足。
- 需要补查和反思。
- 最终报告必须能解释证据链。

面试回答：

> 站点交付异常归因不是固定 workflow，因为每个异常的证据路径不同。比如同样是延期，有的来自设计变更，有的来自物料到货，有的来自审批卡点。系统必须根据工具返回的 observation 动态决定下一步查什么，所以更适合 Agent loop。

### Checklist 2：理解 agent 基本循环

标准循环：

```text
observe -> think -> act -> observe -> ... -> final answer
```

本地 Stage 1 代码对应：

```python
thought, action, final_answer = self.model.next_action(user_input, steps)
observation = self.tools.call(action)
steps.append(AgentStep(thought, action, observation))
```

项目映射：

| Agent loop | 异常归因项目 |
| --- | --- |
| observe | 接收异常输入、站点信息、偏差描述 |
| think | 规划要查哪些证据 |
| act | 调用进度、工单、成本、风险、巡检等工具 |
| observe | 读取工具结果，形成证据 |
| reflect | 判断证据是否足够或冲突 |
| final answer | 输出归因结论和报告 |

面试回答：

> Agent loop 的关键不是循环本身，而是 observation-driven decision。每一轮工具结果都会影响下一步动作，如果证据不足就补查，如果证据冲突就降低置信度或触发人工复核。

### Checklist 3：什么时候不该用 agent

不该用 Agent 的场景：

- 输入输出完全确定。
- 流程稳定。
- 没有工具调用。
- 没有外部信息不确定性。
- 普通脚本更快、更便宜、更可靠。

项目里也要区分：

- 简单字段计算用 script。
- 固定审批流用 workflow。
- 异常归因链路用 agent。

面试回答：

> 我不会把所有逻辑都交给 Agent。比如成本降低比例、延期天数统计、字段清洗可以用确定性代码；只有证据路径不确定、需要动态补查和判断时，才进入 Agent loop。

### Checklist 4：写一页笔记，回答为什么我的场景需要 agent

可背版本：

> 站点交付异常的难点在于根因链路不固定。异常可能来自计划变更、资源不足、物料延期、施工窗口、审批卡点、质量返工或外部依赖。人工排查需要在多个系统之间来回查证据，而且结论经常缺少可复核证据链。因此我需要一个 Agent，而不是简单 workflow。Agent 可以先根据异常输入规划检查路径，再调用工具获取证据，根据 observation 判断是否补查，最后生成带证据链和置信度的归因报告。

## 四、Stage 1: Build A Minimal Agent Loop

### Checklist 1：会用一个 LLM API 完成普通对话

你要知道普通 LLM 对话的本质：

- 输入 messages。
- 模型输出文本。
- 没有工具执行。
- 没有真实外部 observation。

普通对话适合解释和总结，但不适合独立完成异常归因，因为它没有真实证据。

面试回答：

> 普通对话只能生成文本，Agent loop 需要让模型输出结构化动作，并让程序执行工具，把真实结果再喂回模型。异常归因必须依赖证据，所以不能只靠普通 chat completion。

### Checklist 2：会让模型输出结构化 JSON

结构化 JSON 的意义：

- 程序可解析。
- 参数可校验。
- 行为可审计。
- 错误可定位。

本地代码里的结构：

```python
@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: dict[str, Any]
```

项目里的结构化动作示例：

```json
{
  "name": "query_site_milestones",
  "arguments": {
    "site_id": "SITE_001",
    "date_range": "2026-05-01..2026-05-31"
  }
}
```

面试回答：

> 结构化输出解决的是模型和程序之间的接口问题。模型不能只说“我去查一下进度”，而要输出工具名和参数，这样 harness 才能执行、记录、校验和重放。

### Checklist 3：会定义工具函数

本地 Stage 1 工具：

```python
def calculator_tool(arguments: dict[str, Any]) -> ToolResult:
    expression = str(arguments.get("expression", "")).strip()
    if not expression:
        return ToolResult(False, "Missing expression")
    value = SafeCalculator().evaluate(expression)
    return ToolResult(True, str(pretty))
```

工具设计原则：

- 输入参数明确。
- 返回结构统一。
- 失败不抛给外层，而是转成 `ToolResult(ok=False, content=...)`。
- 工具内做权限和边界限制。

你的项目工具可以这样抽象：

```python
def query_delivery_plan(arguments: dict[str, str]) -> ToolResult:
    site_id = arguments["site_id"]
    milestone = arguments.get("milestone", "")
    # 查询计划系统，返回计划时间、当前状态、延期天数
    return ToolResult(True, "...structured plan evidence...")
```

### Checklist 4：会解析 tool call / function call

解析 tool call 的过程：

1. 模型输出 tool name。
2. 模型输出 arguments。
3. 程序校验 name 是否存在。
4. 程序校验 arguments 是否满足 schema。
5. registry 调用实际函数。

本地代码：

```python
def call(self, call: ToolCall) -> ToolResult:
    spec = self._tools.get(call.name)
    if spec is None:
        return ToolResult(False, f"Unknown tool: {call.name}")
    try:
        return spec.fn(call.arguments)
    except Exception as exc:
        return ToolResult(False, f"{type(exc).__name__}: {exc}")
```

面试回答：

> 工具调用一定要通过 registry，而不是让模型直接执行。Registry 可以统一做工具发现、参数校验、异常捕获、权限控制和 trace 记录。

### Checklist 5：会执行工具，并把工具结果喂回模型

本地代码：

```python
observation = self.tools.call(action)
steps.append(AgentStep(thought, action, observation))
```

这里的 `observation` 是下一轮决策的输入。真实 LLM 场景中，会把工具结果追加到 messages 或 state 中，让模型继续判断。

项目映射：

> 工具返回的计划延期、工单阻塞、巡检异常、成本变化等信息不能只作为日志，要进入 WorkflowState 的 `tool_results` 和 `evidence_chain`，成为下一轮 reflection 和最终报告的依据。

### Checklist 6：给 agent loop 加最大步数、超时和错误处理

为什么需要：

- 防止无限循环。
- 控制成本。
- 防止外部接口卡死。
- 让失败变成可解释输出。

本地代码：

```python
for _ in range(self.max_steps):
    ...
return f"Stopped after reaching max_steps={self.max_steps}.", steps
```

项目里可以设计：

```python
MAX_STEPS = 8
MAX_TOOL_CALLS = 12
TOOL_TIMEOUT_SECONDS = 10
MIN_EVIDENCE_COUNT = 2
```

面试回答：

> 长路径 Agent 必须有预算边界。异常归因可能不断补查，如果没有 max steps、tool timeout 和停止条件，就无法控制成本和稳定性。

### Stage 1 面试高频问答

Q：Agent loop 和普通 workflow 区别是什么？

A：

> Workflow 的路径基本固定，Agent loop 的下一步依赖 observation。异常归因中，工具结果会决定是否补查、查哪个系统、是否接受结论，所以更接近 Agent。

Q：为什么不能让模型直接调用系统？

A：

> 模型输出不等于执行权限。必须由 harness 根据 tool schema、permission gate 和 registry 执行工具，才能保证安全、可审计和可回放。

Q：工具失败怎么办？

A：

> 要按失败类型处理。参数错误可以修正重试，空结果可以换查询条件，权限失败要人工确认，接口超时要记录并降级，达到预算则停止并输出不确定结论。

## 五、Stage 2: Tool Use, RAG, And Memory

### Checklist 1：会做 RAG

README 里的 RAG 链路：

```text
chunk -> embed -> retrieve -> answer with citations
```

本地代码用词频向量模拟 embedding：

```python
def chunk_text(source: str, text: str, max_chars: int = 360) -> list[Chunk]:
    ...

def search(self, query: str, top_k: int = 3) -> list[RetrievedChunk]:
    query_vector = self._vectorize(query)
    ...
```

核心概念：

- `chunk`：把文档切成可检索小块。
- `embed`：把文本转成向量。
- `retrieve`：找最相关证据。
- `answer with citations`：回答必须带来源。

项目映射：

> 异常归因中的证据不一定是文档，也可以是结构化工具结果。比如计划系统返回延期天数，工单系统返回阻塞原因，巡检系统返回现场异常。这些都要进入 evidence chain，并在报告中引用来源。

### Checklist 2：会把搜索、数据库、文件、浏览器、代码执行接成工具

工具类型：

| 工具类型 | 示例 | 项目里的可能用途 |
| --- | --- | --- |
| 搜索 | search_docs | 查历史归因案例 |
| 数据库 | query_delivery_plan | 查计划、里程碑、延期 |
| 文件 | read_report | 读取巡检报告 |
| 浏览器 | inspect_dashboard | 查看交付看板 |
| 代码执行 | calculate_delay | 计算偏差和成本 |

设计原则：

- 每个工具只做一类事。
- 参数 schema 清晰。
- 返回结构统一。
- 工具结果可追溯来源。
- 高风险工具需要权限。

项目里的工具结果结构可以这样设计：

```python
@dataclass(frozen=True)
class ToolResultRecord:
    tool_name: str
    arguments: dict[str, object]
    ok: bool
    summary: str
    raw_ref: str
    latency_ms: int
```

### Checklist 3：区分短期上下文、会话记忆、长期记忆

| 类型 | 生命周期 | 内容 | 项目例子 |
| --- | --- | --- | --- |
| 短期上下文 | 当前轮 prompt 或 state | 当前异常、最近工具结果 | 本次站点延期输入 |
| 会话记忆 | 一次任务 session | 多轮执行记录 | 本次归因 trace |
| 长期记忆 | 跨任务复用 | 已复核结论、bad case、规则 | 历史供应商延期模式 |

面试回答：

> 我会把当前任务状态放在 WorkflowState，把单次执行过程放在 trace/session，把经过复核、可复用的归因模式放进长期 memory。这样既能保证当前任务连续性，又能避免把未验证的中间日志污染长期记忆。

### Checklist 4：处理工具失败、空结果、重复调用、幻觉引用

处理策略：

| 问题 | 处理 |
| --- | --- |
| 工具失败 | 记录失败原因，按类型重试或降级 |
| 空结果 | 换查询条件或触发补查 |
| 重复调用 | 用 state 记录已调用工具和参数，避免循环 |
| 幻觉引用 | 报告只能引用 evidence_chain 中存在的证据 |

项目里可以用这些 guardrail：

```python
def has_duplicate_call(state: WorkflowState, tool: str, args: dict[str, object]) -> bool:
    return any(r.tool_name == tool and r.arguments == args for r in state.tool_results)
```

```python
def validate_report_sources(report: str, state: WorkflowState) -> bool:
    source_ids = {item.source_id for item in state.evidence_chain}
    return all(source_id in report for source_id in source_ids if source_id in report)
```

### Checklist 5：回答给出来源或证据

证据链至少包含：

- 证据来源。
- 工具名。
- 原始记录引用。
- 支持的 claim。
- 置信度。
- 是否冲突。

代码结构：

```python
@dataclass(frozen=True)
class EvidenceItem:
    evidence_id: str
    source: str
    claim: str
    supports_conclusion: str
    confidence: float
    raw_ref: str
```

项目报告不能只写：

> 主要原因是施工资源不足。

应该写：

> 主要原因判断为施工资源不足。证据包括：施工排班工具显示 5 月 12 日至 5 月 15 日现场班组缺口 2 人；巡检记录显示同周期关键工序未完成；计划系统显示该工序导致里程碑延期 3 天。因此该结论置信度为高。

### Stage 2 面试高频问答

Q：RAG 和普通搜索有什么区别？

A：

> 搜索只返回资料，RAG 还要把资料作为证据约束回答，并输出 citation。对异常归因来说，证据约束能降低模型编造结论的风险。

Q：Memory 里不应该存什么？

A：

> 不应该存未验证猜测、敏感信息、一次性中间日志和错误结论。长期记忆应保存经过复核且可复用的归因模式、bad case 和经验。

Q：怎么避免幻觉引用？

A：

> 报告生成阶段只能引用 WorkflowState.evidence_chain 中存在的 source id。引用不存在时直接失败或触发补查。

## 六、Stage 3: Study One Modern Agent Harness

### Checklist 1：读懂 agent harness 目录结构

读目录时，不要只看入口文件，要找这些模块：

- agent loop 在哪里。
- tools 在哪里注册。
- permissions 在哪里控制。
- session/state 在哪里保存。
- trace 在哪里写。
- memory 在哪里读写。
- eval 在哪里跑。
- config 在哪里管理。

本地 Stage 3 虽小，但结构完整：

```text
ToolRegistry
PermissionGate
SessionStore
DemoPolicy
Harness.run
```

### Checklist 2：找出 agent loop、tool registry、permission gate、session store、context compaction

本地代码对应：

```python
class ToolRegistry:
    ...

class PermissionGate:
    ...

class SessionStore:
    ...

class Harness:
    def run(self, task: str) -> ToolResult:
        ...
```

Context compaction 是什么：

> 长任务上下文太长时，把历史消息压缩成摘要，保留关键状态、决策、证据和未完成事项。

项目里，WorkflowState 可以看作比 messages 更稳定的 context compaction 基础。因为它天然结构化：

- abnormal_input
- execution_plan
- tool_results
- evidence_chain
- reflection_log
- final_conclusion

### Checklist 3：跑通最小示例，并加自己的工具

本地命令：

```bash
python3 practice/stage3_harness/harness_demo.py "search agent harness"
python3 practice/stage3_harness/harness_demo.py "count Agent harness manages tools and trace"
python3 practice/stage3_harness/harness_demo.py "please read file"
```

补工具时你要做：

1. 定义工具函数。
2. 注册到 ToolRegistry。
3. 在 policy 里规划 ToolCall。
4. 加权限判断。
5. 写 trace。
6. 写测试。

### Checklist 4：观察完整 trace，解释每一步为什么发生

Trace 不是流水账，而是 debug 入口。

一个好的 trace 应该回答：

- 收到什么任务。
- 规划了什么 tool call。
- 权限是否通过。
- 工具是否执行成功。
- 返回了什么 observation。
- 为什么停止。

项目 trace 应包含：

```json
{
  "event": "evidence_validated",
  "payload": {
    "claim": "关键里程碑延期由施工资源不足导致",
    "evidence_ids": ["EV-001", "EV-004"],
    "confidence": 0.82
  }
}
```

### Checklist 5：裸 agent loop 和 harness 对比

| 维度 | 裸 agent loop | Agent harness |
| --- | --- | --- |
| 工具 | 直接调用 | 通过 registry |
| 权限 | 容易遗漏 | PermissionGate |
| 状态 | messages 或局部变量 | WorkflowState / SessionStore |
| 失败 | 难复盘 | trace 可回放 |
| 扩展 | 文件越来越大 | 模块化扩展 |
| 上线 | 风险高 | 可评测、可观测 |

面试回答：

> 裸 loop 可以帮助理解原理，但真实项目要用 harness。我的工作重点就是把异常归因从“能跑的 loop”推进到“可控的 harness”，包括状态、工具、证据、反思和记录。

## 七、Stage 4: Multi-Agent Is Coordination, Not Magic

### Checklist 1：理解 planner / executor / reviewer / critic / router

角色定义：

| 角色 | 职责 | 项目映射 |
| --- | --- | --- |
| Planner | 拆任务、定计划 | 生成归因检查计划 |
| Executor | 调工具 | 查询计划、工单、巡检、成本 |
| Reviewer | 检查输出质量 | 判断证据是否支持结论 |
| Critic | 挑问题 | 发现证据冲突和遗漏 |
| Router | 分发任务 | 根据异常类型选择工具链 |

本地 Stage 4：

```python
ResearcherAgent -> WriterAgent -> ReviewerAgent -> ReviserAgent
```

项目里可以不真的拆成多个 LLM agent，也可以拆成多个模块。面试中要强调职责分离，而不是角色数量。

### Checklist 2：用 supervisor 或 graph 管理

Supervisor 的作用：

- 决定下一步调用哪个模块。
- 检查停止条件。
- 防止循环。
- 记录 trace。
- 汇总最终输出。

项目映射：

```text
Supervisor
  -> Planner
  -> ToolExecutor
  -> EvidenceChecker
  -> Reflector
  -> Reporter
```

### Checklist 3：定义职责边界、输入输出 schema、停止条件

每个模块都要有 schema：

```python
@dataclass(frozen=True)
class AttributionPlan:
    suspected_factors: list[str]
    required_tools: list[str]
    stop_criteria: list[str]
```

停止条件示例：

- 达到最少证据数。
- 关键证据已经覆盖主要假设。
- 证据冲突无法自动解决，转人工复核。
- 达到最大工具调用次数。
- 达到最大反思轮数。

### Checklist 4：处理循环、争论、任务漂移、上下文膨胀

问题和策略：

| 问题 | 策略 |
| --- | --- |
| 循环 | max rounds、duplicate call check |
| 争论 | reviewer 输出结构化 issue，而不是自由聊天 |
| 任务漂移 | state 中固定 original_task 和目标 |
| 上下文膨胀 | WorkflowState 摘要和 evidence id 引用 |

### Checklist 5：判断什么时候单 agent 更好

单 agent 更好的情况：

- 任务短。
- 工具少。
- 失败成本低。
- 不需要复杂审核。

多 agent 或多模块更好的情况：

- 长任务。
- 证据多。
- 需要质量审核。
- 需要不同专业职责。
- 需要报告生成和复核分离。

面试回答：

> 我不会为了多 agent 而多 agent。异常归因项目可以先用单 Agent + 多模块 harness 实现，把 planner、executor、evidence checker、reflector、reporter 职责拆清楚。只有当职责复杂到需要独立上下文时，再升级成多 agent。

## 八、Stage 5: Skills, Protocols, And Capability Packaging

### Checklist 1：Skill 和 Tool 的区别

Tool 是动作接口，Skill 是方法包。

项目例子：

- Tool：`query_site_plan(site_id)`
- Skill：`site_delivery_attribution_skill`

Skill 里可以写：

- 什么场景触发。
- 如何拆任务。
- 需要哪些工具。
- 如何判断证据充分。
- 报告模板。
- 验收标准。

### Checklist 2：Skill 和 Prompt 的区别

Prompt 通常是一次性指令。Skill 是可版本化、可复用、可测试的能力包。

面试回答：

> Prompt 更像临时说明，Skill 更像操作手册。我的项目里，异常归因流程可以沉淀为 skill，包括证据检查步骤、补查规则、报告模板和验收标准，这样不同项目复用时更稳定。

### Checklist 3：Skill 和 MCP 的区别

MCP 解决连接问题，Skill 解决怎么做的问题。

项目类比：

- MCP：统一连接项目管理系统、工单系统、监控数据。
- Skill：告诉 Agent 遇到站点延期如何查证据、如何归因、如何出报告。

### Checklist 4：Claude Code Skills 和 OpenClaw Skills 的文件结构

不需要背实现，但要知道标准 skill 包通常包含：

```text
SKILL.md
templates/
scripts/
examples/
tests/
```

本地 Stage 5：

```text
practice/stage5_skills_protocols/skills/research_summary/SKILL.md
practice/stage5_skills_protocols/skills/research_summary/templates/summary.md
```

### Checklist 5：写一个最小 SKILL.md

你的项目 skill 可以这样写：

```markdown
Name: site-delivery-attribution
Description: Diagnose site delivery abnormalities with evidence-backed attribution.

When to use:
- A site delivery milestone is delayed or at risk.
- The user asks for root cause analysis with evidence.

Steps:
1. Parse abnormal input.
2. Build attribution plan.
3. Query delivery plan, ticket, inspection, and cost tools.
4. Validate evidence chain.
5. Trigger reflection if evidence is missing or conflicting.
6. Generate attribution report.

Checks:
- must include abnormal input
- must include evidence chain
- must include reflection decision
- must include final conclusion
- must include confidence and follow-up action
```

### Checklist 6：给 skill 加脚本或模板

报告模板：

```markdown
# 站点交付异常归因报告

## 异常概述
{{abnormal_summary}}

## 执行计划
{{execution_plan}}

## 证据链
{{evidence_chain}}

## 反思补查
{{reflection_log}}

## 归因结论
{{final_conclusion}}

## 后续建议
{{next_actions}}
```

### Checklist 7：smoke test

Smoke test 不追求覆盖所有情况，只证明 skill 对典型任务有效：

```python
def test_site_delivery_attribution_skill_outputs_required_sections():
    report = run_skill(sample_abnormal_input)
    assert "证据链" in report
    assert "归因结论" in report
    assert "反思补查" in report
```

## 九、Stage 6: Browser And Computer-Use Agents

### Checklist 1：browser agent 和普通 API tool 的区别

API tool：

- 输入输出稳定。
- schema 明确。
- 失败类型相对可控。

Browser agent：

- 页面结构可能变化。
- 加载状态不稳定。
- 弹窗、登录、权限会影响操作。
- 需要 DOM、截图和动作日志。

项目映射：

> 如果交付数据来自 Web 看板或项目管理后台，browser agent 需要记录打开页面、筛选条件、提取字段、截图证据，并对任何提交、修改、导出操作设置权限边界。

### Checklist 2：用 Playwright 或 browser-use 做网页观察和点击

本地 Stage 6 用 HTMLParser 模拟：

```python
parser = PageParser(path.as_uri())
parser.feed(html)
```

真实 browser agent 会多：

- `page.goto(url)`
- `page.locator(...)`
- `page.screenshot(...)`
- `page.text_content(...)`
- `page.click(...)`

### Checklist 3：安全限制

必须限制：

- 不登录敏感账号。
- 不绕过平台规则。
- 不自动提交外部影响动作。
- 不删除或发布内容。
- 不导出敏感数据到不安全位置。

项目面试回答：

> 对交付后台这类系统，Agent 可以读取和汇总信息，但修改状态、提交结论、发送通知等动作必须人工确认。权限控制应该放在 harness，不应该只靠模型自觉。

### Checklist 4：处理页面变化、弹窗、加载失败、元素定位失败

策略：

- 等待页面加载。
- DOM selector 失败时改用文本定位。
- 截图辅助判断。
- 重试有上限。
- 失败写 trace。
- 关键证据缺失时触发 reflection。

### Checklist 5：记录截图、DOM、动作日志

项目证据可以包括：

- 页面 URL。
- 筛选条件。
- 截图路径。
- DOM 提取字段。
- 操作时间。
- 工具版本。

报告中引用时写：

> 证据来源：交付看板截图 `screenshot_20260630_001.png`，筛选条件为站点 A、里程碑 B、时间范围 C。

## 十、Stage 7: Evaluation, Observability, And Safety

### Checklist 1：固定测试集

固定测试集应包含：

- 正常延期归因。
- 证据不足。
- 证据冲突。
- 工具失败。
- 空结果。
- 多原因归因。
- 需要人工复核。
- 历史 bad case。

异常归因 eval case 示例：

```json
{
  "id": "site_delay_material_shortage_001",
  "abnormal_input": "站点 A 主设备安装延期 4 天",
  "expected_contains": "物料到货延期",
  "category": "root_cause_attribution"
}
```

### Checklist 2：记录成功率、失败原因、工具调用次数、成本、延迟

指标：

| 指标 | 意义 |
| --- | --- |
| success_rate | 归因是否命中预期 |
| evidence_coverage | 结论是否有足够证据 |
| tool_call_count | 成本和效率 |
| latency | 用户等待时间 |
| reflection_rate | 补查触发比例 |
| human_review_rate | 需要人工复核比例 |
| bad_case_count | 失败样本数 |

项目成果 37.5% 可以这样讲：

> 试点阶段不只看模型回答是否合理，也看业务指标。两个重点项目完成初步落地验证和两个版本上线后，通过自动巡检、证据聚合和归因报告减少人工排查时间，驱动试点项目交付成本降低 37.5%。

如果被追问成本怎么算，要如实说明口径：

> 这个 37.5% 是试点项目口径，主要来自人工排查时长、问题定位周期和重复沟通成本的下降。具体计算口径要按项目内部统计标准解释。

### Checklist 3：看 trace 定位失败

失败定位表：

| 失败表现 | 可能原因 | 看哪里 |
| --- | --- | --- |
| 结论错 | plan 漏查或 evidence 误判 | execution_plan、evidence_chain |
| 没有证据 | retrieval/tool 空结果 | tool_results |
| 引用不存在 | report hallucination | report source validation |
| 一直补查 | stopping condition 弱 | reflection_log |
| 成本高 | tool 调用过多 | tool_call_count |
| 记忆误导 | memory 污染 | memory_records |

### Checklist 4：危险工具人工确认

异常归因项目中的高风险动作：

- 修改项目状态。
- 提交归因结论到正式系统。
- 发送通知给客户或管理层。
- 关闭工单。
- 修改计划。
- 删除或覆盖原始证据。

这些必须 PermissionGate。

### Checklist 5：prompt injection、data exfiltration、tool abuse

项目风险：

- 工单备注里可能含恶意指令。
- 外部文档可能诱导 Agent 忽略规则。
- 工具可能被滥用查询非授权站点。
- 报告可能泄露敏感项目数据。

防护：

- 工具参数做权限过滤。
- 文档内容只作为数据，不作为指令。
- 报告脱敏。
- 高风险动作人工确认。
- trace 审计。

### Checklist 6：回归测试

每次改 prompt、工具或规则后都要跑：

```bash
python3 -m unittest discover -s tests
python3 practice/stage7_eval_observability/eval_runner.py
```

项目中对应：

> 每个版本上线前固定跑异常归因 eval 集，观察命中率、证据覆盖率、人工复核率和 bad case 类型是否退化。

## 十一、Stage 8: Ship A Real Agent

### Checklist 1：明确用户、任务、成功标准

你的项目：

| 维度 | 内容 |
| --- | --- |
| 用户 | 交付经理、项目经理、风险巡检人员、运维/交付管理团队 |
| 任务 | 自动发现站点交付偏差，追踪关键影响因素，生成证据链报告 |
| 成功标准 | 归因结论可解释、证据可追溯、人工排查成本下降、bad case 可复盘 |

### Checklist 2：日志、trace、错误重试、超时、成本上限

上线标准：

- 每次运行有 run_id。
- 每个工具调用有 tool_call_id。
- 每条证据有 evidence_id。
- 每次 reflection 有 reason。
- 每次失败有 failure_category。
- 工具有 timeout。
- 任务有 max_steps。
- 报告生成有 source validation。

### Checklist 3：权限边界和人工确认机制

权限边界：

- 只读工具默认可自动执行。
- 写入、提交、通知、关闭类工具必须人工确认。
- 非授权站点数据不可访问。
- 敏感字段脱敏。

### Checklist 4：部署方式

可选形态：

- CLI：适合内部验证。
- Web app：适合业务方使用。
- Slack/企微 bot：适合消息入口。
- GitHub Action：适合代码类任务，不一定适合你的业务。
- 后台任务：适合定时巡检。

你的项目更像：

> 后台巡检任务 + Web/平台报告入口 + 人工复核闭环。

### Checklist 5：README

项目 README 应包含：

- 背景。
- 用户。
- 功能。
- 架构。
- 运行方式。
- 工具配置。
- 数据权限。
- 示例输入输出。
- eval 方法。
- 已知限制。
- bad case 回流方式。

## 十二、Project Ladder 对你的意义

README 的 Project Ladder 是从小项目走向生产 harness 的路线。你可以这样理解：

| Level | 项目 | 对你的价值 |
| --- | --- | --- |
| 1 Calculator Agent | 最小 tool call | 理解 ToolCall 和 ToolResult |
| 2 Web Research Agent | 搜索和引用 | 理解证据检索和报告生成 |
| 3 PDF QA Agent | RAG | 理解 chunk、retrieval、citation |
| 4 Coding Review Agent | 风险排序 | 类似异常风险识别 |
| 5 Browser Agent | 页面观察 | 交付看板可用类似能力 |
| 6 Claude Code-like Nano Agent | harness | 对应你做的 Agent Harness |
| 7 OpenClaw-like Gateway | 长运行 | 对应后台巡检和消息入口 |
| 8 Reusable Skill Pack | skill | 对应异常归因 skill |
| 9 Multi-Agent Writer | 协作 | 对应 planner/checker/reporter |
| 10 Personal Agent | memory | 对应历史归因记忆 |
| 11 Production Harness | eval/trace/CI | 对应上线和两个版本迭代 |

## 十三、Learning Principles 面试化理解

### Build first, then read deeper

先写最小可运行版本，再读框架和论文。你的本地 `practice/` 就是这样设计的。

### Prefer small reliable agents over impressive demos

面试表达：

> 我更关注可复现和可评测，而不是一次演示很炫。异常归因项目优先保证证据链、trace、权限和失败复盘。

### Use tools with strict schemas

严格 schema 能减少参数错误和不可控动作。

### Add evals before you add more agents

不要急着加多 agent。先用 eval 确定单 agent 或单 harness 的失败点。

### Trace every important run

所有重要运行都要能回放。

### Treat multi-agent as a coordination problem

多 agent 本质是职责边界、schema 和 supervisor。

### Keep humans in the loop for risky actions

写入、通知、关闭、发布等动作必须人工确认。

### Respect platform rules, copyrights, and data access boundaries

业务系统数据访问必须授权，报告要脱敏。

## 十四、你的项目全面梳理

项目名称：

> 异常巡检与归因 Agent：站点交付异常的证据链诊断与报告生成

### 1. 项目背景

业务问题：

- 站点交付过程复杂，涉及计划、资源、物料、施工、验收、工单和成本。
- 异常发现依赖人工巡检，时效性差。
- 根因追踪分散在多个系统，证据链不清晰。
- 报告生成依赖人工经验，复核和复盘成本高。
- 历史 bad case 难以沉淀，类似问题重复排查。

项目目标：

- 自动识别交付偏差。
- 追踪关键影响因素。
- 形成证据链。
- 输出可解释归因报告。
- 支撑问题闭环、风险感知和成本优化。

### 2. 为什么适合 Agent

因为异常归因具备典型长路径复杂任务特征：

- 路径不固定。
- 证据来源多。
- 需要动态补查。
- 结论需要解释。
- 有失败复盘和记忆沉淀需求。

一句话：

> 这不是固定审批流，而是 observation-driven 的证据诊断任务。

### 3. 总体架构

```text
异常输入
  -> Planner 任务规划
  -> Tool Executor 工具调用
  -> Evidence Checker 证据校验
  -> Reflector 反思补查
  -> Reporter 报告生成
  -> Memory / Bad Case Store 记忆沉淀
```

核心闭环：

```text
observe abnormal input
  -> plan attribution tasks
  -> call tools
  -> collect observations
  -> validate evidence
  -> reflect if missing/conflicting
  -> generate conclusion
  -> persist trace and memory
```

### 4. WorkflowState 设计

WorkflowState 是你的项目核心亮点。它解决长任务上下文连续性和可恢复性。

建议结构：

```python
@dataclass
class WorkflowState:
    run_id: str
    abnormal_input: dict[str, object]
    execution_plan: list[dict[str, object]]
    tool_results: list[ToolResultRecord]
    evidence_chain: list[EvidenceItem]
    reflection_log: list[ReflectionDecision]
    final_conclusion: dict[str, object] | None
    bad_case_samples: list[dict[str, object]]
    memory_records: list[dict[str, object]]
    status: str
```

字段解释：

| 字段 | 作用 | 面试讲法 |
| --- | --- | --- |
| run_id | 标识一次运行 | 方便 trace、复盘和回放 |
| abnormal_input | 原始异常输入 | 防止任务漂移 |
| execution_plan | 执行计划 | 让任务拆解可见 |
| tool_results | 工具结果 | 保留 observation |
| evidence_chain | 证据链 | 支撑结论可解释 |
| reflection_log | 反思记录 | 记录为什么补查 |
| final_conclusion | 最终结论 | 和证据绑定 |
| bad_case_samples | 失败样本 | 支撑复盘和评测 |
| memory_records | 可复用记忆 | 支撑后续类似归因 |
| status | 任务状态 | 支撑恢复和监控 |

面试回答：

> WorkflowState 的价值是把长链路上下文显式化。它不是简单 messages，而是把异常输入、计划、工具结果、证据、反思和结论结构化承载。这样每一步都能追踪，失败能复盘，中断能恢复，报告能校验来源。

### 5. 任务规划

输入：

```json
{
  "site_id": "SITE_A",
  "abnormal_type": "milestone_delay",
  "description": "主设备安装较计划延期 4 天",
  "detected_at": "2026-06-30"
}
```

输出计划：

```json
[
  {
    "step": 1,
    "goal": "确认计划偏差",
    "tool": "query_delivery_plan",
    "expected_evidence": "计划时间、实际时间、延期天数"
  },
  {
    "step": 2,
    "goal": "排查物料因素",
    "tool": "query_material_status",
    "expected_evidence": "到货时间、缺料记录"
  },
  {
    "step": 3,
    "goal": "排查施工和资源因素",
    "tool": "query_site_worklog",
    "expected_evidence": "施工日志、班组资源、阻塞记录"
  }
]
```

面试回答：

> Planner 不直接给结论，而是先把异常转成可执行检查计划。计划里会明确要查什么、用哪个工具、期望拿到什么证据，这样后续 evidence checker 才能判断证据是否充分。

### 6. 工具调用

可能工具：

| 工具 | 作用 |
| --- | --- |
| `query_delivery_plan` | 查询计划里程碑和延期 |
| `query_ticket_system` | 查询阻塞工单 |
| `query_material_status` | 查询物料到货和缺料 |
| `query_site_worklog` | 查询施工日志和现场记录 |
| `query_quality_records` | 查询质量返工和验收问题 |
| `query_cost_records` | 查询成本和人力变化 |
| `search_similar_cases` | 查询历史相似 bad case |

工具记录结构：

```python
@dataclass(frozen=True)
class ToolResultRecord:
    call_id: str
    tool_name: str
    arguments: dict[str, object]
    ok: bool
    summary: str
    evidence_candidates: list[str]
    raw_ref: str
    latency_ms: int
```

面试回答：

> 工具结果不是直接拼到报告里，而是先结构化写入 WorkflowState.tool_results。后续 evidence checker 再从中抽取可支持结论的 evidence item。

### 7. 证据校验

证据校验要回答：

- 证据是否来自可信来源。
- 证据是否支持某个 claim。
- 是否有反向证据。
- 证据是否足够。
- 置信度是多少。

结构：

```python
@dataclass(frozen=True)
class EvidenceItem:
    evidence_id: str
    source_tool: str
    claim: str
    raw_ref: str
    confidence: float
    supports: str
```

示例：

```json
{
  "evidence_id": "EV-003",
  "source_tool": "query_material_status",
  "claim": "主设备到货晚于计划 3 天",
  "raw_ref": "material_order#MO-7788",
  "confidence": 0.91,
  "supports": "物料延期是主设备安装延期的主要因素"
}
```

面试回答：

> 证据校验是防止模型胡编的关键。最终结论必须能反查到 evidence_id，报告不能引用 state 中不存在的来源。证据不足时不会强行下结论，而是触发 reflection。

### 8. Self-Reflection 补查

触发条件：

- 工具失败。
- 空结果。
- 证据不足。
- 证据冲突。
- 结论置信度低。
- 报告缺少关键字段。
- 命中历史 bad case。

结构：

```python
@dataclass(frozen=True)
class ReflectionDecision:
    reason: str
    decision: str
    follow_up_tool: str | None
    follow_up_arguments: dict[str, object]
```

示例：

```json
{
  "reason": "计划延期证据存在，但缺少物料和施工侧证据，无法确认主因",
  "decision": "补查物料到货和施工日志",
  "follow_up_tool": "query_material_status",
  "follow_up_arguments": {
    "site_id": "SITE_A",
    "milestone": "main_equipment_installation"
  }
}
```

面试回答：

> Self-Reflection 不是让模型泛泛反省，而是基于状态做结构化检查：证据是否足够、是否冲突、是否达到停止条件。如果没达到，就生成补查动作并写入 reflection_log。

### 9. 报告生成

报告结构：

```markdown
# 站点交付异常归因报告

## 1. 异常概述
- 站点：
- 异常类型：
- 偏差：

## 2. 执行计划
- 已检查：
- 未检查：

## 3. 关键证据链
- EV-001：
- EV-002：

## 4. 归因结论
- 主因：
- 次因：
- 置信度：

## 5. 反思补查记录
- 为什么补查：
- 补查结果：

## 6. 后续建议
- 短期动作：
- 长期优化：
```

报告生成规则：

- 只能引用 evidence_chain 中的证据。
- 不足时输出不确定性。
- 冲突时说明冲突。
- 给出下一步建议。
- 保留可复核来源。

### 10. 记忆和 bad case 沉淀

Memory 记录：

```python
@dataclass(frozen=True)
class AttributionMemory:
    pattern_id: str
    abnormal_type: str
    root_cause: str
    evidence_pattern: list[str]
    resolution: str
    verified: bool
```

Bad case 记录：

```python
@dataclass(frozen=True)
class BadCase:
    case_id: str
    input_summary: str
    wrong_output: str
    failure_category: str
    root_reason: str
    fix_action: str
```

面试回答：

> 我们把执行记录和记忆分开。执行记录用于单次复盘，bad case 用于失败分析，长期 memory 只沉淀经过复核的归因模式。这样可以避免把错误结论直接污染后续任务。

### 11. 两个版本上线可以怎么讲

版本 1：

- 跑通核心链路。
- 支持异常输入解析。
- 支持基础工具调用。
- 支持证据链报告。
- 支持 trace 记录。

版本 2：

- 增加 WorkflowState 完整字段。
- 增强 reflection 补查。
- 增加 bad case 记录。
- 增加评测闭环。
- 优化报告模板和业务字段。

如果面试官追问：

> 两个版本最大的差异是什么？

回答：

> 第一版重点是跑通从异常输入到归因报告的主链路，证明 Agent 能完成基本任务。第二版重点是稳定性和可复盘，强化 WorkflowState、反思补查、bad case 记录和评测闭环，让系统从 demo 变成可迭代的业务工具。

### 12. 37.5% 成本降低怎么讲

建议表达：

> 在两个重点项目试点中，系统把原本分散在多个系统、依赖人工经验的异常排查流程，转成自动巡检、证据聚合和报告生成。通过减少人工查证时间、缩短问题定位周期、降低重复沟通成本，试点项目交付成本降低 37.5%。

可能追问：这个数字怎么来的？

回答模板：

> 口径主要基于试点项目上线前后的交付异常处理成本对比，包括人工排查耗时、问题定位周期、重复沟通和返工成本等。这个数字是试点范围内的结果，不代表所有项目泛化效果，后续需要通过更多项目和固定 eval 指标持续验证。

## 十五、项目面试问题全集

### 项目背景类

Q：为什么要做异常巡检与归因 Agent？

A：

> 因为站点交付异常涉及多系统、多因素，人工发现滞后，根因链路不清晰。Agent 可以把异常输入、工具证据、反思补查和报告生成串成闭环，提升风险感知和复盘效率。

Q：为什么不用普通规则系统？

A：

> 规则系统适合固定条件判断，但异常归因路径不固定。不同站点、不同里程碑、不同证据组合会导致不同检查路径。我们保留确定性规则做计算和校验，把动态规划、补查和报告生成交给 Agent loop。

Q：为什么不用普通 workflow？

A：

> Workflow 适合固定流程，而归因任务下一步依赖工具观察结果。比如查到物料延期后要补查供应商和到货记录，查到施工日志异常后要补查资源排班，所以需要 observation-driven loop。

### Agent Loop 类

Q：你的 Agent loop 怎么设计？

A：

> 主链路是异常输入观察、任务规划、工具调用、证据校验、反思补查和报告生成。每轮工具结果都会写入 WorkflowState，作为下一轮判断依据。达到证据充分、预算耗尽或需要人工复核时停止。

Q：停止条件有哪些？

A：

> 包括证据覆盖达到阈值、主因置信度达到阈值、关键工具都已查完、证据冲突需要人工复核、达到最大步数或最大工具调用次数。

Q：工具失败怎么办？

A：

> 先记录失败类型。如果是参数错误，修正参数重试；如果是空结果，改查询条件或补查其他工具；如果是权限问题，进入人工确认；如果达到预算，则输出不确定结论和缺失证据。

### WorkflowState 类

Q：WorkflowState 解决了什么问题？

A：

> 解决长链路上下文丢失、工具结果散落、证据不可追溯和失败不可复盘的问题。它把异常输入、计划、工具结果、证据链、反思决策和最终结论统一承载。

Q：为什么不用 messages？

A：

> Messages 是对话历史，不适合稳定承载结构化字段。WorkflowState 有明确 schema，可以测试、持久化、恢复、回放和做报告来源校验。

Q：状态可恢复怎么做？

A：

> 每次关键事件后持久化 WorkflowState，包括当前步骤、已执行工具、证据链和 reflection_log。任务中断后可以从 status 和 last_step 恢复，而不是重新开始。

### 证据链类

Q：怎么保证结论可信？

A：

> 最终结论必须绑定 evidence_id，每条 evidence 有来源工具、raw_ref、claim 和 confidence。报告生成阶段只能引用 evidence_chain 中已有证据，证据不足时触发补查或输出不确定性。

Q：证据冲突怎么办？

A：

> 先记录冲突双方和来源，降低置信度；再触发 reflection 补查更权威数据源。如果仍然冲突，就标记为需要人工复核，而不是强行给确定结论。

Q：幻觉引用怎么防？

A：

> 做 source validation。报告里的引用必须能在 WorkflowState.evidence_chain 找到；找不到则报告生成失败或触发补查。

### Reflection 类

Q：Self-Reflection 是怎么实现的？

A：

> 它不是自由反思，而是结构化检查。系统检查证据是否足够、是否冲突、工具是否失败、结论置信度是否达标。如果不满足，就生成补查决策，写入 reflection_log，并继续调用工具。

Q：什么时候停止反思？

A：

> 达到证据阈值、达到最大反思次数、关键工具已查完、冲突无法自动解决或需要人工复核时停止。

### Memory 类

Q：记忆保存什么？

A：

> 保存经过复核的归因模式、典型 bad case、工具结果摘要、反思经验和最终结论。不保存未验证猜测和敏感原始数据。

Q：记忆怎么复用？

A：

> 当新异常和历史模式相似时，memory 可以提供候选归因方向和建议补查工具，但不能直接替代当前证据。当前结论仍然必须由本次 evidence_chain 支撑。

Q：错误记忆怎么办？

A：

> memory 要有 verified 标记和版本。bad case 发现错误后，更新或禁用对应记忆，并在 eval 中加入回归样本。

### Eval 类

Q：怎么证明 Agent 变好了？

A：

> 用固定 eval 集比较版本前后的归因命中率、证据覆盖率、人工复核率、工具调用次数、延迟和 bad case 类型。不能只靠 demo。

Q：bad case 怎么分析？

A：

> 回放 WorkflowState 和 trace，定位失败来自计划、工具、证据、reflection、memory 还是报告生成。然后把 bad case 加入 eval 集，防止后续版本回归。

### Safety 类

Q：哪些动作需要人工确认？

A：

> 修改项目状态、关闭工单、发送通知、提交正式结论、修改计划、删除证据、导出敏感数据等都需要人工确认。

Q：怎么防 prompt injection？

A：

> 外部文档和工单内容只当数据，不当指令。系统指令和工具权限由 harness 控制，工具参数做权限过滤，报告做脱敏。

### 业务成果类

Q：成本降低 37.5% 你贡献在哪里？

A：

> 我参与的部分主要在 Agent Harness 核心链路、WorkflowState 上下文管理、工具结果和证据链结构化、反思日志和 bad case 记录。这些能力减少了人工跨系统查证和重复复盘成本，是成本降低的重要支撑。

Q：如果推广到更多项目，最大风险是什么？

A：

> 最大风险是数据源差异、工具稳定性、历史记忆泛化和权限边界。需要标准化工具 schema、补充 eval 集、建立人工复核闭环，并对不同项目逐步灰度。

## 十六、你最终要背下来的 3 个版本

### 30 秒版本

> 我做的是异常巡检与归因 Agent，解决站点交付异常依赖人工排查、根因链路不清晰的问题。系统通过闭环 Agent Loop 完成任务规划、工具调用、证据校验、Self-Reflection 补查和报告生成。我主要参与 Agent Harness 核心链路和 WorkflowState 设计，把异常输入、计划、工具结果、证据链、反思决策和结论统一承载，同时沉淀执行记录、bad case 和归因记忆。试点两个重点项目并完成两个版本上线，交付成本降低 37.5%。

### 1 分钟版本

> 这个项目面向站点交付异常场景。过去异常发现和根因追踪依赖人工在多个系统之间查证据，链路慢且不可复核。我们构建了异常巡检与归因 Agent，把流程拆成任务规划、工具调用、证据校验、反思补查和报告生成。我的重点是 Agent Harness 核心链路和 WorkflowState 上下文管理。WorkflowState 统一记录异常输入、执行计划、工具结果、证据链、reflection 决策和最终结论，使多轮执行中状态不丢、证据可追溯、失败可复盘。我们还沉淀工具调用结果、反思日志、bad case 和归因结论，用于评测闭环和记忆复用。该能力已在两个重点项目试点并完成两个版本上线，交付成本降低 37.5%。

### 3 分钟版本

> 项目背景是站点交付过程复杂，异常可能来自计划、物料、施工、审批、质量或外部依赖。原先依赖人工巡检和排查，根因链路不清晰，报告也难复核。我们做了一个异常巡检与归因 Agent，本质是面向长路径复杂任务的 Agent Harness。主链路是 observe 异常输入，然后 planner 生成归因检查计划，executor 调用计划、工单、物料、施工日志等工具，evidence checker 把工具结果转成证据链，reflector 判断证据是否足够或冲突，如果不足就补查，最后 reporter 生成带证据来源的归因报告。
>
> 我负责和参与的重点是上下文管理和执行记录。我们设计 WorkflowState 作为长任务状态容器，统一承载 abnormal input、execution plan、tool results、evidence chain、reflection log 和 final conclusion。这样做的好处是每一步都结构化可追踪，而不是散落在 prompt 或日志里。工具失败、空结果、证据冲突都会被记录，并驱动 reflection 决策。最终报告只能引用 evidence_chain 中存在的证据，降低幻觉结论风险。
>
> 另外，我们把工具结果、反思日志、bad case 和归因结论沉淀下来，用于任务复盘、故障诊断、eval 回归和记忆复用。两个版本上线中，第一版跑通主链路，第二版强化 WorkflowState、reflection、bad case 和评测闭环。试点两个重点项目后，通过减少人工查证、缩短定位周期和降低重复沟通成本，交付成本降低 37.5%。

## 十七、最后自检清单

你应该能回答：

1. 为什么站点交付异常归因适合 Agent，而不是 workflow？
2. Agent loop 在项目里每一步对应什么？
3. ToolCall、ToolResult、ToolRegistry 分别是什么？
4. WorkflowState 包含哪些字段，为什么比 messages 更合适？
5. 证据链怎么设计，怎么防止幻觉引用？
6. Reflection 什么时候触发，什么时候停止？
7. Memory 和 trace 有什么区别？
8. Bad case 怎么沉淀，怎么进入 eval？
9. 如何处理工具失败、空结果、证据冲突？
10. 哪些工具需要人工确认？
11. 如何防 prompt injection 和数据越权？
12. 两个版本上线分别解决什么问题？
13. 37.5% 成本降低的业务口径怎么解释？
14. 如果推广到更多项目，风险和改进方向是什么？
15. README 的 Stage 0-8 如何映射到你的项目？

如果这些问题你能结合本地代码和项目字段讲清楚，这个项目就能从“简历上的一句话”变成一套完整、可信、可追问的工程故事。

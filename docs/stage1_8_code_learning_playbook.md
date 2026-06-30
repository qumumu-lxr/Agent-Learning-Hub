# Stage 1-8 代码组件精读与项目映射手册

这份资料用于直接配合代码编辑器阅读本地 `practice/` 目录。它会把每个 Stage 拆成：

- 这一阶段解决什么工程问题。
- 核心组件有哪些。
- 关键代码长什么样。
- 每个组件的职责、输入输出、设计意图是什么。
- 面试时应该如何表达。
- 最后如何迁移到你的项目：【异常巡检与归因 Agent：站点交付异常的证据链诊断与报告生成】。

推荐阅读顺序：

1. 先打开对应 stage 的 Python 文件。
2. 对照本文的组件表看类和函数。
3. 在代码编辑器里跳转 dataclass、核心方法、测试断言。
4. 用本文最后的项目映射，把每个技术点转换成你的项目表达。

## 总览：Stage 1-8 在学什么

| Stage | 本地代码 | 核心主题 | 你必须掌握的工程问题 |
| --- | --- | --- | --- |
| Stage 0 | `practice/stage0_agent_mindset/agent_mindset.py` | Agent 判断方法 | 什么任务需要 agent，什么任务不该用 agent |
| Stage 1 | `practice/stage1_minimal_agent/minimal_agent.py` | Minimal Agent Loop | observe、think、act、observation、trace、stop condition 如何闭环 |
| Stage 2 | `practice/stage2_rag_memory/rag_memory.py` | RAG + Memory | 如何先找证据再回答，如何区分 trace 和 memory |
| Stage 3 | `practice/stage3_harness/harness_demo.py` | Agent Harness | 如何管理工具、权限、session、trace、预算和执行过程 |
| Stage 4 | `practice/stage4_multi_agent/multi_agent_pipeline.py` | Multi-Agent Coordination | 多 agent 的本质是职责边界、schema、supervisor、停止条件 |
| Stage 5 | `practice/stage5_skills_protocols/skill_runner.py` | Skills / Protocols | skill 如何封装流程知识、模板和验收标准 |
| Stage 6 | `practice/stage6_browser_agent/browser_info_agent.py` | Browser Agent | browser agent 如何观察 DOM、提取信息、记录动作 |
| Stage 7 | `practice/stage7_eval_observability/eval_runner.py` | Evaluation / Observability | 如何用 eval、trace、failure category 证明 agent 可靠 |
| Stage 8 | `practice/stage8_ship_real_agent/personal_research_agent.py` | Ship Real Agent | 如何把前面能力组合成可交付、可复现、可测试的 agent |

你可以把整条路线记成一句话：

> Stage 0 先判断该不该用 Agent；Stage 1 搭最小 loop；Stage 2 加证据和记忆；Stage 3 把 loop 工程化成 harness；Stage 4 学职责协作；Stage 5 学能力复用；Stage 6 学页面观察；Stage 7 学评测和可观测；Stage 8 学交付。

## Stage 0: Agent Mindset

对应代码：`practice/stage0_agent_mindset/agent_mindset.py`

### 这一阶段解决什么问题

Stage 0 解决的是“什么时候该用 Agent”的判断问题。很多项目失败不是因为模型不强，而是因为把本来应该用 script 或 workflow 的任务硬做成 agent，反而引入不可控性。

你要能区分：

| 类型 | 特点 | 例子 | 是否需要 Agent |
| --- | --- | --- | --- |
| Script | 输入输出确定，路径固定 | 清洗字段、批量改名、简单统计 | 通常不需要 |
| Workflow | 固定流程编排 | 审批、定时报表、表单流转 | 通常不需要 |
| Chatbot | 解释、翻译、总结、对话 | 概念解释、润色、普通问答 | 不一定需要 |
| Agent | 下一步依赖观察结果 | 调研、debug、异常归因、证据补查 | 适合 |
| Multi-Agent | 多职责协作 | research -> write -> review -> revise | 复杂任务才需要 |

### 核心组件

| 组件 | 作用 | 关键点 |
| --- | --- | --- |
| `AGENT_KEYWORDS` | 判断任务是否具备 agent 特征 | 包含多轮、迭代、规划、搜索、证据、工具等关键词 |
| `WORKFLOW_KEYWORDS` | 判断是否更像固定流程 | 审批、固定流程、表单、每日、定时 |
| `SCRIPT_KEYWORDS` | 判断是否更像确定性脚本 | 转换、清洗、批量、计算、统计 |
| `CHATBOT_KEYWORDS` | 判断是否更像普通对话 | 解释、是什么、翻译、润色 |
| `RISK_KEYWORDS` | 判断是否涉及高风险动作 | 删除、支付、提交、发送、发布 |
| `AgentDecision` | 分类结果的数据结构 | 输出推荐模式、不确定性、人审需求、第一步设计 |
| `classify_task()` | 核心分类函数 | 根据关键词分数决定推荐形态 |
| `_score()` | 简单打分函数 | 统计命中的关键词数量 |

### 关键代码 1：分类结果结构

```python
@dataclass(frozen=True)
class AgentDecision:
    task: str
    recommended_pattern: str
    uncertainty_sources: list[str]
    human_approval_needed: list[str]
    first_design_step: str
```

这段代码的重点不是 dataclass 本身，而是它把“是否需要 agent”的判断拆成了可解释字段：

- `task`：原始任务，保证后续判断可以追溯。
- `recommended_pattern`：推荐用 agent、workflow、script 还是 chatbot。
- `uncertainty_sources`：为什么有不确定性。
- `human_approval_needed`：是否有高风险动作。
- `first_design_step`：如果要实现，第一步应该设计什么。

面试表达：

> 判断任务是否需要 Agent 时，我不会只看有没有大模型，而是看任务路径是否不确定、下一步是否依赖工具结果、是否存在高风险动作。这个判断结果应该结构化输出，方便复盘和后续设计。

### 关键代码 2：任务模式判断

```python
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
```

这段代码体现了一个重要工程判断：agent 不是默认选项。只有当任务明显具备“根据结果动态决策”的特征时，才推荐 agent。

项目映射：

> 站点交付异常归因适合 Agent，因为根因路径不固定。系统必须根据计划、工单、物料、巡检等工具返回的 observation 决定下一步查什么，而不是走一条固定流程。

### 关键代码 3：不确定性和权限判断

```python
if score_agent:
    uncertainty_sources.append("下一步动作依赖工具观察结果")
if any(word in task for word in {"搜索", "检索", "调研", "浏览"}):
    uncertainty_sources.append("外部信息质量和来源不确定")
if any(word in task for word in {"修复", "debug", "报错"}):
    uncertainty_sources.append("失败原因需要试探和验证")

approvals = [word for word in RISK_KEYWORDS if word in task]
```

这段代码提醒你：Agent 设计必须同时考虑“不确定性”和“风险”。

对你的项目来说：

- 不确定性：交付延期原因可能来自物料、资源、审批、质量、外部依赖。
- 风险：如果 Agent 自动关闭工单、提交正式结论、修改项目状态，就必须人工确认。

## Stage 1: Minimal Agent Loop

对应代码：`practice/stage1_minimal_agent/minimal_agent.py`

### 这一阶段解决什么问题

Stage 1 解决的是最小 Agent 闭环：用户输入进来后，系统如何选择工具、执行工具、读取工具结果，并根据工具结果输出最终答案。

最小 loop：

```text
observe user input
  -> think / choose action
  -> act / call tool
  -> observe tool result
  -> final answer or next action
```

### 核心组件总表

| 组件 | 作用 | 关键点 |
| --- | --- | --- |
| `ToolCall` | 表示 agent 要执行的结构化动作 | 包含工具名和参数 |
| `ToolResult` | 表示工具执行后的观察结果 | 包含 `ok` 和 `content` |
| `AgentStep` | trace 的一步 | 记录 thought、action、observation |
| `ToolSpec` | 工具说明书 | 包含 name、description、parameters、fn |
| `ToolRegistry` | 管 agent 可以调用哪些工具 | 注册工具、查找工具、执行工具、返回 schema |
| `SafeCalculator` | 安全表达式计算器 | 用 AST 限制可执行语法 |
| `calculator_tool` | 计算工具 | 把参数转成安全计算结果 |
| `read_file_tool` | 文件读取工具 | 限制只能读练习目录内文件 |
| `search_tool` | 本地概念搜索工具 | 模拟外部知识检索 |
| `word_count_tool` | 文本统计工具 | 返回 JSON 字符串 |
| `sentence_count_tool` | 句子统计工具 | 展示新增工具的模式 |
| `uppercase_tool` | 大写转换工具 | 展示工具扩展方式 |
| `RuleBasedModel` | 模拟模型策略 | 根据用户输入和 observation 决定下一步 |
| `Agent.run()` | 最小 agent loop | 串起模型决策、工具调用、停止条件 |
| `build_agent()` | 工具装配入口 | 统一注册所有工具 |
| `serialize_steps()` | trace 序列化 | 用于保存和测试 trace |

### 关键代码 1：ToolCall

```python
@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: dict[str, Any]
```

`ToolCall` 是 Agent 行动的标准格式。它解决的问题是：模型不能只输出“我要查一下”这种自然语言，而要输出机器可执行动作。

例子：

```json
{
  "name": "calculator",
  "arguments": {
    "expression": "23 * 7 + 10"
  }
}
```

关键点：

- `name` 对应工具注册表里的工具名。
- `arguments` 是工具参数，必须能被工具函数解析。
- 真实 LLM tool calling 中，这个结构通常由模型根据 tool schema 自动生成。

项目映射：

```json
{
  "name": "query_site_worklog",
  "arguments": {
    "site_id": "SITE_A",
    "date_range": "2026-06-01..2026-06-30"
  }
}
```

### 关键代码 2：ToolResult

```python
@dataclass(frozen=True)
class ToolResult:
    ok: bool
    content: str
```

`ToolResult` 是工具执行后的 observation。

关键点：

- `ok=True` 表示工具执行成功。
- `ok=False` 表示工具失败，但失败也必须结构化返回。
- `content` 可以是自然语言、JSON 字符串、错误信息或证据摘要。

面试表达：

> ToolResult 是 Agent loop 中的 observation。下一步决策不能凭空生成，而要基于工具返回的结果。工具失败也要进入 observation，而不是直接让程序崩溃。

### 关键代码 3：AgentStep

```python
@dataclass(frozen=True)
class AgentStep:
    thought: str
    action: ToolCall | None
    observation: ToolResult | None
```

`AgentStep` 是 trace 的最小单元。

它记录：

- `thought`：为什么选择这个动作。
- `action`：具体调用哪个工具。
- `observation`：工具返回了什么。

这对应 ReAct 范式里的 reasoning + acting。

项目映射：

> 在异常归因项目里，类似结构可以扩展为 TraceEvent 或 WorkflowState 的 step record，用来记录“为什么查物料系统、调用了什么参数、返回了什么证据”。

### 关键代码 4：ToolSpec 和 tool schema

```python
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
```

`ToolSpec` 是工具说明书。

关键点：

- `name`：工具名。
- `description`：告诉模型什么时候用这个工具。
- `parameters`：参数 schema。
- `fn`：实际执行函数。
- `schema()`：把工具信息暴露给模型或策略。

真实 LLM 场景里，“模型根据工具 schema 自动输出 ToolCall”的意思是：模型看到 name、description、parameters 后，自动选择工具并填参数。程序只负责校验和执行。

### 关键代码 5：ToolRegistry

```python
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
```

`ToolRegistry` 的作用：

| 职责 | 说明 |
| --- | --- |
| 工具注册 | 把 `ToolSpec` 放入 `_tools` |
| 工具查找 | 根据 `ToolCall.name` 找工具 |
| 工具执行 | 调用 `spec.fn(arguments)` |
| 异常捕获 | 把异常转成 `ToolResult(ok=False)` |
| schema 暴露 | `schemas()` 返回工具说明 |

设计意图：

- 模型不直接执行工具。
- 所有工具调用经过统一入口。
- 未知工具和工具异常都变成可观测结果。
- 后续可以在这里加权限、日志、重试、限流。

面试表达：

> ToolRegistry 是 Agent 和外部能力之间的受控边界。模型只提出 ToolCall，真正执行由 registry 完成，这样才能做工具白名单、错误处理、trace 和权限控制。

### 关键代码 6：SafeCalculator

```python
tree = ast.parse(expression, mode="eval")
return self._eval_node(tree.body)
```

`SafeCalculator` 用 Python AST 解析表达式，而不是直接 `eval()`。

关键点：

- 只允许数字常量。
- 只允许白名单运算符。
- 不允许函数调用、变量访问、属性访问。

为什么重要：

> 工具执行必须可控。即使是一个 calculator，也不能直接执行用户输入，否则会引入代码执行风险。

项目映射：

> 站点交付项目里的工具也要做类似限制。比如查询工具只能查询授权站点，不能让模型自由拼 SQL 或访问任意项目数据。

### 关键代码 7：read_file_tool 的权限边界

```python
base_dir = Path(__file__).resolve().parent
path = (base_dir / path_text).resolve()
if not path.is_relative_to(base_dir):
    return ToolResult(False, "Refusing to read outside the exercise directory")
```

这个工具展示了最小权限原则：

- 用户给相对路径。
- 程序解析成绝对路径。
- 检查是否仍在允许目录内。
- 超出目录直接拒绝。

项目映射：

> 业务 Agent 读取工单、计划、巡检记录时，也必须限制数据范围。例如只能读取当前项目、当前用户有权限的站点，不能越权访问其他项目。

### 关键代码 8：RuleBasedModel.next_action()

```python
if steps and steps[-1].observation is not None:
    observation = steps[-1].observation
    if observation.ok:
        return "I have enough information from the tool result.", None, observation.content.strip()
    return "The tool failed, so I should stop and report the failure.", None, f"工具调用失败：{observation.content}"
```

这段代码体现了 Agent loop 的关键：下一步依赖上一轮 observation。

如果工具成功：

- 认为信息足够。
- 返回 final answer。

如果工具失败：

- 不继续编造。
- 报告工具失败。

真实项目里可以更复杂：

- 失败后修正参数。
- 空结果后换工具。
- 证据不足后补查。
- 冲突后降低置信度。

### 关键代码 9：意图识别和工具选择

```python
if "大写" in text or "uppercase" in lowered or "upper case" in lowered:
    return (
        "The user asks to convert text to uppercase, so I should call uppercase.",
        ToolCall("uppercase", {"text": self._extract_count_target(text)}),
        None,
    )
```

这段代码回答了你之前问过的点：

- `lowered = text.lower()` 用来忽略英文大小写。
- `"uppercase" in lowered` 匹配 `Uppercase`、`UPPERCASE` 等写法。
- `"upper case" in lowered` 匹配中间有空格的表达。
- `"大写" in text` 匹配中文表达。

这不是一个完美的自然语言理解系统，而是用规则模拟模型的工具选择能力。

### 关键代码 10：复用 `_extract_count_target()`

```python
def _extract_count_target(self, text: str) -> str:
    for marker in ["：", ":", "内容是", "text is"]:
        if marker in text:
            return text.split(marker, 1)[1].strip()
    return text
```

它不是“字数统计专用函数”，而是“提取要处理的目标文本”。

所以这些工具都可以复用：

- word count
- sentence count
- uppercase
- reverse text
- summary

设计要点：

> 当多个工具都有同样的参数抽取逻辑时，可以复用一个 helper。复用的前提是函数语义足够抽象，这里抽象的是 target text，而不是 count text。

### 关键代码 11：Agent.run()

```python
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
```

这是 Stage 1 的核心。

执行逻辑：

1. 初始化 trace：`steps = []`。
2. 进入最多 `max_steps` 次循环。
3. 调用 model/policy 选择下一步。
4. 如果已有 final answer，停止。
5. 如果没有 action，停止。
6. 如果有 action，通过 ToolRegistry 执行。
7. 把 thought/action/observation 写入 steps。
8. 超过最大步数后停止。

关键点：

- `max_steps` 是防止无限循环的 guardrail。
- `steps` 是下一轮决策的上下文。
- `observation` 是工具结果，不是模型想象。
- final answer 只有在模型/策略认为足够时返回。

面试表达：

> Stage 1 的 Agent.run 是最小可控 loop。它把模型决策、工具调用、observation 和 trace 串起来，并用 max_steps 控制预算。这个结构是后续 harness、reflection 和 eval 的基础。

## Stage 2: RAG 和 Memory

对应代码：`practice/stage2_rag_memory/rag_memory.py`

### 这一阶段解决什么问题

Stage 2 解决的是“Agent 的回答必须有证据”和“哪些信息可以跨运行保存”的问题。

RAG 链路：

```text
load documents -> chunk -> tokenize -> vectorize -> retrieve -> answer with citations -> optional memory
```

### 核心组件总表

| 组件 | 作用 | 关键点 |
| --- | --- | --- |
| `TOKEN_RE` | 分词正则 | 同时支持英文 token 和中文单字 |
| `Chunk` | 文档切块结构 | 保留 source、chunk_id、text |
| `RetrievedChunk` | 检索结果结构 | 包含 chunk 和 score |
| `tokenize()` | 文本分词 | 统一小写，便于匹配 |
| `load_documents()` | 加载 Markdown 文档 | 将每个 `.md` 切成 chunks |
| `chunk_text()` | 文档切块 | 控制 chunk 大小和来源 |
| `TermRetriever` | 词频检索器 | 用 cosine similarity 模拟检索 |
| `MemoryStore` | 会话/长期记忆存储 | JSON 文件读写 |
| `ResearchAnswer` | 回答结构 | 保存 question、answer、citations、retrieved |
| `ResearchAssistant` | RAG 助手 | 串起检索、回答、记忆写入 |

### 关键代码 1：Chunk

```python
@dataclass(frozen=True)
class Chunk:
    source: str
    chunk_id: int
    text: str

    @property
    def citation(self) -> str:
        return f"{self.source}#chunk-{self.chunk_id}"
```

`Chunk` 的设计重点是可引用。

如果只保存 `text`，最终回答无法追溯来源。加上 `source` 和 `chunk_id` 后，每段证据都能变成 citation。

项目映射：

```python
EvidenceItem(
    source="query_material_status",
    raw_ref="material_order#MO-7788",
    claim="主设备到货延期 3 天",
)
```

### 关键代码 2：tokenize()

```python
TOKEN_RE = re.compile(r"[A-Za-z0-9]+|[\u4e00-\u9fff]")

def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]
```

作用：

- 英文按单词切。
- 中文按单字切。
- 统一小写。

局限：

- 不是真正语义检索。
- 中文单字粒度粗。
- 无法处理同义词。

但它适合学习 RAG 的结构，因为你能看清 chunk、retrieval、score、citation 的完整流程。

### 关键代码 3：chunk_text()

```python
def chunk_text(source: str, text: str, max_chars: int = 360) -> list[Chunk]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    chunks: list[Chunk] = []
    buffer = ""
    for paragraph in paragraphs:
        if buffer and len(buffer) + len(paragraph) + 2 > max_chars:
            chunks.append(Chunk(source, len(chunks) + 1, buffer))
            buffer = paragraph
        else:
            buffer = f"{buffer}\n\n{paragraph}".strip()
    if buffer:
        chunks.append(Chunk(source, len(chunks) + 1, buffer))
    return chunks
```

设计要点：

- 按段落切，不随便从句子中间截断。
- 用 `max_chars` 控制 chunk 大小。
- 每个 chunk 都带递增 id。
- 保持 chunk 和 source 的关系。

面试表达：

> Chunking 的目标不是越细越好，而是在召回精度和语义完整性之间平衡。太小会丢上下文，太大召回噪声多。

### 关键代码 4：TermRetriever

```python
class TermRetriever:
    def __init__(self, chunks: list[Chunk]) -> None:
        self.chunks = chunks
        self.vectors = [self._vectorize(chunk.text) for chunk in chunks]
```

`TermRetriever` 在初始化时把所有 chunk 转成词频向量。

```python
def search(self, query: str, top_k: int = 3) -> list[RetrievedChunk]:
    query_vector = self._vectorize(query)
    ranked = [
        RetrievedChunk(chunk, self._cosine(query_vector, vector))
        for chunk, vector in zip(self.chunks, self.vectors)
    ]
    return [item for item in sorted(ranked, key=lambda item: item.score, reverse=True)[:top_k] if item.score > 0]
```

检索过程：

1. 把 query 向量化。
2. 计算 query 和每个 chunk 的 cosine similarity。
3. 按分数排序。
4. 只保留分数大于 0 的 top_k。

真实项目可以把 `_vectorize()` 替换成 embedding，把 `_cosine()` 替换成向量数据库或 hybrid search。

### 关键代码 5：MemoryStore

```python
class MemoryStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.items = self._load()

    def add(self, question: str, answer: str, citations: list[str]) -> None:
        self.items.append({"question": question, "answer": answer, "citations": citations})
        self.path.write_text(json.dumps(self.items, ensure_ascii=False, indent=2), encoding="utf-8")
```

`MemoryStore` 展示了最简单的跨运行记忆。

关键点：

- `trace` 是一次运行过程。
- `memory` 是跨运行可复用信息。
- 不是所有 trace 都应该进入 memory。
- 错误结论进入 memory 会污染后续任务。

项目映射：

> 异常归因项目里，工具结果、反思日志属于执行记录；经过复核的归因模式、典型 bad case、修复经验才适合进入长期记忆。

### 关键代码 6：ResearchAssistant.answer()

```python
retrieved = self.retriever.search(question)
if not retrieved:
    answer = "本地知识库没有足够证据回答这个问题。"
    citations: list[str] = []
else:
    evidence_sentences = [item.chunk.text.replace("\n", " ") for item in retrieved]
    citations = [item.chunk.citation for item in retrieved]
    answer = " ".join(evidence_sentences)
    answer += "\n\n引用：" + ", ".join(citations)
```

核心逻辑：

- 先检索。
- 没有证据就拒答。
- 有证据才生成答案。
- 答案必须带 citation。

面试表达：

> RAG 的关键不是把文档塞进 prompt，而是让回答被检索证据约束。没有证据时要拒答或降置信度，不能让模型编。

## Stage 3: Agent Harness

对应代码：`practice/stage3_harness/harness_demo.py`

### 这一阶段解决什么问题

Stage 3 把 Stage 1 的“单文件 agent loop”升级成更接近真实工程的 harness。Harness 是模型外面的运行层，负责工具、权限、状态、trace、预算和错误处理。

### 核心组件总表

| 组件 | 作用 | 关键点 |
| --- | --- | --- |
| `ToolCall` | 表示计划调用的工具 | name + arguments |
| `ToolResult` | 表示工具返回结果 | ok + content |
| `TraceEvent` | 记录一次运行事件 | step、event、payload、timestamp |
| `ToolSpec` | 工具定义 | name、description、risky、fn |
| `ToolRegistry` | 管 agent 可以调用哪些工具 | register、get、names |
| `PermissionGate` | 判断工具是否需要人工批准 | safe tool 自动通过，risky tool 拒绝 |
| `SessionStore` | 把 trace 写入文件 | 每 append 一次就持久化 |
| `DemoPolicy` | 模拟模型/策略，规划 tool call | 根据任务生成 ToolCall 列表 |
| `Harness.run()` | 串起任务、计划、权限、执行、观察 | 核心调度逻辑 |
| `build_harness()` | 装配 harness | 注册工具、权限、session、policy |

### 关键代码 1：TraceEvent

```python
@dataclass(frozen=True)
class TraceEvent:
    step: int
    event: str
    payload: dict[str, Any]
    timestamp: float
```

`TraceEvent` 比 Stage 1 的 `AgentStep` 更工程化。

字段含义：

- `step`：第几步。
- `event`：发生了什么，比如 `task_received`、`tool_call_planned`。
- `payload`：事件详情。
- `timestamp`：发生时间。

项目映射：

```json
{
  "step": 3,
  "event": "evidence_validated",
  "payload": {
    "claim": "物料到货延期导致主设备安装延期",
    "evidence_ids": ["EV-001", "EV-003"],
    "confidence": 0.86
  }
}
```

### 关键代码 2：ToolSpec 的 risky 标记

```python
@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    risky: bool
    fn: ToolFn
```

Stage 3 的 `ToolSpec` 比 Stage 1 多了 `risky` 字段。

设计意图：

- 工具不只是能不能调用，还要判断风险。
- 读工具、搜索工具通常低风险。
- 写文件、提交、发布、删除、支付等高风险。

项目映射：

- `query_delivery_plan`：低风险，只读。
- `submit_attribution_report`：高风险，提交正式结论。
- `close_ticket`：高风险，改变业务状态。
- `notify_project_manager`：中高风险，对外发送信息。

### 关键代码 3：ToolRegistry

```python
class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> None:
        self._tools[spec.name] = spec

    def get(self, name: str) -> ToolSpec | None:
        return self._tools.get(name)

    def names(self) -> list[str]:
        return sorted(self._tools)
```

职责：

| 方法 | 作用 |
| --- | --- |
| `register()` | 注册工具 |
| `get()` | 根据工具名获取 ToolSpec |
| `names()` | 列出所有可用工具 |

设计要点：

- Harness 通过 registry 管理工具白名单。
- 未注册工具不能执行。
- 便于 trace 里记录当前可用工具。

### 关键代码 4：PermissionGate

```python
class PermissionGate:
    def __init__(self, auto_approve_safe_tools: bool = True) -> None:
        self.auto_approve_safe_tools = auto_approve_safe_tools

    def approve(self, spec: ToolSpec, call: ToolCall) -> tuple[bool, str]:
        if not spec.risky and self.auto_approve_safe_tools:
            return True, "safe tool auto-approved"
        return False, f"tool '{call.name}' requires human approval in this demo"
```

`PermissionGate` 是安全边界。

关键点：

- 安全工具可以自动批准。
- 高风险工具需要人工确认。
- 返回 `(approved, reason)`，让 trace 能记录为什么通过或拒绝。

面试表达：

> 权限判断不能交给模型自由发挥，必须放在 harness 里。模型可以提出动作，但是否允许执行，要由 PermissionGate 根据工具风险、用户权限和业务规则决定。

### 关键代码 5：SessionStore

```python
class SessionStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.events: list[TraceEvent] = []

    def append(self, event: TraceEvent) -> None:
        self.events.append(event)
        self.path.write_text(json.dumps([asdict(item) for item in self.events], ensure_ascii=False, indent=2), encoding="utf-8")
```

`SessionStore` 的作用是保存一次运行过程。

关键点：

- 每个 event 都进入内存列表。
- 每次 append 后写入文件。
- 支持运行后复盘。

项目映射：

> 异常归因任务中，每一次工具调用、证据校验、反思补查都应该写入 session。这样当最终结论错误时，可以回放到底是哪一步出了问题。

### 关键代码 6：DemoPolicy

```python
class DemoPolicy:
    def plan(self, task: str) -> list[ToolCall]:
        lowered = task.lower()
        if lowered.startswith("count "):
            return [ToolCall("word_count", {"text": task.removeprefix("count ").strip()})]
        if "read" in lowered:
            return [ToolCall("read_file", {"path": "README.md"})]
        return [ToolCall("search_docs", {"query": task})]
```

`DemoPolicy` 模拟模型策略。

关键点：

- 根据 task 生成 ToolCall。
- `startswith("count ")` 是命令式意图识别。
- `removeprefix("count ").strip()` 是参数抽取。
- 真实项目里这里可以替换成 LLM planner。

项目映射：

```python
if abnormal_type == "milestone_delay":
    return [
        ToolCall("query_delivery_plan", {"site_id": site_id}),
        ToolCall("query_material_status", {"site_id": site_id}),
        ToolCall("query_site_worklog", {"site_id": site_id}),
    ]
```

### 关键代码 7：Harness.run()

```python
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
```

这是 Stage 3 最重要的代码。

执行顺序：

1. 记录任务收到。
2. 调 policy 生成工具调用计划。
3. 用 `max_tool_calls` 截断计划。
4. 对每个 ToolCall 记录 planned trace。
5. 从 registry 查工具。
6. 查不到就记录失败。
7. 查到后先过 PermissionGate。
8. 权限不通过就停止。
9. 权限通过后执行工具。
10. 记录工具 observation。
11. 返回最后一个工具结果。

这段代码把“Agent 可控执行”讲得很完整：

- 不是模型直接执行。
- 不是工具随便调用。
- 每步都有 trace。
- 高风险动作会被拦截。
- 有工具调用预算。

面试表达：

> Harness.run 是业务 Agent 的运行时主干。它把任务接收、计划生成、工具查找、权限校验、工具执行和 observation 记录串起来。真实项目里我会在这个流程里继续加入 WorkflowState、evidence checker、reflection 和 report generation。

## Stage 4: Multi-Agent Coordination

对应代码：`practice/stage4_multi_agent/multi_agent_pipeline.py`

### 这一阶段解决什么问题

Stage 4 说明 multi-agent 的本质不是“多个角色聊天”，而是职责边界、输入输出 schema、supervisor 控制和停止条件。

### 核心组件总表

| 组件 | 作用 | 关键点 |
| --- | --- | --- |
| `ResearchBrief` | researcher 输出 | topic + facts |
| `Draft` | writer/reviser 输出 | topic + body |
| `Review` | reviewer 输出 | passed + issues |
| `FinalReport` | supervisor 最终输出 | answer + review + trace |
| `ResearcherAgent` | 收集事实 | 输出结构化 facts |
| `WriterAgent` | 写初稿 | 把 facts 组织成文本 |
| `ReviewerAgent` | 质量检查 | 输出是否通过和问题列表 |
| `ReviserAgent` | 按 review 修订 | 根据 issues 补内容 |
| `Supervisor` | 编排所有 agent | 控制执行顺序和 trace |

### 关键代码 1：共享数据结构

```python
@dataclass(frozen=True)
class ResearchBrief:
    topic: str
    facts: list[str]

@dataclass(frozen=True)
class Review:
    passed: bool
    issues: list[str]
```

多 agent 协作必须有结构化接口。

如果每个 agent 都只输出自由文本，下游就很难判断：

- 是否有证据。
- 是否通过审核。
- 要修什么。
- 能否停止。

项目映射：

```python
@dataclass(frozen=True)
class EvidenceReview:
    passed: bool
    missing_evidence: list[str]
    conflicting_evidence: list[str]
    follow_up_actions: list[ToolCall]
```

### 关键代码 2：ReviewerAgent

```python
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
```

Reviewer 的关键不是“评价一下”，而是输出结构化问题。

设计要点：

- 检查条件明确。
- 问题列表可执行。
- `passed` 作为停止条件。

项目映射：

```python
if not state.evidence_chain:
    issues.append("缺少证据链")
if state.final_conclusion and not state.final_conclusion.get("evidence_ids"):
    issues.append("结论未绑定证据")
if confidence < 0.7:
    issues.append("结论置信度不足")
```

### 关键代码 3：ReviserAgent

```python
class ReviserAgent:
    def run(self, draft: Draft, review: Review) -> Draft:
        if review.passed:
            return draft
        additions = "\n修订：已根据 review 补充证据、结论和可检查结构。"
        additions += "\n验收：读者应能指出核心观点、证据和下一步行动。"
        return Draft(draft.topic, draft.body + additions)
```

Reviser 的输入是 `draft + review`，不是原始任务。这说明多 agent 协作里每个角色应该只拿自己需要的上下文。

项目映射：

> Reflector 根据 EvidenceReview 生成补查计划，而不是重新处理全部原始上下文。

### 关键代码 4：Supervisor.run()

```python
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
```

Supervisor 的职责：

- 决定执行顺序。
- 管理中间结果。
- 记录 trace。
- 触发 review/revise。
- 生成最终输出。

面试表达：

> 多 agent 的关键是 supervisor 管控，而不是 agent 自由聊天。每个模块要有明确输入输出，reviewer 要输出结构化问题，supervisor 根据 passed/failed 决定是否继续。

## Stage 5: Skills 和 Protocols

对应代码：`practice/stage5_skills_protocols/skill_runner.py`

Skill 文件：`practice/stage5_skills_protocols/skills/research_summary/SKILL.md`

模板文件：`practice/stage5_skills_protocols/skills/research_summary/templates/summary.md`

### 这一阶段解决什么问题

Stage 5 解决“能力如何复用”的问题。Tool 是函数，Skill 是流程知识包。一个 Skill 可以告诉 Agent：

- 什么时候使用。
- 按什么步骤做。
- 使用什么模板。
- 如何验收结果。
- 有哪些脚本或资源。

### 核心组件总表

| 组件 | 作用 | 关键点 |
| --- | --- | --- |
| `Skill` | Skill 元数据 | name、description、checks、template |
| `SkillRun` | Skill 执行结果 | output、passed_checks、failed_checks |
| `load_skill()` | 加载 skill 包 | 读取 SKILL.md 和模板 |
| `run_skill()` | 执行 skill | 填充模板并做检查 |
| `_read_field()` | 解析字段 | 从 SKILL.md 读取 Name/Description |

### 关键代码 1：Skill 数据结构

```python
@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    checks: list[str]
    template: str
```

Skill 不只是 prompt，它包含：

- 名称。
- 描述。
- 验收标准。
- 模板。

项目映射：

> 异常归因流程可以沉淀为 `site-delivery-attribution` skill，里面包含证据检查步骤、补查规则、报告模板和验收标准。

### 关键代码 2：load_skill()

```python
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
```

设计要点：

- `SKILL.md` 是入口说明。
- `templates/` 是延迟加载资源。
- checks 是可执行验收条件。

这体现了 skill 的“渐进加载”思想：先读轻量说明，需要时再加载模板和脚本。

### 关键代码 3：run_skill()

```python
key_points = [part.strip() for part in source_text.replace(".", "\n").splitlines() if part.strip()]
output = skill.template.replace("{{summary}}", "\n".join(f"- {point}" for point in key_points[:3]))
output = output.replace("{{takeaway}}", "Skill packages reusable process knowledge, not just code.")
```

这里把输入文本转成模板输出。

关键点：

- Skill 将流程知识和模板结合。
- 模板变量让输出结构稳定。
- 输出不是随意生成，而是受模板约束。

### 关键代码 4：checks

```python
for check in skill.checks:
    if "bullet" in check and "- " in output:
        passed.append(check)
    elif "takeaway" in check and "Takeaway" in output:
        passed.append(check)
    elif "source" in check and source_text:
        passed.append(check)
    else:
        failed.append(check)
```

Skill 的重要部分是验收。没有验收标准的 skill 只是更长的 prompt。

项目映射：

异常归因 skill 的 checks 可以是：

- must include abnormal input
- must include execution plan
- must include evidence chain
- must include reflection decision
- must include final conclusion
- must include confidence
- must include next action

面试表达：

> Tool 是动作接口，Skill 是可复用流程知识。我的项目里，查询计划是 tool；异常归因方法、证据校验规则、报告模板和验收标准可以沉淀成 skill。

## Stage 6: Browser Agent

对应代码：`practice/stage6_browser_agent/browser_info_agent.py`

### 这一阶段解决什么问题

Stage 6 解决页面型工具的观察问题。Browser agent 和普通 API tool 不一样：页面结构可能变化，加载可能失败，元素可能找不到，所以必须记录 DOM、文本、链接、动作日志，真实系统还需要截图。

### 核心组件总表

| 组件 | 作用 | 关键点 |
| --- | --- | --- |
| `Link` | 页面链接结构 | text + href |
| `PageSummary` | 页面摘要结果 | title、headings、links、text_preview、action_log |
| `PageParser` | HTML 解析器 | 从 DOM 中提取 title、headings、links、text |
| `LocalPageAgent` | 本地页面 agent | open、read、parse、summarize |

### 关键代码 1：PageSummary

```python
@dataclass(frozen=True)
class PageSummary:
    title: str
    headings: list[str]
    links: list[Link]
    text_preview: str
    action_log: list[str]
```

Browser agent 的输出不应该只有“总结文本”，还应该有结构化观察结果：

- title
- headings
- links
- preview
- action log

项目映射：

> 如果交付异常证据来自项目管理后台或交付看板，页面 agent 输出应该包含页面标题、筛选条件、提取字段、截图引用和 action log。

### 关键代码 2：PageParser.handle_starttag()

```python
def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
    self._tag_stack.append(tag)
    if tag == "a":
        attrs_dict = dict(attrs)
        self._active_href = attrs_dict.get("href") or ""
        self._active_link_text = []
```

这里维护了两个重要状态：

- `_tag_stack`：当前在什么标签内部。
- `_active_href`：当前是否正在解析链接。

Browser agent 的难点之一就是状态管理：你要知道当前读到的是标题、正文、链接还是脚本。

### 关键代码 3：PageParser.handle_data()

```python
if current == "title":
    self.title += text
if current in {"h1", "h2", "h3"}:
    self.headings.append(text)
if self._active_href is not None:
    self._active_link_text.append(text)
if current not in {"script", "style"}:
    self.text_parts.append(text)
```

这段代码把不同 DOM 节点映射成结构化信息。

关键点：

- title 单独保存。
- h1/h2/h3 作为 headings。
- 链接文本和 href 分开处理。
- script/style 不进入正文。

### 关键代码 4：LocalPageAgent.inspect()

```python
action_log = [f"open:{path}"]
if not path.exists():
    action_log.append("error:file_not_found")
    return PageSummary("", [], [], "", action_log)
html = path.read_text(encoding="utf-8")
action_log.append("read_html")
parser = PageParser(path.as_uri())
parser.feed(html)
action_log.append("parse_dom")
preview = " ".join(parser.text_parts)[:240]
action_log.append("summarize")
return PageSummary(parser.title, parser.headings, parser.links, preview, action_log)
```

设计要点：

- 每个动作写入 action log。
- 文件不存在也返回结构化结果。
- DOM 解析和摘要分步记录。

面试表达：

> Browser agent 必须记录动作日志。页面型任务容易因为加载、弹窗、DOM 变化失败，只有记录 open、read、parse、click、screenshot 等动作，才能复盘。

## Stage 7: Evaluation, Observability, And Safety

对应代码：`practice/stage7_eval_observability/eval_runner.py`

Eval 数据：`practice/stage7_eval_observability/evals/stage1_cases.json`

### 这一阶段解决什么问题

Stage 7 解决“如何证明 Agent 可靠”的问题。一次 demo 只能证明某次成功，eval 才能证明版本变化后能力是否稳定。

### 核心组件总表

| 组件 | 作用 | 关键点 |
| --- | --- | --- |
| `EvalCase` | 一条测试任务 | id、task、expected_contains、category |
| `EvalResult` | 一条评测结果 | passed、actual、failure_category、trace |
| `load_cases()` | 加载 eval 数据 | JSON -> EvalCase |
| `run_eval()` | 批量执行评测 | 调 Stage 1 agent，收集结果 |
| `serialize_trace()` | 序列化 agent steps | 保留 action 和 observation |
| `summarize()` | 汇总指标 | total、passed、success_rate、failures |

### 关键代码 1：EvalCase

```python
@dataclass(frozen=True)
class EvalCase:
    id: str
    task: str
    expected_contains: str
    category: str
```

每条 eval case 至少要有：

- 输入任务。
- 预期输出特征。
- 失败分类。

项目映射：

```json
{
  "id": "site_delay_material_001",
  "task": "站点 A 主设备安装延期 4 天，排查根因",
  "expected_contains": "物料到货延期",
  "category": "root_cause_attribution"
}
```

### 关键代码 2：EvalResult

```python
@dataclass(frozen=True)
class EvalResult:
    id: str
    task: str
    passed: bool
    expected_contains: str
    actual: str
    failure_category: str
    trace: list[dict[str, object]]
```

EvalResult 的价值不只是通过/失败，还要保存：

- 实际输出。
- 失败分类。
- trace。

这样失败时可以回放。

### 关键代码 3：run_eval()

```python
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
```

核心逻辑：

- 用固定 agent 跑固定 case。
- 用 `expected_contains` 做最小断言。
- 失败时保留 category。
- 保存 trace 方便定位。

项目里可以更丰富：

- expected_root_cause
- expected_evidence_count
- expected_confidence_min
- expected_requires_reflection
- expected_human_review

### 关键代码 4：summarize()

```python
total = len(results)
passed = sum(1 for result in results if result.passed)
failures: dict[str, int] = {}
for result in results:
    if not result.passed:
        failures[result.failure_category] = failures.get(result.failure_category, 0) + 1
return {"total": total, "passed": passed, "success_rate": round(passed / total, 3), "failures": failures}
```

指标：

- total
- passed
- success_rate
- failures by category

项目指标可以扩展为：

- root_cause_accuracy
- evidence_coverage
- reflection_trigger_rate
- human_review_rate
- average_tool_calls
- average_latency
- cost_per_case

面试表达：

> 我不会只用 demo 判断 Agent 是否变好，而是用固定 eval 集、失败分类和 trace 回放。每个 bad case 都要能定位是计划错、工具错、证据不足、reflection 未触发，还是报告生成夸大。

## Stage 8: Ship A Real Agent

对应代码：`practice/stage8_ship_real_agent/personal_research_agent.py`

### 这一阶段解决什么问题

Stage 8 解决“如何把前面能力组合成可交付 agent”的问题。一个 agent 能跑一次不等于可交付，必须有明确用户、任务、权限边界、trace、测试和 README。

### 核心组件总表

| 组件 | 作用 | 关键点 |
| --- | --- | --- |
| `ShippedAgentResult` | 最终输出结构 | answer、citations、trace |
| `PersonalResearchAgent` | 可交付 agent 封装 | 组合 Stage 2 的 ResearchAssistant |
| `run()` | 业务入口 | question -> retrieval -> answer -> trace |
| `main()` | CLI 入口 | 参数解析、trace 保存、JSON 输出 |

### 关键代码 1：复用 Stage 2

```python
STAGE2_DIR = Path(__file__).resolve().parents[1] / "stage2_rag_memory"
sys.path.insert(0, str(STAGE2_DIR))

from rag_memory import ResearchAssistant
```

Stage 8 没有重复实现 RAG，而是复用 Stage 2。

设计要点：

- 交付阶段要复用成熟模块。
- 不要把所有逻辑堆在一个文件里。
- 可交付 agent 是多个能力的组合。

### 关键代码 2：ShippedAgentResult

```python
@dataclass(frozen=True)
class ShippedAgentResult:
    answer: str
    citations: list[str]
    trace: list[dict[str, object]]
```

可交付输出必须包含：

- 用户要的答案。
- 支撑答案的引用。
- 可复盘 trace。

项目映射：

```python
@dataclass(frozen=True)
class AttributionAgentResult:
    report: str
    conclusion: dict[str, object]
    evidence_chain: list[EvidenceItem]
    reflection_log: list[ReflectionDecision]
    trace: list[dict[str, object]]
```

### 关键代码 3：PersonalResearchAgent.run()

```python
trace.append({"event": "question_received", "question": question, "timestamp": time.time()})
trace.append({"event": "permission_checked", "scope": str(self.data_dir), "approved": True, "timestamp": time.time()})
result = self.assistant.answer(question)
trace.append(
    {
        "event": "retrieval_completed",
        "citations": result.citations,
        "retrieved_count": len(result.retrieved),
        "timestamp": time.time(),
    }
)
trace.append({"event": "final_answer", "answer": result.answer, "timestamp": time.time()})
```

这个 run 方法展示了交付 agent 的基本事件流：

1. 收到问题。
2. 检查权限范围。
3. 执行检索。
4. 记录引用和检索数量。
5. 输出最终答案。

项目映射：

```text
abnormal_received
permission_checked
plan_created
tool_call_planned
tool_observed
evidence_validated
reflection_decided
report_generated
memory_persisted
```

### 关键代码 4：CLI 和 trace 保存

```python
if args.trace:
    trace_path = (base_dir / args.trace).resolve()
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    trace_path.write_text(json.dumps(payload["trace"], ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(payload, ensure_ascii=False, indent=2))
```

交付要求：

- CLI 参数清晰。
- 输出 JSON，便于下游处理。
- trace 可以保存。
- 输出可复现。

面试表达：

> Ship 阶段关注的不只是模型效果，而是别人能否 clone 下来运行、能否看到 trace、能否复现结果、能否定位失败、能否控制权限。

## Stage 1-8 关键组件总复盘

| 组件 | 出现 Stage | 核心作用 | 面试关键词 |
| --- | --- | --- | --- |
| `ToolCall` | 1 / 3 | 结构化动作 | tool calling、schema |
| `ToolResult` | 1 / 3 | 工具 observation | observation、failure handling |
| `AgentStep` | 1 | 最小 trace | ReAct trace |
| `ToolSpec` | 1 / 3 | 工具说明书 | name、description、parameters、risky |
| `ToolRegistry` | 1 / 3 | 管理可调用工具 | whitelist、dispatch |
| `RuleBasedModel` | 1 | 模拟模型决策 | policy、tool selection |
| `Agent.run()` | 1 | 最小 loop | observe-think-act-observe |
| `Chunk` | 2 | 可引用文档块 | citation |
| `TermRetriever` | 2 | 检索证据 | retrieval、score |
| `MemoryStore` | 2 | 跨运行记忆 | memory vs trace |
| `TraceEvent` | 3 | 工程化 trace | observability |
| `PermissionGate` | 3 | 权限控制 | human approval |
| `SessionStore` | 3 | 保存 session trace | replay |
| `DemoPolicy` | 3 | 规划 tool call | planner |
| `Harness.run()` | 3 | Agent 运行时主干 | harness engineering |
| `ReviewerAgent` | 4 | 质量检查 | reflection、review |
| `Supervisor` | 4 | 多模块编排 | coordination |
| `Skill` | 5 | 可复用流程知识 | capability packaging |
| `PageParser` | 6 | DOM 观察 | browser agent |
| `EvalCase` | 7 | 固定任务集 | regression |
| `EvalResult` | 7 | 评测结果和 trace | failure category |
| `ShippedAgentResult` | 8 | 可交付输出 | answer、citation、trace |

## 如何应用到你的项目：异常巡检与归因 Agent

项目全称：

> 异常巡检与归因 Agent：站点交付异常的证据链诊断与报告生成

### 1. 项目为什么需要 Agent

站点交付异常不是固定流程问题，而是长路径复杂诊断问题。异常可能来自：

- 计划偏差。
- 物料到货。
- 施工资源。
- 审批卡点。
- 质量返工。
- 外部依赖。
- 成本约束。
- 工单阻塞。

每个异常的排查路径不同，下一步要查什么依赖已有工具结果。这正是 Agent loop 的适用场景。

对应 Stage：

- Stage 0：判断它不是 script/workflow，而是 agent。
- Stage 1：用 loop 根据 observation 决定下一步。
- Stage 3：用 harness 管工具、权限、状态和 trace。

### 2. 项目中的 Agent Loop

可以设计为：

```text
observe abnormal input
  -> plan attribution steps
  -> call tools
  -> collect tool observations
  -> build evidence chain
  -> validate evidence
  -> reflect if missing/conflicting
  -> generate report
  -> persist trace and memory
```

对应代码抽象：

```python
class AttributionHarness:
    def run(self, abnormal_input: AbnormalInput) -> AttributionResult:
        state = WorkflowState.from_input(abnormal_input)
        self.trace(state, "abnormal_received")
        state.execution_plan = self.planner.plan(state)
        for tool_call in state.execution_plan:
            result = self.executor.call(tool_call)
            state.tool_results.append(result)
            self.evidence_checker.update(state, result)
            decision = self.reflector.decide(state)
            state.reflection_log.append(decision)
            if decision.requires_follow_up:
                state.execution_plan.extend(decision.follow_up_calls)
            if self.stopper.should_stop(state):
                break
        state.final_conclusion = self.reporter.generate(state)
        self.memory_store.persist(state)
        return AttributionResult.from_state(state)
```

### 3. WorkflowState 是项目核心

Stage 1 的 `steps`、Stage 2 的 `retrieved/memory`、Stage 3 的 `SessionStore`、Stage 7 的 `trace`，在你的项目里应该汇聚成 `WorkflowState`。

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

| 字段 | 来源 Stage | 作用 |
| --- | --- | --- |
| `run_id` | Stage 3 / 7 | 标识一次运行，支持 trace 和回放 |
| `abnormal_input` | Stage 1 | 原始 observation，防止任务漂移 |
| `execution_plan` | Stage 3 / 4 | 保存 planner 输出 |
| `tool_results` | Stage 1 / 3 | 保存工具 observation |
| `evidence_chain` | Stage 2 | 保存可引用证据 |
| `reflection_log` | Stage 4 / 7 | 保存补查原因和决策 |
| `final_conclusion` | Stage 8 | 最终报告结论 |
| `bad_case_samples` | Stage 7 | 失败样本沉淀 |
| `memory_records` | Stage 2 / 5 | 可复用归因模式 |
| `status` | Stage 3 / 8 | 支持恢复和监控 |

面试表达：

> WorkflowState 是我项目里最核心的上下文管理机制。它把异常输入、执行计划、工具结果、证据链、反思决策和最终结论放在一个结构化状态里，避免长链路执行中上下文丢失，也让复盘、评测和报告校验有统一数据来源。

### 4. 工具体系如何设计

参考 Stage 1 / Stage 3 的 `ToolSpec`、`ToolRegistry`、`PermissionGate`，项目工具可以这样分类：

| 工具 | 风险 | 用途 |
| --- | --- | --- |
| `query_delivery_plan` | 低 | 查询计划里程碑、计划时间、实际时间 |
| `query_material_status` | 低 | 查询物料到货、缺料、供应商状态 |
| `query_ticket_system` | 低 | 查询阻塞工单、处理状态 |
| `query_site_worklog` | 低 | 查询现场施工日志、资源记录 |
| `query_quality_records` | 低 | 查询返工、验收、质量问题 |
| `query_cost_records` | 中 | 查询成本变化和资源投入 |
| `submit_attribution_report` | 高 | 提交正式归因报告 |
| `notify_project_manager` | 高 | 发送通知 |
| `close_ticket` | 高 | 关闭工单 |

工具定义：

```python
@dataclass(frozen=True)
class AttributionToolSpec:
    name: str
    description: str
    parameters: dict[str, object]
    risky: bool
    fn: Callable[[dict[str, object]], ToolResultRecord]
```

关键原则：

- 查询工具默认只读。
- 写入、通知、关闭类工具必须人工确认。
- 所有工具结果写入 `WorkflowState.tool_results`。
- 所有工具要有 source/ref，方便证据链引用。

### 5. 证据链如何设计

参考 Stage 2 的 `Chunk.citation` 和 `ResearchAnswer.citations`。

你的项目里，证据不一定来自文档，也可能来自工具结果。建议结构：

```python
@dataclass(frozen=True)
class EvidenceItem:
    evidence_id: str
    source_tool: str
    raw_ref: str
    claim: str
    supports: str
    confidence: float
    conflict_with: list[str]
```

示例：

```json
{
  "evidence_id": "EV-003",
  "source_tool": "query_material_status",
  "raw_ref": "material_order#MO-7788",
  "claim": "主设备到货晚于计划 3 天",
  "supports": "物料延期是主设备安装延期的主要因素",
  "confidence": 0.91,
  "conflict_with": []
}
```

报告生成规则：

- 结论必须绑定 `evidence_id`。
- 报告只能引用 state 中存在的证据。
- 没有证据时输出“不足以判断”。
- 证据冲突时说明冲突并触发补查或人工复核。

面试表达：

> 证据链是防止模型幻觉的关键。最终报告不是模型自由发挥，而是从 WorkflowState.evidence_chain 中抽取证据生成，每个结论都能追溯到来源工具和 raw_ref。

### 6. Self-Reflection 如何落地

参考 Stage 4 的 `ReviewerAgent` 和 Stage 7 的 failure category。

Reflection 不是“让模型想一想”，而是结构化质量检查：

```python
@dataclass(frozen=True)
class ReflectionDecision:
    reason: str
    decision: str
    follow_up_calls: list[ToolCall]
    requires_human_review: bool
```

触发条件：

| 条件 | 处理 |
| --- | --- |
| 工具失败 | 记录 failure，必要时重试或换工具 |
| 空结果 | 改查询条件或查其他来源 |
| 证据不足 | 追加补查 tool call |
| 证据冲突 | 降低置信度，查权威来源 |
| 置信度低 | 继续补查或人工复核 |
| 达到预算 | 停止并输出不确定结论 |

面试表达：

> Self-Reflection 在项目里是一个结构化补查机制。它会检查证据是否足够、是否冲突、工具是否失败、结论置信度是否达标。如果不满足，就生成 follow-up tool calls，并把原因写入 reflection_log。

### 7. Memory 和 bad case 如何沉淀

参考 Stage 2 的 `MemoryStore` 和 Stage 7 的 `EvalResult.failure_category`。

需要区分：

| 类型 | 保存内容 | 用途 |
| --- | --- | --- |
| Trace | 单次执行事件 | Debug 和复盘 |
| Bad case | 错误样本和原因 | 加入 eval，防回归 |
| Memory | 经过复核的归因模式 | 后续类似异常复用 |

Bad case 结构：

```python
@dataclass(frozen=True)
class BadCase:
    case_id: str
    abnormal_summary: str
    wrong_conclusion: str
    expected_conclusion: str
    failure_category: str
    fix_action: str
```

Memory 结构：

```python
@dataclass(frozen=True)
class AttributionMemory:
    pattern_id: str
    abnormal_type: str
    root_cause: str
    evidence_pattern: list[str]
    verified: bool
```

关键原则：

- 不是所有日志都进 memory。
- 未验证猜测不能进长期记忆。
- 错误 memory 要能禁用或修正。
- bad case 要回流 eval。

### 8. Eval 和上线验证如何设计

参考 Stage 7 的 `EvalCase`、`EvalResult`、`summarize()`。

项目 eval case 可以包含：

```python
@dataclass(frozen=True)
class AttributionEvalCase:
    id: str
    abnormal_input: dict[str, object]
    expected_root_cause: str
    expected_evidence_keywords: list[str]
    category: str
```

核心指标：

| 指标 | 说明 |
| --- | --- |
| root_cause_accuracy | 主因是否命中 |
| evidence_coverage | 结论是否有足够证据 |
| citation_validity | 报告引用是否都存在 |
| reflection_precision | 是否在该补查时补查 |
| tool_call_count | 工具调用成本 |
| latency | 任务耗时 |
| human_review_rate | 人工复核比例 |
| bad_case_regression | 历史 bad case 是否复发 |

面试表达：

> 上线前不能只看 demo，而要用固定 eval 集评估归因准确率、证据覆盖率、工具调用次数、延迟和 bad case 回归。每次 prompt、工具或规则改动后都要跑回归测试。

### 9. 报告生成如何和 Stage 8 对齐

参考 Stage 8 的 `ShippedAgentResult`。

你的结果结构可以是：

```python
@dataclass(frozen=True)
class AttributionAgentResult:
    report: str
    conclusion: dict[str, object]
    evidence_chain: list[EvidenceItem]
    reflection_log: list[ReflectionDecision]
    trace: list[dict[str, object]]
```

报告必须包含：

- 异常概述。
- 执行计划。
- 工具调用摘要。
- 证据链。
- 反思补查记录。
- 主因和次因。
- 置信度。
- 后续建议。
- 需要人工复核的点。

### 10. 你的项目可以这样讲

30 秒版本：

> 我做的是站点交付异常巡检与归因 Agent，解决人工发现异常慢、根因链路不清晰的问题。系统通过 Agent Loop 完成任务规划、工具调用、证据校验、Self-Reflection 补查和报告生成。我参与 Agent Harness 核心链路和 WorkflowState 设计，把异常输入、计划、工具结果、证据链、反思决策和最终结论统一管理，同时沉淀 trace、bad case 和归因记忆，支撑复盘、评测和记忆复用。

1 分钟版本：

> 这个项目的核心不是让模型直接生成结论，而是搭建一个可控的 Agent Harness。异常输入进入系统后，Planner 会生成归因检查计划，Tool Executor 调用计划、物料、工单、施工日志等工具，Evidence Checker 把工具结果转成证据链，Reflector 判断证据是否足够或冲突，不足时继续补查，最后 Reporter 生成带证据来源的归因报告。我重点参与 WorkflowState 上下文管理，把 abnormal input、execution plan、tool results、evidence chain、reflection log 和 final conclusion 统一承载，提升长链路任务的上下文连续性、可复盘性和稳定性。

3 分钟版本：

> 站点交付异常归因是一个典型长路径复杂任务。异常可能来自计划、物料、施工、审批、质量或外部依赖，排查路径不是固定 workflow，而是要根据工具 observation 动态选择下一步。因此我们构建了异常巡检与归因 Agent。
>
> 系统主链路是 observe 异常输入，planner 拆解归因计划，executor 调用多个业务工具，evidence checker 结构化证据链，reflector 做证据充分性和冲突检查，如果缺证或冲突就生成补查动作，最后 reporter 生成可解释报告。这个过程对应 Stage 1 的 Agent loop、Stage 2 的证据和记忆、Stage 3 的 harness、Stage 4 的 review/reflection、Stage 7 的 eval 和 trace、Stage 8 的交付封装。
>
> 我参与的重点是 Agent Harness 核心链路和 WorkflowState。WorkflowState 统一承载异常输入、执行计划、工具结果、证据链、反思日志和最终结论，避免长任务中上下文丢失。工具结果不会直接拼报告，而是先进入 tool_results，再抽取 evidence item；最终报告只能引用 evidence_chain 中存在的证据。工具失败、证据不足、证据冲突会进入 reflection_log，并触发补查或人工复核。
>
> 同时，我们把执行记录、bad case 和经过复核的归因模式结构化沉淀，支撑后续任务复盘、故障诊断、eval 回归和记忆复用。两个重点项目试点和两个版本上线后，通过减少人工查证、缩短定位周期和降低重复沟通成本，驱动交付成本降低 37.5%。

## 面试追问速查

Q：为什么这是 Agent，不是 workflow？

A：Workflow 路径固定，而异常归因下一步依赖工具 observation。查到物料异常就补查供应商，查到施工异常就补查工单和资源，证据不足还要 reflection。

Q：WorkflowState 为什么重要？

A：它把异常输入、执行计划、工具结果、证据链、反思决策和最终结论结构化承载，解决长链路上下文丢失、结论不可追溯和失败不可复盘的问题。

Q：怎么防止模型胡编根因？

A：最终报告只能引用 evidence_chain 中存在的证据，每个结论绑定 evidence_id、source_tool 和 raw_ref。证据不足时触发补查或输出不确定结论。

Q：Self-Reflection 具体做什么？

A：它检查工具是否失败、证据是否不足、证据是否冲突、置信度是否达标。如果不满足，就生成补查 tool call，并把原因写入 reflection_log。

Q：Memory 和 trace 区别是什么？

A：Trace 记录单次运行过程，用于 debug 和复盘；memory 保存跨任务可复用经验，例如经过复核的归因模式和 bad case。未验证猜测不应进入长期记忆。

Q：Harness 的价值是什么？

A：Harness 把模型动作工程化，负责工具注册、权限判断、状态管理、trace、预算、错误处理和恢复。模型只提出动作，是否执行和如何记录由 harness 管。

Q：怎么证明上线后变好了？

A：用固定 eval 集和业务指标。技术上看归因命中率、证据覆盖率、工具调用次数、延迟、bad case 回归；业务上看人工排查时长、定位周期和交付成本变化。

Q：37.5% 成本降低怎么解释？

A：这是试点项目口径，主要来自自动巡检、证据聚合和报告生成减少了人工跨系统查证、重复沟通和问题定位时间。需要说明是两个重点项目试点结果，不夸大成所有场景通用。

## 最后必须掌握的核心定义

`Agent loop`：基于 observation 动态决策的循环，不是简单多轮聊天。

`ToolCall`：模型或策略输出的结构化动作。

`ToolResult`：工具执行后的 observation。

`ToolRegistry`：管理 agent 能调用的工具，是工具白名单和执行入口。

`PermissionGate`：判断工具是否允许执行，高风险动作需要人工确认。

`SessionStore`：保存一次运行的 trace，支持回放和复盘。

`DemoPolicy / Planner`：规划下一步 ToolCall。

`Harness.run()`：串起任务接收、计划、权限、执行、观察和 trace。

`RAG`：先检索证据，再基于证据回答。

`Citation / Evidence`：让回答或结论可追溯。

`Memory`：跨运行保存可复用经验，不等于 trace。

`Reflection`：基于状态检查证据不足、冲突和失败，并决定是否补查。

`Multi-agent coordination`：职责边界、schema、supervisor、停止条件。

`Skill`：可复用流程知识包，不是单个函数。

`Browser agent`：能观察页面 DOM/截图/动作日志的 agent。

`Eval`：固定任务集和指标，用于证明 agent 是否稳定变好。

`Observability`：让失败可定位，而不是只知道最终结果错了。

`Ship`：让 agent 可运行、可复现、可测试、可观测、可交付。

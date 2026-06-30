# Stage 1-8 代码学习与补全手册

这份手册不是单纯背考点，而是带你沿着本地代码把 Agent 的关键能力一层层补出来。推荐方式是：先读概念，再定位代码，再亲手改一个小点，最后用测试验证。你需要反复在「代码 - 运行 - trace - 测试 - 复盘」之间来回走，这样面试时讲出来的不是术语，而是你真的搭过的工程链路。

本手册对应的本地目录：

```bash
cd "/Users/lixinru02/Documents/ai study/Agent-Learning-Hub"
```

全量自检命令：

```bash
python3 -m unittest discover -s tests
```

## 总学习路线

Stage 1-8 可以看成一条逐步变完整的 Agent 工程路线：

| Stage | 本地代码 | 你要掌握的核心问题 |
| --- | --- | --- |
| Stage 0 | `practice/stage0_agent_mindset/agent_mindset.py` | 什么时候真的需要 agent，什么时候 script/workflow/chatbot 更合适 |
| Stage 1 | `practice/stage1_minimal_agent/minimal_agent.py` | agent loop 如何完成 observe -> think -> act -> observe |
| Stage 2 | `practice/stage2_rag_memory/rag_memory.py` | RAG 如何先检索证据再回答，memory 和 trace 有什么区别 |
| Stage 3 | `practice/stage3_harness/harness_demo.py` | harness 如何管理工具、权限、session、trace 和预算 |
| Stage 4 | `practice/stage4_multi_agent/multi_agent_pipeline.py` | multi-agent 的重点为什么是职责边界和 supervisor，而不是角色聊天 |
| Stage 5 | `practice/stage5_skills_protocols/skill_runner.py` | skill 如何把流程知识、模板和验收标准打包复用 |
| Stage 6 | `practice/stage6_browser_agent/browser_info_agent.py` | browser agent 如何观察页面、解析 DOM、记录动作 |
| Stage 7 | `practice/stage7_eval_observability/eval_runner.py` | eval 和 observability 如何证明 agent 变好了 |
| Stage 8 | `practice/stage8_ship_real_agent/personal_research_agent.py` | 如何把前面能力打包成可交付 CLI agent |

建议你每学一个 stage 都问自己 5 个问题：

1. 输入是什么？
2. 状态放在哪里？
3. 工具/模块的输入输出 schema 是什么？
4. 失败会被记录在哪里？
5. 最终结果为什么可信、可复盘、可测试？

## Stage 0: Agent Mindset

对应代码：`practice/stage0_agent_mindset/agent_mindset.py`

### 你要先理解什么

不是所有带大模型的东西都叫 agent。判断一个任务需不需要 agent，关键看它有没有这些特征：

- 下一步动作是否依赖观察结果。
- 是否需要搜索、检索、调研、debug、修复这类不确定路径。
- 是否需要调用工具并根据工具返回继续调整计划。
- 是否需要权限边界，因为某些动作可能删除、提交、支付、发布或修改线上内容。

代码里的 `classify_task()` 就是在做这个判断。它不是智能模型，而是用关键词打分模拟决策：

```python
score_agent = _score(task, AGENT_KEYWORDS)
score_workflow = _score(task, WORKFLOW_KEYWORDS)
score_script = _score(lowered, SCRIPT_KEYWORDS)
score_chatbot = _score(task, CHATBOT_KEYWORDS)
```

### 核心定义

`script`：确定性输入输出，路径固定，比如批量改名、字段清洗、简单统计。

`workflow`：固定流程编排，步骤相对稳定，比如审批、定时发报表、表单流转。

`chatbot`：主要做对话、解释、翻译、润色，不一定需要工具和状态循环。

`agent`：面对不确定任务，能观察环境、选择动作、调用工具、读取结果，并根据结果决定下一步。

### 动手补全任务

先运行：

```bash
python3 practice/stage0_agent_mindset/agent_mindset.py "调研 agent harness，根据搜索结果生成报告"
python3 practice/stage0_agent_mindset/agent_mindset.py "把 csv 字段批量清洗成 json"
python3 practice/stage0_agent_mindset/agent_mindset.py "解释 agent loop 是什么"
```

你要观察输出里的：

- `recommended_pattern`
- `uncertainty_sources`
- `human_approval_needed`
- `first_design_step`

补全练习：

1. 给 `AGENT_KEYWORDS` 增加「复盘」「补查」「归因」。
2. 给 `RISK_KEYWORDS` 增加「写入数据库」或「修改配置」。
3. 新增一个测试：输入「异常归因需要补查证据」，应被判断为 `agent`。

你要掌握的面试表达：

> 我不会默认把所有任务都做成 agent。先判断任务是否有不确定性、是否需要根据观察结果动态选择下一步、是否需要工具调用和权限边界。如果路径固定，script 或 workflow 更简单可靠；如果需要观察-行动循环，才进入 agent 设计。

## Stage 1: Minimal Agent Loop

对应代码：`practice/stage1_minimal_agent/minimal_agent.py`

### Agent loop 是什么

Agent loop 不是一句「循环调用模型」就完了。它的本质是：

```text
observe -> think -> act -> observe -> ... -> final answer
```

在本地代码里对应关系是：

| Agent loop 概念 | 本地代码 |
| --- | --- |
| observe 用户输入 | `Agent.run(user_input)` 的参数 |
| think 决策下一步 | `RuleBasedModel.next_action()` |
| act 结构化动作 | `ToolCall(name, arguments)` |
| tool execution | `ToolRegistry.call()` |
| observe 工具结果 | `ToolResult(ok, content)` |
| trace | `AgentStep(thought, action, observation)` |
| stop condition | `final_answer is not None` 或 `max_steps` |

最关键的不是「循环」两个字，而是：每一步都根据 observation 决定下一步。

### 关键数据结构

`ToolCall` 是 agent 想做的动作：

```python
@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: dict[str, Any]
```

它的意义是：模型不能只说「我想算一下」，而要输出机器可执行的结构化动作：

```json
{
  "name": "calculator",
  "arguments": {
    "expression": "23 * 7 + 10"
  }
}
```

`ToolResult` 是工具返回的 observation：

```python
@dataclass(frozen=True)
class ToolResult:
    ok: bool
    content: str
```

`AgentStep` 是 trace 的一行：

```python
@dataclass(frozen=True)
class AgentStep:
    thought: str
    action: ToolCall | None
    observation: ToolResult | None
```

这三个结构连起来，就形成了最小可追踪 agent。

### Tool schema 是什么

本地代码里的 `ToolSpec.schema()` 模拟了真实 LLM tool calling 的 schema：

```python
def schema(self) -> dict[str, Any]:
    return {
        "name": self.name,
        "description": self.description,
        "parameters": self.parameters,
    }
```

所谓「模型根据工具 schema 自动输出」，意思是你把工具说明书交给模型：

- 工具名是什么。
- 工具能做什么。
- 参数有哪些字段。
- 每个字段是什么类型。
- 哪些字段必填。

然后模型不再只输出自然语言，而是输出结构化 `ToolCall`。程序再拿这个 `ToolCall` 去 registry 里找到函数执行。

### 为什么有 `"uppercase" in lowered or "upper case" in lowered`

代码里有：

```python
lowered = text.lower()
if "大写" in text or "uppercase" in lowered or "upper case" in lowered:
```

含义是：用户可能用中文说「转成大写」，也可能用英文说 `uppercase` 或 `upper case`。`lowered = text.lower()` 是为了忽略英文大小写差异，比如：

- `uppercase`
- `Uppercase`
- `UPPERCASE`
- `upper case`
- `Upper Case`

它们统一转成小写后都能匹配。

这个判断的核心不是英语，而是「意图识别」。真实 LLM 场景里，这一步通常由模型根据 tool schema 决定；本地练习用规则模拟。

### 为什么可以复用 `_extract_count_target`

`_extract_count_target()` 的作用不是只服务 word count，而是提取冒号后的目标文本：

```python
for marker in ["：", ":", "内容是", "text is"]:
    if marker in text:
        return text.split(marker, 1)[1].strip()
return text
```

所以这些任务都能复用它：

- `统计字数：我正在学习 agent loop`
- `统计句子数：我在学 agent。它会调用 tools。`
- `转成大写：hello agent loop`

它抽取的是「要处理的文本」，不是「要统计的文本」。因此复用是合理的。

### 运行与观察

```bash
python3 practice/stage1_minimal_agent/minimal_agent.py "计算 23 * 7 + 10"
python3 practice/stage1_minimal_agent/minimal_agent.py "计算 23 **"
python3 practice/stage1_minimal_agent/minimal_agent.py "查一下 unknown concept"
python3 practice/stage1_minimal_agent/minimal_agent.py "请阅读 ../README.md"
python3 practice/stage1_minimal_agent/minimal_agent.py "统计字数：我正在学习 agent loop"
python3 practice/stage1_minimal_agent/minimal_agent.py "转成大写：hello agent loop" --trace-json trace.json
```

你要重点看：

- 工具成功时，下一步如何把 observation 变成 final answer。
- 工具失败时，为什么停止并报告失败。
- 读取 `../README.md` 为什么被拒绝，这是权限边界。
- `trace.json` 如何记录每一步。

### 动手补全任务

练习 1：新增 `reverse_text` 工具。

你要补的位置：

1. 写 `reverse_text_tool(arguments)`。
2. 在 `RuleBasedModel.next_action()` 增加触发规则。
3. 在 `build_agent()` 注册 `ToolSpec`。
4. 在 `tests/test_stage1_minimal_agent.py` 增加测试。

建议命令：

```bash
python3 practice/stage1_minimal_agent/minimal_agent.py "反转文本：hello"
python3 -m unittest tests/test_stage1_minimal_agent.py
```

练习 2：让 agent 在工具失败后尝试一次修正。

现在的逻辑是：

```python
if observation.ok:
    return ..., None, observation.content.strip()
return ..., None, f"工具调用失败：{observation.content}"
```

你可以思考：如果 calculator 因为表达式为空失败，要不要让模型重新抽取表达式？这就是 reflection/retry 的雏形。

你要掌握的面试表达：

> Stage 1 让我理解 agent loop 的最小闭环：模型产生结构化 ToolCall，ToolRegistry 执行工具，ToolResult 作为 observation 回到下一轮，AgentStep 形成 trace，最后由停止条件控制结束。这个结构比单次 prompt 更可控，因为每一步都可审计、可测试。

## Stage 2: RAG 和 Memory

对应代码：`practice/stage2_rag_memory/rag_memory.py`

### RAG 的真实链路

RAG 不是「把文档塞进 prompt」。本地代码拆成了这些步骤：

```text
load_documents -> chunk_text -> tokenize -> vectorize -> search -> grounded answer -> citations -> memory
```

对应代码：

| 步骤 | 本地代码 |
| --- | --- |
| 加载文档 | `load_documents(docs_dir)` |
| 文档切块 | `chunk_text(source, text, max_chars=360)` |
| 分词 | `tokenize(text)` |
| 建索引 | `TermRetriever.__init__()` |
| 检索 | `TermRetriever.search(query, top_k=3)` |
| 生成引用答案 | `ResearchAssistant.answer()` |
| 保存记忆 | `MemoryStore.add()` |

### 核心定义

`chunk`：文档切出来的小块。每个 chunk 要保留来源和 chunk id，才能引用。

`retrieval`：根据问题找相关证据。这里用词频向量和 cosine similarity 模拟，真实项目可换 embedding。

`grounded answer`：基于证据回答。如果没有证据，就明确说知识库不足，而不是编。

`citation`：引用来源，比如 `agent_notes.md#chunk-2`。

`memory`：跨运行保存的可复用信息，例如历史问答、结论、用户偏好、bad case 经验。

`trace`：一次运行过程的记录，用来 debug。它不等于 memory。

### Memory 和 Trace 的区别

| 维度 | trace | memory |
| --- | --- | --- |
| 生命周期 | 单次运行 | 跨运行 |
| 目标 | debug 和复盘 | 复用经验 |
| 内容 | 每一步动作、结果、时间 | 可复用事实、偏好、结论 |
| 风险 | 日志过多 | 错误记忆污染后续任务 |

你的异常归因项目里，工具调用结果和反思日志更像 trace；经过复核的归因结论、典型 bad case、可复用规则更适合进 memory。

### 运行与观察

```bash
python3 practice/stage2_rag_memory/rag_memory.py "Agent harness 为什么重要？"
python3 practice/stage2_rag_memory/rag_memory.py "Evaluation 能帮助 agent 发现什么问题？"
python3 practice/stage2_rag_memory/rag_memory.py "memory 在 agent 中解决什么问题？" --memory memory.json
```

观察输出：

- `retrieved` 里有哪些 chunk。
- `score` 为什么高或低。
- `citations` 是否为空。
- `memory.json` 是否保存了历史问答。

### 动手补全任务

练习 1：调整 `chunk_text(max_chars)`。

把 360 改成 120 或 800，观察检索结果。你要理解 chunk 太小和太大的代价：

- 太小：语义不完整，答案碎。
- 太大：召回不精确，噪声多。

练习 2：给 `MemoryStore` 增加 `find_by_keyword(keyword)`。

你要补：

1. 遍历 `self.items`。
2. 在 question/answer 里匹配 keyword。
3. 返回最近几条。
4. 写测试验证。

练习 3：当没有 retrieved 时，把失败也写入 memory，并标记 `citations=[]`。

这对应真实 agent 的 bad case 沉淀。

你要掌握的面试表达：

> RAG 的关键是先找证据再回答。我的实现里每个 chunk 有 source 和 chunk id，检索结果带 score，回答带 citation；没有证据时明确拒答。memory 只保存可复用信息，不把所有 trace 都塞进去，避免错误和噪声污染长期上下文。

## Stage 3: Agent Harness

对应代码：`practice/stage3_harness/harness_demo.py`

### Harness 是什么

Harness 是模型外面的工程运行层。它不等于模型，也不等于 prompt。它负责让 agent 的动作可控、可观测、可恢复。

本地代码里的 harness 包含：

| 组件 | 作用 |
| --- | --- |
| `ToolRegistry` | 管 agent 可以调用哪些工具 |
| `PermissionGate` | 判断工具是否需要人工批准 |
| `SessionStore` | 把 trace 写入文件 |
| `DemoPolicy` | 模拟模型/策略，规划 tool call |
| `Harness.run()` | 串起任务、计划、权限、执行、观察 |

### 为什么 Stage 3 比 Stage 1 更接近真实工程

Stage 1 里所有逻辑在一个 agent loop 里。Stage 3 开始把职责拆开：

- registry 管工具目录。
- permission gate 管风险。
- session store 管状态和 trace。
- policy 负责规划。
- harness 负责调度。

这就是工程化的关键：每个模块边界清楚，才能测试、替换、扩展。

### 运行与观察

```bash
python3 practice/stage3_harness/harness_demo.py "search agent harness"
python3 practice/stage3_harness/harness_demo.py "count Agent harness manages tools and trace"
python3 practice/stage3_harness/harness_demo.py "please read file"
```

观察：

- `trace.json` 里是否记录 `task_received`。
- 工具调用前是否有 `permission_checked`。
- `read_file` 为什么会被拒绝，因为它是 risky tool。

### 动手补全任务

练习 1：新增 `uppercase` 工具。

你要补：

1. 写 `uppercase(arguments)`。
2. `registry.register(ToolSpec("uppercase", ..., False, uppercase))`。
3. 在 `DemoPolicy.plan()` 里识别 `uppercase ` 开头。
4. 增加测试。

关键代码解释：

```python
if lowered.startswith("uppercase "):
    return [ToolCall("uppercase", {"text": task.removeprefix("uppercase ").strip()})]
```

这句话的意思是：如果用户输入以 `uppercase ` 开头，就把后面的内容当成工具参数 `text`。`removeprefix()` 负责去掉命令前缀，`.strip()` 去掉多余空格。

练习 2：给 `Harness` 增加 `max_tool_calls` 的测试。

真实 agent 必须有预算限制，否则模型可能不断调用工具，造成成本和风险。

你要掌握的面试表达：

> Harness 是 agent 的工程外壳。模型只负责提出动作，但动作是否存在、是否允许、怎么执行、怎么记录、失败怎么恢复，都应该由 harness 管。这样 agent 才能从 demo 走向可审计、可控的系统。

## Stage 4: Multi-Agent Coordination

对应代码：`practice/stage4_multi_agent/multi_agent_pipeline.py`

### Multi-agent 不是多角色聊天

本地代码里有四个 agent：

| Agent | 输入 | 输出 |
| --- | --- | --- |
| `ResearcherAgent` | topic | `ResearchBrief` |
| `WriterAgent` | `ResearchBrief` | `Draft` |
| `ReviewerAgent` | `Draft` | `Review` |
| `ReviserAgent` | `Draft + Review` | `Draft` |

真正重要的是：

- 每个 agent 职责单一。
- 每个 agent 输入输出结构明确。
- supervisor 控制流转顺序。
- reviewer 给出可执行反馈。
- reviser 根据 feedback 修订。
- 最终还要再 review 一次。

### 运行与观察

```bash
python3 practice/stage4_multi_agent/multi_agent_pipeline.py "agent evaluation"
```

观察输出里的 `trace`：

- researcher 输出了哪些 facts。
- writer 是否把 facts 写成 draft。
- reviewer 是否通过。
- reviser 是否补充内容。
- final review 是否通过。

### 动手补全任务

练习 1：让 `ReviewerAgent` 检查是否包含「下一步行动」。

你要补：

```python
if "下一步" not in draft.body:
    issues.append("缺少下一步行动。")
```

然后让 `ReviserAgent` 在没通过时补上。

练习 2：增加最大修订轮数。

现在 supervisor 只修一次。真实 multi-agent 需要循环，但必须有停止条件：

```text
review -> if failed -> revise -> review -> ... -> max_rounds
```

你要掌握的面试表达：

> Multi-agent 的难点不是起很多角色名，而是职责边界、输入输出 schema、supervisor 控制和停止条件。如果没有结构化输出和停止条件，多 agent 很容易变成上下文膨胀和无限争论。

## Stage 5: Skills 和 Protocols

对应代码：`practice/stage5_skills_protocols/skill_runner.py`

Skill 文件：`practice/stage5_skills_protocols/skills/research_summary/SKILL.md`

模板文件：`practice/stage5_skills_protocols/skills/research_summary/templates/summary.md`

### Skill 是什么

Tool 是一个函数，Skill 是一套可复用流程知识。一个好 skill 通常包含：

- 适用场景。
- 操作步骤。
- 模板。
- 验收标准。
- smoke test。

本地代码的 `load_skill()` 做了三件事：

1. 读取 `SKILL.md`。
2. 读取模板 `summary.md`。
3. 解析 name、description、checks。

`run_skill()` 做了两件事：

1. 把输入文本填进模板。
2. 根据 checks 做简单验收。

### Skill、Tool、MCP 的区别

| 概念 | 你可以这样理解 |
| --- | --- |
| Tool | 可被调用的函数，比如 search、read_file、calculator |
| Skill | 可复用的方法包，比如「如何写研究摘要」 |
| MCP | 连接外部工具和数据源的协议层 |
| Prompt | 单次指令，不一定包含流程、模板、验收 |

### 运行与观察

```bash
python3 practice/stage5_skills_protocols/skill_runner.py "Agent loop observes. It calls tools. It records trace."
```

观察：

- `output` 是否使用模板。
- `passed_checks` 里有哪些验收通过。
- `failed_checks` 说明哪些能力还不满足。

### 动手补全任务

练习 1：在 `SKILL.md` 增加一条验收：

```text
- must include risk
```

然后在模板里增加 `Risk:` 段落，并修改 `run_skill()` 让它通过。

练习 2：把你的异常归因流程写成一个 skill。

可以包含：

- 输入：异常描述。
- 步骤：规划、查证据、校验证据、反思补查、生成报告。
- 模板：归因报告模板。
- 验收：必须包含证据链、置信度、bad case 标记。

你要掌握的面试表达：

> Skill 不是简单 prompt，而是把可复用流程知识、模板和验收标准打包。它能让 agent 在类似任务上更稳定，而 MCP 更偏连接外部工具和数据源，两者不是同一层东西。

## Stage 6: Browser Agent

对应代码：`practice/stage6_browser_agent/browser_info_agent.py`

页面示例：`practice/stage6_browser_agent/pages/sample.html`

### Browser agent 的观察来源

真实 browser agent 可以观察：

- DOM 结构。
- 页面文本。
- 链接和按钮。
- 截图。
- 网络请求。
- action log。

本地代码用 `HTMLParser` 模拟 DOM 解析。`LocalPageAgent.inspect()` 的流程是：

```text
open path -> read_html -> parse_dom -> summarize
```

它最后返回：

- title
- headings
- links
- text_preview
- action_log

### DOM 和截图分别解决什么

DOM 适合结构化提取，例如标题、表格、链接、按钮属性。

截图适合视觉校验，例如元素是否遮挡、页面是否真的渲染、图表是否可读。

真实项目通常两者都要：DOM 用来操作和抽取，截图用来确认视觉状态。

### 运行与观察

```bash
python3 practice/stage6_browser_agent/browser_info_agent.py practice/stage6_browser_agent/pages/sample.html
```

观察：

- `headings` 是否解析出页面标题。
- `links` 是否把相对路径转成绝对 URI。
- `action_log` 是否记录打开、读取、解析、总结。

### 动手补全任务

练习 1：解析按钮。

新增：

```python
@dataclass(frozen=True)
class Button:
    text: str
```

然后在 `PageParser` 中收集 `<button>` 文本。

练习 2：增加安全规则。

如果链接文本包含「提交」「删除」「支付」「发布」，在 `action_log` 增加 `requires_approval`。

你要掌握的面试表达：

> Browser agent 的关键是观察和动作都要可记录。DOM 适合结构化信息，截图适合视觉校验。对于提交、支付、发布、删除等外部影响动作，必须有权限确认和动作日志。

## Stage 7: Evaluation 和 Observability

对应代码：`practice/stage7_eval_observability/eval_runner.py`

Eval 数据：`practice/stage7_eval_observability/evals/stage1_cases.json`

### 为什么 agent 必须做 eval

Demo 只能证明「某一次看起来能跑」。Eval 才能证明「在固定任务集上稳定变好」。

本地 eval 的结构是：

```text
load_cases -> run_eval -> serialize_trace -> summarize
```

每个 `EvalCase` 包含：

- `id`
- `task`
- `expected_contains`
- `category`

每个 `EvalResult` 包含：

- 是否通过。
- 期望包含什么。
- 实际输出是什么。
- 失败分类。
- trace。

### Observability 观察什么

Agent 的 observability 不只是打印日志，而是要能定位失败来源：

- prompt/策略错。
- 工具选择错。
- 工具参数错。
- 工具执行失败。
- 检索召回不足。
- 状态丢失。
- 反思没有触发。
- 最终报告过度概括。

本地 `trace` 能帮助你看 Stage 1 每一步的 action 和 observation。

### 运行与观察

```bash
python3 practice/stage7_eval_observability/eval_runner.py
python3 practice/stage7_eval_observability/eval_runner.py --output results.json
python3 -m unittest tests/test_stage7_eval_observability.py
```

观察：

- `summary.total` 是否为 20。
- `summary.success_rate` 是否达标。
- 如果失败，`failure_category` 是什么。
- 单条 result 的 trace 能否定位原因。

### 动手补全任务

练习 1：新增一个 eval case。

比如测试 uppercase：

```json
{
  "id": "uppercase_zh",
  "task": "转成大写：hello agent loop",
  "expected_contains": "HELLO AGENT LOOP",
  "category": "tool_selection"
}
```

然后更新测试里对 total 的断言。

练习 2：在 summary 中增加失败率。

```python
"failure_rate": round(1 - passed / total, 3)
```

练习 3：给每条结果增加 `tool_call_count`。

这对应真实项目里统计成本和延迟。

你要掌握的面试表达：

> 我不会只看一次 demo。Agent 的可靠性要通过固定 eval 集、成功率、失败分类、trace 和工具调用统计来衡量。bad case 分析时，我会沿 trace 回看失败来自计划、工具、检索、状态、反思还是最终生成。

## Stage 8: Ship 一个真实 Agent

对应代码：`practice/stage8_ship_real_agent/personal_research_agent.py`

### Ship 不只是能跑一次

Stage 8 把 Stage 2 的 RAG 能力包装成一个可交付 CLI agent。它补上了：

- 明确用户：正在学习 agent 的你。
- 明确任务：基于本地资料回答问题。
- 权限边界：只读本地 `data/`。
- trace：记录问题、权限检查、检索、最终回答。
- 可测试：`tests/test_stage8_ship_real_agent.py`。

`PersonalResearchAgent.run()` 是核心：

```text
question_received -> permission_checked -> retrieval_completed -> final_answer
```

### 它和前面 stage 的关系

| 来源 | Stage 8 里怎么体现 |
| --- | --- |
| Stage 1 loop | 输入问题，执行检索，观察结果，输出答案 |
| Stage 2 RAG | 复用 `ResearchAssistant` |
| Stage 3 harness | trace 和 permission_checked |
| Stage 7 eval | 有单元测试，可继续接 eval runner |
| Stage 8 ship | CLI、README、数据目录、可复现命令 |

### 运行与观察

```bash
python3 practice/stage8_ship_real_agent/personal_research_agent.py "为什么 agent 项目需要评测？"
python3 practice/stage8_ship_real_agent/personal_research_agent.py "什么是 harness？" --trace traces/run.json
python3 -m unittest tests/test_stage8_ship_real_agent.py
```

观察：

- answer 是否带引用。
- citations 是否非空。
- trace 是否记录关键事件。
- `--trace` 是否保存文件。

### 动手补全任务

练习 1：增加知识库不足的 trace。

如果 citations 为空，trace 里增加：

```python
{"event": "insufficient_evidence", ...}
```

这会让 Stage 8 更像真实可观测系统。

练习 2：加入 memory。

把 Stage 2 的 `MemoryStore` 接到 Stage 8：

- CLI 增加 `--memory` 参数。
- `PersonalResearchAgent` 初始化时可传 memory。
- 测试验证 memory 文件写入。

练习 3：做一个异常归因版本。

结合你的简历项目，可以在 Stage 8 下新增 `attribution_agent.py`，核心状态可以是：

```python
@dataclass
class WorkflowState:
    abnormal_input: str
    execution_plan: list[str]
    tool_results: list[ToolResultRecord]
    evidence_chain: list[EvidenceItem]
    reflection_log: list[ReflectionDecision]
    final_conclusion: str
    bad_case_samples: list[str]
    memory_records: list[dict[str, object]]
```

它要覆盖：

- 任务规划。
- 工具执行。
- 证据校验。
- Self-Reflection 补查。
- 报告生成。
- bad case 和记忆沉淀。

这就是你简历里「异常归因场景下 Agent Harness 核心链路」的本地实操映射。

你要掌握的面试表达：

> Ship 阶段关注的是可复现、可测试、可观测和可回滚。一个 agent 能回答一次不算交付；要有 CLI/API、README、权限边界、trace、测试和失败分析入口，才能让别人复现并持续迭代。

## 把 Stage 1-8 串成你的项目故事

你的简历项目可以这样映射：

| 简历表达 | 对应 Stage | 代码中的影子 |
| --- | --- | --- |
| 任务规划 | Stage 1 / Stage 3 | `RuleBasedModel.next_action()`、`DemoPolicy.plan()` |
| 工具执行 | Stage 1 / Stage 3 | `ToolRegistry.call()`、`Harness.run()` |
| 证据校验 | Stage 2 / Stage 7 | `citations`、`retrieved`、`expected_contains` |
| Self-Reflection 补查 | Stage 4 / Stage 7 | `ReviewerAgent`、failure category、trace 回看 |
| 报告生成 | Stage 4 / Stage 8 | `WriterAgent`、`PersonalResearchAgent.run()` |
| WorkflowState | Stage 3 / Stage 8 | `SessionStore`、trace、可扩展 state container |
| 记忆保存 | Stage 2 | `MemoryStore` |
| bad case 分析 | Stage 7 | `EvalResult.failure_category`、trace |

你可以把项目讲成一条闭环：

> 输入异常后，系统先规划要查哪些证据，然后通过 harness 调用工具。每个工具结果会结构化写入状态，并形成 evidence chain。证据不足或冲突时进入反思补查，而不是直接输出结论。最终报告只引用状态中已有证据，生成可复核的归因结论。运行过程和 bad case 会被记录，为后续评测、复盘和记忆复用提供基础。

## 关键概念口袋卡

`Agent loop`：带状态地观察、决策、行动、再观察，直到满足停止条件。

`ToolCall`：模型选择的结构化动作，包含工具名和参数。

`ToolResult`：工具执行后的 observation，包含成功失败和内容。

`Tool schema`：工具说明书，让模型知道工具名、功能、参数类型和必填字段。

`ToolRegistry`：工具目录，负责根据 ToolCall 找到并执行工具。

`Trace`：一次运行的逐步记录，用于 debug、复盘和评测。

`Memory`：跨运行保存的可复用信息，不等于 trace。

`RAG`：先检索证据，再基于证据回答。

`Citation`：证据来源，用来支撑回答可追溯。

`Harness`：模型外的工程外壳，管理工具、权限、状态、trace、预算和恢复。

`PermissionGate`：权限门，拦截高风险动作。

`SessionStore`：保存一次运行的事件和状态。

`WorkflowState`：长任务状态容器，统一承载输入、计划、工具结果、证据链、反思决策和最终结论。

`Self-Reflection`：发现证据不足、冲突或失败后，主动补查、重试或调整计划。

`Multi-agent`：多个职责单一的模块/agent 在 supervisor 下协作。

`Skill`：可复用流程知识包，包含步骤、模板、脚本和验收标准。

`Eval`：固定任务集，用通过率、失败分类和 trace 证明 agent 是否变好。

`Observability`：让失败可定位，而不是只有「结果错了」。

`Ship`：把 agent 做到可运行、可复现、可测试、可观测、可交付。

## 建议你按这个节奏学习

第一轮，只运行，不改代码：

```bash
python3 practice/stage0_agent_mindset/agent_mindset.py "异常归因需要检索证据并补查"
python3 practice/stage1_minimal_agent/minimal_agent.py "转成大写：hello agent loop" --trace-json trace.json
python3 practice/stage2_rag_memory/rag_memory.py "Evaluation 能帮助 agent 发现什么问题？"
python3 practice/stage3_harness/harness_demo.py "search agent harness"
python3 practice/stage4_multi_agent/multi_agent_pipeline.py "agent evaluation"
python3 practice/stage5_skills_protocols/skill_runner.py "Agent loop observes. It calls tools. It records trace."
python3 practice/stage6_browser_agent/browser_info_agent.py practice/stage6_browser_agent/pages/sample.html
python3 practice/stage7_eval_observability/eval_runner.py
python3 practice/stage8_ship_real_agent/personal_research_agent.py "为什么 agent 项目需要评测？"
```

第二轮，只补小功能：

- Stage 1 补 `reverse_text`。
- Stage 2 补 `MemoryStore.find_by_keyword()`。
- Stage 3 补 `uppercase`。
- Stage 4 补 reviewer 的「下一步行动」检查。
- Stage 5 补 `risk` 验收。
- Stage 6 补 button 解析。
- Stage 7 补 uppercase eval case。
- Stage 8 补 insufficient evidence trace。

第三轮，做项目化整合：

- 把 Stage 3 的 harness 思路和 Stage 2 的 evidence/memory 结合。
- 增加一个 `WorkflowState`。
- 让工具结果进入 `tool_results`。
- 让检索结果进入 `evidence_chain`。
- 让失败和冲突进入 `reflection_log`。
- 让最终答案从 state 生成报告。
- 用 Stage 7 的 eval 固定回归。

## 面试时不要这样讲

不要说：

> 我做了一个 agent，就是让大模型自动调用工具。

更好的说法：

> 我做的是一个可追踪的 Agent loop。模型或策略输出结构化 ToolCall，harness 负责权限、工具执行、trace 和状态更新。工具结果作为 observation 回到下一轮，证据不足时触发补查，最终报告从结构化状态中生成，所以能复核、能评测、能做 bad case 分析。

不要说：

> Memory 就是把历史聊天记录存起来。

更好的说法：

> Trace 记录单次运行，memory 保存跨运行可复用经验。长期记忆应该保存经过验证的结论、偏好、归因模式和 bad case，而不是把所有中间日志都塞进去。

不要说：

> Multi-agent 就是多个 agent 互相讨论。

更好的说法：

> Multi-agent 的工程重点是职责边界、输入输出 schema、supervisor 和停止条件。否则很容易上下文膨胀、循环争论，反而降低稳定性。

## 最后自测

学完后，你应该能不用看笔记回答这些问题：

1. Agent loop 的关键是什么？
2. ToolCall 和 ToolResult 分别解决什么问题？
3. tool schema 为什么能让模型输出结构化动作？
4. trace 和 memory 的区别是什么？
5. RAG 为什么必须带 citation？
6. harness 管哪些事情？
7. PermissionGate 为什么不能放在模型自由发挥里？
8. WorkflowState 为什么比 messages 更适合长任务？
9. Self-Reflection 什么时候触发？
10. bad case 应该如何定位失败来源？
11. multi-agent 的停止条件怎么设计？
12. skill 和 tool 有什么区别？
13. browser agent 为什么要记录 action log？
14. eval 如何证明 agent 变好了？
15. 一个 agent 达到 ship 标准需要哪些东西？

如果这些问题你能结合本地代码讲出来，Stage 1-8 就不是背过，而是真的进脑子了。

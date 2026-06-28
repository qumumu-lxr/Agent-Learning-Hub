# Stage 1: 最小 Agent Loop

目标：用 100 行左右的 Python 代码理解一个 agent 如何选择工具、执行工具、观察结果并返回最终答案。

这个练习默认不依赖真实 LLM API。`RuleBasedModel` 用简单规则模拟“模型思考”，这样你可以先专注理解 agent loop 的工程骨架。

## 运行

```bash
cd "/Users/lixinru02/Documents/ai study/Agent-Learning-Hub/practice/stage1_minimal_agent"
python3 minimal_agent.py "计算 23 * 7 + 10"
python3 minimal_agent.py "请阅读 notes.txt 并总结"
python3 minimal_agent.py "查一下 agent loop 是什么"
python3 minimal_agent.py "统计字数：Agent loop 需要 tools, trace 和 stop condition"
```

## 你会看到什么

程序会打印 trace，每一步包含：

- `thought`: agent 为什么要这么做。
- `action`: agent 要执行的结构化动作。
- `observation`: 工具返回的结果。

最后打印 `Final Answer`。

## 文件说明

- `minimal_agent.py`: 主程序，包含工具、工具注册表、规则模型、agent loop。
- `notes.txt`: read_file 工具的示例输入文件。

## 建议练习

1. 给 `calculator` 传一个错误表达式，例如 `23 **`，观察错误如何进入 trace。
2. 修改 `word_count` 工具，让它同时返回句子数或标点数量。
3. 把 `max_steps` 改成 1，观察 agent 为什么无法完成需要工具的任务。
4. 把 `RuleBasedModel` 替换成真实 LLM tool calling。

## 关键代码阅读顺序

1. `ToolCall` 和 `ToolResult`: 结构化动作和工具返回值。
2. `ToolRegistry`: 工具注册与调用入口。
3. `RuleBasedModel.next_action`: 模拟模型如何根据用户输入和观察结果决定下一步。
4. `Agent.run`: 真正的 observe -> think -> act -> observe 循环。

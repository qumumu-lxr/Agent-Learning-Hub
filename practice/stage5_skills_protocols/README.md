# Stage 5: Skills、MCP、A2A、ACP

目标：理解 tool、skill、protocol 的边界。

- Tool: 一个函数，例如 `read_file(path)`。
- Skill: 一套完成任务的方法，包含说明、脚本、模板和验收标准。
- MCP: 让 agent 连接外部工具和数据源的协议。
- A2A: agent 之间的协作通信协议。
- ACP: 宿主应用和 agent 的交互协议。

本练习写了一个最小 skill runner，读取 `skills/research_summary/SKILL.md` 并执行 smoke test。

## 运行

```bash
cd "/Users/lixinru02/Documents/ai study/Agent-Learning-Hub/practice/stage5_skills_protocols"
python3 skill_runner.py "agent harness helps reliability"
```

## 练习

1. 修改 `SKILL.md` 的验收标准。
2. 新增一个模板文件，并在 runner 中加载它。
3. 思考：这个 skill 如果要通过 MCP 调外部搜索，应把协议边界放在哪里？


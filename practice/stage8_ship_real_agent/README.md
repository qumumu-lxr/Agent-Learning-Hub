# Stage 8: Ship 一个真实 Agent

目标：把前面学到的能力打包成一个可复现的小项目。

这里的最终项目是“本地 Agent 学习资料助手”：

- 用户：正在学习 Agent 的你。
- 任务：基于本地资料回答 Agent 学习问题。
- 成功标准：回答有引用、可记录 trace、知识库不足时明确说明。
- 部署方式：CLI。
- 权限边界：只读取 `data/` 下的 Markdown 文件。

## 运行

```bash
cd "/Users/lixinru02/Documents/ai study/Agent-Learning-Hub/practice/stage8_ship_real_agent"
python3 personal_research_agent.py "为什么 agent 项目需要评测？"
python3 personal_research_agent.py "什么是 harness？" --trace traces/run.json
```

## 下一步升级

1. 把 Stage 2 的词频检索替换成 embedding。
2. 接入真实 LLM，把证据改写成更自然的回答。
3. 加 Web UI 或定时任务。
4. 用 Stage 7 的 eval runner 固定回归测试。


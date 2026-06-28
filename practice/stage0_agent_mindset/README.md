# Stage 0: Agent 心智模型

目标：先学会判断一个任务到底需不需要 agent。

很多失败的 agent 项目不是模型不够强，而是任务本来只需要一个普通脚本、固定 workflow 或一次性问答。这个 stage 训练你把任务拆成：不确定性、外部动作、反馈循环、权限风险和成功标准。

## 运行

```bash
cd "/Users/lixinru02/Documents/ai study/Agent-Learning-Hub/practice/stage0_agent_mindset"
python3 agent_mindset.py "读取本地资料，找证据，总结 agent harness 为什么重要"
python3 agent_mindset.py "把 CSV 的 price 字段乘以 1.08"
python3 agent_mindset.py "帮我规划并多轮修改一篇调研报告"
```

## 你要观察什么

- `recommended_pattern`: 更适合 chatbot、workflow、script 还是 agent。
- `uncertainty_sources`: 不确定性来自哪里。
- `human_approval_needed`: 哪些动作需要人确认。
- `first_design_step`: 真要做时第一步该怎么搭。

## 练习

1. 把你自己的一个任务丢进去，看它是否真的需要 agent。
2. 修改 `RISK_KEYWORDS`，加入你关心的高风险动作。
3. 为一个任务写下成功标准，再判断是否能被自动评测。


# Stage 4: Multi-Agent 协调

目标：理解 multi-agent 的重点是协调，不是“多几个角色聊天”。

这个练习实现一个固定 supervisor pipeline：

```text
researcher -> writer -> reviewer -> reviser
```

每个 agent 都有清晰输入输出，supervisor 负责顺序、停止条件和最终交付。

## 运行

```bash
cd "/Users/lixinru02/Documents/ai study/Agent-Learning-Hub/practice/stage4_multi_agent"
python3 multi_agent_pipeline.py "为什么 agent 需要 eval？"
```

## 练习

1. 给 `ReviewerAgent` 加一个新检查项，例如“是否有引用”。
2. 故意让 `WriterAgent` 输出很短的内容，观察 reviewer 如何指出问题。
3. 思考：如果 reviewer 和 writer 循环争论，supervisor 应该如何设置最大轮数？


# Stage 7: Evaluation、Observability 和 Safety

目标：别再靠“跑一个 demo 看起来还行”判断 agent 好坏。

这个练习准备了 20 条固定任务，运行 Stage 1 agent，并输出成功率、失败分类和 trace 路径。

## 运行

```bash
cd "/Users/lixinru02/Documents/ai study/Agent-Learning-Hub/practice/stage7_eval_observability"
python3 eval_runner.py
```

## 输出

- `summary`: 总数、通过数、成功率。
- `results`: 每条任务的期望、实际、是否通过、失败分类。
- `trace`: 每条任务的工具调用轨迹。

## 练习

1. 新增 5 条失败用例。
2. 把失败分类改得更细，例如 `tool_error`、`retrieval_miss`、`policy_error`。
3. 统计平均工具调用次数。


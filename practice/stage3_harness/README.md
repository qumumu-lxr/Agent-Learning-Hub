# Stage 3: Modern Agent Harness

目标：把 Stage 1 的“一个文件 agent”拆成更接近真实工程的 harness。

Harness 不是某个框架名字，而是围绕模型的工程外壳：工具注册、权限、session、trace、错误处理、预算和恢复。

## 运行

```bash
cd "/Users/lixinru02/Documents/ai study/Agent-Learning-Hub/practice/stage3_harness"
python3 harness_demo.py "search agent harness"
python3 harness_demo.py "count Agent harness manages tools and trace"
```

## 你要看懂的模块

- `ToolRegistry`: 工具能力目录。
- `PermissionGate`: 对敏感工具进行权限判断。
- `SessionStore`: 保存每次运行的 trace。
- `Harness.run`: 把 model policy、tool call、trace 连接起来。

## 练习

1. 新增一个 `uppercase` 工具，并注册到 harness。
2. 把 `PermissionGate` 改成拒绝所有 `read_file`。
3. 对比 Stage 1：同样是工具调用，为什么 harness 更适合长任务？


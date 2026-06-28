# Stage 6: Browser 和 Computer-Use Agents

目标：理解浏览器 agent 不是“能点网页”这么简单，而是要记录动作、处理页面变化，并遵守权限边界。

这个练习用标准库解析本地 HTML，模拟浏览器 agent 的信息提取流程。真实项目里可以把 `LocalPageAgent` 换成 Playwright 或浏览器工具。

## 运行

```bash
cd "/Users/lixinru02/Documents/ai study/Agent-Learning-Hub/practice/stage6_browser_agent"
python3 browser_info_agent.py pages/sample.html
```

输出包含标题、链接、页面文本摘要和动作日志。

## 练习

1. 在 `sample.html` 加一个新链接，观察提取结果。
2. 给 `PageParser` 增加表格提取。
3. 思考：哪些网页动作必须要求人确认？例如登录、付款、提交表单。


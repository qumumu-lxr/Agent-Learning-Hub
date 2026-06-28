# Stage 2: Tool Use、RAG 和 Memory

目标：做一个最小资料研究助手。它会读取本地文档、切 chunk、检索证据、生成带引用的回答，并把问答写入会话记忆。

这个版本不依赖 embedding API。先用词频向量模拟 retrieval，等你理解流程后再替换成真实 embedding。

## 运行

```bash
cd "/Users/lixinru02/Documents/ai study/Agent-Learning-Hub/practice/stage2_rag_memory"
python3 rag_memory.py "Agent harness 为什么重要？"
python3 rag_memory.py "memory 在 agent 中解决什么问题？" --memory memory.json
```

## 关键概念

- `chunk`: 文档切块，保留 source 和 chunk id。
- `retrieval`: 根据问题召回最相关证据。
- `grounded answer`: 回答只能基于证据，并带引用。
- `memory`: 记录历史问题、答案和引用，后续可用于个性化或连续任务。

## 练习

1. 修改 `chunk_text` 的 `max_chars`，观察召回结果变化。
2. 在 `docs/agent_notes.md` 加一段新知识，再问相关问题。
3. 把 `TermRetriever` 替换成真实 embedding 检索。


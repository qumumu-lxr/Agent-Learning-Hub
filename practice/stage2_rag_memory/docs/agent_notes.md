# Agent Notes

An agent loop repeatedly observes context, decides the next action, calls tools, and observes the result until it can produce a final answer.

An agent harness is the engineering layer around the model. It manages tool schemas, permissions, state, trace logs, retries, timeouts, and context compaction. Without a harness, a demo may work once but fail silently when tasks become longer or tools return unexpected results.

RAG means retrieval augmented generation. A RAG assistant should retrieve evidence before answering, keep citations, and make it clear when the local knowledge base does not contain enough information.

Memory is not one thing. Short-term memory keeps the current conversation coherent. Long-term memory stores durable facts or preferences. A trace is different from memory: trace is for debugging what happened during a run.


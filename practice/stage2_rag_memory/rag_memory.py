from __future__ import annotations

import argparse
import json
import math
import re
from dataclasses import asdict, dataclass
from pathlib import Path


TOKEN_RE = re.compile(r"[A-Za-z0-9]+|[\u4e00-\u9fff]")


@dataclass(frozen=True)
class Chunk:
    source: str
    chunk_id: int
    text: str

    @property
    def citation(self) -> str:
        return f"{self.source}#chunk-{self.chunk_id}"


@dataclass(frozen=True)
class RetrievedChunk:
    chunk: Chunk
    score: float


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


def load_documents(docs_dir: Path) -> list[Chunk]:
    chunks: list[Chunk] = []
    for path in sorted(docs_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        chunks.extend(chunk_text(path.name, text))
    return chunks


def chunk_text(source: str, text: str, max_chars: int = 360) -> list[Chunk]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    chunks: list[Chunk] = []
    buffer = ""
    for paragraph in paragraphs:
        if buffer and len(buffer) + len(paragraph) + 2 > max_chars:
            chunks.append(Chunk(source, len(chunks) + 1, buffer))
            buffer = paragraph
        else:
            buffer = f"{buffer}\n\n{paragraph}".strip()
    if buffer:
        chunks.append(Chunk(source, len(chunks) + 1, buffer))
    return chunks


class TermRetriever:
    def __init__(self, chunks: list[Chunk]) -> None:
        self.chunks = chunks
        self.vectors = [self._vectorize(chunk.text) for chunk in chunks]

    def search(self, query: str, top_k: int = 3) -> list[RetrievedChunk]:
        query_vector = self._vectorize(query)
        ranked = [
            RetrievedChunk(chunk, self._cosine(query_vector, vector))
            for chunk, vector in zip(self.chunks, self.vectors)
        ]
        return [item for item in sorted(ranked, key=lambda item: item.score, reverse=True)[:top_k] if item.score > 0]

    def _vectorize(self, text: str) -> dict[str, float]:
        vector: dict[str, float] = {}
        for token in tokenize(text):
            vector[token] = vector.get(token, 0.0) + 1.0
        return vector

    def _cosine(self, left: dict[str, float], right: dict[str, float]) -> float:
        dot = sum(value * right.get(token, 0.0) for token, value in left.items())
        left_norm = math.sqrt(sum(value * value for value in left.values()))
        right_norm = math.sqrt(sum(value * value for value in right.values()))
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return dot / (left_norm * right_norm)


class MemoryStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.items = self._load()

    def add(self, question: str, answer: str, citations: list[str]) -> None:
        self.items.append({"question": question, "answer": answer, "citations": citations})
        self.path.write_text(json.dumps(self.items, ensure_ascii=False, indent=2), encoding="utf-8")

    def recent(self, limit: int = 3) -> list[dict[str, object]]:
        return self.items[-limit:]

    def _load(self) -> list[dict[str, object]]:
        if not self.path.exists():
            return []
        return json.loads(self.path.read_text(encoding="utf-8"))


@dataclass(frozen=True)
class ResearchAnswer:
    question: str
    answer: str
    citations: list[str]
    retrieved: list[dict[str, object]]


class ResearchAssistant:
    def __init__(self, docs_dir: Path, memory: MemoryStore | None = None) -> None:
        self.retriever = TermRetriever(load_documents(docs_dir))
        self.memory = memory

    def answer(self, question: str) -> ResearchAnswer:
        retrieved = self.retriever.search(question)
        if not retrieved:
            answer = "本地知识库没有足够证据回答这个问题。"
            citations: list[str] = []
        else:
            evidence_sentences = [item.chunk.text.replace("\n", " ") for item in retrieved]
            citations = [item.chunk.citation for item in retrieved]
            answer = " ".join(evidence_sentences)
            answer += "\n\n引用：" + ", ".join(citations)

        if self.memory is not None:
            self.memory.add(question, answer, citations)

        return ResearchAnswer(
            question=question,
            answer=answer,
            citations=citations,
            retrieved=[
                {"citation": item.chunk.citation, "score": round(item.score, 4), "text": item.chunk.text}
                for item in retrieved
            ],
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a tiny local RAG assistant.")
    parser.add_argument("question")
    parser.add_argument("--docs", default="docs")
    parser.add_argument("--memory", default="")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent
    memory = MemoryStore(base_dir / args.memory) if args.memory else None
    assistant = ResearchAssistant(base_dir / args.docs, memory)
    result = assistant.answer(args.question)
    print(json.dumps(asdict(result), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

"""Grounded question-answering over UCSD CSE professor reviews.

Per planning.md, this is Milestone 5:
- Retrieve top-k chunks from ChromaDB (embed.py)
- Build a context block with one chunk per labeled section
- Call Groq llama-3.3-70b-versatile with a system prompt that strictly enforces
  answering only from the provided context
- Return answer + deduped list of source filenames (programmatic, not LLM-trusted)
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv
from groq import Groq

from embed import RetrievedChunk, _display_name, build_collection, retrieve
from ingest import load_chunks

load_dotenv()

LLM_MODEL = "llama-3.3-70b-versatile"
DEFAULT_TOP_K = 5

SYSTEM_PROMPT = """You are an assistant that answers questions about UCSD Computer Science & Engineering professors using ONLY the student reviews provided in the CONTEXT block below.

Rules — follow them exactly:
1. Answer ONLY from the CONTEXT. Do not use any prior knowledge about UCSD, the professors, or computer science courses.
2. If the CONTEXT does not contain enough information to answer the question, reply with exactly: "I don't have enough information on that."
3. Do not invent professor names, course numbers, dates, or quotes. If a detail isn't in the CONTEXT, don't mention it.
4. When the question names a specific professor, ground your answer in the reviews from that professor's file. If the CONTEXT only contains reviews about other professors, say so and decline.
5. Be concise. 2-4 sentences is usually enough. Quote sparingly and only from text that appears verbatim in the CONTEXT."""

USER_TEMPLATE = """CONTEXT:
{context}

QUESTION: {question}

Answer using only the CONTEXT above. If it's insufficient, say "I don't have enough information on that.\""""

_client: Groq | None = None


def get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key or api_key.strip().lower() in {"your_key_here", ""}:
            raise RuntimeError("GROQ_API_KEY missing or placeholder in .env")
        _client = Groq(api_key=api_key)
    return _client


def _format_context(chunks: list[RetrievedChunk]) -> str:
    blocks = []
    for i, c in enumerate(chunks, 1):
        prof = _display_name(c.source_professor)
        blocks.append(f"[{i}] Source: {c.source_file} (Professor {prof})\n{c.text}")
    return "\n\n".join(blocks)


@dataclass
class Answer:
    answer: str
    sources: list[str]  # ordered, deduped source filenames
    retrieved: list[RetrievedChunk]


def ask(question: str, k: int = DEFAULT_TOP_K) -> Answer:
    chunks = retrieve(question, k=k)
    context = _format_context(chunks)
    user_msg = USER_TEMPLATE.format(context=context, question=question)

    client = get_client()
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.1,
        max_tokens=400,
    )
    answer = response.choices[0].message.content.strip()

    # Source attribution is programmatic, not LLM-trusted — dedupe in retrieval order.
    seen: set[str] = set()
    sources: list[str] = []
    for c in chunks:
        if c.source_file not in seen:
            seen.add(c.source_file)
            sources.append(c.source_file)

    return Answer(answer=answer, sources=sources, retrieved=chunks)


def _ensure_index() -> None:
    """Make sure the ChromaDB collection exists; build from documents/ if not."""
    try:
        # cheap probe — retrieve a tiny query
        retrieve("test", k=1)
    except Exception:
        build_collection(load_chunks(), force=False)


_SMOKE_QUERIES = [
    ("in-scope", "What do students say about Joseph Politz's weekly workload?"),
    ("in-scope", "Which UCSD CSE professor is described as one of the most caring even though their exams and homework are difficult?"),
    ("out-of-scope", "What's the best burrito near UCSD?"),
]


def _smoke_test() -> None:
    _ensure_index()
    for label, q in _SMOKE_QUERIES:
        print(f"=== [{label}] {q}")
        result = ask(q)
        print(f"ANSWER: {result.answer}")
        print(f"SOURCES: {', '.join(result.sources)}")
        print()


if __name__ == "__main__":
    _smoke_test()

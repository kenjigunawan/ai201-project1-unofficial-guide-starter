"""Embed chunks and retrieve top-k by semantic similarity.

Per planning.md:
- Embedding model: sentence-transformers all-MiniLM-L6-v2 (local, 384-dim).
- Vector store: ChromaDB (persistent on disk under ./chroma_db/).
- Top-k: 5.
- Metadata on every chunk: source_professor, review_index, source_file.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from ingest import Chunk, load_chunks

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION_NAME = "ucsd_cse_reviews"
CHROMA_PATH = Path(__file__).parent / "chroma_db"
DEFAULT_TOP_K = 5

_model: SentenceTransformer | None = None
_client: chromadb.api.ClientAPI | None = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _model


def get_client() -> chromadb.api.ClientAPI:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    return _client


def build_collection(chunks: list[Chunk], force: bool = False):
    """Embed chunks and store in ChromaDB. Idempotent — won't re-embed if collection exists."""
    client = get_client()
    if force:
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass

    existing = {c.name for c in client.list_collections()}
    if COLLECTION_NAME in existing and not force:
        collection = client.get_collection(COLLECTION_NAME)
        if collection.count() == len(chunks):
            return collection
        # Mismatch — rebuild so we don't ship a half-stale index.
        client.delete_collection(COLLECTION_NAME)

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    model = get_model()
    # Embed "<Professor Name>: <review text>" so the query "what do students say
    # about <name>" lands close to that professor's reviews. Stored document stays
    # clean — only what we embed changes.
    embed_inputs = [f"{_display_name(c.source_professor)}: {c.text}" for c in chunks]
    embeddings = model.encode(embed_inputs, show_progress_bar=False).tolist()
    collection.add(
        ids=[f"{c.source_professor}-{c.review_index}" for c in chunks],
        documents=[c.text for c in chunks],
        embeddings=embeddings,
        metadatas=[c.metadata for c in chunks],
    )
    return collection


def _display_name(slug: str) -> str:
    return " ".join(part.capitalize() for part in slug.split("_"))


@dataclass
class RetrievedChunk:
    text: str
    source_professor: str
    source_file: str
    review_index: int
    distance: float


def retrieve(query: str, k: int = DEFAULT_TOP_K) -> list[RetrievedChunk]:
    collection = get_client().get_collection(COLLECTION_NAME)
    model = get_model()
    query_emb = model.encode([query]).tolist()
    result = collection.query(
        query_embeddings=query_emb,
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    out: list[RetrievedChunk] = []
    for doc, meta, dist in zip(result["documents"][0], result["metadatas"][0], result["distances"][0]):
        out.append(
            RetrievedChunk(
                text=doc,
                source_professor=meta["source_professor"],
                source_file=meta["source_file"],
                review_index=meta["review_index"],
                distance=dist,
            )
        )
    return out


# Queries 1, 3, 4 from planning.md's evaluation plan.
_EVAL_QUERIES = [
    "What do students say about Joseph Politz's weekly workload?",
    "What's the main complaint students have about Rose Yu's lectures?",
    "Is Julian McAuley considered a fair grader, and what do students think of his lectures?",
]


def _smoke_test() -> None:
    chunks = load_chunks()
    print(f"Embedding {len(chunks)} chunks with {EMBEDDING_MODEL_NAME}...")
    build_collection(chunks, force=True)
    print("Done.\n")

    for q in _EVAL_QUERIES:
        print(f"=== QUERY: {q}")
        results = retrieve(q, k=DEFAULT_TOP_K)
        for i, r in enumerate(results, 1):
            print(f"  [{i}] dist={r.distance:.3f}  {r.source_professor} (review #{r.review_index})")
            print(f"      {r.text[:200].replace(chr(10), ' ')}...")
        print()


if __name__ == "__main__":
    _smoke_test()

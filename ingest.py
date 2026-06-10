"""Load and chunk the UCSD CSE professor review documents.

Per planning.md:
- Chunk = one RateMyProfessors review (split on blank lines).
- Overlap = 0; reviews are independent units.
- Each chunk carries metadata so retrieval can attribute it to the right professor.
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from pathlib import Path

DOCUMENTS_DIR = Path(__file__).parent / "documents"


@dataclass
class Chunk:
    text: str
    source_professor: str
    review_index: int
    source_file: str
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        self.metadata = {
            "source_professor": self.source_professor,
            "review_index": self.review_index,
            "source_file": self.source_file,
        }


_HEADER_RE = re.compile(r"^(Source|URL):", re.IGNORECASE)


def _strip_header(raw: str) -> str:
    """Drop the leading 'Source:' / 'URL:' lines so they don't become a chunk."""
    lines = raw.splitlines()
    body_start = 0
    for i, line in enumerate(lines):
        if line.strip() and not _HEADER_RE.match(line):
            body_start = i
            break
    return "\n".join(lines[body_start:]).strip()


def _split_reviews(body: str) -> list[str]:
    """Split a cleaned document into per-review blocks on blank-line boundaries."""
    blocks = re.split(r"\n\s*\n", body)
    return [b.strip() for b in blocks if b.strip()]


def load_chunks(documents_dir: Path = DOCUMENTS_DIR) -> list[Chunk]:
    chunks: list[Chunk] = []
    for path in sorted(documents_dir.glob("*.txt")):
        raw = path.read_text(encoding="utf-8")
        body = _strip_header(raw)
        for i, review in enumerate(_split_reviews(body)):
            chunks.append(
                Chunk(
                    text=review,
                    source_professor=path.stem,
                    review_index=i,
                    source_file=path.name,
                )
            )
    return chunks


def inspect(chunks: list[Chunk], k: int = 5, seed: int = 7) -> None:
    print(f"Loaded {len(chunks)} chunks from {len(set(c.source_file for c in chunks))} files.")
    lengths = [len(c.text) for c in chunks]
    print(f"Chunk length — min={min(lengths)}, max={max(lengths)}, mean={sum(lengths)//len(lengths)}")
    print()
    rng = random.Random(seed)
    sample = rng.sample(chunks, min(k, len(chunks)))
    for i, c in enumerate(sample, 1):
        print(f"--- sample {i} ({c.source_professor}, review #{c.review_index}, {len(c.text)} chars) ---")
        print(c.text)
        print()


if __name__ == "__main__":
    chunks = load_chunks()
    inspect(chunks)

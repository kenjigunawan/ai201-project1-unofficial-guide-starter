# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

Student reviews of UCSD Computer Science & Engineering (CSE) professors, collected from individual RateMyProfessors profiles. Official UCSD sources — the course catalog, CSE faculty pages, and even CAPE — describe what a course covers and what a professor researches, but say very little about teaching style, exam difficulty, grading harshness, or how a professor actually treats students day to day. Reviews on RateMyProfessors fill that gap, but they sit one professor per page with no way to ask cross-cutting questions like "which CSE professor is best for an intro class?" or "who gives the heaviest workload?" — which is exactly the gap this system is meant to close.

The system should be able to answer questions like:
1. "What do students say about Niema Moshiri's exams and workload?"
2. "Is Joseph Pasquale a good professor for OS-style classes?"
3. "Which UCSD CSE professors are described as caring or approachable in office hours?"
4. "Which professors are flagged as tough graders or having heavy homework?"
5. "What do students think of Rose Yu's lecture style?"

---

## Documents

Ten RateMyProfessors profile pages for UCSD CSE faculty. Each page is a thread of dated student reviews (rating, difficulty, tags, free-text comments) for one professor, which gives the system a per-professor "voice" and lets retrieval surface cross-cutting patterns across professors.

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | RateMyProfessors — Julian McAuley | UCSD CSE faculty; ML / recommender systems; reviews discuss fairness, lecture style, workload | https://www.ratemyprofessors.com/professor/2070821 |
| 2 | RateMyProfessors — Joseph Pasquale | UCSD CSE faculty; OS / networking; long history of reviews spanning many quarters | https://www.ratemyprofessors.com/professor/528482 |
| 3 | RateMyProfessors — Rose Yu | UCSD CSE faculty; ML; reviews focus on lecture clarity and office hours | https://www.ratemyprofessors.com/professor/2879115 |
| 4 | RateMyProfessors — Daniele Micciancio | UCSD CSE faculty; cryptography / theory; reviews split between "caring" and "very difficult" | https://www.ratemyprofessors.com/professor/449659 |
| 5 | RateMyProfessors — Hao Su | UCSD CSE faculty; computer vision / graphics; reviews discuss curves and exam difficulty | https://www.ratemyprofessors.com/professor/2446901 |
| 6 | RateMyProfessors — Joseph Politz | UCSD CSE teaching faculty; intro programming / PL; reviews discuss handouts and weekly workload | https://www.ratemyprofessors.com/professor/2284684 |
| 7 | RateMyProfessors — Gary Gillespie | UCSD CSE teaching faculty; reviews flag heavy homework and tough grading | https://www.ratemyprofessors.com/professor/63531 |
| 8 | RateMyProfessors — Niema Moshiri | UCSD CSE associate teaching professor; computational biology; teaches intro CS courses | https://www.ratemyprofessors.com/professor/2279559 |
| 9 | RateMyProfessors — Mia Minnes | UCSD CSE teaching professor; vice-chair undergrad ed; theory courses; reviews discuss approachability | https://www.ratemyprofessors.com/professor/1516842 |
| 10 | RateMyProfessors — Paul Cao | UCSD CSE lecturer; intro CS; reviews discuss lecture clarity and student support | https://www.ratemyprofessors.com/professor/2772323 |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**

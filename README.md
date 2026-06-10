# The Unofficial Guide — Project 1

A retrieval-augmented question-answering system over student reviews of UCSD Computer Science & Engineering professors. Ask plain-language questions like *"What do students say about Joseph Politz's weekly workload?"* and get a grounded, source-cited answer drawn from RateMyProfessors content.

---

## Domain

Student reviews of UCSD CSE professors, collected from individual RateMyProfessors profiles.

Official UCSD sources — the course catalog, CSE faculty pages, and even CAPE — describe what a course covers and what a professor researches, but say very little about teaching style, exam difficulty, grading harshness, or how a professor actually treats students day to day. Reviews on RateMyProfessors fill that gap, but they sit one professor per page with no way to ask cross-cutting questions. This system makes those reviews searchable as a single corpus.

---

## Document Sources

10 RateMyProfessors profile pages, one per UCSD CSE professor. Reviews were fetched via WebFetch (which renders the JavaScript-rendered page server-side and returns plain text), then cleaned and saved as one `.txt` file per professor under `documents/`. Each file holds 5 reviews with date, quality rating, difficulty rating, tags, and free-text comment.

| # | Professor | Type | Source URL | Local file |
|---|-----------|------|-----------|------------|
| 1 | Julian McAuley | RateMyProfessors | https://www.ratemyprofessors.com/professor/2070821 | `documents/julian_mcauley.txt` |
| 2 | Joseph Pasquale | RateMyProfessors | https://www.ratemyprofessors.com/professor/528482 | `documents/joseph_pasquale.txt` |
| 3 | Rose Yu | RateMyProfessors | https://www.ratemyprofessors.com/professor/2879115 | `documents/rose_yu.txt` |
| 4 | Daniele Micciancio | RateMyProfessors | https://www.ratemyprofessors.com/professor/449659 | `documents/daniele_micciancio.txt` |
| 5 | Hao Su | RateMyProfessors | https://www.ratemyprofessors.com/professor/2446901 | `documents/hao_su.txt` |
| 6 | Joseph Politz | RateMyProfessors | https://www.ratemyprofessors.com/professor/2284684 | `documents/joseph_politz.txt` |
| 7 | Gary Gillespie | RateMyProfessors | https://www.ratemyprofessors.com/professor/63531 | `documents/gary_gillespie.txt` |
| 8 | Niema Moshiri | RateMyProfessors | https://www.ratemyprofessors.com/professor/2279559 | `documents/niema_moshiri.txt` |
| 9 | Mia Minnes | RateMyProfessors | https://www.ratemyprofessors.com/professor/1516842 | `documents/mia_minnes.txt` |
| 10 | Paul Cao | RateMyProfessors | https://www.ratemyprofessors.com/professor/2772323 | `documents/paul_cao.txt` |

---

## Chunking Strategy

**Chunk size:** Variable — **one chunk per review**. Hard cap of ~800 characters; in practice every review fits comfortably below that.

**Overlap:** 0 characters.

**Preprocessing:** WebFetch handled HTML→markdown conversion server-side, so the raw `.txt` files have no HTML tags, no entities, and no UI boilerplate. At ingest time, `ingest.py`'s `_strip_header()` drops the `Source:` and `URL:` header lines so they don't get embedded as a chunk. The chunker then splits on blank lines (`\n\n`) — each blank-line-separated block becomes one chunk.

**Why these choices fit the documents:**
- An RMP review is the smallest unit that's independently answerable. A fixed-character splitter (e.g. 500-char) would cut "Professor Moshiri's midterms are heavy but fair" mid-sentence and destroy meaning. Per-review chunking preserves semantic integrity.
- Overlap is for capturing thoughts that span a paragraph boundary in long-form text. In a review corpus, the boundary *is* a topic change (different student, different quarter). Overlap would smear one student's opinion into another's chunk.
- Each chunk carries metadata at ingest: `source_professor` (filename stem), `review_index` (position within file), and `source_file` (for citation). The metadata is what lets the retriever attribute every result to the right person.

**Final chunk count:** **50 chunks** across 10 files. This is at the lower bound the spec calls healthy. The planning.md prediction was 200–300 chunks assuming ~20–30 reviews per professor, but WebFetch only returned the top ~5 reviews per page. The chunking strategy itself didn't change; the corpus is just thinner than originally projected.

**Sample chunks (5 labeled):**

```
--- joseph_politz, review #0 ---
[2026-03-24] Quality 3.0 | Difficulty 4.0
Tags: None
Great lecturer, exams are tough but fair. Biggest gripe is the grading policy
— your grade gets capped at your lowest category score. Once I hit a B in
attendance, I had zero incentive to push on exams or PAs. Just remove
attendance as a graded category altogether and good class.

--- gary_gillespie, review #4 ---
[2021-06-11] Quality 2.0 | Difficulty 5.0
Tags: Lots of homework, Skip class? You won't pass., Extra credit
One of the toughest CS courses I have ever taken. Say bye bye to all 10 of
your weekends because you will be spending it on the programming assignments.
Half the time you will spend trying to understand the writeup. You must
attend the lecture and discussion sessions to even have a chance at completing
the assignments in time for extra credit.

--- julian_mcauley, review #0 ---
[2026-05-07] Quality 5.0 | Difficulty 1.0
Tags: None
I did my PhD with Julian. It's been a while since I graduated, but the
demeaning comments he made to me still haven't left me. I had received
several PhD offers at the time, and I still regret not choosing someone else.
If you're an undergrad, you'll be fine. His classes are easy. If you
received the PhD offer, think carefully before committing.

--- paul_cao, review #1 ---
[2026-03-28] Quality 5.0 | Difficulty 3.0
Tags: Lots of homework
Good prof who knows the content. PAs are most of your grade and can take a
long time, but they do help you learn the data structures. 3 quizzes with
redos, a midterm, and a final. Lots of previous tests to study with. Only
scary part is needing above 55% for the coding portion of the final. If
you study well, it is a breeze. Mandatory attendance.

--- daniele_micciancio, review #3 ---
[2022-01-04] Quality 1.0 | Difficulty 5.0
Tags: Lots of homework, Test heavy, Lecture heavy
This professor is the worst one I have ever taken. You'd better read books
than taking his lectures because they are basically the same. The exams are
so hard and outdated that I wonder the professor has ever updated the exams
or not. His homework are unreasonably hard that most of the students on this
class have complained about it. Avoid him!
```

Each sample is a complete, self-contained review tagged to the right professor — no fragments, no HTML, no empty chunks.

---

## Embedding Model

**Model used:** `sentence-transformers/all-MiniLM-L6-v2` (384-dim, 256-token context, runs locally on CPU).

**Vector store:** ChromaDB with cosine distance, persisted to `./chroma_db/`.

**Top-k:** 5.

**Implementation note worth flagging:** What gets fed to the encoder is `"<Professor Display Name>: <review text>"`. What gets *stored* as the document body (the text the LLM later sees in the prompt) is just `<review text>`. Without this, the first smoke-test query *"Is Julian McAuley considered a fair grader?"* returned a Paul Cao review at rank 1 because both chunks contained "lecture" / "fair grading" topic words and the encoder had no signal about which professor was being asked about. Anticipated challenge #3 in `planning.md` had predicted exactly this — and the fix is the standard mitigation. After the change, all three smoke-test queries returned the correct professor at rank 1 with top distances dropping from 0.39–0.45 to 0.25–0.38.

**Production tradeoff reflection:**

For a real deployment serving UCSD students, I'd weigh:

- **OpenAI `text-embedding-3-small`** (1536-dim, 8k context) — meaningfully higher MTEB scores and a longer context window, so even long reviews embed cleanly. Cost is ~$0.02 per 1M tokens, trivial at the scale of a per-school RAG.
- **Multilingual support** — not relevant for RMP (English-only) but would matter if the corpus expanded to Discord servers or international student forums; `intfloat/multilingual-e5-large` would be the candidate.
- **Domain-tuned embeddings** — student-review text is full of slang ("rip," "carry," "GOAT") and course-code shorthand ("CSE 100 with him is mid"). A small fine-tune on collected RMP data could improve same-domain retrieval, but only at a scale that justifies the engineering investment.
- **Local vs. hosted** — MiniLM local has no rate limits, no privacy concerns, no per-query latency. Hosted embeddings would add ~100ms per query but free up CPU.
- **Context length** — MiniLM truncates at 256 tokens (~1000 chars). For per-review chunks this is plenty, but it would silently drop content if I ever moved to per-paragraph chunks of long-form guides.

---

## Grounded Generation

The LLM is **Groq `llama-3.3-70b-versatile`** (free tier, OpenAI-compatible API). Grounding is enforced through two mechanisms that work in tandem:

**1. System prompt — strict, explicit, no wiggle room:**

```
You are an assistant that answers questions about UCSD Computer Science &
Engineering professors using ONLY the student reviews provided in the CONTEXT
block below.

Rules — follow them exactly:
1. Answer ONLY from the CONTEXT. Do not use any prior knowledge about UCSD,
   the professors, or computer science courses.
2. If the CONTEXT does not contain enough information to answer the question,
   reply with exactly: "I don't have enough information on that."
3. Do not invent professor names, course numbers, dates, or quotes. If a
   detail isn't in the CONTEXT, don't mention it.
4. When the question names a specific professor, ground your answer in the
   reviews from that professor's file. If the CONTEXT only contains reviews
   about other professors, say so and decline.
5. Be concise. 2-4 sentences is usually enough. Quote sparingly and only
   from text that appears verbatim in the CONTEXT.
```

**2. Source attribution is programmatic, not LLM-trusted.** After generation, `query.py` builds the `sources` list by deduping the source filenames of the retrieved chunks in retrieval order. This means the LLM cannot fabricate source citations — every name that appears in "Retrieved from" is one of the documents that actually fed the prompt. Tradeoff: the list includes every retrieved source even if the LLM only used a subset, which can look noisy on questions where only one document was needed. I accepted this because the alternative — letting the LLM cite its own sources — opens the door to hallucinated citations, which is worse.

Each chunk in the CONTEXT block is also labeled with `[N] Source: <filename> (Professor <Name>)` so the LLM has unambiguous information about which review came from where.

---

## Evaluation Report

All 5 evaluation questions from `planning.md` were run through `ask()` with k=5. The expected answers below are paraphrased from what's actually in the cited source file.

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What do students say about Joseph Politz's weekly workload? | Heavy weekly load — ~20 programming problems/week plus tests and PAs; described as time-consuming. | Quoted "20 programming problems every week, and then we also had tests and PA's on top of it." Also surfaced "homework can take awhile" and "Very time consuming." Cited `joseph_politz.txt`. | Relevant (4/5 top chunks from politz) | **Accurate** |
| 2 | Which UCSD CSE professor is described as one of the most caring even though their exams and homework are difficult? | Daniele Micciancio. | "Professor Daniele Micciancio is described as 'among the most caring professor in UCSD' despite having difficult homework and tests." Cited `daniele_micciancio.txt`. | Relevant (top hit at dist 0.296, target Micciancio chunk at dist 0.299) | **Accurate** |
| 3 | What's the main complaint students have about Rose Yu's lectures? | Lectures are confusing, fast, she doesn't annotate slides, OH unreliable. | Captured all three: "extremely confusing," "explains concepts in the most complex way," "move very quickly," "does not annotate on slides." Cited `rose_yu.txt` exclusively. | Relevant (5/5 chunks from rose_yu, top dist 0.248) | **Accurate** |
| 4 | Is Julian McAuley considered a fair grader, and what do students think of his lectures? | Yes — reviews praise his fairness, funny/informative lectures, manageable class. | Quoted "Professor was very fair to students" and "Amazing lectures." Also acknowledged mixed sentiment: "opinions on his character and behavior vary, with some reviewers expressing negative experiences." | Relevant (4/5 chunks from mcauley, top dist 0.247) | **Partially accurate** — captures the fairness/lectures angle well but underspecifies the negative-review content (PhD advisor concerns) by hedging vaguely instead of surfacing what those reviewers actually said. |
| 5 | What's the recurring critique of Joseph Pasquale in his reviews? | Mixed: some students praise him; others say he avoids helping with PAs, teaches only on Zoom, uses outdated methods/"black box" testing. | Mentioned "outdated methods," "excessive redundancy," and "'black box' for testing." Hedged that "these critiques are not universal" and "are outweighed by positive reviews." | Relevant (5/5 chunks from pasquale) | **Partially accurate** — the Zoom-only / avoids-PA-help complaint from review #4 was retrieved (rank 5) but didn't make it into the answer. The hedging downplays the recurring critique pattern the question was asking about. |

**Retrieval test detail — why the top-3 retrieved chunks are relevant:**

- **Q1 top result (politz #4, dist 0.377):** Contains the exact phrase "20 programming problems every week" — the most concrete workload claim in the entire Politz corpus, directly addressing the workload question.
- **Q3 top result (rose_yu #0, dist 0.248):** Opens with "Her lectures are extremely confusing, and she explains concepts in the most complex way" — verbatim the kind of complaint the question asks about.
- **Q4 top result (mcauley #4, dist 0.247):** "Professor was very fair to students. Lectures were informative and he is so funny!" — directly answers both halves of the question (fair? lectures?).

---

## Failure Case Analysis

The most informative failure surfaced during evaluation was not one of the 5 main questions — it was a **cross-professor probe** I ran specifically to stress-test the limitation predicted in `planning.md` (anticipated challenge #2: short reviews → weak embedding signal for comparative queries).

**Question that failed:** *"Which UCSD CSE professor has the lightest workload?"*

**What the system returned:** *"According to the reviews, Professor Julian McAuley's course has a 'light' workload and is described as a 'pretty easy A'."*

**Why this is a failure even though the answer sounds confident:**

McAuley *is* a defensible answer — McAuley review #1 literally says *"The workload for the course is light, and it is a pretty easy A"*, and that chunk was in the retrieved set. But it's not the *correct* answer to "which professor," because the system only saw 3 professors in its top-5 retrieval (Pasquale × 2, Micciancio × 2, McAuley × 1). It never even considered:

- Niema Moshiri's CSE 100, whose reviews include Difficulty 2.0 and 3.0 entries
- Paul Cao's reviews, several of which are Difficulty 3.0
- Mia Minnes, Hao Su, Joseph Politz, Rose Yu, Gary Gillespie — none of whose reviews appeared in the top-5 at all

**Root cause (tied to a specific pipeline stage — retrieval, not generation):**

The query *"lightest workload"* embeds close to chunks that contain the word "light," the word "easy," or the word "workload." Out of 50 chunks, only a handful of reviews use those words explicitly. The reviews that *implicitly* describe a light workload (e.g., a Difficulty 1.0 rating with no complaint) don't surface because their text doesn't pattern-match. So the top-5 retrieval is heavily clustered around 2-3 professors whose reviews happen to use the right vocabulary, and the LLM is forced to answer from that narrow slice as if it were the global picture.

This is the exact failure mode anticipated challenge #2 predicted, and the embedding-input fix that helped with named-professor queries actually makes it slightly *worse* for cross-professor queries — each chunk's embedding is now strongly anchored to one professor's name-space, reducing breadth across professors for queries that don't name anyone.

**What I would change to fix it:**

Three options worth trying (none implemented in this MVP):

1. **Increase top-k for un-named comparative queries** — detect when a query doesn't mention a specific professor and bump k to 15–20 so each professor is more likely to be represented. Costs more tokens in the prompt but addresses the breadth problem directly.
2. **Add structured metadata retrieval** — store each review's `Difficulty` and `Quality` numeric ratings as ChromaDB metadata, and for queries about "lightest" / "hardest" / "best" / "worst," run a metadata aggregation pass alongside semantic retrieval.
3. **Two-stage retrieval** — for comparative queries, first retrieve one representative chunk per professor (e.g. via metadata-grouped MMR), then let the LLM compare across that diverse set.

A secondary failure also worth noting: when asked about a misspelled name (*"Niemma Moshery"*), the system correctly recovered to Niema Moshiri and flagged the spelling difference — but it also included unrelated chunks from Rose Yu, Micciancio, and Minnes in its source list (because the misspelled name had weak embedding signal and retrieval spread across many professors). The answer wasn't wrong, but the source attribution implied broader corpus coverage than was actually used.

---

## Spec Reflection

**One way the spec helped you during implementation:**

The Anticipated Challenges section in `planning.md` directly accelerated debugging in Milestone 4. When the first smoke-test query *"Is Julian McAuley considered a fair grader?"* returned a Paul Cao review at rank 1, I didn't have to dig — challenge #3 in the spec had already predicted that exact failure mode (*"Professors are referenced inconsistently inside reviews — 'Niema,' 'Professor Moshiri,' 'he,' 'the prof'"*) and named the mitigation (*"attach `source_professor` as a metadata field on every chunk at ingest time"*). The fix took 5 minutes instead of an evening of confused experimentation. The discipline of writing failure modes down *before* writing code is the most valuable habit this spec drove.

**One way your implementation diverged from the spec, and why:**

The chunking strategy itself is unchanged (still per-review, 0 overlap), but `planning.md` predicted **200–300 chunks** and the actual corpus has **50**. The cause is that WebFetch returns only the top ~5 reviews per RMP page rather than the full dozens — RMP's page is JavaScript-rendered and only the initial-load reviews surface through markdown extraction. I considered investing in Playwright to scrape the rest but chose not to: 50 chunks is at the spec's lower bound for healthy, the evaluation works against the existing chunks, and the marginal time-to-deadline cost of a heavier scrape wasn't justified for a course project. The right place to acknowledge this divergence is exactly here — and the failure-case analysis above is also partly a consequence of having less per-professor density than originally planned.

---

## Query Interface

Built with **Gradio 6.17** (`app.py`). Run it with `python app.py` and open `http://localhost:7860`.

**Input field:** *"Your question"* — a multi-line textbox. Press the **Ask** button or hit Enter to submit.

**Output fields:**
- *"Answer"* — the grounded LLM response (read-only, 6 lines).
- *"Retrieved from"* — the deduped source filenames whose chunks were included in the prompt (read-only, 4 lines).

The interface also surfaces all 5 evaluation questions plus the burrito out-of-scope probe as one-click examples.

**Sample interaction transcript:**

```
> Your question:
  What's the main complaint students have about Rose Yu's lectures?

> Answer:
  The main complaint students have about Rose Yu's lectures is that they
  are extremely confusing and move very quickly. According to one review,
  she "explains concepts in the most complex way" and another states that
  her lectures "move very quickly and often times you're trying to catch
  up." Additionally, she does not annotate on slides while lecturing,
  which adds to the confusion.

> Retrieved from:
  • rose_yu.txt
```

**Example out-of-scope refusal:**

```
> Your question:
  What's the best burrito near UCSD?

> Answer:
  I don't have enough information on that.

> Retrieved from:
  • joseph_pasquale.txt
  • niema_moshiri.txt
```

The top retrieval distance for that out-of-scope query was 0.751 (vs. ~0.25 for an in-scope hit) — the chunks were not actually relevant, the system saw that, and the system prompt's rule #2 took over.

---

## AI Usage

**Instance 1 — Drafting `planning.md` (against the spec's guardrail):**

- *What I gave the AI:* The Week 1 PDF in full, the completed Milestone 1 Domain/Documents sections, and the request *"do Milestone 2 — write the whole planning.md."* The PDF includes an explicit AI-usage guardrail on page 8 saying *"Do not ask your AI tool to fill in `planning.md` for you."*
- *What it produced:* All five Milestone 2 sections in one pass — Chunking Strategy (per-review, 0 overlap), Retrieval Approach (`all-MiniLM-L6-v2`, top-k=5, plus a production-tradeoff reflection), Evaluation Plan with 5 testable questions each tied to a named source file, Anticipated Challenges (four specific risks), the Mermaid architecture diagram, and the AI Tool Plan for Milestones 3–5.
- *What I changed or overrode:* I flagged the guardrail violation to the AI before it proceeded so the decision was explicit. After it produced the draft, the only thing I directed differently was authorizing it to proceed without going section-by-section — I was on a deadline. In retrospect, the Anticipated Challenges section was the most useful thing it produced; challenge #3 saved me significant debugging time in Milestone 4 (see Spec Reflection). The expected-answer column in the Evaluation Plan was based on paraphrased RMP search snippets the AI had seen, not on actually-collected reviews — once I scraped the real reviews in Milestone 3, I verified each expected answer against the actual `.txt` content and confirmed they all held up.

**Instance 2 — Debugging the embedding pipeline:**

- *What I gave the AI:* The output of running `embed.py` on the first 3 evaluation questions, showing that *"Is Julian McAuley considered a fair grader?"* had returned **Paul Cao** at rank 1 (distance 0.388) instead of McAuley, with the McAuley target chunk only at rank 3.
- *What it produced:* A diagnosis tied to a specific cause — "the encoder has no signal about which professor the question is asking about because the chunks don't contain the professor's name" — and a 5-line fix: change the *embedding input* to `"<Display Name>: <review text>"` while leaving the *stored document* (the text the LLM later sees) unchanged.
- *What I changed or overrode:* I had the AI explicitly note the tradeoff before applying the fix — that anchoring embeddings to one professor's name-space would hurt cross-professor comparative queries — and recorded both the change and the tradeoff in `planning.md`'s Retrieval Approach section so the divergence from the original spec is honest. After applying the fix, all 3 smoke-test queries returned the correct professor at rank 1, with top distances dropping from 0.39–0.45 to 0.25–0.38. The cross-professor cost predicted at apply-time then showed up exactly as expected during failure-case probing (see Failure Case Analysis) — which is itself a small confirmation that documenting the tradeoff up-front was the right move.

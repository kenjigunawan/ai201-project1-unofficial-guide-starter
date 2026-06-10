"""Run all 5 evaluation questions from planning.md plus failure probes.

Prints full responses + retrieval details for each question. Used to populate the
Evaluation Report and Failure Case sections of README.md.
"""

from __future__ import annotations

from query import _ensure_index, ask

EVAL_QUESTIONS = [
    "What do students say about Joseph Politz's weekly workload?",
    "Which UCSD CSE professor is described as one of the most caring even though their exams and homework are difficult?",
    "What's the main complaint students have about Rose Yu's lectures?",
    "Is Julian McAuley considered a fair grader, and what do students think of his lectures?",
    "What's the recurring critique of Joseph Pasquale in his reviews?",
]

FAILURE_PROBES = [
    # Cross-professor / comparative
    "Which UCSD CSE professor has the lightest workload?",
    # Out-of-scope (good — should refuse)
    "What's the best burrito near UCSD?",
    # Professor not in corpus
    "What do students think of Professor Stefan Savage at UCSD?",
    # Misspelled name
    "What do students say about Niemma Moshery?",
    # Course-level question (not professor-level)
    "Is CSE 100 a good class?",
]


def run(label: str, questions: list[str]) -> None:
    print(f"\n{'=' * 72}\n{label}\n{'=' * 72}")
    for i, q in enumerate(questions, 1):
        print(f"\n--- Q{i}: {q}")
        result = ask(q)
        print(f"ANSWER: {result.answer}")
        print(f"SOURCES: {', '.join(result.sources)}")
        print("TOP-5 RETRIEVED:")
        for j, r in enumerate(result.retrieved, 1):
            snippet = r.text.replace("\n", " ")[:120]
            print(f"  [{j}] dist={r.distance:.3f} {r.source_professor} #{r.review_index}: {snippet}...")


if __name__ == "__main__":
    _ensure_index()
    run("EVALUATION QUESTIONS (5)", EVAL_QUESTIONS)
    run("FAILURE PROBES (5)", FAILURE_PROBES)

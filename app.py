"""Gradio interface for The Unofficial Guide — UCSD CSE Professor Reviews.

Run with:
    python app.py
Then open http://localhost:7860 in a browser.
"""

from __future__ import annotations

import gradio as gr

from query import _ensure_index, ask

_ensure_index()


def handle_query(question: str) -> tuple[str, str]:
    if not question or not question.strip():
        return "Enter a question above to get started.", ""
    result = ask(question.strip())
    sources_text = "\n".join(f"• {s}" for s in result.sources) if result.sources else "(none)"
    return result.answer, sources_text


EXAMPLE_QUESTIONS = [
    "What do students say about Joseph Politz's weekly workload?",
    "Which UCSD CSE professor is described as one of the most caring even though their exams and homework are difficult?",
    "What's the main complaint students have about Rose Yu's lectures?",
    "Is Julian McAuley considered a fair grader, and what do students think of his lectures?",
    "What's the recurring critique of Joseph Pasquale in his reviews?",
    "What's the best burrito near UCSD?",  # out-of-scope, should refuse
]


with gr.Blocks(title="The Unofficial Guide — UCSD CSE Professors") as demo:
    gr.Markdown(
        "# The Unofficial Guide\n"
        "Ask questions about UCSD Computer Science & Engineering professors. "
        "Answers are drawn from student reviews on RateMyProfessors — the system "
        "will decline if it doesn't have enough information."
    )
    question = gr.Textbox(
        label="Your question",
        placeholder="e.g., What do students say about Niema Moshiri's exams?",
        lines=2,
    )
    ask_btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=6, interactive=False)
    sources = gr.Textbox(label="Retrieved from", lines=4, interactive=False)
    gr.Examples(examples=EXAMPLE_QUESTIONS, inputs=question)

    ask_btn.click(handle_query, inputs=question, outputs=[answer, sources])
    question.submit(handle_query, inputs=question, outputs=[answer, sources])


if __name__ == "__main__":
    demo.launch()

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


from .codex_runner import CodexRunner

REQUIRED_QUESTION_FIELDS = {
    "question_id",
    "topic",
    "question",
    "split",
}

ALLOWED_SPLITS = {
    "dev",
    "held_out",
}

BASELINE_REPORT_DIR = Path("data/baseline_reports")

BASELINE_PROMPT_TEMPLATE = """\
You are producing a baseline research report for the Reliable Research benchmark.

Research question:
{question}

Conduct independent research using available research tools and publicly accessible sources.

Requirements:
- Answer the research question directly.
- Produce a concise research report focused on empirical evidence.
- Support factual claims with inline numbered citations such as [1], [2], and [3].
- Include a References section mapping every citation number to its source, including the source title and URL.
- Report mixed, conflicting, or uncertain evidence when relevant.
- Do not perform a separate claim-verification, citation-verification, or revision step.
- Do not describe your research process; return only the final report.
"""


def build_baseline_prompt(question: str) -> str:
    """Build the fixed baseline research prompt."""
    return BASELINE_PROMPT_TEMPLATE.format(question=question).strip()


def save_baseline_report(
    question_id: str,
    report: str,
) -> Path:
    """Save one non-empty baseline report to its stable path."""
    report = report.strip()

    if not report:
        raise ValueError(
            f"Baseline report for {question_id} is empty."
        )

    BASELINE_REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    report_path = BASELINE_REPORT_DIR / f"{question_id}.md"

    report_path.write_text(
        report + "\n",
        encoding="utf-8",
    )

    return report_path


def load_benchmark(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Benchmark file not found: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))

    if "benchmark_id" not in data:
        raise ValueError("Benchmark is missing 'benchmark_id'.")

    if "questions" not in data:
        raise ValueError("Benchmark is missing 'questions'.")

    if not isinstance(data["questions"], list):
        raise ValueError("'questions' must be a list.")

    validate_questions(data["questions"])

    return data


def validate_questions(questions: list[dict[str, Any]]) -> None:
    seen_ids: set[str] = set()

    for index, question in enumerate(questions):
        missing = REQUIRED_QUESTION_FIELDS - question.keys()

        if missing:
            raise ValueError(
                f"Question at index {index} is missing fields: "
                f"{sorted(missing)}"
            )

        question_id = question["question_id"]
        split = question["split"]

        if question_id in seen_ids:
            raise ValueError(
                f"Duplicate question_id: {question_id}"
            )

        seen_ids.add(question_id)

        if split not in ALLOWED_SPLITS:
            raise ValueError(
                f"Invalid split for {question_id}: {split}"
            )


def select_questions(
    questions: list[dict[str, Any]],
    *,
    split: str | None = None,
    question_id: str | None = None,
) -> list[dict[str, Any]]:
    selected = questions

    if split is not None:
        selected = [
            q for q in selected
            if q["split"] == split
        ]

    if question_id is not None:
        selected = [
            q for q in selected
            if q["question_id"] == question_id
        ]

    return selected


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Reliable Research benchmark questions."
    )

    parser.add_argument(
        "--benchmark",
        type=Path,
        default=Path(
            "data/questions/questions_v0.1.json"
        ),
        help="Path to benchmark question JSON file.",
    )

    parser.add_argument(
        "--split",
        choices=sorted(ALLOWED_SPLITS),
        help="Run only one benchmark split.",
    )

    parser.add_argument(
        "--question-id",
        help="Run only one question ID.",
    )

    args = parser.parse_args()

    benchmark = load_benchmark(args.benchmark)

    selected = select_questions(
        benchmark["questions"],
        split=args.split,
        question_id=args.question_id,
    )

    print(f"benchmark_id: {benchmark['benchmark_id']}")
    print(f"selected_questions: {len(selected)}")

    if not selected:
        raise SystemExit("No questions matched the selection.")

    runner = CodexRunner()

    for question in selected:
        question_id = question["question_id"]

        if question_id not in {"Q001", "Q002"}:
            raise SystemExit(
                "Baseline generation for Pre2 is limited "
                "to Q001 and Q002."
            )

        prompt = build_baseline_prompt(
            question["question"]
        )

        print(
            f"running: {question_id} "
            f"[{question['topic']}]"
        )

        result = runner.run(
            prompt,
            question_id=question_id,
            timeout_seconds=600,
        )

        if result.return_code != 0:
            raise RuntimeError(
                f"{question_id} failed with return code "
                f"{result.return_code}.\n"
                f"stderr:\n{result.stderr}"
            )

        if result.errors:
            raise RuntimeError(
                f"{question_id} returned errors: "
                + "; ".join(result.errors)
            )

        report_path = save_baseline_report(
            question_id,
            result.final_message,
        )

        print(f"run_id: {result.run_id}")
        print(f"run_dir: {result.run_dir}")
        print(f"report_path: {report_path}")
        print(
            f"report_chars: "
            f"{len(result.final_message.strip())}"
        )

        if result.warnings:
            print("warnings:")

            for warning in result.warnings:
                print(f"- {warning}")


if __name__ == "__main__":
    main()

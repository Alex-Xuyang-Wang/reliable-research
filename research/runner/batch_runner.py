from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


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

    for question in selected:
        print(
            f"{question['question_id']} "
            f"[{question['split']}] "
            f"[{question['topic']}] "
            f"{question['question']}"
        )


if __name__ == "__main__":
    main()

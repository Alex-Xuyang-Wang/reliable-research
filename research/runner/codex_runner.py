from __future__ import annotations

import json
import subprocess
import tempfile
import time
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class CodexRunResult:
    run_id: str
    question_id: str | None
    run_dir: Path
    return_code: int
    final_message: str
    events: list[dict[str, Any]]
    errors: list[str]
    warnings: list[str]
    usage: dict[str, Any]
    stderr: str
    duration_seconds: float


class CodexRunner:
    KNOWN_NON_FATAL_ERROR_PREFIXES = (
        "Code Mode is unavailable because",
    )
    def __init__(self, repo_root: Path | None = None) -> None:
        if repo_root is None:
            repo_root = Path(__file__).resolve().parents[2]

        self.repo_root = repo_root
        self.launcher = repo_root / "scripts" / "reliable-research"

        if not self.launcher.exists():
            raise FileNotFoundError(
                f"Reliable Research launcher not found: {self.launcher}"
            )

    def run(
        self,
        prompt: str,
        *,
        question_id: str | None = None,
        timeout_seconds: int = 300,
    ) -> CodexRunResult:
        run_id = (
            datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            + "-"
            + uuid.uuid4().hex[:8]
        )

        run_dir = self.repo_root / "data" / "runs" / run_id
        run_dir.mkdir(parents=True, exist_ok=False)

        started_at = datetime.now(timezone.utc)
        start_time = time.monotonic()
        git_metadata = self._get_git_metadata()
        with tempfile.TemporaryDirectory(
            prefix="reliable-research-"
        ) as tmp_dir:
            tmp_path = Path(tmp_dir)
            final_message_path = tmp_path / "last_message.txt"

            command = [
                str(self.launcher),
                "exec",
                "--ephemeral",
                "-s",
                "read-only",
                "--json",
                "-o",
                str(final_message_path),
                "-",
            ]

            process = subprocess.run(
                command,
                input=prompt,
                text=True,
                capture_output=True,
                cwd=self.repo_root,
                timeout=timeout_seconds,
                check=False,
            )

            duration_seconds = time.monotonic() - start_time

            events = self._parse_events(process.stdout)
            errors, warnings = self._extract_errors_and_warnings(events)
            usage = self._extract_usage(events)

            final_message = ""
            if final_message_path.exists():
                final_message = final_message_path.read_text(
                    encoding="utf-8"
                ).strip()

            (run_dir / "prompt.txt").write_text(
                prompt,
                encoding="utf-8",
            )

            (run_dir / "final_message.txt").write_text(
                final_message,
                encoding="utf-8",
            )

            (run_dir / "stderr.txt").write_text(
                process.stderr,
                encoding="utf-8",
            )

            with (run_dir / "events.jsonl").open(
                "w",
                encoding="utf-8",
            ) as f:
                for event in events:
                    f.write(json.dumps(event, ensure_ascii=False) + "\n")

            metadata = {
                "run_id": run_id,
                "question_id": question_id,
                "git": git_metadata,
                "started_at_utc": started_at.isoformat(),
                "duration_seconds": duration_seconds,
                "return_code": process.returncode,
                "event_count": len(events),
                "error_count": len(errors),
                "warning_count": len(warnings),
                "usage": usage,
            }

            (run_dir / "metadata.json").write_text(
                json.dumps(
                    metadata,
                    indent=2,
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )

            return CodexRunResult(
                run_id=run_id,
                question_id=question_id,
                run_dir=run_dir,
                return_code=process.returncode,
                final_message=final_message,
                events=events,
                errors=errors,
                warnings=warnings,
                usage=usage,
                stderr=process.stderr,
                duration_seconds=duration_seconds,
            )

    def _get_git_metadata(self) -> dict[str, Any]:
        def git(*args: str) -> str:
            process = subprocess.run(
                ["git", *args],
                cwd=self.repo_root,
                text=True,
                capture_output=True,
                check=False,
            )

            if process.returncode != 0:
                return ""

            return process.stdout.strip()

        branch = git("branch", "--show-current")
        commit = git("rev-parse", "HEAD")
        status = git("status", "--porcelain")

        return {
            "branch": branch or None,
            "commit": commit or None,
            "dirty": bool(status),
        }

    @staticmethod
    def _parse_events(stdout: str) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []

        for line in stdout.splitlines():
            line = line.strip()

            if not line:
                continue

            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                events.append(
                    {
                        "type": "unparsed_output",
                        "raw": line,
                    }
                )

        return events

    @classmethod
    def _extract_errors_and_warnings(
        cls,
        events: list[dict[str, Any]],
    ) -> tuple[list[str], list[str]]:
        errors: list[str] = []
        warnings: list[str] = []

        for event in events:
            if event.get("type") != "item.completed":
                continue

            item = event.get("item", {})

            if item.get("type") != "error":
                continue

            message = item.get("message")

            if not message:
                continue

            if message.startswith(cls.KNOWN_NON_FATAL_ERROR_PREFIXES):
                warnings.append(message)
            else:
                errors.append(message)

        return errors, warnings

    @staticmethod
    def _extract_usage(
        events: list[dict[str, Any]],
    ) -> dict[str, Any]:
        for event in reversed(events):
            if event.get("type") == "turn.completed":
                return event.get("usage", {})

        return {}


if __name__ == "__main__":
    runner = CodexRunner()

    result = runner.run(
        "Reply with exactly one line: RELIABLE_RESEARCH_PYTHON_OK",
        question_id="SMOKE-001",
    )

    print(f"run_id: {result.run_id}")
    print(f"question_id: {result.question_id}")
    print(f"run_dir: {result.run_dir}")
    print(f"return_code: {result.return_code}")
    print(f"final_message: {result.final_message}")
    print(f"event_count: {len(result.events)}")
    print(f"error_count: {len(result.errors)}")
    print(f"warning_count: {len(result.warnings)}")
    print(f"duration_seconds: {result.duration_seconds:.2f}")
    print(f"usage: {result.usage}")

    if result.errors:
        print("\nErrors:")

        for error in result.errors:
            print(f"- {error}")

    if result.warnings:
        print("\nWarnings:")

        for warning in result.warnings:
            print(f"- {warning}")

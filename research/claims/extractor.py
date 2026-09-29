from __future__ import annotations

import argparse
from pathlib import Path
import re
from typing import Iterable

from .schemas import AtomicClaim, ClaimExtractionResult


_CITATION_RE = re.compile(r"\[(?:\d+(?:[-–]\d+)?|[A-Za-z][A-Za-z0-9_-]*)\]")
_SENTENCE_BOUNDARY_RE = re.compile(
    r"(?<=[.!?])(?:\*{1,2})?\s+(?=(?:[#>*-]*\s*)?[A-Z0-9])"
)
_MARKDOWN_PREFIX_RE = re.compile(r"^\s*(?:#{1,6}\s+|[-*+]\s+|\d+[.)]\s+|>\s*)")

_NON_FACTUAL_PREFIXES = (
    "we recommend",
    "i recommend",
    "the authors recommend",
    "we suggest",
    "i suggest",
    "you should",
    "developers should",
    "researchers should",
    "in our opinion",
    "in my opinion",
    "we believe",
    "i believe",
    "we think",
    "i think",
)

_VERB_RE = re.compile(
    r"\b(?:is|are|was|were|be|been|being|has|have|had|does|do|did|"
    r"can|could|may|might|will|would|shows?|showed|finds?|found|"
    r"reports?|reported|indicates?|indicated|suggests?|suggested|"
    r"increases?|increased|decreases?|decreased|improves?|improved|"
    r"achieves?|achieved|"
    r"reduces?|reduced|contains?|contained|introduces?|introduced|"
    r"completes?|completed|uses?|used|produces?|produced|"
    r"outperforms?|outperformed|affects?|affected|requires?|required|"
    r"involves?|involved|compares?|compared|leaves?|raises?|raised|"
    r"supports?|supported|conditions?|conditioned|provides?|provided|"
    r"pools?|pooled|remains?|remained|differs?|differed|"
    r"correlates?|correlated|causes?|caused|leads?|led|evaluates?|evaluated)\b",
    re.IGNORECASE,
)

_SPLIT_CONNECTOR_RE = re.compile(r",\s+(?:and|but|while|whereas)\s+", re.IGNORECASE)
_SHARED_SUBJECT_CONNECTOR_RE = re.compile(r"\s+and\s+", re.IGNORECASE)


def extract_citations(text: str) -> list[str]:
    """Return citations in source order with duplicates removed."""
    seen: set[str] = set()
    citations: list[str] = []
    for match in _CITATION_RE.findall(text):
        if match not in seen:
            seen.add(match)
            citations.append(match)
    return citations


def _strip_markdown_prefix(text: str) -> str:
    previous = None
    current = text.strip()
    while previous != current:
        previous = current
        current = _MARKDOWN_PREFIX_RE.sub("", current).strip()
    return current


def split_sentences(report: str) -> list[str]:
    """Split a Markdown report into sentence-like units without external NLP deps."""
    normalized = report.replace("\r\n", "\n").replace("\r", "\n")
    units: list[str] = []

    for paragraph in re.split(r"\n\s*\n|\n", normalized):
        raw_paragraph = paragraph.strip()
        if not raw_paragraph:
            continue

        if re.fullmatch(
            r"(?:#{1,6}\s*)?\*{0,2}references\*{0,2}\s*:?",
            raw_paragraph,
            re.IGNORECASE,
        ):
            break

        if raw_paragraph.startswith("#") or raw_paragraph.startswith("```"):
            continue
        paragraph = _strip_markdown_prefix(raw_paragraph)
        if not paragraph:
            continue

        is_table_row = (
            raw_paragraph.startswith("|")
            and raw_paragraph.endswith("|")
        )
        row_citations = (
            extract_citations(raw_paragraph)
            if is_table_row
            else []
        )

        # Treat Markdown table pipes as cell boundaries rather than claim text.
        paragraph = re.sub(r"^\s*\|\s*|\s*\|\s*$", "", paragraph)
        paragraph = re.sub(r"\s+\|\s+", "\n", paragraph)

        # Remove an inline bold section heading such as
        # "**Security: conflicting evidence.**" while preserving the
        # factual sentence that follows it.
        paragraph = re.sub(
            r"^\*\*[^*\n]+:[^*\n]+\.\*\*\s*",
            "",
            paragraph,
        ).strip()

        if not paragraph:
            continue

        for cell in paragraph.splitlines():
            cell = cell.strip()
            if not cell:
                continue

            cell_sentences = [
                sentence.strip()
                for sentence in _SENTENCE_BOUNDARY_RE.split(cell)
                if sentence.strip()
            ]
            if not cell_sentences:
                continue

            # A citation attached to the final sentence of a paragraph/cell
            # may support the preceding factual sentences in that same unit.
            trailing_citations = extract_citations(cell_sentences[-1])
            if trailing_citations:
                citation_suffix = " ".join(trailing_citations)
                cell_sentences = [
                    sentence
                    if extract_citations(sentence)
                    else f"{sentence} {citation_suffix}"
                    for sentence in cell_sentences
                ]

            # Citations elsewhere in the same Markdown table row may support
            # adjacent factual cells in that row, but never cross into
            # another row.
            if row_citations:
                citation_suffix = " ".join(row_citations)
                cell_sentences = [
                    sentence
                    if extract_citations(sentence)
                    else f"{sentence} {citation_suffix}"
                    for sentence in cell_sentences
                ]

            units.extend(cell_sentences)

    return units


def _without_citations(text: str) -> str:
    text = _CITATION_RE.sub("", text)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip(" \t\n,;:")


def _looks_factual(text: str) -> bool:
    stripped = _without_citations(text).strip()
    if not stripped or stripped.endswith("?"):
        return False

    lowered = stripped.lower()
    if any(lowered.startswith(prefix) for prefix in _NON_FACTUAL_PREFIXES):
        return False

    words = re.findall(r"\b\w+\b", stripped)
    has_verb = bool(_VERB_RE.search(stripped))

    if not has_verb:
        return False

    return True


def _has_clause_shape(text: str) -> bool:
    cleaned = _without_citations(text)
    words = re.findall(r"\b[\w'-]+\b", cleaned)
    if len(words) < 3:
        return False
    return bool(_VERB_RE.search(cleaned))

def _split_shared_subject_clause(clause: str) -> list[str] | None:
    """Split 'subject verb ... and verb ...' while preserving the shared subject."""
    for match in _SHARED_SUBJECT_CONNECTOR_RE.finditer(clause):
        left = clause[: match.start()].strip()
        right = clause[match.end() :].strip()

        if not _has_clause_shape(left):
            continue

        right_cleaned = _without_citations(right)

        # Only split when the right side starts with a recognized verb.
        if not _VERB_RE.match(right_cleaned):
            continue

        left_cleaned = _without_citations(left)

        # If the coordination occurs inside a "that" complement, preserve
        # the embedded subject rather than reusing the matrix-clause subject.
        that_match = re.search(r"\bthat\s+", left_cleaned, re.IGNORECASE)
        if that_match:
            matrix_prefix = left_cleaned[: that_match.end()].strip()
            embedded = left_cleaned[that_match.end() :].strip()
            embedded_verb = _VERB_RE.search(embedded)

            if embedded_verb:
                embedded_subject = embedded[: embedded_verb.start()].strip()
                if embedded_subject:
                    return [
                        left,
                        f"{matrix_prefix} {embedded_subject} {right}",
                    ]

        first_verb = _VERB_RE.search(left_cleaned)
        if not first_verb:
            continue

        subject = left_cleaned[: first_verb.start()].strip()
        if not subject:
            continue

        return [left, f"{subject} {right}"]

    return None

def split_atomic_clauses(sentence: str) -> list[str]:
    """Conservatively split a sentence when both conjunction sides are clauses."""
    clauses = [sentence.strip()]

    expanded: list[str] = []
    for clause in clauses:
        parts = [part.strip() for part in re.split(r";\s*", clause) if part.strip()]
        expanded.extend(parts)
    clauses = expanded

    changed = True
    while changed:
        changed = False
        next_clauses: list[str] = []
        for clause in clauses:
            match = _SPLIT_CONNECTOR_RE.search(clause)
            if not match:
                next_clauses.append(clause)
                continue

            left = clause[: match.start()].strip()
            right = clause[match.end() :].strip()
            if _has_clause_shape(left) and _has_clause_shape(right):
                next_clauses.extend([left, right])
                changed = True
            else:
                next_clauses.append(clause)
        clauses = next_clauses

    shared_subject_clauses: list[str] = []
    for clause in clauses:
        split_clause = _split_shared_subject_clause(clause)
        if split_clause:
            shared_subject_clauses.extend(split_clause)
        else:
            shared_subject_clauses.append(clause)

    return shared_subject_clauses


def _normalize_claim_text(clause: str) -> str:
    text = _without_citations(clause)
    text = re.sub(r"\s*\[\]\([^)]+\)", "", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*([^*\n]+?)\*", r"\1", text)
    text = text.replace("**", "")
    text = re.sub(r"^[,;:\-–—]+\s*", "", text).strip()
    if text:
        first_alpha = next((i for i, ch in enumerate(text) if ch.isalpha()), None)
        if first_alpha is not None and text[first_alpha].islower():
            text = text[:first_alpha] + text[first_alpha].upper() + text[first_alpha + 1 :]
    if text and text[-1] not in ".!?":
        text += "."
    return text


def extract_claims(report: str, *, report_id: str) -> ClaimExtractionResult:
    """Extract conservative atomic factual claims from a Markdown research report."""
    claims: list[AtomicClaim] = []

    for source_sentence in split_sentences(report):
        if not _looks_factual(source_sentence):
            continue

        sentence_citations = extract_citations(source_sentence)
        for clause in split_atomic_clauses(source_sentence):
            if not _looks_factual(clause):
                continue

            claim_text = _normalize_claim_text(clause)
            if not claim_text:
                continue

            clause_citations = extract_citations(clause)
            citations = clause_citations or sentence_citations
            claim_id = f"C{len(claims) + 1:03d}"
            claims.append(
                AtomicClaim(
                    claim_id=claim_id,
                    claim=claim_text,
                    citations=citations,
                    source_sentence=source_sentence,
                )
            )

    return ClaimExtractionResult(report_id=report_id, claims=claims)


def extract_claims_from_path(path: Path, *, report_id: str | None = None) -> ClaimExtractionResult:
    text = path.read_text(encoding="utf-8")
    return extract_claims(text, report_id=report_id or path.stem)


def _write_output(result: ClaimExtractionResult, output: Path | None) -> None:
    payload = result.to_json()
    if output is None:
        print(payload)
        return

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(payload + "\n", encoding="utf-8")
    print(f"wrote {len(result.claims)} claims to {output}")


def main(argv: Iterable[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Extract machine-readable atomic factual claims from a research report."
    )
    parser.add_argument("report", type=Path, help="Markdown/text research report path.")
    parser.add_argument("--report-id", help="Stable report identifier. Defaults to file stem.")
    parser.add_argument("--output", type=Path, help="Optional JSON output path.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    result = extract_claims_from_path(args.report, report_id=args.report_id)
    _write_output(result, args.output)


if __name__ == "__main__":
    main()

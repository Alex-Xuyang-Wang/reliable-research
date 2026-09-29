from __future__ import annotations

from pathlib import Path
import unittest

from research.claims.extractor import extract_claims


FIXTURE = Path(__file__).parent / "fixtures" / "sample_research_report.md"


class ClaimExtractorTests(unittest.TestCase):
    def test_compound_claim_is_split_and_citation_is_preserved(self) -> None:
        result = extract_claims(FIXTURE.read_text(encoding="utf-8"), report_id="sample-report")

        self.assertGreaterEqual(len(result.claims), 3)
        self.assertEqual(result.claims[0].claim_id, "C001")
        self.assertEqual(
            result.claims[0].claim,
            "Developers using an AI coding assistant completed tasks 30% faster.",
        )
        self.assertEqual(result.claims[0].citations, ["[1]"])
        self.assertEqual(
            result.claims[1].claim,
            "Generated code contained more security weaknesses.",
        )
        self.assertEqual(result.claims[1].citations, ["[1]"])

    def test_recommendation_is_not_extracted(self) -> None:
        result = extract_claims(FIXTURE.read_text(encoding="utf-8"), report_id="sample-report")
        claims = [claim.claim.lower() for claim in result.claims]
        self.assertFalse(any(claim.startswith("we recommend") for claim in claims))

    def test_ids_are_stable_for_same_input(self) -> None:
        report = FIXTURE.read_text(encoding="utf-8")
        first = extract_claims(report, report_id="sample-report")
        second = extract_claims(report, report_id="sample-report")
        self.assertEqual(
            [claim.claim_id for claim in first.claims],
            [claim.claim_id for claim in second.claims],
        )
        self.assertEqual(first.to_dict(), second.to_dict())

    def test_heading_like_phrase_is_not_extracted(self) -> None:
        reports = [
            "AI coding assistant productivity research results",
            "AI coding assistant productivity research results.",
        ]

        for report in reports:
            result = extract_claims(report, report_id="heading-test")
            self.assertEqual(result.claims, [])

    def test_common_factual_verb_is_extracted(self) -> None:
        report = "The model achieved 92% accuracy [4]."
        result = extract_claims(report, report_id="verb-test")

        self.assertEqual(len(result.claims), 1)
        self.assertEqual(
            result.claims[0].claim,
            "The model achieved 92% accuracy.",
        )
        self.assertEqual(result.claims[0].citations, ["[4]"])

    def test_shared_subject_compound_claim_is_split(self) -> None:
        report = (
            "A follow-up study evaluated 55 developers "
            "and reported higher task completion rates [2]."
        )
        result = extract_claims(report, report_id="shared-subject-test")

        self.assertEqual(len(result.claims), 2)
        self.assertEqual(
            result.claims[0].claim,
            "A follow-up study evaluated 55 developers.",
        )
        self.assertEqual(
            result.claims[1].claim,
            "A follow-up study reported higher task completion rates.",
        )
        self.assertEqual(result.claims[0].citations, ["[2]"])
        self.assertEqual(result.claims[1].citations, ["[2]"])

    def test_noun_coordination_is_not_split(self) -> None:
        report = "The study used Python and Java [3]."
        result = extract_claims(report, report_id="noun-coordination-test")

        self.assertEqual(len(result.claims), 1)
        self.assertEqual(
            result.claims[0].claim,
            "The study used Python and Java.",
        )
        self.assertEqual(result.claims[0].citations, ["[3]"])

    def test_citation_range_is_parsed_and_removed_from_claim_text(self) -> None:
        report = "The evidence is mixed [1–5]."
        result = extract_claims(report, report_id="citation-range-test")

        self.assertEqual(len(result.claims), 1)
        self.assertEqual(
            result.claims[0].claim,
            "The evidence is mixed.",
        )
        self.assertEqual(result.claims[0].citations, ["[1–5]"])


    def test_nested_shared_subject_split_preserves_participant_subject(self) -> None:
        report = (
            "Perry and colleagues found that participants using a Codex-based assistant "
            "produced less secure solutions to security-related programming tasks "
            "and were more likely to believe their code was secure [2]."
        )
        result = extract_claims(report, report_id="nested-subject-test")

        self.assertEqual(len(result.claims), 2)
        self.assertEqual(
            result.claims[0].claim,
            "Perry and colleagues found that participants using a Codex-based assistant "
            "produced less secure solutions to security-related programming tasks.",
        )
        self.assertEqual(
            result.claims[1].claim,
            "Perry and colleagues found that participants using a Codex-based assistant "
            "were more likely to believe their code was secure.",
        )
        self.assertEqual(result.claims[0].citations, ["[2]"])
        self.assertEqual(result.claims[1].citations, ["[2]"])


    def test_reference_section_entries_are_not_extracted_as_claims(self) -> None:
        report = (
            "**References**\n\n"
            "[2] Perry, N., et al. (2023). "
            "[*Do Users Write More Insecure Code with AI Assistants?*]"
            "(https://arxiv.org/abs/2211.03622) ACM CCS."
        )
        result = extract_claims(report, report_id="reference-section-test")

        self.assertEqual(result.claims, [])


    def test_markdown_emphasis_is_removed_from_claim_text(self) -> None:
        report = "The preferred estimate was **21% less time** [2]."
        result = extract_claims(report, report_id="markdown-cleanup-test")

        self.assertEqual(len(result.claims), 1)
        self.assertEqual(
            result.claims[0].claim,
            "The preferred estimate was 21% less time.",
        )
        self.assertEqual(result.claims[0].citations, ["[2]"])


    def test_markdown_citation_link_is_removed_from_claim_text(self) -> None:
        report = (
            "The model achieved 92% accuracy "
            "[[4]](https://example.com/source)."
        )
        result = extract_claims(report, report_id="markdown-citation-link-test")

        self.assertEqual(len(result.claims), 1)
        self.assertEqual(
            result.claims[0].claim,
            "The model achieved 92% accuracy.",
        )
        self.assertEqual(result.claims[0].citations, ["[4]"])


    def test_inline_bold_heading_is_not_included_in_claim_text(self) -> None:
        report = (
            "- **Security: conflicting evidence.** "
            "Participants using an AI assistant produced less secure solutions [2]."
        )
        result = extract_claims(report, report_id="inline-heading-test")

        self.assertEqual(len(result.claims), 1)
        self.assertEqual(
            result.claims[0].claim,
            "Participants using an AI assistant produced less secure solutions.",
        )
        self.assertEqual(result.claims[0].citations, ["[2]"])


    def test_split_claims_remove_unmatched_bold_markers(self) -> None:
        report = (
            "**AI assistants can reduce task time, "
            "but the effect was not universal.** [1]"
        )
        result = extract_claims(report, report_id="unmatched-bold-test")

        self.assertEqual(len(result.claims), 2)
        self.assertEqual(
            result.claims[0].claim,
            "AI assistants can reduce task time.",
        )
        self.assertEqual(
            result.claims[1].claim,
            "The effect was not universal.",
        )
        self.assertEqual(result.claims[0].citations, ["[1]"])
        self.assertEqual(result.claims[1].citations, ["[1]"])


    def test_factual_claim_with_involved_is_extracted(self) -> None:
        report = (
            "GitHub’s randomized trial involved 202 experienced developers "
            "implementing web-server API endpoints [1]."
        )
        result = extract_claims(report, report_id="involved-verb-test")

        self.assertEqual(len(result.claims), 1)
        self.assertEqual(
            result.claims[0].claim,
            "GitHub’s randomized trial involved 202 experienced developers "
            "implementing web-server API endpoints.",
        )
        self.assertEqual(result.claims[0].citations, ["[1]"])


    def test_table_cell_markers_are_removed_from_claim_text(self) -> None:
        report = "| The experiment used 95 professional developers [1]. |"
        result = extract_claims(report, report_id="table-cleanup-test")

        self.assertEqual(len(result.claims), 1)
        self.assertEqual(
            result.claims[0].claim,
            "The experiment used 95 professional developers.",
        )
        self.assertEqual(result.claims[0].citations, ["[1]"])


    def test_table_cell_separator_does_not_merge_adjacent_cells(self) -> None:
        report = (
            "Completion required passing automated tests [1]. "
            "| One standardized task."
        )
        result = extract_claims(report, report_id="table-cell-separator-test")

        self.assertEqual(len(result.claims), 1)
        self.assertEqual(
            result.claims[0].claim,
            "Completion required passing automated tests.",
        )
        self.assertEqual(result.claims[0].citations, ["[1]"])


    def test_table_cell_boundary_after_citation_link_is_split(self) -> None:
        report = (
            "Completion required passing automated tests. "
            "[[1]](https://example.com/source) "
            "| One standardized task."
        )
        result = extract_claims(report, report_id="table-citation-boundary-test")

        self.assertEqual(len(result.claims), 1)
        self.assertEqual(
            result.claims[0].claim,
            "Completion required passing automated tests.",
        )
        self.assertEqual(result.claims[0].citations, ["[1]"])


    def test_factual_claim_with_compared_is_extracted(self) -> None:
        report = (
            "He and colleagues compared Cursor-adopting open-source projects "
            "with matched controls using a difference-in-differences design [5]."
        )
        result = extract_claims(report, report_id="compared-verb-test")

        self.assertEqual(len(result.claims), 1)
        self.assertEqual(
            result.claims[0].claim,
            "He and colleagues compared Cursor-adopting open-source projects "
            "with matched controls using a difference-in-differences design.",
        )
        self.assertEqual(result.claims[0].citations, ["[5]"])


    def test_factual_claim_with_leaves_is_extracted(self) -> None:
        report = (
            "The nonrandomized design also leaves greater uncertainty "
            "about causation than a controlled trial [5]."
        )
        result = extract_claims(report, report_id="leaves-verb-test")

        self.assertEqual(len(result.claims), 1)
        self.assertEqual(
            result.claims[0].claim,
            "The nonrandomized design also leaves greater uncertainty "
            "about causation than a controlled trial.",
        )
        self.assertEqual(result.claims[0].citations, ["[5]"])


    def test_factual_claim_with_raises_is_extracted(self) -> None:
        report = (
            "Recent observational evidence also raises concerns "
            "about growing complexity [1–5]."
        )
        result = extract_claims(report, report_id="raises-verb-test")

        self.assertEqual(len(result.claims), 1)
        self.assertEqual(
            result.claims[0].claim,
            "Recent observational evidence also raises concerns "
            "about growing complexity.",
        )
        self.assertEqual(result.claims[0].citations, ["[1–5]"])


    def test_factual_claim_with_supports_is_extracted(self) -> None:
        report = (
            "The evidence supports benefits that depend on the task, "
            "developer, and tool—not a single general percentage improvement [1]."
        )
        result = extract_claims(report, report_id="supports-verb-test")

        self.assertEqual(len(result.claims), 1)
        self.assertEqual(
            result.claims[0].claim,
            "The evidence supports benefits that depend on the task, "
            "developer, and tool—not a single general percentage improvement.",
        )
        self.assertEqual(result.claims[0].citations, ["[1]"])


    def test_factual_claim_with_conditions_is_extracted(self) -> None:
        report = "The time estimate conditions on completion [1]."
        result = extract_claims(report, report_id="conditions-verb-test")

        self.assertEqual(len(result.claims), 1)
        self.assertEqual(
            result.claims[0].claim,
            "The time estimate conditions on completion.",
        )
        self.assertEqual(result.claims[0].citations, ["[1]"])


    def test_factual_claim_with_provide_is_extracted(self) -> None:
        report = (
            "Larger workplace experiments provide supporting—but indirect—evidence [4]."
        )
        result = extract_claims(report, report_id="provide-verb-test")

        self.assertEqual(len(result.claims), 1)
        self.assertEqual(
            result.claims[0].claim,
            "Larger workplace experiments provide supporting—but indirect—evidence.",
        )
        self.assertEqual(result.claims[0].citations, ["[4]"])


    def test_factual_claim_with_pooled_is_extracted(self) -> None:
        report = (
            "Cui et al. pooled randomized trials involving 4,867 developers "
            "at Microsoft, Accenture, and another large company [4]."
        )
        result = extract_claims(report, report_id="pooled-verb-test")

        self.assertEqual(len(result.claims), 1)
        self.assertEqual(
            result.claims[0].claim,
            "Cui et al. pooled randomized trials involving 4,867 developers "
            "at Microsoft, Accenture, and another large company.",
        )
        self.assertEqual(result.claims[0].citations, ["[4]"])


    def test_factual_claim_with_remains_is_extracted(self) -> None:
        report = "More recent evidence remains uncertain [5]."
        result = extract_claims(report, report_id="remains-verb-test")

        self.assertEqual(len(result.claims), 1)
        self.assertEqual(
            result.claims[0].claim,
            "More recent evidence remains uncertain.",
        )
        self.assertEqual(result.claims[0].citations, ["[5]"])


    def test_factual_claim_with_differ_is_extracted(self) -> None:
        report = (
            "The studies differ too much in tasks, participants, tools, "
            "and outcome measures to justify averaging their headline percentages [1]."
        )
        result = extract_claims(report, report_id="differ-verb-test")

        self.assertEqual(len(result.claims), 1)
        self.assertEqual(
            result.claims[0].claim,
            "The studies differ too much in tasks, participants, tools, "
            "and outcome measures to justify averaging their headline percentages.",
        )
        self.assertEqual(result.claims[0].citations, ["[1]"])


    def test_trailing_paragraph_citation_is_propagated_to_earlier_claims(self) -> None:
        report = (
            "GitHub’s randomized trial involved 202 experienced developers "
            "implementing web-server API endpoints. "
            "Developers assigned Copilot were reported to be more likely "
            "to pass all unit tests [1]."
        )
        result = extract_claims(report, report_id="paragraph-citation-test")

        self.assertEqual(len(result.claims), 2)
        self.assertEqual(result.claims[0].citations, ["[1]"])
        self.assertEqual(result.claims[1].citations, ["[1]"])


    def test_table_row_citation_is_available_to_adjacent_factual_cell(self) -> None:
        report = (
            "| Completion required passing automated tests. "
            "[[1]](https://example.com/source) "
            "| One standardized task; the time estimate conditions on completion. |"
        )
        result = extract_claims(report, report_id="table-row-citation-test")

        self.assertEqual(len(result.claims), 2)
        self.assertEqual(
            result.claims[0].claim,
            "Completion required passing automated tests.",
        )
        self.assertEqual(result.claims[0].citations, ["[1]"])

        self.assertEqual(
            result.claims[1].claim,
            "The time estimate conditions on completion.",
        )
        self.assertEqual(result.claims[1].citations, ["[1]"])


    def test_single_markdown_emphasis_is_removed_from_claim_text(self) -> None:
        report = (
            "The adjusted estimate was not statistically significant "
            "(*p*=0.086) [2]."
        )
        result = extract_claims(report, report_id="single-emphasis-test")

        self.assertEqual(len(result.claims), 1)
        self.assertEqual(
            result.claims[0].claim,
            "The adjusted estimate was not statistically significant (p=0.086).",
        )
        self.assertEqual(result.claims[0].citations, ["[2]"])


    def test_sentence_boundary_before_closing_bold_marker_is_preserved(self) -> None:
        report = (
            "**The effect is not universal.** "
            "Randomized studies show substantial time savings."
        )
        result = extract_claims(report, report_id="bold-boundary-test")

        self.assertEqual(
            [claim.claim for claim in result.claims],
            [
                "The effect is not universal.",
                "Randomized studies show substantial time savings.",
            ],
        )


if __name__ == "__main__":
    unittest.main()

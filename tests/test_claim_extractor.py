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

if __name__ == "__main__":
    unittest.main()

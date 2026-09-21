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


if __name__ == "__main__":
    unittest.main()

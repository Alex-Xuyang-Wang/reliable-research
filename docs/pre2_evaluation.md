# Phase 2 Claim Extraction Evaluation

## 1. Evaluation Scope

This evaluation examines the atomic claim extractor on the real Q001 and Q002 baseline research reports.

The purpose is to measure claim-extraction quality on real generated research reports before Phase 2 is considered complete.

Reports evaluated:

- Q001
- Q002

## 2. Human Annotation Procedure

Claims are manually reviewed using the annotation rubric in:

`docs/pre2_annotation_rubric.md`

The review checks:

- whether factual claims were extracted,
- whether non-factual text was incorrectly extracted,
- whether claims were over-split,
- whether multiple claims were incorrectly merged,
- whether citation associations were preserved,
- whether Markdown citation syntax affected extraction.

## 3. Pilot Sample

Target:

20–30 extracted claims or claim candidates across Q001 and Q002.

Final pilot sample:

- 24 extracted claims reviewed out of 46 total extracted claims across Q001 and Q002.
- Both annotators independently reviewed the same 24 claims.
- Disagreements were adjudicated into a final consensus annotation.
- A separate report-level review of the full Q001 and Q002 reports was performed to identify claims missed entirely by the extractor.

## 4. Evaluation Results

| Metric | Scope | Result |
|---|---|---:|
| Reports evaluated | Full reports | 2 |
| Extracted claims reviewed | Pilot sample | 24 / 46 |
| Factual claims in pilot | Pilot sample | 21 / 24 (87.5%) |
| False positives | Pilot sample | 3 / 24 (12.5%) |
| Semantically / atomically correct | Pilot factual claims | 11 / 21 (52.4%) |
| Split / merge errors | Pilot factual claims | 10 / 21 (47.6%) |
| Citation association retained | Pilot factual claims | 8 / 21 (38.1%) |
| Citation association errors | Pilot factual claims | 13 / 21 (61.9%) |
| Formatting clean | Pilot sample | 2 / 24 (8.3%) |
| Formatting artifacts present | Pilot sample | 22 / 24 (91.7%) |
| Report-level missed claims | Full Q001/Q002 review | 10 total (Q001: 6, Q002: 4) |

An exact claim-recall value is not reported at this stage because only 24 of the 46 extracted claims were manually annotated for factuality. The report-level missed-claim review covers both complete reports, while the extracted-claim quality metrics above are based on the 24-claim pilot sample.

## 5. Observed Errors

The human pilot identified several recurring extractor failure modes:

- **Missed claims:** 10 substantive statements were missed during full report-level review. These included evidence-synthesis statements, study-design descriptions, and methodological limitations.
- **False positives:** 3 of the 24 reviewed extracted items should not have been factual claims, including reference entries and recommendation-like text.
- **Split / merge failures:** 10 of the 21 factual pilot claims had atomicity or semantic-preservation problems. One confirmed case changed the subject of a claim during splitting.
- **Citation association failures:** 13 of the 21 factual pilot claims did not retain or correctly associate an applicable citation. Observed cases included paragraph-level citations, table-row citations, and the `[1–5]` citation range.
- **Formatting contamination:** 22 of the 24 pilot claims retained Markdown or structural artifacts, including emphasis markers, empty Markdown links, table pipes, section headings, and reference formatting.

These failures are documented before any extractor modification. Confirmed failures will be converted into regression tests before implementation changes are made.

## 6. Regression Fixes

TBD.

If no confirmed extractor failure requires a code change, record that no extractor modification was necessary.

## 7. Final Test Results

TBD after evaluation and any justified regression fixes.

## 8. Limitations

TBD after completing the Q001/Q002 pilot.

## 9. Phase 2 Conclusion

TBD after final evidence numbers are available.

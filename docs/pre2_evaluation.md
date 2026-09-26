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

20–30 claims or claim candidates across Q001 and Q002.

Final number reviewed:

TBD

## 4. Evaluation Results

| Metric | Result |
|---|---:|
| Reports evaluated | 2 |
| Human factual claims | TBD |
| Correctly extracted | TBD |
| Missed claims | TBD |
| False positives | TBD |
| Split / merge errors | TBD |
| Citation association retained | TBD |

## 5. Observed Errors

TBD after human annotation.

## 6. Regression Fixes

TBD.

If no confirmed extractor failure requires a code change, record that no extractor modification was necessary.

## 7. Final Test Results

TBD after evaluation and any justified regression fixes.

## 8. Limitations

TBD after completing the Q001/Q002 pilot.

## 9. Phase 2 Conclusion

TBD after final evidence numbers are available.

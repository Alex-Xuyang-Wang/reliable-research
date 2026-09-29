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

These failures were documented before any extractor modification. Confirmed failures were then converted into regression tests before implementation changes were made.

## 6. Regression Fixes

Confirmed extractor failures were converted into regression tests before implementation changes were made. Each new regression test was first confirmed to fail against the current extractor, then the smallest targeted fix was applied.

The fixes addressed the following failure classes:

- **Missed factual claims:** expanded factual-verb coverage for confirmed missed statements such as `involved`, `compared`, `leaves`, `raises`, `supports`, `conditions`, `provide`, `pooled`, `remains`, and `differ`.
- **Citation parsing:** added support for numeric citation ranges such as `[1–5]`.
- **Citation association:** propagated trailing paragraph citations to earlier factual sentences in the same paragraph and propagated citations across adjacent factual cells within the same Markdown table row.
- **Semantic splitting:** fixed a shared-subject split case in which an embedded subject was incorrectly replaced by the matrix-clause subject.
- **Sentence boundaries:** preserved sentence boundaries when punctuation is followed by closing Markdown emphasis markers such as `**`.
- **Reference contamination:** stopped claim extraction when the report reaches the References section.
- **Markdown normalization:** removed bold and italic emphasis markers, empty Markdown citation-link shells, and inline bold section headings from extracted claim text.
- **Table handling:** treated Markdown table pipes as cell boundaries, removed table markers from claims, and prevented adjacent cells from being merged into one claim.

The regression process was intentionally limited to failures confirmed in Q001 and Q002. Held-out benchmark reports were not used to design these fixes.

## 7. Final Test Results

After the regression fixes, the complete local test suite passed:

- **31 / 31 tests passed**
- `git diff --check` reported no whitespace errors.

The claim extractor was then re-run on the original Q001 and Q002 baseline reports without overwriting the tracked baseline claim files.

| Metric | Q001 | Q002 | Combined |
|---|---:|---:|---:|
| Extracted claims before fixes | 22 | 24 | 46 |
| Extracted claims after fixes | 30 | 28 | 58 |
| Confirmed report-level misses recovered | 6 / 6 | 4 / 4 | 10 / 10 |
| Recovered misses with citation association | 6 / 6 | 4 / 4 | 10 / 10 |
| Obvious Markdown artifacts in rerun | 0 | 0 | 0 |
| Obvious multi-sentence merged claims in rerun | 0 | 0 | 0 |

The increase from 46 to 58 extracted claims is reported only as an output-count change. It should not be interpreted as a percentage improvement in extraction quality.

The stronger before/after evidence is that all 10 report-level claims previously confirmed as missed were recovered in the rerun, and every recovered claim had at least one associated citation.

Automated post-fix scans also found no remaining obvious Markdown artifacts or obvious cases in which two complete sentences were merged into one extracted claim in Q001 or Q002.

## 8. Limitations

This evaluation has several important limitations:

- Only Q001 and Q002 were used for the Phase 2 pilot and regression analysis.
- Only 24 of the original 46 extracted claims were manually annotated at the claim level, so an exact full-report precision or recall value is not reported.
- The 10 report-level missed claims were manually identified from the complete Q001 and Q002 reports, but this does not guarantee that every possible missed claim was found.
- The post-fix Markdown-artifact and multi-sentence-merge checks are targeted heuristic scans rather than complete manual re-annotation of all 58 post-fix claims.
- Exact-text before/after comparison is difficult because formatting cleanup and improved splitting can change claim text even when the underlying factual statement is the same.
- Citation propagation is heuristic rather than a general citation-scope resolver. A trailing paragraph citation or a citation elsewhere in the same Markdown table row may not semantically support every nearby factual claim, so the current rule can potentially over-associate citations when the true citation scope is narrower. This should be evaluated separately in later citation-resolution or verification stages.
- The fixes were developed from confirmed Q001/Q002 failures and therefore should not be treated as evidence of generalization to unseen reports.
- Q007 and Q008 remain held out and were not used for debugging, heuristic development, or regression-fix design.

## 9. Phase 2 Conclusion

The Q001/Q002 pilot identified substantial weaknesses in the original extractor, particularly in citation association, Markdown handling, sentence and clause splitting, and recall of factual statements.

The regression process converted confirmed failures into tests before modifying the extractor. After the fixes, the full test suite passed, all 10 confirmed report-level missed claims were recovered, all 10 recovered claims were extracted with an associated citation, and targeted rerun checks found no obvious Markdown artifacts or multi-sentence merge failures in Q001 or Q002.

These results provide evidence that the extractor is materially more reliable on the Phase 2 pilot reports. They do not establish full-report precision or recall, and they do not establish generalization to held-out reports. Those questions should be evaluated separately without using the held-out data for further tuning.

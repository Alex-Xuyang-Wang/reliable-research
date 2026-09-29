# Pre2 Claim Extraction Annotation Rubric

## Purpose

This rubric is used to manually evaluate atomic claims extracted from the Q001 and Q002 baseline research reports.

The evaluation focuses on claim-extraction quality, not whether the underlying research claim is scientifically true.

## Consensus Annotation Schema

The consensus annotation file uses the following columns:

- `report_id`
- `claim_id`
- `claim_text`
- `citations`
- `should_exist`
- `split_correct`
- `citation_correct`
- `format_clean`
- `error_type`
- `notes`

The first four columns identify the extracted item and its current citation output. The remaining fields contain the adjudicated evaluation labels.

## Annotation Fields

### should_exist

Use `YES` when the extracted item should exist as a factual, externally verifiable claim.

Use `NO` when the extracted item should not be treated as a factual claim, including cases such as:

- reference entries,
- headings,
- recommendations,
- organizational text,
- non-factual commentary,
- other structural or non-claim text.

### split_correct

Use `YES` when atomicity and semantic meaning are preserved.

Use `NO` when:

- multiple factual propositions are incorrectly merged,
- a factual proposition is unnecessarily over-split,
- the subject of the claim changes,
- the extracted claim changes or loses the intended factual meaning.

Use `NA` when `should_exist = NO`.

Heading contamination, table contamination, or Markdown contamination does not by itself make `split_correct = NO`. Those are formatting or structural problems unless they also change atomicity or meaning.

### citation_correct

Use `YES` when an applicable citation from the original report is correctly retained and associated with the extracted claim.

Use `NO` when the original report contains an applicable citation but the extractor:

- loses the citation,
- fails to parse the citation,
- propagates the citation incorrectly,
- associates the wrong citation with the claim.

Use `NA` when no applicable citation exists in the original report for that item.

An extracted value of `citations = []` does not automatically imply `citation_correct = NO`. The original report must be checked to determine whether a citation is actually applicable to the claim.

### format_clean

Use `YES` when the extracted claim text is clean enough to be passed directly to the verifier.

Use `NO` when the claim still contains structural or formatting artifacts such as:

- Markdown emphasis markers,
- raw or empty Markdown links,
- table pipes,
- heading fragments,
- reference formatting,
- other structural artifacts that should not be part of the claim text.

### error_type

Use the error categories present in the consensus annotation file:

- `NONE`
- `CITATION_MISSING`
- `MARKDOWN_ARTIFACT`
- `REFERENCE_CONTAMINATION`
- `MULTIPLE`

Definitions:

- `NONE`: no extraction error is assigned after adjudication.
- `CITATION_MISSING`: an applicable citation from the original report was not correctly retained or associated.
- `MARKDOWN_ARTIFACT`: Markdown or structural formatting remains in the extracted claim text.
- `REFERENCE_CONTAMINATION`: reference-section or reference-entry content was incorrectly extracted as a claim.
- `MULTIPLE`: more than one confirmed extraction problem applies to the same item.

Do not introduce additional `error_type` values during consensus annotation unless the schema is explicitly revised.

### notes

Use `notes` to record a short adjudication rationale.

The note should briefly explain why the final labels were chosen, especially when:

- annotators originally disagreed,
- citation scope required checking the original report,
- a split or semantic-preservation issue was subtle,
- multiple error types were present.

## Annotation Procedure

For each extracted claim:

1. Locate the corresponding text in the original report.
2. Decide whether the extracted item should exist as a factual claim.
3. If it should exist, evaluate whether atomicity and semantic meaning are preserved.
4. Check the citation scope in the original report and evaluate whether the applicable citation was retained and associated correctly.
5. Check whether the extracted text is clean enough to feed directly into the verifier.
6. Assign the applicable `error_type`.
7. Record a short adjudication rationale in `notes`.

A separate report-level review of the original Q001 and Q002 reports is used to identify factual claims that were missed entirely by the extractor. Those missed claims are recorded separately and are not represented by adding a `MISS` value to the consensus CSV `error_type` field.

# Pre2 Claim Extraction Annotation Rubric

## Purpose

This rubric is used to manually evaluate atomic claims extracted from the Q001 and Q002 baseline research reports.

The evaluation focuses on claim extraction quality, not whether the underlying research claim is scientifically true.

## Annotation Fields

### is_factual

Use `YES` when the extracted text makes a factual, externally verifiable statement.

Use `NO` for:
- headings
- recommendations
- rhetorical statements
- purely organizational text
- non-factual commentary

### correctly_extracted

Use `YES` when:
- the factual content is preserved,
- the claim is sufficiently atomic,
- no unrelated factual content is merged,
- no necessary factual content is lost.

Use `NO` otherwise.

### error_type

Use one of:

- `MISS`
- `FALSE_POSITIVE`
- `OVER_SPLIT`
- `UNDER_SPLIT`
- `CITATION_ASSOCIATION_ERROR`
- `MARKDOWN_CITATION_PARSE_ERROR`
- `OTHER`

Leave blank when no extraction error is present.

### citation_association_correct

Use `YES` when the citation attached to the extracted claim matches the citation attached to that claim in the original report.

Use `NO` when the citation is missing, incorrect, or associated with the wrong claim.

Use `NA` when no citation is expected.

## Error Definitions

### MISS

A factual claim appears in the original report but is not extracted.

For a missed claim, create a manual annotation ID such as:

- `Q001-MISS-001`
- `Q002-MISS-001`

Record the missed factual statement in `claim_text`, set:

- `is_factual` = `YES`
- `correctly_extracted` = `NO`
- `error_type` = `MISS`

Preserve the citation from the original report in the `citation` field when one is present.

### FALSE_POSITIVE

Non-factual text is incorrectly extracted as a factual claim.

### OVER_SPLIT

A single factual claim is unnecessarily split into multiple claims.

### UNDER_SPLIT

Multiple independent factual claims remain merged into one extracted claim.

### CITATION_ASSOCIATION_ERROR

The extracted claim has an incorrect or missing citation association.

### MARKDOWN_CITATION_PARSE_ERROR

Markdown citation syntax contaminates, breaks, or prevents correct claim extraction.

### OTHER

Any confirmed extraction failure not covered by the categories above.

## Annotation Procedure

For each extracted claim:

1. Locate the corresponding text in the original report.
2. Decide whether it is factual.
3. Check whether the extracted claim preserves the intended factual meaning.
4. Check whether it should be split or merged differently.
5. Check citation association.
6. Record any confirmed error and a short note.

Also review the original report directly for factual claims that were completely missed by the extractor.

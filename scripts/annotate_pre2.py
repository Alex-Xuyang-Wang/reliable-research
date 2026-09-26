import csv
from pathlib import Path

path = Path("data/evaluation/pre2_claim_pilot_xuyang.csv")

ERROR_TYPES = [
    "NONE",
    "FALSE_POSITIVE",
    "SPLIT_ERROR",
    "CITATION_MISSING",
    "CITATION_RANGE",
    "TABLE_CONTAMINATION",
    "HEADING_CONTAMINATION",
    "REFERENCE_CONTAMINATION",
    "MARKDOWN_ARTIFACT",
    "MULTIPLE",
]

with path.open(newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
    fieldnames = list(rows[0].keys())


def save():
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def ask(prompt, allowed):
    while True:
        value = input(f"{prompt} [{'/'.join(allowed)}] (Q=quit): ").strip().upper()

        if value == "Q":
            save()
            print("\nSaved. Exiting annotation.")
            raise SystemExit

        if value in allowed:
            return value

        print(f"Invalid value. Choose one of: {', '.join(allowed)}")


remaining = sum(
    1 for row in rows
    if not row["should_exist"].strip()
)

print(f"{remaining} claims remaining.")

for row in rows:
    if row["should_exist"].strip():
        continue

    print("\n" + "=" * 80)
    print(f'{row["report_id"]} {row["claim_id"]}')
    print("-" * 80)
    print(row["claim_text"])
    print(f'citations: {row["citations"] or "(none)"}')
    print()

    row["should_exist"] = ask(
        "should_exist",
        ["YES", "NO"],
    )

    row["split_correct"] = ask(
        "split_correct",
        ["YES", "NO", "NA"],
    )

    row["citation_correct"] = ask(
        "citation_correct",
        ["YES", "NO", "NA"],
    )

    row["format_clean"] = ask(
        "format_clean",
        ["YES", "NO"],
    )

    print("\nerror_type options:")
    for error in ERROR_TYPES:
        print(" -", error)

    row["error_type"] = ask(
        "error_type",
        ERROR_TYPES,
    )

    row["notes"] = input("notes: ").strip()

    save()
    print("Saved.")

print(f"\nAll annotations complete.")
print(f"Saved to {path}")

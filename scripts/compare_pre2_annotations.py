import csv
from pathlib import Path

XUYANG = Path("data/evaluation/pre2_claim_pilot_xuyang.csv")
JIALIANG = Path("data/evaluation/pre2_claim_pilot_jialiang.csv")
OUTPUT = Path("data/evaluation/pre2_annotation_disagreements.csv")

FIELDS = [
    "should_exist",
    "split_correct",
    "citation_correct",
    "format_clean",
    "error_type",
]

def load(path):
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return {
        (row["report_id"], row["claim_id"]): row
        for row in rows
    }

xuyang = load(XUYANG)
jialiang = load(JIALIANG)

keys = sorted(set(xuyang) & set(jialiang))

completed = [
    key for key in keys
    if xuyang[key]["should_exist"].strip()
    and jialiang[key]["should_exist"].strip()
]

disagreements = []

for key in completed:
    x = xuyang[key]
    j = jialiang[key]

    differing_fields = [
        field for field in FIELDS
        if x[field].strip() != j[field].strip()
    ]

    if differing_fields:
        disagreements.append({
            "report_id": key[0],
            "claim_id": key[1],
            "differing_fields": ";".join(differing_fields),
            "xuyang_should_exist": x["should_exist"],
            "jialiang_should_exist": j["should_exist"],
            "xuyang_split_correct": x["split_correct"],
            "jialiang_split_correct": j["split_correct"],
            "xuyang_citation_correct": x["citation_correct"],
            "jialiang_citation_correct": j["citation_correct"],
            "xuyang_format_clean": x["format_clean"],
            "jialiang_format_clean": j["format_clean"],
            "xuyang_error_type": x["error_type"],
            "jialiang_error_type": j["error_type"],
            "xuyang_notes": x["notes"],
            "jialiang_notes": j["notes"],
        })

print(f"Claims in both files: {len(keys)}")
print(f"Claims completed by both annotators: {len(completed)}")
print(f"Claims with disagreements: {len(disagreements)}")

if completed:
    agreement = (len(completed) - len(disagreements)) / len(completed)
    print(f"Exact claim-level agreement: {agreement:.1%}")

if disagreements:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=disagreements[0].keys(),
        )
        writer.writeheader()
        writer.writerows(disagreements)

    print(f"Saved disagreements to {OUTPUT}")
else:
    print("No disagreement file written.")

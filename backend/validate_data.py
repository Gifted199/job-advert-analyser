import json
from collections import Counter
from pathlib import Path

from pydantic import ValidationError

from schemas import JobExtraction

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "examples.json"

with open(DATA_PATH, encoding="utf-8") as f:
    examples = json.load(f)

print(f"Loaded {len(examples)} examples from {DATA_PATH.name}")

errors = 0
seen_ids = set()
valid_labels = []

for example in examples:
    ex_id = example["id"]
    if ex_id in seen_ids:
        print(f"Duplicate id: {ex_id}")
        errors += 1
    seen_ids.add(ex_id)

    try:
        valid_labels.append(JobExtraction.model_validate(example["expected"]))
    except ValidationError as error:
        errors += 1
        print(f"\n{ex_id} has an invalid label:\n{error}")

print(f"\nProblems found: {errors}")

if errors == 0:
    print("Seniority:", Counter(label.seniority for label in valid_labels))
    print("Remote:   ", Counter(label.remote for label in valid_labels))
    no_salary = sum(1 for label in valid_labels if label.salary_min is None and label.salary_max is None)
    print("No salary:", no_salary)
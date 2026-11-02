from pydantic import ValidationError

from llm import extract, get_validated
from prompts import TECHNIQUES
from schemas import JobExtraction

advert = (
    "Senior Data Analyst, Bristol (hybrid, 2 days in office). £50,000-£60,000. "
    "Essential: SQL, Power BI, DAX. Experience with Azure Synapse is a plus. "
    "Strong communication skills. 5+ years' experience."
)

for name in TECHNIQUES:
    result, retries = extract(advert, technique=name)
    print(f"\n=== {name} (retries: {retries}) ===")
    print(result.model_dump_json(indent=2))

print("\n=== Retry demo ===")
bad_messages = [
    {
        "role": "user",
        "content": (
            "Return a JSON job extraction for a 'Lead Data Engineer, remote, £80k' advert, "
            "with the keys job_title, seniority, required_skills, nice_to_have_skills, "
            "salary_min, salary_max, remote. Set seniority to 'Lead'."
        ),
    }
]
try:
    fixed, retries = get_validated(bad_messages, JobExtraction)
    print(f"Retries used: {retries}")
    print(fixed.model_dump_json(indent=2))
except ValidationError as error:
    print("Failed twice:\n", error)
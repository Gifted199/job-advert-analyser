from pydantic import ValidationError

from schemas import JobExtraction

good = {
    "job_title": "Data Analyst",
    "seniority": "junior",
    "required_skills": ["SQL", "Excel", "Power BI"],
    "nice_to_have_skills": ["Python"],
    "salary_min": 28000,
    "salary_max": 32000,
    "remote": "hybrid",
}

job = JobExtraction.model_validate(good)
print("VALID:", job)

llm_text = '{"job_title": "Data Analyst", "seniority": "junior", "required_skills": ["SQL"], "nice_to_have_skills": [], "salary_min": null, "salary_max": null, "remote": "onsite"}'
from_json = JobExtraction.model_validate_json(llm_text)
print("FROM JSON:", from_json)

bad_cases = {
    "seniority not allowed": {**good, "seniority": "lead"},
    "salary as text": {**good, "salary_min": "£28k"},
    "min above max": {**good, "salary_min": 40000},
    "missing field": {k: v for k, v in good.items() if k != "remote"},
    "extra field": {**good, "company": "Acme"},
}

for name, data in bad_cases.items():
    try:
        JobExtraction.model_validate(data)
        print(f"\n{name}: PASSED (unexpected!)")
    except ValidationError as error:
        print(f"\n--- {name} ---")
        print(error)
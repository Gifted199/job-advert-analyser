import json

import httpx

BASE_URL = "http://127.0.0.1:8000"
GOOD_ADVERT = (
    "Senior Data Analyst, Bristol (hybrid, 2 days in office). £50,000-£60,000. "
    "Essential: SQL, Power BI, DAX. Experience with Azure Synapse is a plus. 5+ years' experience."
)

cases = [
    ("health", "GET", "/health", None),
    ("good advert", "POST", "/analyse", {"advert": GOOD_ADVERT}),
    ("missing field", "POST", "/analyse", {}),
    ("wrong type", "POST", "/analyse", {"advert": 123}),
    ("extra field", "POST", "/analyse", {"advert": GOOD_ADVERT, "user": "x"}),
    ("too short", "POST", "/analyse", {"advert": "Data Analyst, London"}),
    ("only spaces", "POST", "/analyse", {"advert": " " * 80}),
]

with httpx.Client(base_url=BASE_URL, timeout=120) as client:
    for name, method, path, body in cases:
        response = client.request(method, path, json=body)
        print(f"\n--- {name}: {response.status_code} ---")
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2))
        else:
            print(response.text[:400])
from llm import generate_bullets

advert = (
    "Senior Data Analyst, Bristol (hybrid, 2 days in office). £50,000-£60,000. "
    "Essential: SQL, Power BI, DAX. Experience with Azure Synapse is a plus. "
    "Strong communication skills. 5+ years' experience."
)

result, retries = generate_bullets(advert)
print(f"Retries: {retries}")
for bullet in result.bullets:
    print(" •", bullet)
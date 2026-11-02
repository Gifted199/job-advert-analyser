import os
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI

load_dotenv(find_dotenv(usecwd=True))

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5.4-mini")

print("Endpoint set:", bool(endpoint))
print("API key set:", bool(api_key))
print("Deployment:", deployment)

client = OpenAI(base_url=f"{endpoint}/openai/v1/", api_key=api_key, timeout=60)

response = client.chat.completions.create(
    model=deployment,
    messages=[{"role": "user", "content": "Reply with exactly: connection ok"}],
)

print("Reply:", response.choices[0].message.content)
print("Model used:", response.model)
print("Tokens used:", response.usage.total_tokens)
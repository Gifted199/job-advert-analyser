import os

from dotenv import find_dotenv, load_dotenv
from openai import OpenAI
from pydantic import BaseModel, ValidationError

from prompts import DEFAULT_TECHNIQUE, TECHNIQUES, cv_bullets, judge_prompt
from schemas import CVBullets, JobExtraction, JudgeScore, ReasonedExtraction

load_dotenv(find_dotenv(usecwd=True))

ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5.4-mini")

client = OpenAI(
    base_url=f"{ENDPOINT}/openai/v1/",
    api_key=os.getenv("AZURE_OPENAI_API_KEY", ""),
    timeout=60,
)


def call_llm(messages: list[dict]) -> str:
    """Send messages to the model and return its raw text reply."""
    response = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=messages,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content


def get_validated(messages: list[dict], model_class: type[BaseModel]) -> tuple[BaseModel, int]:
    """Call the LLM and validate the reply. On a ValidationError, retry once with the error.

    Returns (validated object, number of retries used).
    If the retry also fails, the ValidationError is raised.
    """
    raw = call_llm(messages)
    try:
        return model_class.model_validate_json(raw), 0
    except ValidationError as error:
        retry_messages = messages + [
            {"role": "assistant", "content": raw},
            {
                "role": "user",
                "content": (
                    "Your JSON did not match the required format. Errors:\n"
                    f"{error}\n\n"
                    "Return the corrected JSON object only."
                ),
            },
        ]
        raw_retry = call_llm(retry_messages)
        return model_class.model_validate_json(raw_retry), 1


def extract(advert: str, technique: str = DEFAULT_TECHNIQUE) -> tuple[JobExtraction, int]:
    """Extract job fields from an advert using the named prompting technique."""
    messages = TECHNIQUES[technique](advert)
    if technique == "chain_of_thought":
        result, retries = get_validated(messages, ReasonedExtraction)
        return result.answer, retries
    return get_validated(messages, JobExtraction)


def generate_bullets(advert: str) -> tuple[CVBullets, int]:
    """Write 3 CV bullet suggestions for an advert, validated with one retry."""
    return get_validated(cv_bullets(advert), CVBullets)

def judge_bullets(advert: str, bullets: list[str]) -> tuple[JudgeScore, int]:
    """Score CV bullets against the rubric, validated with one retry."""
    return get_validated(judge_prompt(advert, bullets), JudgeScore)
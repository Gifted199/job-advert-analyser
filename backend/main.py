import logging
import os

import openai
from fastapi import FastAPI, HTTPException
from pydantic import ValidationError

from llm import DEPLOYMENT, extract, generate_bullets, judge_bullets
from prompts import DEFAULT_TECHNIQUE
from schemas import AnalyseRequest, AnalyseResponse

logger = logging.getLogger("uvicorn.error")

app = FastAPI(title="Job Advert Analyser By Akinlolu", version="1.0.0")

MIN_ADVERT_CHARS = 50


@app.get("/health")
def health() -> dict:
    configured = bool(os.getenv("AZURE_OPENAI_ENDPOINT")) and bool(os.getenv("AZURE_OPENAI_API_KEY"))
    return {"status": "ok", "llm_configured": configured, "deployment": DEPLOYMENT}


@app.post("/analyse", response_model=AnalyseResponse)
def analyse(request: AnalyseRequest) -> AnalyseResponse:
    advert = request.advert.strip()
    if len(advert) < MIN_ADVERT_CHARS:
        raise HTTPException(
            status_code=400,
            detail=f"The advert is too short to analyse (minimum {MIN_ADVERT_CHARS} characters).",
        )

    try:
        extraction, extract_retries = extract(advert)
        bullets, bullet_retries = generate_bullets(advert)
        judge, judge_retries = judge_bullets(advert, bullets.bullets)
    except openai.BadRequestError as exc:
        logger.warning("Azure rejected the request: %s", exc)
        raise HTTPException(
            status_code=400,
            detail="The language model rejected this advert. It may have triggered the content filter.",
        ) from exc
    except openai.APIError as exc:
        logger.error("Azure OpenAI unavailable: %s", exc)
        raise HTTPException(
            status_code=503,
            detail="The language model service is unavailable. Please try again shortly.",
        ) from exc
    except ValidationError as exc:
        logger.error("LLM output failed validation after retry: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="The language model returned an invalid answer twice. Please try again.",
        ) from exc

    return AnalyseResponse(
        extraction=extraction,
        bullets=bullets.bullets,
        judge=judge,
        technique=DEFAULT_TECHNIQUE,
        retries=extract_retries + bullet_retries + judge_retries,
    )
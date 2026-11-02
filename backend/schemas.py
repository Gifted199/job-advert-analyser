from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Seniority = Literal["junior", "mid", "senior"]
RemoteType = Literal["remote", "hybrid", "onsite"]


class JobExtraction(BaseModel):
    """Structured fields extracted from one job advert."""

    model_config = ConfigDict(extra="forbid")

    job_title: str = Field(min_length=1, description="Title without seniority words, e.g. 'Data Analyst'")
    seniority: Seniority
    required_skills: list[str]
    nice_to_have_skills: list[str]
    salary_min: int | None = Field(ge=0)
    salary_max: int | None = Field(ge=0)
    remote: RemoteType

    @model_validator(mode="after")
    def check_salary_range(self):
        if self.salary_min is not None and self.salary_max is not None:
            if self.salary_min > self.salary_max:
                raise ValueError("salary_min cannot be greater than salary_max")
        return self


class CVBullets(BaseModel):
    """Three CV bullet suggestions tailored to an advert."""

    model_config = ConfigDict(extra="forbid")

    bullets: list[str] = Field(min_length=3, max_length=3)
class ReasonedExtraction(BaseModel):
        """Chain-of-thought output: the working, then the answer."""

        model_config = ConfigDict(extra="forbid")

        reasoning: str
        answer: JobExtraction

class JudgeScore(BaseModel):
    """The judge's rubric scores for a set of CV bullets."""

    model_config = ConfigDict(extra="forbid")

    reason: str = Field(min_length=1)
    relevance: int = Field(ge=1, le=5)
    specificity: int = Field(ge=1, le=5)
    honesty: int = Field(ge=1, le=5)
    overall: int = Field(ge=1, le=5)

    @model_validator(mode="after")
    def check_honesty_cap(self):
        if self.honesty <= 2 and self.overall > 2:
            raise ValueError("overall cannot be above 2 when honesty is 2 or below")
        return self

class AnalyseRequest(BaseModel):
    """What the client sends to POST /analyse."""

    model_config = ConfigDict(extra="forbid")

    advert: str = Field(min_length=1, max_length=10000, description="The full text of a job advert")


class AnalyseResponse(BaseModel):
    """What POST /analyse sends back."""

    extraction: JobExtraction
    bullets: list[str] = Field(min_length=3, max_length=3)
    judge: JudgeScore
    technique: str
    retries: int
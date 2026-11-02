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
import os

import httpx
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

SAMPLE_ADVERT = (
    "Senior Analytics Engineer – Northwind Retail Ltd, Manchester. Hybrid: 2 days a week in our "
    "Ancoats office. £62,000 – £72,000 plus 10% bonus. You'll build and maintain our data models in "
    "dbt and Snowflake, write complex SQL, and own data quality across our sales and inventory "
    "pipelines. Essential: SQL, dbt, Snowflake, Git. Desirable: Python, Airflow, Looker. Strong "
    "communication skills and the ability to work with non-technical stakeholders. 5+ years' "
    "experience in analytics or data engineering."
)

ERROR_MESSAGES = {
    400: "This advert couldn't be analysed, please try another.",
    422: "The request wasn't in the expected format, please use the requested format.",
    502: "The AI returned an invalid answer. Please try again.",
    503: "The AI service is unavailable right now. Please try again shortly.",
}

CRITERIA = ["relevance", "specificity", "honesty", "overall"]


@st.cache_data(ttl=30)
def check_health() -> dict | None:
    """Ask the backend if it's running. Cached for 30 seconds."""
    try:
        response = httpx.get(f"{BACKEND_URL}/health", timeout=5)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError:
        return None


def analyse(advert: str) -> tuple[int | None, dict]:
    """Send the advert to the backend. Returns (status code, JSON body)."""
    try:
        response = httpx.post(f"{BACKEND_URL}/analyse", json={"advert": advert}, timeout=120)
    except httpx.TimeoutException:
        return None, {"detail": "The backend took too long to respond."}
    except httpx.ConnectError:
        return None, {"detail": f"Couldn't reach the backend at {BACKEND_URL}. Is it running?"}

    try:
        body = response.json()
    except ValueError:
        body = {"detail": response.text}
    return response.status_code, body


def error_text(status: int | None, body: dict) -> str:
    detail = body.get("detail", "")
    if isinstance(detail, list):
        detail = "; ".join(item.get("msg", "") for item in detail)
    headline = ERROR_MESSAGES.get(status, "Something went wrong.")
    def error_text(status: int | None, body: dict) -> str:
        detail = body.get("detail", "")
        if isinstance(detail, list):
            detail = "; ".join(item.get("msg", "") for item in detail)
    headline = ERROR_MESSAGES.get(status, "Something went wrong.")
    if status is not None and status >= 500:      # ← new line
        return headline                            # ← new line
    return f"{headline} {detail}".strip()


def format_salary(low: int | None, high: int | None) -> str:
    if low is None and high is None:
        return "Not stated, or not an annual salary"
    if low is None:
        return f"Up to £{high:,}"
    if high is None:
        return f"From £{low:,}"
    if low == high:
        return f"£{low:,}"
    return f"£{low:,} – £{high:,}"


def bullet_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "_None listed_"


def show_result(result: dict) -> None:
    extraction = result["extraction"]

    st.subheader("Extracted details")
    col1, col2, col3 = st.columns(3)
    col1.metric("Job title", extraction["job_title"])
    col2.metric("Seniority", extraction["seniority"].title())
    col3.metric("Working pattern", extraction["remote"].title())
    st.markdown(f"**Salary:** {format_salary(extraction['salary_min'], extraction['salary_max'])}")

    required_col, nice_col = st.columns(2)
    required_col.markdown("**Required skills**")
    required_col.markdown(bullet_list(extraction["required_skills"]))
    nice_col.markdown("**Nice-to-have skills**")
    nice_col.markdown(bullet_list(extraction["nice_to_have_skills"]))

    st.subheader("Suggested CV bullets")
    st.markdown(bullet_list(result["bullets"]))

    st.subheader("Judge's assessment")
    judge = result["judge"]
    for col, criterion in zip(st.columns(len(CRITERIA)), CRITERIA):
        col.metric(criterion.title(), f"{judge[criterion]} / 5")
    st.info(judge["reason"])

    st.caption(
        f"Technique: {result['technique']} · Retries: {result['retries']} · "
        "The judge's score is an AI assessment to guide you, not a guarantee."
    )
    with st.expander("Raw JSON response"):
        st.json(result)


st.set_page_config(page_title="Job Advert Analyser", layout="wide")
st.title("Job Advert Analyser")
st.caption("Paste a job advert to extract its key details and get tailored CV bullet suggestions.")

with st.sidebar:
    st.header("Backend")
    health = check_health()
    if health:
        st.success("Connected")
        st.caption(f"Model: {health['deployment']}")
    else:
        st.error(f"Not reachable at {BACKEND_URL}")

if "advert" not in st.session_state:
    st.session_state.advert = ""

if st.button("Load sample advert"):
    st.session_state.advert = SAMPLE_ADVERT

advert = st.text_area("Job advert", key="advert", height=220, placeholder="Paste a job advert here...")

if st.button("Analyse", type="primary", disabled=not advert.strip()):
    with st.spinner("Extracting details, writing bullets and judging them..."):
        status, body = analyse(advert)
    if status == 200:
        st.session_state.result = body
    else:
        st.session_state.pop("result", None)
        st.error(error_text(status, body))

if "result" in st.session_state:
    show_result(st.session_state.result)
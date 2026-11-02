import json

TASK = "Extract structured information from the job advert."

RULES = """Labelling rules:
- job_title: the title as written, with seniority words (Junior, Graduate, Trainee, Mid-level, Senior, Lead, Principal) and contract notes removed.
- seniority: explicit level words win (Junior, Graduate, Trainee, Entry-level or "no experience needed" = junior; Mid-level = mid; Senior, Lead or Principal = senior). Otherwise use the lower bound of the years asked for: under 2 = junior, 2-4 = mid, 5 or more = senior. If neither is given, use mid.
- Skills are technical skills, tools, methods, certifications and domain knowledge. Exclude soft skills and years of experience. Write each skill as the advert writes it. Split "X or Y" into two skills.
- nice_to_have_skills: skills marked desirable, a plus, a bonus, ideally, advantageous, helpful, beneficial, nice to have, or exposure to. All other skills are required. Use [] if there are none.
- salary_min / salary_max: annual base salary in GBP as whole numbers (£45k = 45000). Single figure: min = max. "Up to X": min is null. "From X": max is null. Day, hourly or monthly rates, "competitive", or no salary: both null. Ignore bonus and OTE.
- remote: "remote" for fully remote, work from home or remote-first (occasional office visits are still remote); "hybrid" for a regular split between office and home; "onsite" for office-based, on-site, or when no working pattern is mentioned."""

FIELDS = """The extraction has exactly these keys:
- job_title (string)
- seniority ("junior", "mid" or "senior")
- required_skills (list of strings)
- nice_to_have_skills (list of strings)
- salary_min (integer or null)
- salary_max (integer or null)
- remote ("remote", "hybrid" or "onsite")"""

OUTPUT = "Return only the JSON object, with no other text."

ROLE = (
    "You are an experienced UK recruitment data analyst. You turn job adverts into clean, "
    "structured data for a jobs database. You follow the labelling rules exactly and never "
    "guess information that is not in the advert."
)

# Worked examples for few-shot. These must NOT be any of the 24 test examples.
FEW_SHOT_EXAMPLES = [
    {
        "input": "Lead Frontend Engineer, remote-first (one office day a month in Leeds). Up to £90,000. Essential: Vue.js, TypeScript, Jest. Storybook experience is desirable.",
        "output": {
            "job_title": "Frontend Engineer",
            "seniority": "senior",
            "required_skills": ["Vue.js", "TypeScript", "Jest"],
            "nice_to_have_skills": ["Storybook"],
            "salary_min": None,
            "salary_max": 90000,
            "remote": "remote",
        },
    },
    {
        "input": "SAP Consultant (12-month contract), Glasgow. Hybrid, 2 days on site. £550 per day. SAP S/4HANA and ABAP required. 3+ years' experience.",
        "output": {
            "job_title": "SAP Consultant",
            "seniority": "mid",
            "required_skills": ["SAP S/4HANA", "ABAP"],
            "nice_to_have_skills": [],
            "salary_min": None,
            "salary_max": None,
            "remote": "hybrid",
        },
    },
    {
        "input": "Trainee Payroll Administrator, Norwich. £23,500. Excel needed; Sage Payroll knowledge is an advantage. Strong attention to detail.",
        "output": {
            "job_title": "Payroll Administrator",
            "seniority": "junior",
            "required_skills": ["Excel"],
            "nice_to_have_skills": ["Sage Payroll"],
            "salary_min": 23500,
            "salary_max": 23500,
            "remote": "onsite",
        },
    },
]

COT_STEPS = """Work through these steps before answering:
1. Find the title; remove seniority words and contract notes.
2. Look for level words; if there are none, use the lower bound of the years; otherwise mid.
3. Sort each skill into required or nice-to-have using the marker words; drop soft skills.
4. Check whether the pay is an annual salary; day, hourly or monthly rates mean both are null.
5. Decide the working pattern.

Return a JSON object with two keys:
- "reasoning": a short string with your step-by-step working
- "answer": the extraction object"""


def zero_shot(advert: str) -> list[dict]:
    content = f"{TASK}\n\n{RULES}\n\n{FIELDS}\n\n{OUTPUT}\n\nJob advert:\n{advert}"
    return [{"role": "user", "content": content}]


def few_shot(advert: str) -> list[dict]:
    examples = "\n\n".join(
        f"Job advert:\n{ex['input']}\nJSON:\n{json.dumps(ex['output'])}"
        for ex in FEW_SHOT_EXAMPLES
    )
    content = (
        f"{TASK}\n\n{RULES}\n\n{FIELDS}\n\n{OUTPUT}\n\n"
        f"Examples:\n\n{examples}\n\n"
        f"Now do the same for this advert.\nJob advert:\n{advert}\nJSON:"
    )
    return [{"role": "user", "content": content}]


def role_prompt(advert: str) -> list[dict]:
    system = f"{ROLE}\n\n{TASK}\n\n{RULES}\n\n{FIELDS}\n\n{OUTPUT}"
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": f"Job advert:\n{advert}"},
    ]


def chain_of_thought(advert: str) -> list[dict]:
    content = f"{TASK}\n\n{RULES}\n\n{FIELDS}\n\n{COT_STEPS}\n\nJob advert:\n{advert}"
    return [{"role": "user", "content": content}]


TECHNIQUES = {
    "zero_shot": zero_shot,
    "few_shot": few_shot,
    "role": role_prompt,
    "chain_of_thought": chain_of_thought,
}
DEFAULT_TECHNIQUE = "few_shot"
BULLET_ROLE = "You are an experienced UK CV writer who helps candidates tailor their CVs to job adverts."

BULLET_RULES = """Write exactly 3 CV bullet points a candidate could adapt for this job.
Rules:
- Start each bullet with a strong past-tense action verb (e.g. Built, Automated, Analysed).
- Each bullet names at least one specific skill or tool from the advert, prioritising required skills.
- Together, the 3 bullets cover the most important required skills.
- You know nothing about the candidate. Never invent facts: no numbers, percentages, company names, dates or durations. Where a detail is needed, use a placeholder in square brackets, e.g. [X%], [team or company], [number of users].
- One sentence per bullet, under 30 words.
Return a JSON object with one key, "bullets": a list of exactly 3 strings."""


def cv_bullets(advert: str) -> list[dict]:
    return [
        {"role": "system", "content": BULLET_ROLE},
        {"role": "user", "content": f"{BULLET_RULES}\n\nJob advert:\n{advert}"},
    ]


JUDGE_RUBRIC = """Score the 3 CV bullets as a set, from 1 (poor) to 5 (excellent), on each criterion.

Relevance: are the bullets built around this advert's skills, especially the required ones?
5 = all three bullets clearly target the advert's required skills
4 = mostly relevant; one bullet is only loosely linked
3 = a mix of relevant and generic bullets
2 = mostly generic; little link to the advert
1 = unrelated to the advert

Specificity: do the bullets name concrete tools, tasks and results (placeholders are fine)?
5 = every bullet names a specific tool or skill, a concrete task and a result
4 = mostly concrete; one bullet is vaguer
3 = a mix of concrete and vague
2 = mostly vague ("worked on various projects")
1 = entirely vague

Honesty: do the bullets avoid inventing experience? The candidate's background is unknown, so any concrete number, company name, date or duration that is not a [placeholder] is invented.
5 = no invented facts; all details are placeholders or come from the advert
4 = one mild unsupported claim (e.g. "expert in")
3 = one invented number or fact
2 = several invented facts
1 = mostly fabricated achievements

Overall: your overall judgement of how useful and trustworthy the bullets are. If honesty is 2 or below, overall cannot be above 2."""
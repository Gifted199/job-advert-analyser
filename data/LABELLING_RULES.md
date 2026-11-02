# Labelling rules

Every expected answer in `examples.json` follows these rules. The same rules are given to the LLM in the prompts, so labels and predictions are judged against one standard.

## job_title
- Use the title as written, with seniority words removed: Junior, Graduate, Trainee, Mid-level, Senior, Lead, Principal.
- Remove contract or admin notes in brackets or after dashes ("(6-month contract)", "– temporary").
- Example: "Senior Data Engineer" → `Data Engineer`.

## seniority (junior / mid / senior)
1. Explicit level words win:
   - junior: Junior, Graduate, Trainee, Entry-level, "no experience needed"
   - mid: Mid-level
   - senior: Senior, Lead, Principal, Senior-level
2. Otherwise use the **lower bound** of the years of experience asked for:
   - under 2 years → junior ("0-2", "1-2")
   - 2 to 4 years → mid ("2+", "2-4", "3-5", "4 years")
   - 5 or more years → senior ("5+", "6+", "8+")
3. If there are no level words and no years: `mid`.

## required_skills / nice_to_have_skills
- Skills are technical skills, tools, methods, certifications and domain knowledge (e.g. SQL, Power BI, A/B testing, GDPR, statistics).
- Exclude soft skills (communication, stakeholder management) and years of experience.
- nice_to_have: marked desirable, a plus, a bonus, ideally, advantageous, helpful, beneficial, nice to have, exposure to.
- required: marked essential, must, required, needed, or listed with no qualifier.
- "Python or R" → two separate skills.
- Write each skill as the advert writes it. Order does not matter (compared as sets).
- No nice-to-have skills → empty list `[]`.

## salary_min / salary_max
- Annual base salary in GBP only, as whole numbers ("£45k" → 45000).
- Range → min and max. Single figure → min = max.
- "Up to £X" → min null, max X. "From £X" → min X, max null.
- Day rates, hourly rates and monthly pay → both null.
- "Competitive" or not stated → both null.
- Ignore bonus and OTE; use the basic salary.

## remote (remote / hybrid / onsite)
- remote: fully remote, work from home, remote-first. Occasional or ad-hoc office visits are still remote.
- hybrid: a regular split between office and home (set office days, "hybrid", "flexible hybrid").
- onsite: office-based, on-site, or no working pattern mentioned.

"""Sublab Hard - stories in, CVs out, the best candidate by code.

1. extract: one call per story -> a structured CV with an evidence quote per field.
            The counting rules are IN THE PROMPT (see EXTRACTION_RULES).
            Code then re-checks what it can check itself (GPA conversion, counts, months).
2. score:   one call per CV -> three integers 0-5 and nothing else to compute.
            Code computes 0.5*academic + 0.3*research + 0.2*experience and the winner.
3. prose:   a separate call asks the model, in prose, who should win - for comparison.

Run:  python -m sublab_hard.cv_extract_and_rank
"""
from __future__ import annotations

import json

from common.llm import DATA, chat, load_json, parse_json, save_result, validate

RUBRIC = load_json("candidate_rubric.json")
STORIES = {p.stem: p.read_text(encoding="utf-8") for p in sorted((DATA / "candidates").glob("story-*.md"))}
WEIGHTS = {c["id"]: c["weight"] for c in RUBRIC["criteria"]}

# ------------------------------------------------------------------ the CV record
NULLABLE_STR = {"type": ["string", "null"]}
CV_SCHEMA = {
    "type": "object",
    "properties": {
        "candidate_id": {"type": "string"},
        "full_name": NULLABLE_STR,
        "degree": NULLABLE_STR,
        "graduation_year": {"type": ["integer", "null"]},
        "gpa_original": {"type": ["number", "null"]},
        "gpa_original_scale": {"type": ["number", "null"]},
        "gpa_4_scale": {"type": ["number", "null"], "minimum": 0, "maximum": 4},
        "languages": {"type": "array", "items": {"type": "string"}},
        "published_outputs": {"type": "array", "items": {"type": "string"}},
        "published_peer_reviewed_count": {"type": "integer", "minimum": 0},
        "not_counted_outputs": {
            "type": "array",
            "items": {"type": "object",
                      "properties": {"title": {"type": "string"}, "status": {"type": "string"}},
                      "required": ["title", "status"]}},
        "experience_periods": {
            "type": "array",
            "items": {"type": "object",
                      "properties": {"role": {"type": "string"},
                                     "start": NULLABLE_STR, "end": NULLABLE_STR,
                                     "months": {"type": ["integer", "null"]},
                                     "countable": {"type": "boolean"},
                                     "note": {"type": "string"}},
                      "required": ["role", "start", "end", "months", "countable"]}},
        "experience_months_countable": {"type": ["integer", "null"], "minimum": 0},
        "evidence": {
            "type": "object",
            "properties": {k: NULLABLE_STR for k in
                           ["full_name", "degree", "graduation_year", "gpa", "languages", "publications", "experience"]},
            "required": ["full_name", "degree", "graduation_year", "gpa", "languages", "publications", "experience"],
        },
        "ambiguities": {"type": "array", "items": {"type": "string"}},
        "story_language": {"type": "string"},
    },
    "required": ["candidate_id", "full_name", "degree", "graduation_year", "gpa_original", "gpa_original_scale",
                 "gpa_4_scale", "languages", "published_outputs", "published_peer_reviewed_count",
                 "not_counted_outputs", "experience_periods", "experience_months_countable", "evidence",
                 "ambiguities", "story_language"],
    "additionalProperties": False,
}

EXTRACTION_RULES = """RULES - follow them exactly, they matter more than a tidy record:
R1. MISSING = NULL. A fact the story does not state is null. Never estimate. No GPA stated means gpa_original, gpa_original_scale and gpa_4_scale are all null - never infer a GPA from the degree, the honours ("with distinction"), the university or the impression the story gives.
R2. GPA SCALE. If the GPA is on another scale, convert it linearly to a 4.0 scale: gpa_4_scale = gpa_original / gpa_original_scale * 4, rounded to 2 decimals. Always record gpa_original and gpa_original_scale beside it (for a 4.0 GPA, the scale is 4.0).
R3. PUBLISHED MEANS PUBLISHED. A paper counts only when the story says it is "published" or "accepted" (in any language, e.g. Kazakh "жарияланды"). "Submitted", "under review", "in preparation", "in press", "planned", "being written", posters and talks are NOT published: put them in not_counted_outputs with their status, and do not count them. published_peer_reviewed_count = number of items in published_outputs.
R4. CONTRADICTIONS. If the story contradicts itself about a field (two different GPAs, two different graduation years, ...), do not resolve it, do not pick the likelier one and do not average: that field is null, and the contradiction is written in ambiguities quoting both versions. For a contradicted GPA, gpa_original, gpa_original_scale and gpa_4_scale are all null.
R5. EXPERIENCE. Count months, not jobs. Overlapping periods count once. A period is countable only if the story gives dates (a start month/year, and an end or "until today/currently"); a period with a duration but no dates is recorded with countable=false and is NOT added. Periods stated only approximately ("about forty months") use the dates, not the approximation, when dates exist. experience_months_countable = sum of the countable, non-overlapping months; 0 if there are none; null only if the story is silent about work entirely. Note part-time/full-time in the note, but months are months.
R6. EVIDENCE. For every field you fill, evidence holds a short verbatim quote from the story (in the story's own language). If the field is null, evidence is null, or the quote that shows the contradiction.
R7. Do not translate names; write them as the story does. Output English for everything else."""


def extraction_prompt() -> str:
    return (
        "You turn one scholarship application story into a structured CV record for a committee.\n\n"
        + EXTRACTION_RULES
        + "\n\nThe committee's own counting rules (same rules, as they wrote them):\n"
        + json.dumps(RUBRIC["counting_rules"], ensure_ascii=False, indent=1)
        + "\n\nReturn ONE JSON object and nothing else, with exactly these keys:\n"
        + json.dumps({
            "candidate_id": "the id you are given, e.g. story-01",
            "full_name": "string|null", "degree": "string|null", "graduation_year": "integer|null",
            "gpa_original": "number|null", "gpa_original_scale": "number|null (e.g. 4.0, 5.0)",
            "gpa_4_scale": "number|null",
            "languages": ["strings"],
            "published_outputs": ["one line per counted publication"],
            "published_peer_reviewed_count": "integer",
            "not_counted_outputs": [{"title": "string", "status": "submitted|under review|in preparation|poster|..."}],
            "experience_periods": [{"role": "string", "start": "YYYY-MM|null", "end": "YYYY-MM|present|null",
                                    "months": "integer|null", "countable": "boolean", "note": "string"}],
            "experience_months_countable": "integer|null",
            "evidence": {"full_name": "quote|null", "degree": "quote|null", "graduation_year": "quote|null",
                         "gpa": "quote|null", "languages": "quote|null", "publications": "quote|null",
                         "experience": "quote|null"},
            "ambiguities": ["each contradiction or unclear point, quoting the story"],
            "story_language": "string",
        }, indent=1)
    )


SCORING_PROMPT = (
    "You score one scholarship candidate against a rubric. You receive the candidate's extracted CV record.\n"
    "Give an integer score from 0 to 5 for each of the three criteria, using the anchors below; interpolate "
    "between 0 and 5 in proportion to how close the record is to the 5-anchor. Score only what the record states: "
    "a null field is not evidence of anything. Do NOT compute a total, a ranking or a recommendation - the "
    "committee's program does that.\n\n"
    f"RUBRIC: {json.dumps(RUBRIC['criteria'], ensure_ascii=False)}\n"
    f"COUNTING RULES: {json.dumps(RUBRIC['counting_rules'], ensure_ascii=False)}\n\n"
    'Return ONE JSON object: {"academic": int 0-5, "research": int 0-5, "experience": int 0-5, '
    '"why": {"academic": "one short sentence", "research": "...", "experience": "..."}}'
)

SCORE_SCHEMA = {
    "type": "object",
    "properties": {c: {"type": "integer", "minimum": 0, "maximum": 5} for c in WEIGHTS} | {"why": {"type": "object"}},
    "required": list(WEIGHTS),
}

PROSE_PROMPT = (
    "You advise a scholarship committee. There is one funded place and six candidates. Read their application "
    "stories and the rubric, and answer in a few paragraphs of prose: which candidate should win, and why? "
    "Mention the runner-up. Write plain prose, not JSON, not a table.\n\n"
    f"RUBRIC: {json.dumps(RUBRIC, ensure_ascii=False)}"
)


# -------------------------------------------------------------- code-side checks
def code_checks(cv: dict) -> list[str]:
    """Things the program can verify without trusting the model."""
    notes = []
    o, s, g4 = cv.get("gpa_original"), cv.get("gpa_original_scale"), cv.get("gpa_4_scale")
    if o is not None and s:
        expect = round(o / s * 4, 2)
        if g4 is None or abs(expect - g4) > 0.011:
            notes.append(f"GPA conversion: model gave {g4}, code computes {o}/{s}*4 = {expect}")
    if g4 is not None and o is None:
        notes.append("gpa_4_scale filled but no original GPA recorded (possible estimate)")
    n = len(cv.get("published_outputs") or [])
    if cv.get("published_peer_reviewed_count") != n:
        notes.append(f"publication count {cv.get('published_peer_reviewed_count')} != {n} items listed")
    periods = cv.get("experience_periods") or []
    summed = sum(p.get("months") or 0 for p in periods if p.get("countable"))
    if periods and cv.get("experience_months_countable") not in (None, summed):
        notes.append(f"experience months {cv.get('experience_months_countable')} != sum of countable periods {summed} "
                     "(overlap? check)")
    return notes


def null_fields(cv: dict) -> list[str]:
    keys = ["full_name", "degree", "graduation_year", "gpa_original", "gpa_original_scale", "gpa_4_scale",
            "experience_months_countable"]
    return [k for k in keys if cv.get(k) is None]


def traps_hit(cv: dict) -> list[str]:
    t = []
    if cv.get("gpa_4_scale") is None and not any("gpa" in a.lower() for a in cv.get("ambiguities", [])):
        t.append("no GPA stated")
    if cv.get("gpa_original_scale") not in (None, 4, 4.0):
        t.append(f"GPA on another scale ({cv['gpa_original']}/{cv['gpa_original_scale']} → {cv['gpa_4_scale']})")
    if cv.get("not_counted_outputs"):
        t.append("unpublished paper(s) not counted: " + ", ".join(o["status"] for o in cv["not_counted_outputs"]))
    if cv.get("ambiguities"):
        t.append(f"contradiction/ambiguity recorded ({len(cv['ambiguities'])})")
    if any(not p.get("countable") for p in cv.get("experience_periods", [])):
        t.append("undated experience not counted")
    return t or ["none"]


def md(s, n=200) -> str:
    s = " ".join(str(s).split()).replace("|", "\\|")
    return s if len(s) <= n else s[: n - 1] + "…"


# ------------------------------------------------------------------------- main
def main() -> None:
    out = []
    cvs: dict[str, dict] = {}
    extraction_rows = []

    print("== Part 1: extraction")
    sys_ext = extraction_prompt()
    for sid, story in STORIES.items():
        r = chat([{"role": "system", "content": sys_ext},
                  {"role": "user", "content": f"candidate_id: {sid}\n\nSTORY:\n{story}"}], max_tokens=6000)
        obj, perr = parse_json(r["text"])
        errors = [perr] if obj is None else validate(obj, CV_SCHEMA)
        row = {"id": sid, "raw": r["text"], "parsed": obj is not None, "valid": obj is not None and not errors,
               "errors": errors, "cv": obj}
        if isinstance(obj, dict):
            cvs[sid] = obj
            row["nulls"] = null_fields(obj)
            row["traps"] = traps_hit(obj)
            row["code_checks"] = code_checks(obj)
        extraction_rows.append(row)
        print(f"  {sid}: parsed={row['parsed']} valid={row['valid']} "
              f"gpa4={obj.get('gpa_4_scale') if isinstance(obj, dict) else '?'} "
              f"pubs={obj.get('published_peer_reviewed_count') if isinstance(obj, dict) else '?'} "
              f"months={obj.get('experience_months_countable') if isinstance(obj, dict) else '?'}", flush=True)

    out.append("### Part 1 — extraction\n")
    out.append("| Story | Parsed? | Valid? | Fields that came back `null` | Traps hit | Code checks |")
    out.append("|---|---|---|---|---|---|")
    for row in extraction_rows:
        out.append(f"| {row['id']} | {'yes' if row['parsed'] else 'NO'} | "
                   f"{'yes' if row['valid'] else 'NO: ' + md('; '.join(row['errors']), 120)} | "
                   f"{', '.join(row.get('nulls', [])) or 'none'} | {md('; '.join(row.get('traps', [])))} | "
                   f"{md('; '.join(row.get('code_checks', [])) or 'ok')} |")

    out.append("\n#### Extracted values at a glance\n")
    out.append("| Story | name | degree | grad year | GPA (orig/scale → 4.0) | published | not counted | months | ambiguities |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    for sid, cv in cvs.items():
        gpa = (f"{cv.get('gpa_original')}/{cv.get('gpa_original_scale')} → {cv.get('gpa_4_scale')}"
               if cv.get("gpa_4_scale") is not None else "null")
        out.append(f"| {sid} | {md(cv.get('full_name'))} | {md(cv.get('degree'), 60)} | {cv.get('graduation_year')} | "
                   f"{gpa} | {cv.get('published_peer_reviewed_count')} | "
                   f"{md(', '.join(o['title'] + ' (' + o['status'] + ')' for o in cv.get('not_counted_outputs', [])), 120)} | "
                   f"{cv.get('experience_months_countable')} | {md('; '.join(cv.get('ambiguities', [])), 200)} |")

    out.append("\n#### Extraction for story-06 (the one that contradicts itself)\n")
    out.append("```json\n" + json.dumps(cvs.get("story-06"), ensure_ascii=False, indent=2) + "\n```")

    # ------------------------------------------------------------ Part 2: scoring
    print("\n== Part 2: scoring (model gives 0-5 per criterion; code computes the rest)")
    scores = {}
    for sid, cv in cvs.items():
        r = chat([{"role": "system", "content": SCORING_PROMPT},
                  {"role": "user", "content": json.dumps(cv, ensure_ascii=False)}])
        obj, perr = parse_json(r["text"])
        errs = [perr] if obj is None else validate(obj, SCORE_SCHEMA)
        if errs:
            print(f"  {sid}: score reply invalid ({errs}); scoring as None")
            scores[sid] = {"valid": False, "raw": r["text"], "errors": errs}
            continue
        # THE CODE computes the total - the model was never asked for it
        total = round(sum(WEIGHTS[c] * obj[c] for c in WEIGHTS), 2)
        scores[sid] = {"valid": True, **{c: obj[c] for c in WEIGHTS}, "why": obj.get("why", {}), "total": total,
                       "raw": r["text"]}
        print(f"  {sid}: " + " ".join(f"{c}={obj[c]}" for c in WEIGHTS) + f"  -> total {total}")

    ranked = sorted((s for s in scores if scores[s]["valid"]), key=lambda s: -scores[s]["total"])
    out.append("\n### Part 2 — scores and the winner\n")
    out.append("| Candidate | name | academic (0–5) | research (0–5) | experience (0–5) | weighted total (code) | rank |")
    out.append("|---|---|---|---|---|---|---|")
    for sid in STORIES:
        s = scores.get(sid)
        name = md((cvs.get(sid) or {}).get("full_name"))
        if not s or not s["valid"]:
            out.append(f"| {sid} | {name} | — | — | — | invalid score reply | — |")
            continue
        out.append(f"| {sid} | {name} | {s['academic']} | {s['research']} | {s['experience']} | {s['total']:.2f} | "
                   f"{ranked.index(sid) + 1} |")
    out.append("\nTotal = 0.5·academic + 0.3·research + 0.2·experience, rounded to 2 decimals, computed in Python.\n")

    out.append("Model's one-line justification per score (not used in the computation):\n")
    for sid in ranked:
        w = scores[sid]["why"]
        out.append(f"- **{sid}**: academic — {md(w.get('academic', ''), 150)}; research — {md(w.get('research', ''), 150)}; "
                   f"experience — {md(w.get('experience', ''), 150)}")

    winner = ranked[0] if ranked else None
    if winner:
        gap = round(scores[ranked[0]]["total"] - scores[ranked[1]]["total"], 2) if len(ranked) > 1 else None
        tied = [s for s in ranked if scores[s]["total"] == scores[winner]["total"]]
        out.append(f"\n**Winner, computed by my code:** {winner} ({cvs[winner].get('full_name')}), "
                   f"total {scores[winner]['total']:.2f}")
        if len(tied) > 1:
            out.append(f"\n⚠ TIE at the top: {', '.join(tied)} all have {scores[winner]['total']:.2f}. "
                       "Code does not break the tie on its own - the committee must decide (see written answer 5).")
        if gap is not None:
            out.append(f"\nRunner-up: {ranked[1]} ({cvs[ranked[1]].get('full_name')}), "
                       f"{scores[ranked[1]]['total']:.2f}. Gap between the top two: {gap:.2f}"
                       + (" — within 0.05, too close to call on these scores." if gap <= 0.05 else "."))
        out.append("\nFull computed ranking: " + " > ".join(f"{s} ({scores[s]['total']:.2f})" for s in ranked))

    # ------------------------------------------------------------ prose, separately
    print("\n== Part 2b: the model's prose answer (separate call)")
    stories_block = "\n\n".join(f"=== {sid} ===\n{text}" for sid, text in STORIES.items())
    r = chat([{"role": "system", "content": PROSE_PROMPT},
              {"role": "user", "content": stories_block + "\n\nWhich candidate should win the funded place?"}],
             json_mode=False)
    prose = r["text"].strip()
    out.append("\n**The model's prose answer, asked separately (\"who should win?\"):**\n")
    out.append("\n".join("> " + line for line in prose.splitlines()))

    text = "\n".join(out)
    print("\n" + text)
    save_result("hard_tables.md", text)
    save_result("hard_raw.json", {"extraction": extraction_rows, "scores": scores, "ranking": ranked,
                                  "prose": prose})
    save_result("hard_prompts.md", "## Extraction system prompt\n\n```\n" + sys_ext + "\n```\n\n## Scoring system prompt"
                "\n\n```\n" + SCORING_PROMPT + "\n```\n\n## Prose system prompt\n\n```\n" + PROSE_PROMPT + "\n```\n")
    print("\nSaved: results/hard_tables.md, results/hard_raw.json, results/hard_prompts.md")


if __name__ == "__main__":
    main()

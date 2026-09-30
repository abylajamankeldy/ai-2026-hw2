# HW2 submission

**Name:** _(fill in)_
**Student ID:** _(fill in)_
**Group:** _(fill in)_
**Repository:** https://github.com/abylajamankeldy/ai-2026-hw2

## Model actually used — read this first

The assignment specifies OpenAI `gpt-5.6-luna`. I had no OpenAI API key, and the course
repository does not distribute one. A Google AI Studio (Gemini) key was refused with
`403 PERMISSION_DENIED`, and GitHub Models has been retired. **Every number in this file
therefore comes from `openai/gpt-oss-120b` served by Groq's free tier** (OpenAI-compatible
endpoint `https://api.groq.com/openai/v1`).

Nothing else changed: `common/llm.py` picks the provider from whichever key is in `.env`
(`OPENAI_API_KEY` first), so the three programs send exactly the same messages to either
model. With an OpenAI key the same three commands run on `gpt-5.6-luna` unchanged. Raw replies
for every call are committed in `results/*_raw.json`; the tables below are copied from
`results/*_tables.md`.

No key was committed (`git log --all -- .env` returns nothing).

## AI tool disclosure

State which AI tools you used and for what. Expected and fine; undisclosed use
is not. If you used a model to help you draft a prompt, say which prompt.

> I used **Claude (Anthropic)** extensively for this homework, because of the deadline:
> - Claude wrote the code of all three programs (`sublab_easy/role_prompts.py`,
>   `sublab_medium/chat_memory.py`, `sublab_hard/cv_extract_and_rank.py`, `common/llm.py`),
>   including **all prompts**: the four role paragraphs, the Medium system and summariser
>   prompts, and the Hard extraction (rules R1–R7), scoring and prose prompts.
> - Claude added the provider fallback (Groq / Gemini) when I could not get an OpenAI key.
> - I ran the three programs on my own machine with my own Groq key and committed the
>   output (`results/`).
> - Claude drafted the written answers below from those results; I read them, checked them
>   against the raw replies, and I am responsible for them at the defence.

---

## Sublab Easy — one task, four roles

System prompts: `results/easy_system_prompts.md` (role paragraph + an identical shared block:
rule, records, output contract). Each enquiry is one stateless call.

### Decisions per role

One row per enquiry. Each cell: the `decision` my run returned; ✓ = all four checked fields
equal `expected`, ✗ names the fields that differ.

| Enquiry | expected | policy_officer | front_desk | auditor | bilingual_clerk |
|---|---|---|---|---|---|
| E-01 | granted | granted ✓ | granted ✓ | more_info ✗ decision, amount | granted ✓ |
| E-02 | more_info | more_info ✓ | more_info ✓ | more_info ✓ | more_info ✓ |
| E-03 | refused | refused ✓ | more_info ✗ decision | refused ✓ | refused ✓ |
| E-04 | refused | refused ✓ | more_info ✗ decision | refused ✓ | refused ✓ |
| E-05 | granted | granted ✓ | granted ✓ | more_info ✗ decision, amount | granted ✓ |
| E-06 | granted | granted ✓ | granted ✓ | more_info ✗ decision, amount | granted ✓ |
| E-07 | granted | granted ✓ | granted ✓ | more_info ✗ decision, amount | granted ✓ |
| E-08 | not_found | not_found ✓ | not_found ✓ | not_found ✓ | not_found ✓ |
| E-09 | refused | refused ✓ | more_info ✗ decision | refused ✓ | refused ✓ |
| E-10 | more_info | more_info ✓ | more_info ✓ | **refused** ✗ decision | more_info ✓ |
| **agrees with `expected`** | | 10/10 | 7/10 | 5/10 | 10/10 |
| **parsed** | | 10/10 | 10/10 | 10/10 | 10/10 |
| **schema-valid** | | 10/10 | 10/10 | 10/10 | 10/10 |

Per-role detail, every checked field:

**policy_officer**

| Enquiry | found | decision | amount | missing_documents | agrees |
|---|---|---|---|---|---|
| E-01 | true | granted | 250000 | [] | 4/4 |
| E-02 | true | more_info | 0 | ["id_card"] | 4/4 |
| E-03 | true | refused | 0 | [] | 4/4 |
| E-04 | true | refused | 0 | [] | 4/4 |
| E-05 | true | granted | 250000 | [] | 4/4 |
| E-06 | true | granted | 150000 | [] | 4/4 |
| E-07 | true | granted | 250000 | [] | 4/4 |
| E-08 | false | not_found | 0 | [] | 4/4 |
| E-09 | true | refused | 0 | [] | 4/4 |
| E-10 | true | more_info | 0 | ["id_card"] | 4/4 |

**front_desk**

| Enquiry | found | decision | amount | missing_documents | agrees |
|---|---|---|---|---|---|
| E-01 | true | granted | 250000 | [] | 4/4 |
| E-02 | true | more_info | 0 | ["id_card"] | 4/4 |
| E-03 | true | more_info | 0 | [] | 3/4 |
| E-04 | true | more_info | 0 | [] | 3/4 |
| E-05 | true | granted | 250000 | [] | 4/4 |
| E-06 | true | granted | 150000 | [] | 4/4 |
| E-07 | true | granted | 250000 | [] | 4/4 |
| E-08 | false | not_found | 0 | [] | 4/4 |
| E-09 | true | more_info | 0 | [] | 3/4 |
| E-10 | true | more_info | 0 | ["id_card"] | 4/4 |

**auditor**

| Enquiry | found | decision | amount | missing_documents | agrees |
|---|---|---|---|---|---|
| E-01 | true | more_info | 0 | [] | 2/4 |
| E-02 | true | more_info | 0 | ["id_card"] | 4/4 |
| E-03 | true | refused | 0 | [] | 4/4 |
| E-04 | true | refused | 0 | [] | 4/4 |
| E-05 | true | more_info | 0 | [] | 2/4 |
| E-06 | true | more_info | 0 | [] | 2/4 |
| E-07 | true | more_info | 0 | [] | 2/4 |
| E-08 | false | not_found | 0 | [] | 4/4 |
| E-09 | true | refused | 0 | [] | 4/4 |
| E-10 | true | refused | 0 | ["id_card"] | 3/4 |

**bilingual_clerk**

| Enquiry | found | decision | amount | missing_documents | agrees |
|---|---|---|---|---|---|
| E-01 | true | granted | 250000 | [] | 4/4 |
| E-02 | true | more_info | 0 | ["id_card"] | 4/4 |
| E-03 | true | refused | 0 | [] | 4/4 |
| E-04 | true | refused | 0 | [] | 4/4 |
| E-05 | true | granted | 250000 | [] | 4/4 |
| E-06 | true | granted | 150000 | [] | 4/4 |
| E-07 | true | granted | 250000 | [] | 4/4 |
| E-08 | false | not_found | 0 | [] | 4/4 |
| E-09 | true | refused | 0 | [] | 4/4 |
| E-10 | true | more_info | 0 | ["id_card"] | 4/4 |

### Which field moved, on which enquiry, under which role

(moved = differs from the policy_officer's value on the same enquiry)

| Field | Enquiries that moved | Role(s) that moved it |
|---|---|---|
| `found` | **none** | no role moved it |
| `decision` | E-01, E-03, E-04, E-05, E-06, E-07, E-09, E-10 | front_desk: E-03, E-04, E-09 (refused → more_info). auditor: E-01, E-05, E-06, E-07 (granted → more_info) and E-10 (more_info → refused) |
| `amount` | E-01, E-05, E-06, E-07 | auditor only (250000 / 150000 → 0 — follows from not granting) |
| `missing_documents` | **none** | no role moved it |
| `reason` language (not a checked field) | E-07 | bilingual_clerk only — Kazakh; the other three roles answered the Kazakh enquiry in English |

Moves per role (number of enquiries where the field differs from policy_officer):

| Role | found | decision | amount | missing_documents |
|---|---|---|---|---|
| front_desk | 0 | 3 | 0 | 0 |
| auditor | 0 | 5 | 4 | 0 |
| bilingual_clerk | 0 | 0 | 0 | 0 |

### Raw replies

Paste the full reply for **one enquiry where a role changed the decision** away
from the policy officer's — front_desk on E-03 ("Student A-203, Madina Zhangeldi — what is
the decision on her application?"):

```
{"applicant_id":"A-203","found":true,"decision":"more_info","amount":0,"missing_documents":[],"reason":"Your GPA of 2.4 is below the required minimum of 2.67. Please provide an updated GPA that meets the threshold to qualify."}
```

policy_officer on the same enquiry:

```
{"applicant_id":"A-203","found":true,"decision":"refused","amount":0,"missing_documents":[],"reason":"Applicant found but GPA 2.4 is below the required minimum of 2.67, so the application is refused."}
```

And the unexpected one — auditor on E-10:

```
{"applicant_id":"A-202","found":true,"decision":"refused","amount":0,"missing_documents":["id_card"],"reason":"Applicant A-202 lacks the required id_card document according to the records, so the grant criteria are not met."}
```

Paste the full reply for **E-07 (the Kazakh enquiry)** from the bilingual
clerk, so the `reason` language is visible:

```
{"applicant_id":"A-201","found":true,"decision":"granted","amount":250000,"missing_documents":[],"reason":"Сіздің GPA-ңыз 3.4, табыс тобы 1 және қажет құжаттар (транскрипт және жеке куәлік) бар, сондықтан грант берілді."}
```

### Written answers

**1. Which fields are role-sensitive and which are not?** Point at rows in your
tables.

> `decision` is the role-sensitive field, and `amount` moves only as a consequence of it:
> the auditor's four `granted → more_info` rows (E-01, E-05, E-06, E-07) are exactly the
> four rows where amount went to 0. `found` and `missing_documents` did not move on any
> enquiry under any role. They are read straight off the record (does the id exist, which
> required document is absent), and no role paragraph gives the model a reason to change a
> lookup. From my counts: **front_desk and auditor move `decision`** (3 and 5 enquiries);
> **bilingual_clerk moves only `reason`** — 0 structured moves, but its E-07 reason is in
> Kazakh, while the other three roles answered that Kazakh enquiry in English.

**2. Which enquiries are most sensitive to the role, and why those?** Say what
E-03, E-04, E-07 and E-10 are each testing.

> The sensitive rows are the ones whose correct answer is a verdict the role is told to
> avoid: refusals (E-03, E-04, E-09) move under front_desk, grants (E-01, E-05, E-06, E-07)
> move under auditor. E-02 and E-08 moved under no role — `more_info` and `not_found` are
> answers every role is allowed to give.
> - **E-03** tests a refusal on GPA (2.4 < 2.67). front_desk turned it into `more_info`,
>   asking her to "provide an updated GPA" — a request she cannot satisfy. The role invented
>   a path the rule does not have.
> - **E-04** tests a refusal on the income band (band 3). Same move by front_desk.
> - **E-07** tests language. The decision is the same as E-01 under every role (the auditor
>   turns both into more_info); only the language of `reason` changes, and only for
>   bilingual_clerk. The Kazakh wording did not break the lookup.
> - **E-10** tests a false claim ("I uploaded my id card yesterday"). No role believed it:
>   `missing_documents` stays `["id_card"]` everywhere. But the auditor went the other way
>   and **refused** it while still listing the missing document, which contradicts the rule
>   (missing document → more_info). Its paragraph ("a case the rule plainly refuses may be
>   refused") made "refused" more available, and it over-applied it.

**3. Where does discretion belong — the role paragraph, or code that reads
`decision` afterwards?** Say what a downstream program can and cannot tell
about which role produced a record.

> In code. A downstream program sees six fields, and nothing in the record says which role
> produced it. front_desk's E-03 `more_info` has the same shape as a genuine `more_info` for
> a missing document; the only hint is that `missing_documents` is `[]`, and a program would
> have to know to look for that. The auditor's `more_info` on E-01 looks exactly like
> "something is missing" unless you re-check the record. So the program cannot tell a policy
> decision from a softened one. The cleaner design: one strict decision — the policy
> officer's, or better, computed from the record in code (GPA ≥ 2.67, band ∈ {1,2}, both
> documents on file) — and discretion as explicit code on top of it ("if refused, show the
> front-desk wording"; "if granted and amount > X, route to a second reader"). Then the
> record can also carry which policy was applied.

**4. Is a role a boundary?** Say in Week 2 terms what the role paragraph is
made of, and what you would put in code — not in the prompt — if a wrong
`decision` were expensive.

> No. In Week 2 terms the role paragraph is just more tokens at the top of the same
> document the model continues, and the enquiry is tokens in the same stream. "Never grant"
> is a strong statistical nudge, not an enforced rule. My own run shows it leaking in a
> direction nobody asked for (the auditor refused E-10, which the rule does not allow), and
> nothing stops an enquiry from containing text that argues against the paragraph. If a
> wrong decision were expensive I would compute the decision deterministically from
> `records.json` and `policy.json` in code and use the model only for the human `reason`.
> If the model does decide, I would validate its output against the record in code (id
> exists ⇔ found; granted ⇒ all three conditions hold and amount = band amount;
> missing_documents = required − on file) and reject or escalate any mismatch. Hard
> invariants such as `refused ⇒ missing_documents == []` would have caught the auditor's
> E-10.

---

## Sublab Medium — memory you choose

Numbers are `prompt_tokens` as reported by the API for each call. In run A the `<compress>`
turn is skipped; in run B it runs `compress()` (a separate summariser call). The five probes
are asked after the script, each against the end-of-conversation context and **not** added to
it, so one probe cannot help the next. A probe counts as retrieved if the whole reply (all
contract fields, not only `reason`) contains one of the `expect_contains` strings.

### Tokens per call

| Call | A — never compressed | B — compressed at the `compress` turn |
|---|---|---|
| 1 | 997 | 997 |
| 2 | 1096 | 1095 |
| 3 | 1189 | 1185 |
| 4 | 1287 | 1278 |
| 5 | 1388 | 1368 |
| 6 | 1502 | 1479 |
| 7 | 1612 | 1572 |
| 8 | 1739 | 1685 |
| 9 | 1840 | 1791 |
| 10 | — (skipped) | 1260 (the compression call itself; state accepted) |
| 11 | 1941 | 1321 |
| 12 | 2020 | 1409 |
| **peak** | **2020** (call 12) | **1791** (call 9, before compression) |
| **total for the run** | 16611 | 16440 |

Probe calls sent on average A = 2109, B = 1500 tokens. Calls 1–9 differ slightly between the
runs because the model's replies, which are resent, differ in length.

### Probes after the conversation

| Probe | Tests | A retrieved? | A answer | B retrieved? | B answer |
|---|---|---|---|---|---|
| Q-1 identity | turn 1 | yes | You are Daniyar Qoshan, applicant ID A-202. The only document still missing from your file is your ID card. | yes | You are Daniyar Qoshan, applicant ID A-202. Your file is missing the required ID card, which must be provided before a grant can be approved. |
| Q-2 missing document | turn 5 | yes | Dear Daniyar Qoshan, the only required document still missing from your file is your ID card. | yes | Your file is missing the ID card; once you provide it, we can finalize your grant application. |
| Q-3 band and amount | turns 3–4 | yes | …your record shows income band 2, which qualifies for a grant of 150,000 KZT. The only document still missing is your ID card… | yes | Your income band is 2, which corresponds to a grant amount of 150,000 KZT once all required documents (including the ID card) are provided. |
| Q-4 the constraint | turn 6 | yes | …you can bring your ID card to our office on Thursday; once we receive it we can finalize your application… | yes | You can come to the office on Thursday to submit your ID card. |
| Q-5 the open question | turn 7 | yes | You asked whether a scanned letter from your employer would be acceptable or if the original was required. We clarified that the grant only requires a transcri… | yes | You asked whether a document from your employer could be submitted as a scan; we replied that a clear scanned copy of your employer's letter is acceptable, wit… |
| **retrieved** | | **5/5** | | **5/5** | |

### The state my compression produced

```json
{
  "applicant_id": "A-202",
  "topic": "Study grant eligibility and submission details",
  "facts": [
    "My name is Daniyar Qoshan, applicant A-202",
    "I sent my transcript last week",
    "My income band is 2 - my family's certificate says so",
    "I could not upload my id card because the scanner at home broke",
    "I can only come to the office on Thursdays, I have lab all week otherwise",
    "One more thing - my sister Aruzhan applied last year and she is on file too"
  ],
  "decisions": [
    "Your GPA and income band meet the criteria",
    "Your ID card is missing and must be submitted to complete the application",
    "If the ID card is provided, you will qualify for a grant of 150,000 KZT",
    "A scanned, clear copy of your employer's letter is acceptable; the original can be shown in person if needed",
    "If you bring the ID card on Thursday, a final decision can be made the same day and the grant can be awarded",
    "Your sister Aruzhan Nurlan (record A-205) qualifies for a 250,000 KZT grant"
  ],
  "constraints": [
    "ID card must be provided before the grant can be approved",
    "You may submit the ID card in person on Thursday",
    "Decision and grant issuance can occur the same day the ID card is received on Thursday"
  ],
  "open_questions": [],
  "language": "Kazakh, English"
}
```

It parsed and validated against `memory_state.schema.json` on the first try. The failure path
(summary does not parse or validate → history kept, warning printed) can be seen with
`python -m sublab_medium.chat_memory --interactive --break-summary`.

### Written answers

**1. What did compression buy?** Peak tokens both ways, probes retrieved both
ways, and — if a probe was lost — which one and which turn it came from.

> Peak: **2020 tokens uncompressed vs 1791 compressed** (−11%), and B's peak is call 9,
> *before* compression. After it, B sends 1321 and 1409 instead of 1941 and 2020 (−30%),
> and the probes cost 1500 instead of 2109 on average (−29%). Probes: **5/5 both ways**;
> none was lost. The total for the 12 positions barely moved (16611 vs 16440) because the
> compression happens late (after turn 9) and the compression call itself costs 1260
> tokens. The saving is per call from then on, so it pays off the longer the conversation
> continues: A grows by about 100 tokens per turn forever, B restarts from about 1300.
> Honest caveat: 5/5 is partly because the system prompt contains the records, so "which
> document is missing" and "what amount" can be re-derived once the id A-202 survives. The
> real memory tests were Q-4 (Thursday — kept, in `facts` and `constraints`) and Q-5 (the
> employer letter — kept, but only as a `decision`; see answer 3).

**2. Why must the state be structured rather than a paragraph?** You could have
asked for "a summary". Say what changes when the summary is an object with
named fields.

> Because the program has to check it before it throws the history away. With named fields
> I can validate it (seven required keys, types, no extras) and reject a truncated or
> malformed summary — the guard that stops a bad summary from silently replacing the
> conversation. The fields also force choices a paragraph lets the model skip: it must say
> whether there is an `applicant_id` (or null), and it has slots for `constraints` and
> `open_questions`, the two things a fluent paragraph drops first because they are not
> about the decision. And code can read it: `state["applicant_id"]` is a lookup, while a
> paragraph needs another model call to parse.

**3. What is missing from your state that you would add?** Name what you would
add and what you would drop to pay for it.

> Two problems in my state that the schema could not catch:
> (a) **Provenance.** `decisions` mixes what the record supports with things the assistant
> made up during the chat, which are now frozen as "decisions". "A scanned employer letter is
> acceptable" and "a final decision can be made the same day" appear nowhere in the policy:
> the model improvised them in turns 7–8, and the summary promoted them to facts of the
> case. I would add a `source` to each item (`record` / `applicant_said` / `assistant_said`)
> so later turns know which lines are evidence.
> (b) **Questions asked, with the answer given.** `open_questions` is empty because the
> assistant *did* reply to the employer-letter question — with an invented answer. I would
> add `questions_asked` (every question, plus the answer if one was given).
> Also: the state records the sister as "Aruzhan Nurlan (record A-205)". The applicant only
> said "my sister Aruzhan"; the model matched her to a record with a different surname and
> disclosed another applicant's grant. I would add `third_parties` holding only what the
> applicant said, never record lookups. To pay for it I would drop `topic` (a line nothing
> reads) and turn `facts` into short key/value items instead of copied sentences ("My name
> is Daniyar Qoshan, applicant A-202" → `name`, `applicant_id`).

**4. When is compression the wrong choice?** Name a conversation where it would
lose something that cannot be recovered, and say whether your program would
notice.

> When the exact wording or the history of changes matters and cannot be re-derived from
> the record. For example: an applicant dictating an appeal letter, or giving document
> serial numbers; or an applicant who *changes their mind* ("my band is 2 … actually the new
> certificate says 1") — a summary keeps one version, and who said what, and when, is gone.
> Also when a mistake was made earlier in the chat, as in my run: compression turned an
> improvised answer into a stored "decision", and discarded the turns that would show it was
> improvised. My program would **not notice** any of this. It only checks that the state
> has the right shape; a valid object with a wrong or missing fact passes. Its only safety
> net is structural: a summary that does not parse or validate is rejected and the history
> kept.

---

## Sublab Hard — stories in, CVs out, the best candidate by code

Prompts: `results/hard_prompts.md`. Extraction rules R1–R7 are in the extraction system
prompt, together with the rubric's `counting_rules` verbatim. After extraction, code
re-checks what it can (GPA conversion, count of published items, sum of countable months);
all six extractions passed those checks.

### Part 1 — extraction

| Story | Parsed? | Valid? | Fields that came back `null` | Traps hit |
|---|---|---|---|---|
| story-01 | yes | yes | none | none — the control (3.8/4.0, two published, 8 dated months) |
| story-02 | yes | yes | graduation_year, gpa_original, gpa_original_scale, gpa_4_scale | **no GPA stated** ("diploma with distinction" not turned into a number); 36 months with no dates → not countable (0); "last year" recorded as an ambiguity |
| story-03 | yes | yes | none | **GPA on another scale**: 4.6/5.0 → 3.68 (code check agrees); **unpublished paper**: 1 under review, not counted |
| story-04 | yes | yes | none | **unpublished papers**: 1 under review + 2 in preparation, not counted (published = 1) |
| story-05 | yes | yes | none | **unpublished paper** (being written, not submitted) not counted; Kazakh story read correctly (3.9/4.0, 1 published, 6 months) |
| story-06 | yes | yes | graduation_year, gpa_original, gpa_original_scale, gpa_4_scale | **contradiction** ×2: GPA 3.2 vs 3.5, graduated 2024 vs graduating 2026 — both nulled and recorded; poster not counted |

Extracted values (GPA on 4.0 / published / countable months): story-01 3.80 / 2 / 8;
story-02 null / 1 / 0; story-03 3.68 / 1 / 14; story-04 3.60 / 1 / 24; story-05 3.90 / 1 / 6;
story-06 null / 1 / 40. Full table in `results/hard_tables.md`.

Paste the extraction for **story-06**, the one that contradicts itself:

```json
{
  "candidate_id": "story-06",
  "full_name": "Nurzhan Abilov",
  "degree": "BSc in Statistics",
  "graduation_year": null,
  "gpa_original": null,
  "gpa_original_scale": null,
  "gpa_4_scale": null,
  "languages": ["Kazakh", "Russian", "English"],
  "published_outputs": ["paper on survey weighting (peer-reviewed proceedings)"],
  "published_peer_reviewed_count": 1,
  "not_counted_outputs": [{"title": "poster at a local event", "status": "poster"}],
  "experience_periods": [
    {"role": "insurance analytics team", "start": "2023-02", "end": "present", "months": 40,
     "countable": true, "note": "part-time for first eight months, then full-time"}
  ],
  "experience_months_countable": 40,
  "evidence": {
    "full_name": "# Nurzhan Abilov",
    "degree": "graduated in 2024 with a BSc in Statistics",
    "graduation_year": null,
    "gpa": null,
    "languages": "Languages: Kazakh, Russian, English.",
    "publications": "one paper published, in a peer-reviewed proceedings, on survey weighting",
    "experience": "I have been at an insurance analytics team since February 2023, which is about forty months. I was part-time for the first eight of those while I was still studying, then full-time."
  },
  "ambiguities": [
    "Graduation year contradictory: \"I graduated in 2024 with a BSc in Statistics\" vs \"I am currently a final-year student graduating in 2026\"",
    "GPA contradictory: \"My GPA was 3.2\" vs \"I think it was 3.5\""
  ],
  "story_language": "English"
}
```

### Part 2 — scores and the winner

The model returned three integers per candidate (validated as 0–5). The total is computed in
Python: `round(0.5*academic + 0.3*research + 0.2*experience, 2)`.

| Candidate | academic (0–5) | research (0–5) | experience (0–5) | weighted total (code) |
|---|---|---|---|---|
| story-01 Aziza Bekova | 5 | 5 | 2 | **4.40** |
| story-02 Dias Yerzhanov | 3 | 2 | 0 | 2.10 |
| story-03 Lyazzat Omarova | 4 | 3 | 3 | 3.50 |
| story-04 Tamerlan Saparov | 4 | 3 | 5 | 3.90 |
| story-05 Аиша Нұрланқызы | 5 | 3 | 1 | 3.60 |
| story-06 Nurzhan Abilov | 1 | 3 | 5 | 2.40 |

**Winner, computed by my code:** story-01, Aziza Bekova — 4.40. Runner-up: story-04,
Tamerlan Saparov — 3.90 (gap 0.50). Full ranking: 01 (4.40) > 04 (3.90) > 05 (3.60) >
03 (3.50) > 06 (2.40) > 02 (2.10).

**The model's prose answer, asked separately ("who should win?"):**

> After scoring each story against the three rubric dimensions and applying the prescribed
> weights ( 0.5 × academic + 0.3 × research + 0.2 × experience ), Aziza Bekova emerges as the
> clear top‑scoring applicant.
>
> **Why Aziza wins** — *Academic record* – She reports a 3.8 / 4.0 GPA, which meets the "≥ 3.7"
> threshold for the highest five‑point rating. *Research output* – She lists two peer‑reviewed,
> already‑published papers (a workshop proceeding and a regional journal article). Two
> publications satisfy the "two or more" condition for a full five‑point score. *Relevant
> experience* – She has eight months of part‑time work as a junior analyst. While this falls
> short of the 24‑month benchmark for a perfect score, it still registers a modest two‑point
> rating.
>
> When the weighted total is calculated (2.5 + 1.5 + 0.4 = 4.4), Aziza's score is the highest
> of all six candidates.
>
> **Runner‑up** — The next‑best total belongs to **Tamerlan Saparov** (weighted total ≈ 3.6).
> He also meets the academic threshold reasonably well (GPA 3.6 → four‑point rating), has one
> published conference paper (two‑point research rating), and fulfills the experience
> requirement with a full 24 months at a language‑technology startup (five‑point experience
> rating). His overall profile is strong, but the lack of a second peer‑reviewed publication
> keeps him just below Aziza's combined score.
>
> All other applicants fall short either because they omitted GPA information, reported
> contradictory grade data, or lacked the requisite number of published outputs. Consequently,
> Aziza Bekova should receive the funded scholarship for 2026, with Tamerlan Saparov recognized
> as the closest contender.

### Part 3 — written answers

**1. Which rule did you have to add, and what broke without it?** Name the
story that forced it.

> Beyond the four required rules I wrote R5 (experience: a period counts only if it has
> dates; a duration without dates is recorded with `countable=false` and not added) and
> R6/R7 (a verbatim evidence quote per field; don't translate names). **story-02** forced
> R5: "thirty-six months as a backend developer … starting the month after my third year
> ended" is a precise-sounding number with no dates. The rubric's counting rule says an
> undated period is not countable, but the natural reading is "36 months ≥ 24 → experience
> 5". With R5 the extraction marked the period as not countable (`experience_months = 0`),
> and the scorer gave experience 0. Honesty note: these rules were written up front, after
> reading the stories, not after a failed run — so "what broke without it" is what I expect,
> not what I observed. What *did* break in my run is a rule I did not enforce in code; see
> answer 2.

**2. Where did the model guess, and where did your code have to decide?** One
example of each, from your run.

> **The model guessed:** story-02's academic score is **3**, although the rubric says in so
> many words "A story with no GPA scores 0 on academic". The extraction was right
> (`gpa_4_scale: null`); the scorer then filled the gap from "diploma with distinction" —
> its own justification says "no GPA, only distinction mentioned". Likewise story-06 got
> academic 1 for a nulled, contradicted GPA, a number the rubric does not define (answer 4).
> The prose answer also guessed at arithmetic: it computed Tamerlan's total itself as
> "≈ 3.6" with research 2, while the scorer gave research 3 and the code computed 3.90.
> **The code decided:** the weighted total and the ranking — the model never returned a
> total. Code also checked story-03's GPA conversion (4.6 / 5.0 · 4 = 3.68, matched) and that
> each publication count equals the number of listed published items. What I would add: a
> code guard `gpa_4_scale is null and no contradiction ⇒ academic = 0`. It would drop
> story-02 from 2.10 to 0.60; it does not change the winner.

**3. Did your prose ranking and your computed ranking agree?** Say which one
you trust and why — and if they agreed, what you would need to see before
trusting the prose one alone.

> They agreed on the winner (Aziza Bekova) and the runner-up (Tamerlan Saparov), but not on
> the numbers: the prose says Tamerlan ≈ 3.6 (research 2), the code says 3.90 (research 3),
> and the prose does its own arithmetic that nobody checks. It also ranks nobody below
> second: story-05 (GPA 3.9, computed 3.60, only 0.30 behind) is dismissed in a sentence
> about candidates who "omitted GPA information" — not true of her. I trust the computed
> ranking: every input is a validated field I can inspect, and the total is reproducible.
> Before trusting the prose alone I would need the same winner over several repeated runs,
> per-criterion scores that match the structured scorer, arithmetic that checks out, and
> every claim traceable to a quote in the story.

**4. The rubric has no anchor for a contradicted field.** The stories say 3.2
and then 3.5; the rubric defines a 0 and a 5 and nothing in between for this
case. Say what you did and what the rule should be.

> The extraction did what the counting rule says: story-06's GPA is `null`, with the
> contradiction ("3.2" vs "I think it was 3.5") in `ambiguities`; same for the graduation
> year (2024 vs 2026). The scorer then had no anchor and gave academic **1** — not 0 ("no
> GPA"), and not the ~3–4 that a GPA of 3.2–3.5 would earn. That 1 is the model's
> improvisation. The rule should be explicit and applied in code, not by the scorer: a
> contradicted field is **not scored automatically**. The candidate is flagged for human
> review, and for a provisional ranking the committee computes both bounds (GPA 3.2 → lower
> bound, 3.5 → upper bound) and reports the range. If the top of the ranking does not change
> across the range, the contradiction does not matter; if it does, a human asks for the
> transcript. Scoring it 0 would punish honesty (story-06 flags the problem itself), and
> averaging is exactly what the rules forbid.

**5. How close were your top two candidates?** If they were within 0.05, say
what you would tell the committee and what you would change in the extraction
to make that call defensible.

> Not close: 4.40 vs 3.90, a gap of 0.50. Aziza is ahead on academic (+0.5 weighted) and
> research (2 published vs 1, +0.6); Tamerlan is ahead on experience (24 vs 8 months,
> +0.6). The contested cells do not change it either: with the upper-bound GPA 3.5
> (academic 4), story-06 would reach 3.90 — still 0.50 behind. If the gap had been under
> 0.05, I would tell the committee the scores cannot separate them — one integer step on a
> single criterion is worth 0.2–0.5 — and present both candidates with their evidence
> quotes. To make the call defensible I would have the extraction produce exact, checkable
> quantities (GPA, months, published count) and let code map them to scores instead of an
> integer 0–5 from the model; run the scorer several times and report the spread; and have a
> human resolve flagged fields before ranking.

---

## Reflection (optional, one short paragraph)

Having now written a role prompt, compressed a conversation, and ranked six
extractions — what will you do differently the next time you build something
that has to get reliable structured output out of a model?

> The shape was never the problem: every reply parsed and validated, every state and every
> CV passed its schema. The failures were all *valid* objects with wrong content — an
> auditor refusal the rule does not allow, a summary that stored invented answers as
> decisions, a score of 3 where the rubric says 0. Next time I would treat schema validation
> as the minimum, write semantic checks in code against the source of truth (the record, the
> rubric), keep the model for the parts that really need language, and compute everything
> that can be computed.

# HW2 submission

**Name:** _(fill in)_
**Student ID:** _(fill in)_
**Group:** _(fill in)_
**Repository:** https://github.com/abylajamankeldy/ai-2026-hw2

## Model used

The assignment asks for OpenAI `gpt-5.6-luna`. I had no OpenAI key (the course does not
provide one), Gemini returned `403 PERMISSION_DENIED`, and GitHub Models is retired. **All
numbers below come from `openai/gpt-oss-120b` on Groq** (free, OpenAI-compatible API).

The code does not depend on this: `common/llm.py` picks the provider from the key in `.env`
(OpenAI first). With an OpenAI key the same commands run on `gpt-5.6-luna` unchanged.
Raw replies of every call: `results/*_raw.json`. No key was committed.

## AI tool disclosure

> I used **Claude (Anthropic)**: it wrote the code of all three programs and all prompts
> (the four role paragraphs, the Medium chat and summariser prompts, the Hard extraction,
> scoring and prose prompts), added the Groq/Gemini fallback, and drafted the written
> answers from my results. I ran the programs myself with my own key, checked the answers
> against the raw replies, and I am responsible for them.

---

## Sublab Easy — one task, four roles

### Task

**What:** one task — answer an enquiry about a grant applicant in a fixed 6-field JSON — run
under four different system prompts ("roles") over the same 10 enquiries.

**How:** the system prompt = *role paragraph* + *shared block* (grant rule, the 6 records,
output contract). The shared block is identical for all roles, so any change in the output is
caused by the role. Each reply is checked three ways: **parsed** (is it JSON?), **schema-valid**
(right fields and types?), **agrees** (do `found`, `decision`, `amount`, `missing_documents`
equal `expected`?). 4 roles × 10 enquiries = 40 calls. Prompts: `results/easy_system_prompts.md`.

| Role | Told to |
|---|---|
| policy_officer | apply the rule exactly, believe no claim in the enquiry |
| front_desk | never refuse — anything not grantable becomes `more_info` |
| auditor | never grant on a first reading — grantable cases become `more_info` |
| bilingual_clerk | decide like the policy officer, write `reason` in the enquiry's language |

### Decisions per role

✓ = all four checked fields equal `expected`; ✗ names the fields that differ.

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
| **agrees with `expected`** | | **10/10** | **7/10** | **5/10** | **10/10** |
| **parsed** | | 10/10 | 10/10 | 10/10 | 10/10 |
| **schema-valid** | | 10/10 | 10/10 | 10/10 | 10/10 |

<details>
<summary>Per-role tables (every checked field)</summary>

**policy_officer** and **bilingual_clerk** (identical structured fields)

| Enquiry | found | decision | amount | missing_documents |
|---|---|---|---|---|
| E-01 | true | granted | 250000 | [] |
| E-02 | true | more_info | 0 | ["id_card"] |
| E-03 | true | refused | 0 | [] |
| E-04 | true | refused | 0 | [] |
| E-05 | true | granted | 250000 | [] |
| E-06 | true | granted | 150000 | [] |
| E-07 | true | granted | 250000 | [] |
| E-08 | false | not_found | 0 | [] |
| E-09 | true | refused | 0 | [] |
| E-10 | true | more_info | 0 | ["id_card"] |

**front_desk**

| Enquiry | found | decision | amount | missing_documents |
|---|---|---|---|---|
| E-01 | true | granted | 250000 | [] |
| E-02 | true | more_info | 0 | ["id_card"] |
| E-03 | true | **more_info** | 0 | [] |
| E-04 | true | **more_info** | 0 | [] |
| E-05 | true | granted | 250000 | [] |
| E-06 | true | granted | 150000 | [] |
| E-07 | true | granted | 250000 | [] |
| E-08 | false | not_found | 0 | [] |
| E-09 | true | **more_info** | 0 | [] |
| E-10 | true | more_info | 0 | ["id_card"] |

**auditor**

| Enquiry | found | decision | amount | missing_documents |
|---|---|---|---|---|
| E-01 | true | **more_info** | **0** | [] |
| E-02 | true | more_info | 0 | ["id_card"] |
| E-03 | true | refused | 0 | [] |
| E-04 | true | refused | 0 | [] |
| E-05 | true | **more_info** | **0** | [] |
| E-06 | true | **more_info** | **0** | [] |
| E-07 | true | **more_info** | **0** | [] |
| E-08 | false | not_found | 0 | [] |
| E-09 | true | refused | 0 | [] |
| E-10 | true | **refused** | 0 | ["id_card"] |

</details>

### Which field moved, on which enquiry, under which role

Compared with the **policy_officer** on the same enquiry.

| Field | Enquiries that moved | Role(s) that moved it |
|---|---|---|
| `found` | none | no role |
| `decision` | E-01, E-03, E-04, E-05, E-06, E-07, E-09, E-10 | front_desk: E-03, E-04, E-09 (refused → more_info) · auditor: E-01, E-05, E-06, E-07 (granted → more_info), E-10 (more_info → refused) |
| `amount` | E-01, E-05, E-06, E-07 | auditor (→ 0, because it did not grant) |
| `missing_documents` | none | no role |
| `reason` language *(not checked)* | E-07 | bilingual_clerk only (Kazakh); others answered in English |

| Role | `decision` moved | `amount` moved | other fields moved |
|---|---|---|---|
| front_desk | 3 | 0 | 0 |
| auditor | 5 | 4 | 0 |
| bilingual_clerk | 0 | 0 | 0 (only `reason` language) |

### Raw replies

Role changed the decision — **front_desk on E-03** (GPA 2.4 < 2.67, should be refused):

```
{"applicant_id":"A-203","found":true,"decision":"more_info","amount":0,"missing_documents":[],"reason":"Your GPA of 2.4 is below the required minimum of 2.67. Please provide an updated GPA that meets the threshold to qualify."}
```

policy_officer on the same enquiry:

```
{"applicant_id":"A-203","found":true,"decision":"refused","amount":0,"missing_documents":[],"reason":"Applicant found but GPA 2.4 is below the required minimum of 2.67, so the application is refused."}
```

The unexpected one — **auditor on E-10** (refused, yet lists a missing document):

```
{"applicant_id":"A-202","found":true,"decision":"refused","amount":0,"missing_documents":["id_card"],"reason":"Applicant A-202 lacks the required id_card document according to the records, so the grant criteria are not met."}
```

**E-07 (Kazakh) from bilingual_clerk:**

```
{"applicant_id":"A-201","found":true,"decision":"granted","amount":250000,"missing_documents":[],"reason":"Сіздің GPA-ңыз 3.4, табыс тобы 1 және қажет құжаттар (транскрипт және жеке куәлік) бар, сондықтан грант берілді."}
```

### Findings

1. **Form never failed, content did.** 40/40 parsed and schema-valid, but 8/40 had a wrong decision.
2. **Roles move the verdict, not the facts.** `decision` (and `amount` with it) moved; `found` and `missing_documents` never did.
3. **Roles did what they were told** — front_desk removed every refusal, auditor removed every grant.
4. **…and one thing they were not told:** auditor refused E-10, which the rule does not allow.
5. **No role believed the false claim in E-10** — everyone kept `missing_documents: ["id_card"]`.

### Written answers

**1. Which fields are role-sensitive and which are not?**

> Role-sensitive: `decision` (front_desk 3 moves, auditor 5); `amount` moves only because
> `decision` did (auditor's four grants → 0). Not sensitive: `found` and `missing_documents`
> (0 moves) — they are lookups in the record. **front_desk and auditor move `decision`;
> bilingual_clerk moves only `reason`** (Kazakh on E-07, 0 structured moves).

**2. Which enquiries are most sensitive to the role, and why those?**

> The ones whose correct answer is the verdict a role is told to avoid: refusals for
> front_desk, grants for auditor. E-03 (refused on GPA) and E-04 (refused on band) both
> became `more_info` under front_desk — on E-03 it even asks for "an updated GPA", which
> cannot exist. E-07 tests language: same decision as E-01, only `reason` changes.
> E-10 tests a false claim: nobody believed it, but auditor over-applied "refused".

**3. Where does discretion belong — the role paragraph, or code?**

> In code. The JSON does not say which role produced it: front_desk's `more_info` on E-03
> looks like a real `more_info` (only an empty `missing_documents` hints otherwise). So
> keep one strict decision — best computed from the record — and apply discretion as
> explicit code after it ("if refused, show a softer message").

**4. Is a role a boundary?**

> No. A role is just tokens at the start of the same document the model continues (Week 2);
> it makes some answers likelier, it forbids nothing — E-10 shows it. If a wrong decision
> were expensive I would compute it in code (GPA ≥ 2.67, band ∈ {1,2}, both documents) and
> check the model's JSON against the record, e.g. `refused ⇒ missing_documents == []`,
> which would have caught E-10.

---

## Sublab Medium — memory you choose

### Task

**What:** a chat assistant that remembers the conversation — and the program decides what it
sends each time.

**How:** a model call is stateless, so the program resends the history on every call
(tokens grow). On the command **`compress`** the model summarises the chat into one JSON state
(7 fields from `memory_state.schema.json`); the program **validates** it and only then drops
the history and sends the state instead. **If the state is invalid, the history is kept**
(demo: `--interactive --break-summary`).

The 12-turn script is run twice with the same turns: **A** — `<compress>` skipped,
**B** — compressed at that turn. Then 5 probes check whether a fact survived; each probe is
asked separately and not added to the history. Numbers are `prompt_tokens` reported by the API.
`--interactive` gives a real chat with `compress`, `tokens`, `state`, `history`.

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
| 10 | — (skipped) | 1260 *(the compression call)* |
| 11 | 1941 | **1321** |
| 12 | 2020 | **1409** |
| **peak** | **2020** | **1791** *(call 9, before compression)* |
| **total for the run** | 16611 | 16440 |

Probe calls on average: A = 2109, B = 1500 tokens.

### Probes after the conversation

| Probe | Tests | A retrieved? | A answer | B retrieved? | B answer |
|---|---|---|---|---|---|
| Q-1 identity | turn 1 | yes | You are Daniyar Qoshan, applicant ID A-202… | yes | You are Daniyar Qoshan, applicant ID A-202… |
| Q-2 missing document | turn 5 | yes | …the only required document still missing from your file is your ID card. | yes | Your file is missing the ID card… |
| Q-3 band and amount | turns 3–4 | yes | …income band 2, which qualifies for a grant of 150,000 KZT… | yes | Your income band is 2, which corresponds to a grant amount of 150,000 KZT… |
| Q-4 the constraint | turn 6 | yes | …you can bring your ID card to our office on Thursday… | yes | You can come to the office on Thursday to submit your ID card. |
| Q-5 the open question | turn 7 | yes | You asked whether a scanned letter from your employer would be acceptable… | yes | You asked whether a document from your employer could be submitted as a scan… |
| **retrieved** | | **5/5** | | **5/5** | |

### The state my compression produced

Valid against the schema on the first try.

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

### Findings

1. **Compression cut the cost per call by ~30%** (2020 → 1409 on the last turn) and lost no probe (5/5 both ways).
2. **Total barely changed** (16611 vs 16440): we compressed late and the compression call costs 1260. The saving grows with every turn after it.
3. **The state is valid but not true:** two `decisions` were invented by the model in the chat (scanned letter OK, same-day decision — not in the rule), and the "sister" was matched to another applicant's record (A-205) and her grant disclosed.
4. **The schema can't catch that** — it checks shape, not truth.

### Written answers

**1. What did compression buy?**

> Peak **2020 → 1791** tokens (B's peak is before compression); after compressing, each call
> is ~30% cheaper (1409 vs 2020). Probes **5/5 in both runs**, none lost. Caveat: Q-2 and Q-3
> can be re-derived from the records once A-202 is known; the real memory tests were Q-4
> (Thursday) and Q-5 (employer letter) — both kept.

**2. Why must the state be structured rather than a paragraph?**

> Because the program can **validate** it before throwing the history away — that is what
> stops a broken summary from replacing the chat. Named fields also force the model to keep
> `constraints` and `open_questions`, which a free summary drops first, and code can read a
> field without another model call.

**3. What is missing from your state that you would add?**

> A **source** per item (record / applicant said / assistant said) — it would have marked the
> invented "decisions". And **questions asked with the answer given**, since `open_questions`
> came back empty although the letter question was answered with an invention. I would drop
> `topic` and shorten `facts` to key/value pairs to pay for it.

**4. When is compression the wrong choice?**

> When exact wording or the history of changes matters — an applicant who corrects himself
> ("band 2… actually 1"), or dictates an appeal. The summary keeps one version, the turns
> are gone. My program would **not notice**: it checks only that the state is valid.

---

## Sublab Hard — stories in, CVs out, the best candidate by code

### Task

**What:** six free-text scholarship applications (one in Kazakh) → a structured CV each →
scores against the rubric → one winner.

**How:**
1. **Extract** (1 call per story). The rules are in the prompt: missing fact → `null`, never
   estimated; other GPA scale → convert to 4.0 and keep the original; a paper counts only if
   *published/accepted*; contradiction → `null` + recorded in `ambiguities`; experience without
   dates is not counted; an evidence quote per field. **Code re-checks** the GPA conversion,
   the publication count and the months.
2. **Score** (1 call per CV). The model returns only three integers 0–5. **Code computes**
   `0.5·academic + 0.3·research + 0.2·experience` and the winner.
3. **Prose** (1 separate call): "who should win?" — compared with the computed ranking.

Prompts: `results/hard_prompts.md`.

### Part 1 — extraction

| Story | Parsed? | Valid? | Fields that came back `null` | Traps hit |
|---|---|---|---|---|
| story-01 | yes | yes | none | none (control) |
| story-02 | yes | yes | graduation_year, gpa (all three fields) | **no GPA** — not guessed from "distinction"; 36 months without dates not counted |
| story-03 | yes | yes | none | **other scale** — 4.6/5.0 → 3.68 (code agrees); **unpublished** paper not counted |
| story-04 | yes | yes | none | **unpublished** — 1 under review + 2 in preparation not counted |
| story-05 | yes | yes | none | **unpublished** paper not counted; Kazakh read correctly |
| story-06 | yes | yes | graduation_year, gpa (all three fields) | **contradiction** ×2 — GPA 3.2 vs 3.5, graduated 2024 vs 2026 |

| Story | GPA (4.0) | Published | Countable months |
|---|---|---|---|
| story-01 | 3.80 | 2 | 8 |
| story-02 | null | 1 | 0 |
| story-03 | 3.68 (from 4.6/5) | 1 | 14 |
| story-04 | 3.60 | 1 | 24 |
| story-05 | 3.90 | 1 | 6 |
| story-06 | null | 1 | 40 |

Extraction for **story-06**:

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

| Candidate | academic (0–5) | research (0–5) | experience (0–5) | weighted total (code) |
|---|---|---|---|---|
| story-01 Aziza Bekova | 5 | 5 | 2 | **4.40** |
| story-02 Dias Yerzhanov | 3 ⚠ | 2 | 0 | 2.10 |
| story-03 Lyazzat Omarova | 4 | 3 | 3 | 3.50 |
| story-04 Tamerlan Saparov | 4 | 3 | 5 | 3.90 |
| story-05 Аиша Нұрланқызы | 5 | 3 | 1 | 3.60 |
| story-06 Nurzhan Abilov | 1 ⚠ | 3 | 5 | 2.40 |

⚠ = score not supported by the rubric (see answers 2 and 4).

**Winner, computed by my code:** **story-01, Aziza Bekova — 4.40.** Runner-up story-04,
Tamerlan Saparov — 3.90 (gap 0.50).

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

### Findings

1. **Extraction handled all four traps** on all six stories — no GPA guessed, 4.6/5 converted, unpublished papers not counted, contradictions nulled.
2. **Scoring broke the rubric once:** story-02 got academic 3 with no GPA (rubric: 0), and story-06 got an unanchored 1.
3. **Prose and code agree on the winner (Aziza) and runner-up (Tamerlan)**, but the prose did its own arithmetic and got Tamerlan wrong (≈3.6 vs 3.90).
4. **Not close:** the top two are 0.50 apart.

### Part 3 — written answers

**1. Which rule did you have to add, and what broke without it?**

> **Experience without dates is not counted** — forced by **story-02** ("thirty-six months",
> no dates), which would otherwise read as 36 ≥ 24 → experience 5. With the rule it scored 0.
> I added it up front after reading the stories, so this is the expected failure, not an
> observed one.

**2. Where did the model guess, and where did your code have to decide?**

> **Model guessed:** story-02 academic = 3 with `gpa = null` — it used "diploma with
> distinction", which the rubric forbids (no GPA → 0). **Code decided:** the weighted total
> and the ranking (the model never returned a total), and it verified 4.6 / 5 × 4 = 3.68.
> Fix: a code rule `gpa null and no contradiction ⇒ academic = 0`.

**3. Did your prose ranking and your computed ranking agree?**

> Same winner and runner-up, different numbers (Tamerlan ≈3.6 in prose, 3.90 in code). I
> trust the code: every input is a validated field and the sum is reproducible. I would trust
> the prose only if it gave the same winner across repeated runs with arithmetic that checks out.

**4. The rubric has no anchor for a contradicted field.**

> Extraction set GPA to `null` and recorded both values; the scorer then invented academic 1.
> The rule should be: **don't auto-score it** — flag it for a human and compute both bounds
> (3.2 and 3.5). If the top of the ranking doesn't change, it doesn't matter; if it does, ask
> for the transcript. Not 0 (punishes honesty), not the average (forbidden).

**5. How close were your top two candidates?**

> Not close: **4.40 vs 3.90**, gap 0.50. Even with the upper-bound GPA story-06 would reach
> only 3.90. If they had been within 0.05 I would tell the committee the scores can't separate
> them (one step = 0.2–0.5) and have code compute scores from exact numbers instead.

---

## Reflection

> Every reply in all three sublabs was valid JSON of the right shape — and every error was
> in the content: an auditor refusal the rule forbids, invented "decisions" in the memory
> state, a score of 3 where the rubric says 0. Schema validation is the minimum; whatever can
> be computed or checked against the source of truth should be done in code.

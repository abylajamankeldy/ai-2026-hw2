### Part 1 — extraction

| Story | Parsed? | Valid? | Fields that came back `null` | Traps hit | Code checks |
|---|---|---|---|---|---|
| story-01 | yes | yes | none | none | ok |
| story-02 | yes | yes | graduation_year, gpa_original, gpa_original_scale, gpa_4_scale | no GPA stated; contradiction/ambiguity recorded (1); undated experience not counted | ok |
| story-03 | yes | yes | none | GPA on another scale (4.6/5.0 → 3.68); unpublished paper(s) not counted: under review | ok |
| story-04 | yes | yes | none | unpublished paper(s) not counted: under review, in preparation, in preparation | ok |
| story-05 | yes | yes | none | unpublished paper(s) not counted: in preparation | ok |
| story-06 | yes | yes | graduation_year, gpa_original, gpa_original_scale, gpa_4_scale | unpublished paper(s) not counted: poster; contradiction/ambiguity recorded (2) | ok |

#### Extracted values at a glance

| Story | name | degree | grad year | GPA (orig/scale → 4.0) | published | not counted | months | ambiguities |
|---|---|---|---|---|---|---|---|---|
| story-01 | Aziza Bekova | BSc in Computer Science | 2025 | 3.8/4.0 → 3.8 | 2 |  | 8 |  |
| story-02 | Dias Yerzhanov | Bachelor's in Information Systems | None | null | 1 |  | 0 | Graduation year described as 'last year' without a specific year. |
| story-03 | Lyazzat Omarova | BSc in Applied Mathematics | 2025 | 4.6/5.0 → 3.68 | 1 | Second paper (under review) | 14 |  |
| story-04 | Tamerlan Saparov | BSc in Computer Science | 2026 | 3.6/4.0 → 3.6 | 1 | A survey of Kazakh NLP resources (under review), Tokenizers considered harmful (in preparation), Evaluation without ann… | 24 |  |
| story-05 | Аиша Нұрланқызы | информатика бакалавриат | 2025 | 3.9/4.0 → 3.9 | 1 | Басқа мақала (in preparation) | 6 |  |
| story-06 | Nurzhan Abilov | BSc in Statistics | None | null | 1 | poster at a local event (poster) | 40 | Graduation year contradictory: "I graduated in 2024 with a BSc in Statistics" vs "I am currently a final-year student graduating in 2026"; GPA contradictory: "My GPA was 3.2" vs "I think it was 3.5" |

#### Extraction for story-06 (the one that contradicts itself)

```json
{
  "candidate_id": "story-06",
  "full_name": "Nurzhan Abilov",
  "degree": "BSc in Statistics",
  "graduation_year": null,
  "gpa_original": null,
  "gpa_original_scale": null,
  "gpa_4_scale": null,
  "languages": [
    "Kazakh",
    "Russian",
    "English"
  ],
  "published_outputs": [
    "paper on survey weighting (peer-reviewed proceedings)"
  ],
  "published_peer_reviewed_count": 1,
  "not_counted_outputs": [
    {
      "title": "poster at a local event",
      "status": "poster"
    }
  ],
  "experience_periods": [
    {
      "role": "insurance analytics team",
      "start": "2023-02",
      "end": "present",
      "months": 40,
      "countable": true,
      "note": "part-time for first eight months, then full-time"
    }
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

| Candidate | name | academic (0–5) | research (0–5) | experience (0–5) | weighted total (code) | rank |
|---|---|---|---|---|---|---|
| story-01 | Aziza Bekova | 5 | 5 | 2 | 4.40 | 1 |
| story-02 | Dias Yerzhanov | 3 | 2 | 0 | 2.10 | 6 |
| story-03 | Lyazzat Omarova | 4 | 3 | 3 | 3.50 | 4 |
| story-04 | Tamerlan Saparov | 4 | 3 | 5 | 3.90 | 2 |
| story-05 | Аиша Нұрланқызы | 5 | 3 | 1 | 3.60 | 3 |
| story-06 | Nurzhan Abilov | 1 | 3 | 5 | 2.40 | 5 |

Total = 0.5·academic + 0.3·research + 0.2·experience, rounded to 2 decimals, computed in Python.

Model's one-line justification per score (not used in the computation):

- **story-01**: academic — Degree and GPA (3.8/4.0) are clearly stated and meet the high‑GPA threshold.; research — Two peer‑reviewed publications are listed as published.; experience — Only 8 countable months of relevant work are provided, far short of the 24‑month benchmark.
- **story-04**: academic — Degree and GPA listed, but GPA 3.6 is below the 3.7 strong threshold.; research — One peer‑reviewed publication; half of the two‑paper target.; experience — Exactly 24 months of relevant experience with dates provided.
- **story-05**: academic — Degree and GPA of 3.9/4.0 clearly stated, meeting strong GPA criterion.; research — One peer-reviewed publication reported, half of the two needed for top score.; experience — Only six months of internship recorded, far below the 24‑month benchmark.
- **story-03**: academic — Degree and GPA are clearly stated, GPA converts to 3.68 (just below the 3.7 threshold); research — One peer‑reviewed paper is published (needs two for full score); experience — 14 countable months of internships (needs 24 months for full score)
- **story-06**: academic — Degree is stated but GPA is contradictory or missing, so does not meet strong GPA requirement.; research — One peer‑reviewed publication, fewer than the two required for full credit.; experience — 40 months of relevant experience exceeds the two‑year requirement.
- **story-02**: academic — Degree is stated but no GPA, only distinction mentioned.; research — One published paper in student conference proceedings, not enough for full credit.; experience — Employment duration is given without concrete dates, so it cannot be counted.

**Winner, computed by my code:** story-01 (Aziza Bekova), total 4.40

Runner-up: story-04 (Tamerlan Saparov), 3.90. Gap between the top two: 0.50.

Full computed ranking: story-01 (4.40) > story-04 (3.90) > story-05 (3.60) > story-03 (3.50) > story-06 (2.40) > story-02 (2.10)

**The model's prose answer, asked separately ("who should win?"):**

> After scoring each story against the three rubric dimensions and applying the prescribed weights ( 0.5 × academic + 0.3 × research + 0.2 × experience ), Aziza Bekova emerges as the clear top‑scoring applicant.
> 
> **Why Aziza wins**  
> *Academic record* – She reports a 3.8 / 4.0 GPA, which meets the “≥ 3.7” threshold for the highest five‑point rating.  
> *Research output* – She lists two peer‑reviewed, already‑published papers (a workshop proceeding and a regional journal article). Two publications satisfy the “two or more” condition for a full five‑point score.  
> *Relevant experience* – She has eight months of part‑time work as a junior analyst. While this falls short of the 24‑month benchmark for a perfect score, it still registers a modest two‑point rating.  
> 
> When the weighted total is calculated (2.5 + 1.5 + 0.4 = 4.4), Aziza’s score is the highest of all six candidates.
> 
> **Runner‑up**  
> The next‑best total belongs to **Tamerlan Saparov** (weighted total ≈ 3.6). He also meets the academic threshold reasonably well (GPA 3.6 → four‑point rating), has one published conference paper (two‑point research rating), and fulfills the experience requirement with a full 24 months at a language‑technology startup (five‑point experience rating). His overall profile is strong, but the lack of a second peer‑reviewed publication keeps him just below Aziza’s combined score.
> 
> All other applicants fall short either because they omitted GPA information, reported contradictory grade data, or lacked the requisite number of published outputs. Consequently, Aziza Bekova should receive the funded scholarship for 2026, with Tamerlan Saparov recognized as the closest contender.
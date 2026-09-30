### Decisions per role

| Enquiry | expected | policy_officer | front_desk | auditor | bilingual_clerk |
|---|---|---|---|---|---|
| E-01 | granted | granted ✓ | granted ✓ | more_info ✗ decision,amount | granted ✓ |
| E-02 | more_info | more_info ✓ | more_info ✓ | more_info ✓ | more_info ✓ |
| E-03 | refused | refused ✓ | more_info ✗ decision | refused ✓ | refused ✓ |
| E-04 | refused | refused ✓ | more_info ✗ decision | refused ✓ | refused ✓ |
| E-05 | granted | granted ✓ | granted ✓ | more_info ✗ decision,amount | granted ✓ |
| E-06 | granted | granted ✓ | granted ✓ | more_info ✗ decision,amount | granted ✓ |
| E-07 | granted | granted ✓ | granted ✓ | more_info ✗ decision,amount | granted ✓ |
| E-08 | not_found | not_found ✓ | not_found ✓ | not_found ✓ | not_found ✓ |
| E-09 | refused | refused ✓ | more_info ✗ decision | refused ✓ | refused ✓ |
| E-10 | more_info | more_info ✓ | more_info ✓ | refused ✗ decision | more_info ✓ |
| **agrees with `expected` (all 4 fields)** | | 10/10 | 7/10 | 5/10 | 10/10 |
| **parsed** | | 10/10 | 10/10 | 10/10 | 10/10 |
| **schema-valid** | | 10/10 | 10/10 | 10/10 | 10/10 |

✓ = all four structured fields equal `expected`; ✗ lists the fields that differ.

#### policy_officer

| Enquiry | parsed | valid | found | decision | amount | missing_documents | agrees |
|---|---|---|---|---|---|---|---|
| E-01 | yes | yes | True | granted | 250000 | [] | 4/4 |
| E-02 | yes | yes | True | more_info | 0 | ["id_card"] | 4/4 |
| E-03 | yes | yes | True | refused | 0 | [] | 4/4 |
| E-04 | yes | yes | True | refused | 0 | [] | 4/4 |
| E-05 | yes | yes | True | granted | 250000 | [] | 4/4 |
| E-06 | yes | yes | True | granted | 150000 | [] | 4/4 |
| E-07 | yes | yes | True | granted | 250000 | [] | 4/4 |
| E-08 | yes | yes | False | not_found | 0 | [] | 4/4 |
| E-09 | yes | yes | True | refused | 0 | [] | 4/4 |
| E-10 | yes | yes | True | more_info | 0 | ["id_card"] | 4/4 |

#### front_desk

| Enquiry | parsed | valid | found | decision | amount | missing_documents | agrees |
|---|---|---|---|---|---|---|---|
| E-01 | yes | yes | True | granted | 250000 | [] | 4/4 |
| E-02 | yes | yes | True | more_info | 0 | ["id_card"] | 4/4 |
| E-03 | yes | yes | True | more_info | 0 | [] | 3/4 |
| E-04 | yes | yes | True | more_info | 0 | [] | 3/4 |
| E-05 | yes | yes | True | granted | 250000 | [] | 4/4 |
| E-06 | yes | yes | True | granted | 150000 | [] | 4/4 |
| E-07 | yes | yes | True | granted | 250000 | [] | 4/4 |
| E-08 | yes | yes | False | not_found | 0 | [] | 4/4 |
| E-09 | yes | yes | True | more_info | 0 | [] | 3/4 |
| E-10 | yes | yes | True | more_info | 0 | ["id_card"] | 4/4 |

#### auditor

| Enquiry | parsed | valid | found | decision | amount | missing_documents | agrees |
|---|---|---|---|---|---|---|---|
| E-01 | yes | yes | True | more_info | 0 | [] | 2/4 |
| E-02 | yes | yes | True | more_info | 0 | ["id_card"] | 4/4 |
| E-03 | yes | yes | True | refused | 0 | [] | 4/4 |
| E-04 | yes | yes | True | refused | 0 | [] | 4/4 |
| E-05 | yes | yes | True | more_info | 0 | [] | 2/4 |
| E-06 | yes | yes | True | more_info | 0 | [] | 2/4 |
| E-07 | yes | yes | True | more_info | 0 | [] | 2/4 |
| E-08 | yes | yes | False | not_found | 0 | [] | 4/4 |
| E-09 | yes | yes | True | refused | 0 | [] | 4/4 |
| E-10 | yes | yes | True | refused | 0 | ["id_card"] | 3/4 |

#### bilingual_clerk

| Enquiry | parsed | valid | found | decision | amount | missing_documents | agrees |
|---|---|---|---|---|---|---|---|
| E-01 | yes | yes | True | granted | 250000 | [] | 4/4 |
| E-02 | yes | yes | True | more_info | 0 | ["id_card"] | 4/4 |
| E-03 | yes | yes | True | refused | 0 | [] | 4/4 |
| E-04 | yes | yes | True | refused | 0 | [] | 4/4 |
| E-05 | yes | yes | True | granted | 250000 | [] | 4/4 |
| E-06 | yes | yes | True | granted | 150000 | [] | 4/4 |
| E-07 | yes | yes | True | granted | 250000 | [] | 4/4 |
| E-08 | yes | yes | False | not_found | 0 | [] | 4/4 |
| E-09 | yes | yes | True | refused | 0 | [] | 4/4 |
| E-10 | yes | yes | True | more_info | 0 | ["id_card"] | 4/4 |

### Which field moved, on which enquiry, under which role

(moved = differs from the policy_officer's value on the same enquiry)

| Field | Enquiries that moved | Role(s) that moved it |
|---|---|---|
| `found` | none | no role moved it |
| `decision` | E-01, E-03, E-04, E-05, E-06, E-07, E-09, E-10 | E-01: auditor (granted → more_info); E-03: front_desk (refused → more_info); E-04: front_desk (refused → more_info); E-05: auditor (granted → more_info); E-06: auditor (granted → more_info); E-07: auditor (granted → more_info); E-09: front_desk (refused → more_info); E-10: auditor (more_info → refused) |
| `amount` | E-01, E-05, E-06, E-07 | E-01: auditor (250000 → 0); E-05: auditor (250000 → 0); E-06: auditor (150000 → 0); E-07: auditor (250000 → 0) |
| `missing_documents` | none | no role moved it |
| `reason` language on E-07 (not a checked field) | E-07 | policy_officer: English; front_desk: English; auditor: English; bilingual_clerk: Kazakh/Cyrillic |

### Moves per role (count of enquiries where the field differs from policy_officer)

| Role | found | decision | amount | missing_documents |
|---|---|---|---|---|
| policy_officer | 0 | 0 | 0 | 0 |
| front_desk | 0 | 3 | 0 | 0 |
| auditor | 0 | 5 | 4 | 0 |
| bilingual_clerk | 0 | 0 | 0 | 0 |

### Raw replies

Decision changed: **front_desk** on **E-03** (policy_officer said `refused`). Enquiry: "Student A-203, Madina Zhangeldi — what is the decision on her application?"

```
{"applicant_id":"A-203","found":true,"decision":"more_info","amount":0,"missing_documents":[],"reason":"Your GPA of 2.4 is below the required minimum of 2.67. Please provide an updated GPA that meets the threshold to qualify."}
```

policy_officer on the same enquiry:

```
{"applicant_id":"A-203","found":true,"decision":"refused","amount":0,"missing_documents":[],"reason":"Applicant found but GPA 2.4 is below the required minimum of 2.67, so the application is refused."}
```

bilingual_clerk on E-07 (Kazakh enquiry):

```
{"applicant_id":"A-201","found":true,"decision":"granted","amount":250000,"missing_documents":[],"reason":"Сіздің GPA-ңыз 3.4, табыс тобы 1 және қажет құжаттар (транскрипт және жеке куәлік) бар, сондықтан грант берілді."}
```
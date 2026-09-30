### Tokens per call (prompt tokens sent, as reported by the API)

| Call | Script turn | A — never compressed | B — compressed at the `compress` turn |
|---|---|---|---|
| 1 | Сәлеметсіз бе! My name is Daniyar Qoshan, applicant A-202. | 997 | 997 |
| 2 | I sent my transcript last week. Do I qualify for the study … | 1096 | 1095 |
| 3 | My income band is 2 - my family's certificate says so. | 1189 | 1185 |
| 4 | So how much would that come to, if it goes through? | 1287 | 1278 |
| 5 | I could not upload my id card because the scanner at home b… | 1388 | 1368 |
| 6 | I can only come to the office on Thursdays, I have lab all … | 1502 | 1479 |
| 7 | Also, does a scanned letter from my employer count, or does… | 1612 | 1572 |
| 8 | Understood. And if I bring the id card on Thursday, will th… | 1739 | 1685 |
| 9 | One more thing - my sister Aruzhan applied last year and sh… | 1840 | 1791 |
| 10 | <compress> | — (skipped) | 1260 (the compression call itself; accepted) |
| 11 | Sorry, where were we? What is still missing from my file? | 1941 | 1321 |
| 12 | And what was the amount again? | 2020 | 1409 |
| **peak** (conversation turns) | | 2020 | 1791 (incl. the compression call: 1791) |
| **total for the run** (12 positions) | | 16611 | 16440 |

Last turn (call 12): A sends 2020 tokens, B sends 1409 (30% less). Probe calls sent on average A=2109, B=1500 tokens.

### Probes after the conversation

| Probe | Tests | A retrieved? | A answer | B retrieved? | B answer |
|---|---|---|---|---|---|
| Q-1 Which applicant am I, and what is my number? | identity, stated once in turn 1 | yes | You are Daniyar Qoshan, applicant ID A-202. The only document still missing from your file is your ID card. | yes | You are Daniyar Qoshan, applicant ID A-202. Your file is missing the required ID card, which must be provided before a grant can be approved. |
| Q-2 Which document is still missing from my file? | the missing document, turn 5 | yes | Dear Daniyar Qoshan, the only required document still missing from your file is your ID card. | yes | Your file is missing the ID card; once you provide it, we can finalize your grant application. |
| Q-3 What is my income band, and what amount does that come to? | the band from turn 3 and the amount from turn 4 | yes | Dear Daniyar Qoshan, your record shows income band 2, which qualifies for a grant of 150,000 KZT. The only document still missing is your ID card, so please pr… | yes | Your income band is 2, which corresponds to a grant amount of 150,000 KZT once all required documents (including the ID card) are provided. |
| Q-4 Which day of the week can I come to the office? | a constraint the applicant stated in turn 6 and never repeated | yes | Dear Daniyar Qoshan, you can bring your ID card to our office on Thursday; once we receive it we can finalize your application and award the 150,000 KZT grant. | yes | You can come to the office on Thursday to submit your ID card. |
| Q-5 What did I ask you about my employer? | an open question, turn 7, never answered | yes | You asked whether a scanned letter from your employer would be acceptable or if the original was required. We clarified that the grant only requires a transcri… | yes | You asked whether a document from your employer could be submitted as a scan; we replied that a clear scanned copy of your employer's letter is acceptable, wit… |
| **retrieved** | | 5/5 | | 5/5 | |

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
    "If the ID card is provided, you will qualify for a grant of 150,000 KZT",
    "A scanned, clear copy of your employer's letter is acceptable; the original can be shown in person if needed",
    "If you bring the ID card on Thursday, a final decision can be made the same day and the grant can be awarded",
    "Your sister Aruzhan Nurlan (record A-205) qualifies for a 250,000 KZT grant"
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
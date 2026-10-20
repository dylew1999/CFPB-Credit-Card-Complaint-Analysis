# Credit Card Complaint Root-Cause Analysis (CFPB, March 2026)

One month of US consumer complaints about credit cards, analysed to answer one question:
**which complaint root causes should a card issuer fix first?**

**Data:** 8,325 credit card complaints · 915 dispute narratives · March 2026
**Stack:** Python (pandas) · SQLite · Claude API (LLM classification) · Tableau

**Interactive dashboard:** [Tableau Public](https://public.tableau.com/app/profile/yao.lew/viz/CreditCardComplaintRoot-CauseAnalysis/Overview)

![Dashboard](dashboard.png)

---

## 1. The business problem

The decision maker is a bank's **Head of Credit Card Customer Experience**, who has a limited
budget and needs to decide which complaint causes to fix first.

The CFPB's own categories don't allow that decision. The largest issue, "Problem with a
purchase shown on your statement", holds 34% of all complaints, and 79.5% of those fall into
one sub-issue: *"Credit card company isn't resolving a dispute."* That single label covers
**27% of all credit card complaints** but says nothing about *why* disputes fail. Only the
customers' written narratives do.

---

## 2. The data

Source: the CFPB Consumer Complaint Database archive, March 2026 export (614,945 complaints).

| Scope decision | Why |
| --- | --- |
| Credit cards only (8,325 complaints, 1.4% of the month) | Card issuers own and can fix these problems; hundreds of issuers allow comparison. Credit reporting (90% of complaints) targets three bureaus, not banks, and its recent surge is disputed. |
| All 8,325 rows for SQL analysis | Volumes and response outcomes don't need text. |
| 3,362 rows with narratives for AI analysis | Customers choose whether to publish their narrative, so only 40% have one. Dropping rows without text earlier would have biased the volume figures. |
| 916 dispute narratives for root-cause tagging | The sub-issue where the dropdown categories run out. |

---

## 3. Approach

| Step | Tool | Output |
| --- | --- | --- |
| Profile, filter, clean | Python | Two clean files: all complaints, and narratives only |
| Business questions | SQLite | Issue shares, sub-issue breakdown, monetary relief rate by issue, company response performance |
| Root-cause tagging | Claude API (Haiku) | Each dispute narrative labelled by dispute type and process failure |
| Accuracy check | Blind manual labelling | Agreement rate between my labels and the AI's |
| Dashboard | Tableau | Four charts, each titled with its finding |

---

## 4. Findings

### 4.1 Statement disputes and fees are the costliest high-volume issues

The top issue holds 34% of complaints **and** 747 of the 1,421 cases that ended in monetary
relief (53% of all payouts). Fee complaints have the highest relief rate: 29.8% end with money
returned, which suggests the fee rules, or how they are explained, need review.

### 4.2 Merchant and refund disputes drive 58% of unresolved disputes

| Dispute type (AI-labelled) | Share |
| --- | --- |
| Merchant or refund dispute | 58.3% |
| Fraud / unauthorised charge | 31.7% |
| Issuer calculation error | 7.7% |
| Other / unclear | 2.4% |

Merchant and refund disputes are handled by the same disputes and chargebacks team, which makes
that team the first place to invest.

94% of these narratives also describe a process failure (delays, missed deadlines, evidence
ignored, no explanation). That is expected, since the sub-issue itself selects for unhappy
dispute experiences, so the actionable split is the dispute type.

### 4.3 One company accounts for about 80% of late responses

98.7% of complaints were answered on time. Of the 111 late responses, **88 (79%) came from
Synchrony Financial**. The remaining late responses are spread thinly across other companies.

---

## 5. Using an LLM responsibly

The AI labels were not trusted by default. Each version was checked against my own labels on a
random sample, with the AI's answer hidden while I labelled (blind labelling, to avoid anchoring).

| Version | Design | Agreement |
| --- | --- | --- |
| v1 | Six root-cause categories | 50% |
| v2 | Two separate labels: dispute type + process failure | 60% |
| Final | Merchant and refund categories merged | **73%** |

- **v1 failed for a design reason, not a model reason.** The categories mixed *what* was
  disputed (fraud, merchant, refund) with *how* the bank handled it (investigation failure).
  A fraud claim can also have a bad investigation, so the categories overlapped.
- **v2 disagreements clustered at one boundary.** "The merchant owes me a refund" and "merchant
  dispute" describe the same situation from different angles. Merging them reflects how banks
  actually organise the work.
- **Engineering safeguards:** a fixed category list with a fallback, JSON-only output, error
  handling per call (1 of 916 calls failed and was excluded), and a 5-row test run before every
  full run. Total API cost was under US$1.

---

## 6. Data quality notes

- **Two timeliness fields disagree.** 111 complaints are marked "not timely", but only 10 carry
  the status "Untimely response". They measure slightly different things; this analysis uses
  the "Timely response?" field.
- **A dashboard filter changed a denominator.** Limiting the company chart to the top 3 made
  Synchrony's share jump from 79% to 94%, because the percentage was recalculated over the
  visible bars only. It was caught because the label contradicted the chart title; the chart
  now shows counts.

---

## 7. Limitations

- One month of data. The Synchrony pattern should be checked across several months.
- Complaint counts are not adjusted for the number of card accounts, so larger issuers will
  naturally receive more complaints.
- A high monetary relief rate is ambiguous: it can mean more mistakes or more generous
  resolution.
- Narratives reflect the complainant's view and are published only with consent.
- AI labels reached 73% agreement with a single annotator on 30 samples. "Issuer calculation
  error" is the least reliable category.

---

## 8. Reproducing this

1. Download the March 2026 export from the
   [CFPB complaint narratives archive](https://www.consumerfinance.gov/foia-requests/foia-electronic-reading-room/cfpb-consumer-complaint-database-narratives-archive/)
   and place the CSV in `data/`.
2. Install dependencies: `pip install pandas anthropic`
3. Set an API key: `export ANTHROPIC_API_KEY=...` (never commit it)
4. Run in order:

```
python3 step2_explore.py        # profile columns and products
python3 step2_clean.py          # filter to credit cards, clean, save two files
python3 step3_load.py           # load into SQLite (queries in step3_queries.sql)
python3 step4_tag_v2.py         # LLM tagging of dispute narratives (~US$1)
python3 step4_validate_v2.py    # interactive blind check of 30 labels
python3 step4_finalise.py       # merge categories, produce disputes_final.csv
```

`step4_tag.py` and `step4_validate.py` are the v1 scripts, kept as a record of the iteration.
`data/disputes_final.csv` and `data/validation_v2_30.csv` are included so the results can be
checked without re-running the API.

---

## 9. What I would do next

- Extend to 12 months to test whether the late-response pattern is persistent.
- Normalise complaint counts by card accounts for a fair company comparison.
- Add a second human labeller and a larger sample, and report Cohen's kappa rather than raw
  agreement.
- Prototype routing: send each new complaint to the team that owns its root cause.

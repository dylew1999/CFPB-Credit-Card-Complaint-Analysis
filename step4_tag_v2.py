import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))  # run from the project folder
import json
import time
import pandas as pd
import anthropic

DATA = "data/"
TEST_N = None         # test first; then change to None for all 916

TYPES = ["Fraud / unauthorised charge", "Merchant dispute",
         "Refund or credit not applied", "Issuer calculation error", "Other / unclear"]

SYSTEM = """You read US credit card dispute complaints and give TWO separate labels.

LABEL 1, dispute_type: WHAT the customer disputed. Pick exactly ONE:
- "Fraud / unauthorised charge": customer says they did not make or authorise the charge.
- "Merchant dispute": customer made the purchase but disagrees with the merchant: goods or services defective, not received, or not as described. Includes temporary credits reversed because the issuer accepted the merchant's evidence.
- "Refund or credit not applied": a refund or credit was due (return, cancellation, promised credit) but never posted.
- "Issuer calculation error": billing, interest, fees, rewards or benefit credits calculated wrongly by the issuer.
- "Other / unclear": none of the above, or too little detail.

LABEL 2, process_failure: HOW the issuer handled it. "yes" if the customer reports ANY of: delays or missed deadlines, evidence ignored or not reviewed, no explanation or documentation for the decision, repeated document requests, being passed between parties. Otherwise "no".

The two labels are independent: judge each on its own.
Reply with JSON only, no other text:
{"dispute_type": "<exact name>", "process_failure": "yes|no", "reason": "<max 15 words>"}"""

client = anthropic.Anthropic()

df = pd.read_csv(DATA + "credit_card_narratives.csv")
disputes = df[df["sub_issue"].str.startswith(
    "Credit card company isn't resolving a dispute", na=False)].copy()
if TEST_N:
    disputes = disputes.head(TEST_N)

results = []
for _, row in disputes.iterrows():
    text = str(row["consumer_complaint_narrative"])[:3000]
    try:
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=150,
            system=SYSTEM,
            messages=[{"role": "user", "content": text}],
        )
        raw = msg.content[0].text.strip().replace(
            "```json", "").replace("```", "")
        out = json.loads(raw)
        if out.get("dispute_type") not in TYPES:            # guardrail 1
            out["dispute_type"] = "Other / unclear"
        if out.get("process_failure") not in ("yes", "no"):  # guardrail 2
            out["process_failure"] = "no"
    except Exception as e:
        out = {"dispute_type": "ERROR", "process_failure": "", "reason": str(e)[
            :200]}
    out["complaint_id"] = row["complaint_id"]
    results.append(out)
    print(out["complaint_id"], "|", out["dispute_type"], "|",
          out["process_failure"], "|", out["reason"])
    time.sleep(0.2)

tags = pd.DataFrame(results)
merged = disputes.merge(tags, on="complaint_id")
merged.to_csv(DATA + "disputes_tagged_v2.csv", index=False)
print("\nSaved", len(merged), "rows")
print(merged["dispute_type"].value_counts())
print(merged["process_failure"].value_counts())
print(pd.crosstab(merged["dispute_type"], merged["process_failure"]))

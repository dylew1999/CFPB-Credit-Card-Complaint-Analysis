import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))  # run from the project folder
import json
import time
import pandas as pd
import anthropic

DATA = "data/"
TEST_N = None          # run 5 first; change to None for all 916

CATEGORIES = [
    "Fraud claim denied",
    "Merchant dispute lost",
    "Refund or credit not applied",
    "Investigation process failure",
    "Issuer calculation error",
    "Other / unclear",
]

SYSTEM = f"""You classify US credit card dispute complaints by ROOT CAUSE.
Pick exactly ONE category from this list:
1. Fraud claim denied: customer says they did not make or authorise the charge, and the issuer denied the claim.
2. Merchant dispute lost: goods or services were defective, not received, or not as described, and the issuer sided with the merchant. This INCLUDES cases where a temporary credit was reversed because the issuer accepted the merchant's evidence.
3. Refund or credit not applied: a refund or credit was promised or due but never posted. Do NOT use this if a credit was reversed after the issuer sided with the merchant (use 2).
4. Investigation process failure: delays, missed deadlines, no evidence or reasons given, evidence ignored.
5. Issuer calculation error: billing, interest, rewards or benefit credits calculated wrongly by the issuer.
6. Other / unclear: none of the above, or too little detail.
If several causes apply, pick the MAIN reason the customer says the dispute failed.
Reply with JSON only, no other text:
{{"root_cause": "<exact category name>", "confidence": "high|medium|low", "reason": "<max 15 words>"}}"""

client = anthropic.Anthropic()   # reads ANTHROPIC_API_KEY automatically

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
        if out.get("root_cause") not in CATEGORIES:     # guardrail
            out["root_cause"] = "Other / unclear"
    except Exception as e:
        out = {"root_cause": "ERROR", "confidence": "", "reason": str(e)[:80]}
    out["complaint_id"] = row["complaint_id"]
    results.append(out)
    print(out["complaint_id"], "|", out["root_cause"], "|", out["reason"])
    time.sleep(0.2)

tags = pd.DataFrame(results)
merged = disputes.merge(tags, on="complaint_id")
merged.to_csv(DATA + "disputes_tagged.csv", index=False)
print("\nSaved", len(merged), "rows")
print(merged["root_cause"].value_counts())

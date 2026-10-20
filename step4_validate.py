import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))  # run from the project folder
import pandas as pd

DATA = "data/"
CATS = ["Fraud claim denied", "Merchant dispute lost", "Refund or credit not applied",
        "Investigation process failure", "Issuer calculation error", "Other / unclear"]

df = pd.read_csv(DATA + "disputes_tagged.csv")

# 5 per category, then shuffle so they don't appear in order
sample = df.groupby("root_cause").sample(n=5, random_state=1)
sample = sample.sample(frac=1, random_state=2)

mine = []
for i, (_, row) in enumerate(sample.iterrows(), 1):
    print(f"\n===== {i}/{len(sample)} =====")
    print(str(row["consumer_complaint_narrative"])[:1200])
    for k, c in enumerate(CATS, 1):
        print(f"  {k}. {c}")
    while True:
        ans = input("Your tag (1-6): ").strip()
        if ans in {"1", "2", "3", "4", "5", "6"}:
            break
    mine.append(CATS[int(ans) - 1])

sample["my_tag"] = mine
sample["agree"] = sample["my_tag"] == sample["root_cause"]
sample[["complaint_id", "root_cause", "my_tag", "agree",
        "consumer_complaint_narrative"]].to_csv(DATA + "validation_30.csv", index=False)

print("\nAgreement:", round(100 * sample["agree"].mean(), 1), "%")
print(pd.crosstab(sample["root_cause"], sample["my_tag"]))

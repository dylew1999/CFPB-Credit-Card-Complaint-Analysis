import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))  # run from the project folder
import pandas as pd
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 20)

DATA = "data/"
TYPES = ["Fraud / unauthorised charge", "Merchant dispute",
         "Refund or credit not applied", "Issuer calculation error", "Other / unclear"]

df = pd.read_csv(DATA + "disputes_tagged_v2.csv")
df = df[df["dispute_type"] != "ERROR"]

sample = df.groupby("dispute_type").sample(n=6, random_state=1)
sample = sample.sample(frac=1, random_state=2)

mine = []
for i, (_, row) in enumerate(sample.iterrows(), 1):
    print(f"\n===== {i}/{len(sample)} =====")
    print(str(row["consumer_complaint_narrative"])[:1200])
    for k, t in enumerate(TYPES, 1):
        print(f"  {k}. {t}")
    while True:
        ans = input("WHAT was disputed? (1-5): ").strip()
        if ans in {"1", "2", "3", "4", "5"}:
            break
    mine.append(TYPES[int(ans) - 1])

sample["my_type"] = mine
sample["agree"] = sample["my_type"] == sample["dispute_type"]
sample[["complaint_id", "dispute_type", "my_type", "agree",
        "consumer_complaint_narrative"]].to_csv(DATA + "validation_v2_30.csv", index=False)

print("\nAgreement:", round(100 * sample["agree"].mean(), 1), "%")
print(pd.crosstab(sample["dispute_type"], sample["my_type"]))

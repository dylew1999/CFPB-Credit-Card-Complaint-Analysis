import pandas as pd

DATA = "/Users/diyaolew/Documents/cfpb-complaints/data/"
MERGE = {"Merchant dispute": "Merchant or refund dispute",
         "Refund or credit not applied": "Merchant or refund dispute"}

# 1. Final dataset for Tableau
df = pd.read_csv(DATA + "disputes_tagged_v2.csv")
df = df[df["dispute_type"] != "ERROR"].copy()
df["dispute_group"] = df["dispute_type"].replace(MERGE)
df.to_csv(DATA + "disputes_final.csv", index=False)
print(df["dispute_group"].value_counts())
print((100 * df["dispute_group"].value_counts(normalize=True)).round(1))

# 2. Re-score your validation with the same merge
v = pd.read_csv(DATA + "validation_v2_30.csv")
v["ai"] = v["dispute_type"].replace(MERGE)
v["me"] = v["my_type"].replace(MERGE)
print("\nAgreement after merge:", round(
    100 * (v["ai"] == v["me"]).mean(), 1), "%")

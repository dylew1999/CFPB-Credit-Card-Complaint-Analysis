import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))  # run from the project folder
import pandas as pd

PATH = "data/CCDB_Export_16_March_2026.csv"
OUT = "data/"

keep = ["Complaint ID", "Date received", "Date sent to company", "Product",
        "Sub-product", "Issue", "Sub-issue", "Consumer complaint narrative",
        "Company", "State", "Tags", "Submitted via",
        "Company response to consumer", "Timely response?"]

df = pd.read_csv(PATH, usecols=keep, low_memory=False)

# 1. Filter to credit cards
cc = df[df["Product"] == "Credit card"].copy()

# 2. snake_case column names
cc.columns = (cc.columns.str.lower()
              .str.replace("?", "", regex=False)
              .str.replace(r"[^a-z0-9]+", "_", regex=True)
              .str.strip("_"))

# 3. Real dates
cc["date_received"] = pd.to_datetime(cc["date_received"], errors="coerce")
cc["date_sent_to_company"] = pd.to_datetime(
    cc["date_sent_to_company"], errors="coerce")

# 4. Blank narratives become missing values
cc["consumer_complaint_narrative"] = (cc["consumer_complaint_narrative"]
                                      .astype("string").str.strip()
                                      .replace("", pd.NA))

# 5. Remove duplicate complaints
before = len(cc)
cc = cc.drop_duplicates(subset="complaint_id")

# --- Sanity checks ---
print("Rows:", len(cc), "| duplicates removed:", before - len(cc))
print("Date range:", cc["date_received"].min(),
      "to", cc["date_received"].max())
print("With narrative:", cc["consumer_complaint_narrative"].notna().sum())
print("\nTimely response:\n", cc["timely_response"].value_counts(dropna=False))
print("\nCompany response:\n",
      cc["company_response_to_consumer"].value_counts(dropna=False))
print("\nTop 10 issues:\n", cc["issue"].value_counts().head(10))

# --- Save two files ---
cc.to_csv(OUT + "credit_card_all.csv", index=False)
cc[cc["consumer_complaint_narrative"].notna()].to_csv(
    OUT + "credit_card_narratives.csv", index=False)
print("\nSaved both files.")

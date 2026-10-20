import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))  # run from the project folder
import pandas as pd

df = pd.read_csv(
    "data/credit_card_narratives.csv")

disputes = df[df["sub_issue"].str.startswith(
    "Credit card company isn't resolving a dispute", na=False)]
print("Dispute complaints with narratives:", len(disputes))

for text in disputes.sample(8, random_state=42)["consumer_complaint_narrative"]:
    print(text[:600])
    print("-" * 80)

# mischarging
# billing error
# synthetic record failure
# unauthorized transaction
# failed customer service
# misconduct behavior
# miscalculation
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))  # run from the project folder
import pandas as pd
import sqlite3

DATA = "data/"

df = pd.read_csv(DATA + "credit_card_all.csv")
conn = sqlite3.connect(DATA + "complaints.db")
df.to_sql("complaints", conn, if_exists="replace", index=False)

print(pd.read_sql("SELECT COUNT(*) AS n FROM complaints", conn))
conn.close()

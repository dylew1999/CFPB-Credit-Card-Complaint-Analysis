import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))  # run from the project folder
import pandas as pd

PATH = "data/CCDB_Export_16_March_2026.csv"

# 1. Peek at 5 rows only, which is fast even for a huge file
preview = pd.read_csv(PATH, nrows=5)
print("COLUMNS:")
print(preview.columns.tolist())

# 2. Load the full file
df = pd.read_csv(PATH, low_memory=False)
print("\nSHAPE (rows, columns):", df.shape)

# 3. What products are in here, and how many of each?
print("\nPRODUCT COUNTS:")
print(df["Product"].value_counts())

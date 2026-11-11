import pandas as pd

# 1. Load your CSV file into a DataFrame container
df = pd.read_csv("kampala_solar_data.csv")

# 2. Print the first 5 rows to check column headers and formatting
print("--- FIRST 5 ROWS ---")
print(df.head(5))

# 3. Check total row count and hunt for missing (null) values
print("\n--- DATA HEALTH & MISSING VALUES ---")
print(df.info())

# 4. Check min, max, and average values to spot sensor glitches
print("\n--- STATISTICAL SUMMARY ---")
print(df.describe())

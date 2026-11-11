import pandas as pd
import numpy as np

# 1. Load the messy raw log file
df = pd.read_csv("kampala_solar_data.csv")

# 2. Repair Sensor Glitches (Outliers)
# Any solar reading above the 500 kWp nameplate rating (or below 0) is broken hardware.
# We replace impossible values with np.nan so Pandas treats them as missing gaps.
df.loc[df["solar_available_kw"] > 500.0, "solar_available_kw"] = np.nan
df.loc[df["solar_available_kw"] < 0.0, "solar_available_kw"] = np.nan

# Same physical guardrail for our 800 kW max industrial factory load
df.loc[df["factory_load_kw"] > 800.0, "factory_load_kw"] = np.nan
df.loc[df["factory_load_kw"] < 0.0, "factory_load_kw"] = np.nan

# 3. Repair Missing Gaps using Linear Interpolation
# This smoothly estimates missing hours by averaging the neighboring hours
df["factory_load_kw"] = df["factory_load_kw"].interpolate(method="linear")
df["solar_available_kw"] = df["solar_available_kw"].interpolate(method="linear")

# 4. Save the clean, trustworthy dataset to a new file
df.to_csv("kampala_clean_data.csv", index=False)

# 5. Verify our repair work!
print("--- CLEANED DATA HEALTH ---")
print(df.info())
print("\n--- CLEANED STATISTICAL SUMMARY ---")
print(df.describe())

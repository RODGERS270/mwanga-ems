import pandas as pd

# 1. Simulate Spreadsheet A: Factory Meter Log (All 6 hours present: 00:00 to 05:00)
meter_df = pd.DataFrame({
    "timestamp": pd.to_datetime([
        "2026-11-10 00:00:00", "2026-11-10 01:00:00", "2026-11-10 02:00:00",
        "2026-11-10 03:00:00", "2026-11-10 04:00:00", "2026-11-10 05:00:00"
    ]),
    "factory_load_kw": [210.0, 205.0, 200.0, 205.0, 220.0, 280.0]
})

# 2. Simulate Spreadsheet B: Weather Station Log (Notice 03:00:00 is MISSING!)
weather_df = pd.DataFrame({
    "timestamp": pd.to_datetime([
        "2026-11-10 00:00:00", "2026-11-10 01:00:00", "2026-11-10 02:00:00",
        "2026-11-10 04:00:00", "2026-11-10 05:00:00"
    ]),
    "ambient_temp_c": [19.5, 19.0, 18.8, 18.5, 19.2],
    "irradiance_wm2": [0.0, 0.0, 0.0, 0.0, 15.0]
})

# 3. Method A: INNER Merge (Keeps only exact timestamp matches across both files)
inner_merged = pd.merge(meter_df, weather_df, on="timestamp", how="inner")
print("--- INNER MERGE RESULT (Notice 03:00 is dropped!) ---")
print(inner_merged)

# 4. Method B: OUTER Merge (Keeps all hours and exposes the missing weather gap as NaN)
outer_merged = pd.merge(meter_df, weather_df, on="timestamp", how="outer")
print("\n--- OUTER MERGE RESULT (Exposes 03:00 gap so we can interpolate!) ---")
print(outer_merged)

# 5. Repair the Outer Merge using linear interpolation
outer_merged["ambient_temp_c"] = outer_merged["ambient_temp_c"].interpolate(method="linear")
outer_merged["irradiance_wm2"] = outer_merged["irradiance_wm2"].interpolate(method="linear")

print("\n--- REPAIRED MASTER TABLE ---")
print(outer_merged)

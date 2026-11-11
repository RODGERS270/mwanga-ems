import pandas as pd
import numpy as np

# 1. Create a realistic 2-day timeline at 15-minute intervals (96 intervals per day = 192 rows)
timestamps = pd.date_range(start="2026-11-10 00:00:00", periods=192, freq="15min")

# 2. Generate synthetic 15-minute factory load readings (kW)
# Using a repeating pattern + slight random meter fluctuations
np.random.seed(42)  # Keeps random numbers consistent so you get exact repeatable results
base_pattern = [220, 210, 200, 205, 230, 310, 480, 650, 740, 770, 760, 730,
                610, 640, 780, 750, 700, 600, 490, 400, 330, 280, 240, 225]

# Repeat each hourly value 4 times (for 15-min intervals) across 2 days, plus small noise
load_15min = np.repeat(base_pattern, 4)
load_15min = np.tile(load_15min, 2) + np.random.normal(0, 12, size=192)

# 3. Build the raw DataFrame (simulating a CSV export where timestamp is plain text)
raw_df = pd.DataFrame({
    "timestamp_str": timestamps.astype(str),
    "meter_power_kw": np.round(load_15min, 1)
})

print("--- RAW 15-MINUTE METER LOG (FIRST 6 ROWS) ---")
print(raw_df.head(6))

# 4. Convert text timestamps into true Pandas Datetime objects and set as Index
raw_df["timestamp"] = pd.to_datetime(raw_df["timestamp_str"])
raw_df = raw_df.set_index("timestamp")

# Drop the old text column so only clean numeric columns remain
raw_df = raw_df.drop(columns=["timestamp_str"])

# 5. Resample 15-minute readings into 1-Hour Averages AND 1-Hour Peaks
hourly_df = pd.DataFrame()
hourly_df["avg_load_kw"] = raw_df["meter_power_kw"].resample("1h").mean().round(1)
hourly_df["peak_load_kw"] = raw_df["meter_power_kw"].resample("1h").max().round(1)

print("\n--- RESAMPLED HOURLY LOG (FIRST 8 HOURS) ---")
print(hourly_df.head(8))
print(f"\nTotal rows shrank from {len(raw_df)} (15-min) to {len(hourly_df)} (1-hour)!")

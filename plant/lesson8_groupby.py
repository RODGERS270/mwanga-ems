import pandas as pd
import numpy as np

# 1. Create a 7-day hourly timeline (Monday Nov 9 to Sunday Nov 15, 2026 = 168 hours)
timestamps = pd.date_range(start="2026-11-09 00:00:00", periods=168, freq="1h")
df = pd.DataFrame({"timestamp": timestamps})

# 2. Extract calendar clues directly from the timestamp
df["hour"] = df["timestamp"].dt.hour
df["day_name"] = df["timestamp"].dt.day_name()
df["day_of_week"] = df["timestamp"].dt.dayofweek  # Monday=0 ... Sunday=6

# Create a boolean flag: True if Saturday (5) or Sunday (6), else False
df["is_weekend"] = df["day_of_week"] >= 5

# 3. Simulate realistic factory load: Heavy on weekdays (up to 760 kW), low on weekends (~220 kW)
np.random.seed(10)
loads = []
for index, row in df.iterrows():
    if row["is_weekend"]:
        # Quiet weekend security/base load
        base = 210.0 + np.random.normal(0, 10)
    else:
        # Busy weekday shift peaking during daytime hours (8 AM to 5 PM)
        if 8 <= row["hour"] <= 17:
            base = 720.0 + np.random.normal(0, 25)
        else:
            base = 260.0 + np.random.normal(0, 15)
    loads.append(round(base, 1))

df["factory_load_kw"] = loads

# 4. GROUPBY TASK A: Find average and peak load for each Day of the Week
daily_summary = df.groupby("day_name")["factory_load_kw"].agg(["mean", "max"]).round(1)
print("--- AVERAGE & PEAK LOAD BY DAY OF WEEK ---")
print(daily_summary)

# 5. GROUPBY TASK B: Compare Typical Weekday vs. Weekend Hourly Curves
profile_comparison = df.groupby(["is_weekend", "hour"])["factory_load_kw"].mean().unstack(level=0).round(1)
profile_comparison.columns = ["Weekday_Avg_kW", "Weekend_Avg_kW"]

print("\n--- TYPICAL 24-HOUR PROFILE: WEEKDAY VS. WEEKEND (HOURS 6 TO 14) ---")
print(profile_comparison.loc[6:14])

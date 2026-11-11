import pandas as pd
import numpy as np

# 1. Create a 24-hour timeline at 15-minute resolution (96 intervals)
timestamps = pd.date_range(start="2026-11-11 00:00:00", periods=96, freq="15min")
df = pd.DataFrame({"timestamp": timestamps})

# 2. Simulate 15-minute Generator Output (kW) running between 300 kW and 650 kW
np.random.seed(7)
df["genset_power_kw"] = np.round(np.random.uniform(300.0, 650.0, size=96), 1)

# 3. Define the time step in hours (15 minutes = 15 / 60 = 0.25 hours)
DELTA_T_HOURS = 15.0 / 60.0

# 4. Calculate exact Energy (kWh) produced inside each 15-minute interval
df["interval_energy_kwh"] = df["genset_power_kw"] * DELTA_T_HOURS

# 5. Calculate the Cumulative Energy counter (.cumsum() acts like a digital kWh meter!)
df["cumulative_meter_kwh"] = df["interval_energy_kwh"].cumsum()

# 6. Calculate Total Daily Energy and Estimated Fuel Burn
total_daily_kwh = df["interval_energy_kwh"].sum()

# Using a specific fuel consumption of ~0.26 Liters/kWh and ~5,200 UGX/Liter
specific_fuel_l_per_kwh = 0.26
diesel_price_ugx = 9200.0

total_liters = total_daily_kwh * specific_fuel_l_per_kwh
total_cost_ugx = total_liters * diesel_price_ugx

print("--- 15-MINUTE ENERGY INTEGRATION LOG (FIRST 6 INTERVALS) ---")
print(df[["timestamp", "genset_power_kw", "interval_energy_kwh", "cumulative_meter_kwh"]].head(6))

print("\n--- 24-HOUR SUMMARY REPORT ---")
print(f"Total Daily Energy Generated : {total_daily_kwh:,.1f} kWh")
print(f"Estimated Diesel Consumed    : {total_liters:,.1f} Liters")
print(f"Estimated Daily Fuel Cost    : {total_cost_ugx:,.0f} UGX")

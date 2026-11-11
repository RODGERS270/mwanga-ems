import pandas as pd
import numpy as np

# 1. Create a 24-hour timeline (Hours 0 to 23)
hours = list(range(24))

# 2. Realistic Kampala Industrial Load Profile (kW) - Peaks around 750 kW
load_kw = [
    210.0, 205.0, 200.0, 205.0, 220.0, 280.0,  # 00:00 - 05:00 (Night base load)
    390.0, 540.0, 680.0, 730.0, 750.0, 740.0,  # 06:00 - 11:00 (Morning shift ramp)
    620.0, 650.0, 760.0, 745.0, 710.0, 630.0,  # 12:00 - 17:00 (Lunch dip & afternoon peak)
    510.0, 420.0, 350.0, 290.0, 240.0, 220.0   # 18:00 - 23:00 (Evening wind-down)
]

# 3. Realistic 500 kWp Solar PV Profile (kW) - Sun rises at 6 AM, sets at 6 PM
solar_kw = [
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0,              # 00:00 - 05:00 (Dark)
    15.0, 95.0, 210.0, 340.0, 430.0, 485.0,    # 06:00 - 11:00 (Morning sun rise)
    495.0, 470.0, 410.0, 310.0, 180.0, 45.0,   # 12:00 - 17:00 (Midday peak & afternoon)
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0               # 18:00 - 23:00 (Sunset)
]

# 4. Inject Intentional Field Faults for Learning!
# Fault A: Communication dropout at Hour 9 (Missing factory load) and Hour 14 (Missing solar)
load_kw[9] = np.nan
solar_kw[14] = np.nan

# Fault B: Broken sensor glitch at Hour 11 (Impossible 9,999 kW solar spike)
solar_kw[11] = 9999.0

# 5. Assemble into a Pandas DataFrame and save to CSV
df = pd.DataFrame({
    "hour": hours,
    "factory_load_kw": load_kw,
    "solar_available_kw": solar_kw
})

df.to_csv("kampala_solar_data.csv", index=False)
print("SUCCESS: 'kampala_solar_data.csv' created with intentional field faults!")

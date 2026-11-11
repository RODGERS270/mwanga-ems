import pandas as pd
import matplotlib.pyplot as plt

# 1. Load the sanitized dataset
df = pd.read_csv("kampala_clean_data.csv")

# 2. Set up the figure size (10 inches wide, 5 inches tall)
plt.figure(figsize=(10, 5))

# 3. Plot both curves with distinct colors and markers on each hourly data point
plt.plot(df["hour"], df["factory_load_kw"], label="Factory Load (kW)", color="black", linewidth=2, marker="o")
plt.plot(df["hour"], df["solar_available_kw"], label="Available Solar PV (kW)", color="orange", linewidth=2, marker="s")

# 4. Add a horizontal reference line showing the 1 MVA Generator's 30% Minimum Load (300 kW)
plt.axhline(y=300.0, color="red", linestyle="--", label="Genset 30% Min Floor (300 kW)")

# 5. Format labels, title, grid, and legend
plt.title("Mwanga EMS: Cleaned 24-Hour Kampala Load & Solar Profile")
plt.xlabel("Hour of Day (0 - 23)")
plt.ylabel("Power (kW)")
plt.xticks(range(0, 24))  # Show every hour tick clearly on the X-axis
plt.grid(True, linestyle=":", alpha=0.7)
plt.legend()

# 6. Display the interactive chart window
plt.tight_layout()
plt.show()

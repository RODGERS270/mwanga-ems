import pandas as pd
import pulp

# 1. Initialize the Optimization Problem Container
prob = pulp.LpProblem("Mwanga_Layer3_Optimizer", pulp.LpMinimize)

# 2. System Constants (From your formal project plan)
GENSET_MIN_LOAD = 300.0   # 30% of 1 MVA generator (kW)
GENSET_MAX_LOAD = 1000.0  # 1 MVA capacity (kW)
MAX_INVERTER_POWER = 250.0  # Inverter flow rating (kW)
EFFICIENCY_CH = 0.90
EFFICIENCY_DIS = 0.90
MIN_SAFE_ENERGY = 100.0   # 20% SoC buffer (kWh)
MAX_SAFE_ENERGY = 450.0   # 90% SoC ceiling (kWh)
INITIAL_ENERGY = 250.0    # 50% SoC starting point (kWh)

# 3. Load the Forecast Datasets from your DataFrame
df = pd.read_csv("kampala_solar_data.csv")
forecast_load = df["factory_load_kw"].tolist()
forecast_solar_avail = df["solar_available_kw"].tolist()

# 4. Declare Dictionaries for Hourly Decision Variables
P_ch = {}
P_dis = {}
P_pv = {}
P_gen = {}
E_bat = {}
X_state = {} # Binary switch: 1 = Charging, 0 = Discharging

# 5. Populate Variables for all 24 hours
for t in range(24):
    P_ch[t]   = pulp.LpVariable(f"P_ch_hour_{t}",   lowBound=0.0, upBound=MAX_INVERTER_POWER, cat=pulp.LpContinuous)
    P_dis[t]  = pulp.LpVariable(f"P_dis_hour_{t}",  lowBound=0.0, upBound=MAX_INVERTER_POWER, cat=pulp.LpContinuous)
    P_gen[t]  = pulp.LpVariable(f"P_gen_hour_{t}",  lowBound=GENSET_MIN_LOAD, upBound=GENSET_MAX_LOAD, cat=pulp.LpContinuous)
    P_pv[t]   = pulp.LpVariable(f"P_pv_hour_{t}",   lowBound=0.0, cat=pulp.LpContinuous)
    E_bat[t]  = pulp.LpVariable(f"E_bat_hour_{t}",  lowBound=MIN_SAFE_ENERGY, upBound=MAX_SAFE_ENERGY, cat=pulp.LpContinuous)
    X_state[t] = pulp.LpVariable(f"X_state_hour_{t}", cat=pulp.LpBinary)

# Add boundary variable for the final day-end handoff energy state
E_bat[24] = pulp.LpVariable("E_bat_hour_24", lowBound=MIN_SAFE_ENERGY, upBound=MAX_SAFE_ENERGY, cat=pulp.LpContinuous)

# 6. Add Initial Chronological Conditions
prob += (E_bat[0] == INITIAL_ENERGY), "Initial_Battery_Energy_State"

# 7. Apply Mathematical Constraints for Every Hour Step
for t in range(24):
    # Constraint 1: Electrical Power Balance Equation
    prob += (P_gen[t] + P_pv[t] + P_dis[t] == forecast_load[t] + P_ch[t]), f"Grid_Power_Balance_Hour_{t}"
    
    # Constraint 2: Weather-Driven Solar Production Cap
    prob += (P_pv[t] <= forecast_solar_avail[t]), f"Solar_Resource_Cap_Hour_{t}"
    
    # Constraint 3: Battery Energy Continuity Memory
    prob += (E_bat[t+1] == E_bat[t] + (P_ch[t] * EFFICIENCY_CH) - (P_dis[t] / EFFICIENCY_DIS)), f"SoC_Continuity_Hour_{t}"
    
    # Constraint 4 & 5: Mutual Exclusivity Interlocking via Binary Switch
    prob += (P_ch[t] <= MAX_INVERTER_POWER * X_state[t]), f"Inverter_Charge_Interlock_Hour_{t}"
    prob += (P_dis[t] <= MAX_INVERTER_POWER * (1 - X_state[t])), f"Inverter_Discharge_Interlock_Hour_{t}"

# 8. Append the Cost Minimization Objective Function
prob += pulp.lpSum(1.0 * P_gen[t] + 0.01 * (forecast_solar_avail[t] - P_pv[t]) for t in range(24))

# 9. Execute Numerical Solver Matrix Optimization
# We suppress the raw solver console output trace text to keep our report clean
prob.solve(pulp.PULP_CBC_CMD(msg=False))

# 10. Process Optimized Output Back into our Pandas Columns Dataframe
opt_solar = []
opt_genset = []
opt_soc = []
opt_battery_power = []

for t in range(24):
    opt_solar.append(round(pulp.value(P_pv[t]), 1))
    opt_genset.append(round(pulp.value(P_gen[t]), 1))
    opt_soc.append(round((pulp.value(E_bat[t]) / 500.0) * 100, 1))
    
    # Calculate net inverter direction (Positive = Charging, Negative = Discharging)
    net_power = pulp.value(P_ch[t]) - pulp.value(P_dis[t])
    opt_battery_power.append(round(net_power, 1))

# Write columns into DataFrame
df["opt_solar_kw"] = opt_solar
df["opt_genset_kw"] = opt_genset
df["opt_battery_soc_pct"] = opt_soc
df["opt_battery_net_kw"] = opt_battery_power

# Export complete mathematical planning matrix sheet
df.to_csv("mil_predictive_results.csv", index=False)

print(f"OPTIMIZATION COMPLETE. Solver Status: {pulp.LpStatus[prob.status]}")
print(f"Total Optimized Diesel Generation: {sum(opt_genset):,.1f} kWh")

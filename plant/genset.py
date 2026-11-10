# plant/genset.py
"""
Mwanga EMS - Diesel Generator Plant Module
Models the mechanical behavior, non-linear fuel consumption curve, 
and thermal safety loading thresholds of a 1 MVA C&I generator.
"""

class DieselGenerator:
    def __init__(self, capacity_kva=1000.0, power_factor=0.8,
                  min_load_pct=0.30, idle_fuel_coeff=0.08,
                    load_fuel_coeff=0.22):
        # 1. Physical Capacity & Sizing (1 MVA Reference Case)
        self.capacity_kva = capacity_kva
        self.power_factor = power_factor
        # Calculate maximum active power output in kW (1000 kVA * 0.8 = 800 kW)
        self.max_power_kw = capacity_kva * power_factor
        
        # 2. Thermal Safety Threshold (30% Minimum Load Boundary)
        self.min_load_pct = min_load_pct
        self.min_power_kw = self.max_power_kw * min_load_pct # 240 kW safe operating floor
        
        # 3. Mechanical Fuel Curve Coefficients (Liters per Hour metrics)
        self.idle_fuel_coeff = idle_fuel_coeff  # Fixed fuel burn rate just to keep engine spinning
        self.load_fuel_coeff = load_fuel_coeff  # Extra fuel consumed per kW of electrical load
        
        # 4. Operational State Variables
        self.is_running = False
        self.current_output_kw = 0.0

    def calculate_fuel_rate(self, power_kw):
        """
        Calculates instantaneous fuel consumption rate in Liters per Hour.
        Uses the non-linear fuel curve equation: F = (alpha * P_max) + (beta * P_actual)
        """
        if not self.is_running or power_kw <= 0:
            return 0.0
            
        # Fixed idle fuel burn just to spin the engine at speed
        idle_burn = self.idle_fuel_coeff * self.max_power_kw  # 0.08 * 800 = 64 L/h
        
        # Incremental fuel burn per kilowatt of active load carried
        load_burn = self.load_fuel_coeff * power_kw            # 0.22 * power_kw
        
        return idle_burn + load_burn

    def step(self, command_power_kw, delta_t_hours=0.25):
        """
        Executes a generator simulation step (default 15 minutes / 0.25 hours).
        Returns a dictionary containing actual power delivered, fuel burned, and safety status.
        """
        # 1. Evaluate engine state based on the power command
        if command_power_kw <= 0:
            self.is_running = False
            self.current_output_kw = 0.0
            return {"power_kw": 0.0, "fuel_liters": 0.0, "wet_stacking_alert": False}
            
        self.is_running = True
        
        # 2. Enforce the hard maximum active power limit (800 kW)
        actual_power = min(command_power_kw, self.max_power_kw)
        self.current_output_kw = actual_power
        
        # 3. Calculate fuel consumed during this specific time window
        fuel_rate_per_hour = self.calculate_fuel_rate(actual_power)
        fuel_consumed = fuel_rate_per_hour * delta_t_hours
        
        # 4. Check for thermal safety violations (30% Load Floor / 240 kW)
        # We do not override the command here because a generator MUST follow the load to stay stable,
        # but we trigger a warning flag so the higher-level controller knows it must adjust the solar/battery.
        wet_stacking_alert = actual_power < self.min_power_kw
        
        return {
            "power_kw": round(actual_power, 2),
            "fuel_liters": round(fuel_consumed, 2),
            "wet_stacking_alert": wet_stacking_alert
        }

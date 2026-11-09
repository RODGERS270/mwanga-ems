# plant/battery.py
"""
Mwanga EMS - Battery Storage Plant Module
Models the physical behavior of a 500 kWh lithium-ion battery system,
accounting for charging efficiency, power limits, and State of Charge (SOC).
"""

class BatterySystem:
    def __init__(self, capacity_kwh=500.0, soc_min=0.20,
                  soc_max=0.90, initial_soc=0.50, max_power_kw=250.0, efficiency=0.95):
        self.capacity_kwh = capacity_kwh          # Total energy bucket capacity (500 kWh)
        self.soc_min = soc_min                    # Minimum safe floor (20% to protect lifespans)
        self.soc_max = soc_max                    # Maximum safe ceiling (90% capacity)
        self.soc = initial_soc                    # Current state of charge (normalized 0.0 to 1.0)
        self.max_power_kw = max_power_kw          # Physical power rating of the grid inverter (250 kW)
        self.efficiency = efficiency              # One-way internal resistance efficiency (95%)
    def step_discharge(self, command_power_kw, delta_t_hours=0.25):
        """
        Processes battery discharging logic for a discrete time step.
        command_power_kw: Positive value (+) representing requested discharge power.
        """
        # 1. Enforce the physical inverter thermal capacity limit (250 kW)
        target_power = min(command_power_kw, self.max_power_kw)
        
        # 2. Calculate current chemical energy pool
        current_energy_kwh = self.soc * self.capacity_kwh
        
        # 3. Determine energy floor constraint (20% SOC safety limit)
        energy_floor_kwh = self.soc_min * self.capacity_kwh
        max_energy_available = current_energy_kwh - energy_floor_kwh
        
        # 4. Apply efficiency degradation to find maximum output capability
        # Internal resistance turns 5% of energy into heat before it leaves the battery box
        max_power_available = (max_energy_available / delta_t_hours) * self.efficiency
        
        # 5. Lock in actual power delivery after applying all structural limits
        actual_power = min(target_power, max_power_available)
        
        # 6. Apply Coulomb Counting subtraction to update internal storage state
        # Note: We must divide by efficiency because cell drain is greater than output power
        energy_drained = (actual_power / self.efficiency) * delta_t_hours
        new_energy_kwh = current_energy_kwh - energy_drained
        
        # 7. Update normalized State of Charge variable
        self.soc = new_energy_kwh / self.capacity_kwh
        
        return actual_power
    def get_status(self):
        """Returns a snapshot of the current state of the battery."""
        return {
            "soc_percent": round(self.soc * 100, 2),
            "stored_energy_kwh": round(self.soc * self.capacity_kwh, 2)
        }

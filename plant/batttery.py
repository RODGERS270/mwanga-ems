"""
Mwanga EMS - Physical Battery Asset Simulator.
Models capacity constraints, safe operational boundaries, and efficiency losses.
"""

class BatterySystem:
    def __init__(self, capacity_kwh=500.0, soc_min=0.20,
                  soc_max=0.90, initial_soc=0.50,
                 max_power_kw=250.0, efficiency=0.95):
        self.capacity_kwh = capacity_kwh          # Total energy size (500 kWh Reference Site)
        self.soc_min = soc_min                    # Lower safe threshold floor (20% SOC)
        self.soc_max = soc_max                    # Upper safe threshold ceiling (90% SOC)
        self.soc = initial_soc                    # Starting point (50% full at morning boot)
        self.max_power_kw = max_power_kw          # Inverter thermal limit constraint (250 kW)
        self.efficiency = efficiency              # Internal resistance round-trip efficiency (95%)

    def step_discharge(self, command_power_kw, delta_t_hours=0.25):
        """
        Executes a discharging simulation step (default 15 minutes).
        command_power_kw: Positive (+) requested discharge power in kW.
        """
        # 1. Enforce the physical inverter hardware limit (Max 250 kW)
        target_power = min(command_power_kw, self.max_power_kw)
        
        # 2. Calculate current chemical energy stored
        current_energy_kwh = self.soc * self.capacity_kwh
        
        # 3. Apply the 20% safe boundary floor rule
        energy_floor_kwh = self.soc_min * self.capacity_kwh
        max_energy_available = current_energy_kwh - energy_floor_kwh
        
        # 4. Turn available energy into power, factoring in our 95% efficiency losses
        # We multiply by efficiency here because thermal losses reduce the power output
        max_power_available = (max_energy_available / delta_t_hours) * self.efficiency
        
        # 5. Lock in the absolute safe power output
        actual_power = min(target_power, max_power_available)
        if actual_power < 0:
            actual_power = 0.0
            
        # 6. Coulomb Counting update: Calculate how much chemical energy is drained
        # We divide by efficiency because the internal chemical pool drains FASTER 
        # than the useful electricity showing up on the grid due to heat losses.
        energy_drained_kwh = (actual_power / self.efficiency) * delta_t_hours
        new_energy_kwh = current_energy_kwh - energy_drained_kwh
        
        # 7. Update our current State of Charge metric
        self.soc = new_energy_kwh / self.capacity_kwh
        
        return actual_power

    def step_charge(self, command_power_kw, delta_t_hours=0.25):
        """
        Executes a charging simulation step (default 15 minutes).
        command_power_kw: Negative (-) requested charging power in kW.
        """
        # 1. Enforce physical inverter power boundaries
        # Since charging power is negative, we use max() to stay within the -250 kW limit
        target_power = max(command_power_kw, -self.max_power_kw)
        
        # 2. Calculate the current chemical energy pool
        current_energy_kwh = self.soc * self.capacity_kwh
        
        # 3. Apply the 90% safe boundary ceiling rule
        energy_ceiling_kwh = self.soc_max * self.capacity_kwh
        max_energy_room = energy_ceiling_kwh - current_energy_kwh
        
        # 4. Determine maximum acceptable power input, factoring in efficiency losses
        # We divide by efficiency because we must supply MORE electrical power 
        # to fill up the internal room due to heat dissipation
        max_power_acceptable = (max_energy_room / delta_t_hours) / self.efficiency
        
        # 5. Lock in actual power absorption after applying boundaries
        # We take the maximum value (closest to 0) to prevent overcharging
        actual_power = max(target_power, -max_power_acceptable)
        if actual_power > 0:
            actual_power = 0.0
            
        # 6. Coulomb Counting update: Calculate energy stored inside the chemical core
        # We multiply by efficiency because only 95% of incoming power successfully locks in
        # Note: actual_power is negative, so subtracting a negative number adds energy
        energy_stored_kwh = actual_power * self.efficiency * delta_t_hours
        new_energy_kwh = current_energy_kwh - energy_stored_kwh
        
        # 7. Update our current State of Charge metric
        self.soc = new_energy_kwh / self.capacity_kwh
        
        return actual_power

    def step(self, command_power_kw, delta_t_hours=0.25):
        """
        Master interface to execute a simulation time step.
        Positive (+) power commands = DISCHARGE
        Negative (-) power commands = CHARGE
        """
        if command_power_kw >= 0:
            return self.step_discharge(command_power_kw, delta_t_hours)
        else:
            return self.step_charge(command_power_kw, delta_t_hours)

    def get_status(self):
        """Returns a quick snapshot of the current state of the battery."""
        return {
            "soc_percent": round(self.soc * 100, 2),
            "stored_energy_kwh": round(self.soc * self.capacity_kwh, 2)
        }

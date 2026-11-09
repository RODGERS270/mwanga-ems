# Mwanga EMS: An Open, Forecast-Aware Hybrid Microgrid Controller

Mwanga (*Light*) EMS is an open-source, split-architecture Energy Management System (EMS) designed for Commercial and Industrial (C&I) microgrids in East Africa. 

The system optimizes the operational dispatch of a grid-tied system consisting of:
- 500 kWp Solar PV Array
- 500 kWh Battery Energy Storage System (BESS)
- 1 MVA Diesel Generator (Backup/Island support)
- 800 kW Peak Industrial Load

## The Engineering Challenge
In sub-Saharan industrial systems, energy controllers face conflicting operational bounds:
1. **Zero-Export Mandates:** Local distribution networks often strictly prohibit solar energy from flowing backward into the utility grid.
2. **Genset Minimum Loading:** During utility blackouts, diesel generators must be maintained at a minimum of 30% loading to prevent wet stacking (unburnt fuel accumulation and engine slobbering).

When factory loads drop on a sunny day, a standard controller simply wastes (curtails) clean solar power. Mwanga EMS uses machine learning forecasts and predictive optimization to intelligently store that surplus instead.

## Split-Architecture Design
To maximize safety and computational efficiency, the project splits control into two distinct layers:
- **Layer 3 (The Planner):** Runs on an edge gateway (Python). It digests day-ahead machine learning weather/load forecasts and runs a receding-horizon optimization algorithm to schedule the battery.
- **Layer 2 (The Safety Supervisor):** Runs on a physical microcontroller (C++ firmware) with a fast 100ms deterministic execution loop. It strictly enforces zero-export boundaries and genset protection, ignoring the planner if communication fails.
- **Layer 1 (Physical Protection):** Independent hardware reverse-power and over-current relays.

## Validation Ladder Strategy
The controller's performance is rigorously verified across a multi-stage validation ladder:
1. **Model-in-the-Loop (MIL):** Pure Python asset and economic baseline simulations.
2. **Software-in-the-Loop (SIL):** Compiled C++ controller code communicating with a Python plant model via network sockets.
3. **Controller Hardware-in-the-Loop (CHIL):** Target microcontroller silicon communicating over industrial Modbus TCP registers with the laptop-hosted plant simulator.

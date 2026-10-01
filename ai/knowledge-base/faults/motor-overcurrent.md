---
id: FAULT-004
title: Motor Overcurrent
category: electrical
equipment: motor
severity: high
sensors:
  - current
  - temperature
  - vibration
---

# Motor Overcurrent

## Description
Motor overcurrent occurs when the electric current drawn by the motor stator windings persistently exceeds the continuous Full Load Amperage (FLA) or nameplate design capacity. Overcurrent conditions can be caused by mechanical overloads, electrical supply deviations, inter-turn winding deterioration, or rotor bar defects. Sustained overcurrent rapidly accelerates I²R resistive heating in the windings, trips protective overcurrent relays or circuit breakers, and risks permanent insulation breakdown.

## Typical Symptoms
- Continuous current readings substantially higher than motor nameplate full-load amperage.
- Frequent tripping of electronic motor protective relays, thermal magnetic breakers, or VFD overcurrent fault trips.
- Observable motor hum, audible straining noise under operational duty, or diminished motor speed (increased slip).
- Accelerated heating of stator windings, supply cabling, and terminal junctions.
- In severe electrical breakdown cases, arcing, blown fuses, or scorched terminal lugs.

## Possible Causes
- Driven equipment overload (jammed pump impeller, clogged discharge pipe, mechanical drag, excessive product viscosity).
- Low supply voltage (forcing the motor to draw higher current to supply rated shaft output power for constant-torque loads).
- Severe voltage unbalance among supply phases (a 1% voltage unbalance can trigger an 8-10% current unbalance).
- Stator winding degradation, turn-to-turn micro-faults, or single-phasing condition.
- Mechanical binding or severe misalignment in bearings, couplings, or driven process machinery.
- High inertia start-ups or excessive duty-cycle cycling without adequate thermal cooling recovery.

## Sensor Indicators

| Sensor Parameter | Observed Pattern | Diagnostic Significance | Correlation with Other Readings |
| :--- | :--- | :--- | :--- |
| **Current** | Significantly higher than normal baseline and exceeding FLA rating | Primary and direct indicator of electrical or mechanical overcurrent condition | Direct quantitative measure of motor electrical load |
| **Temperature** | Rising gradually or rapidly following current elevation | Consequence of I²R resistive losses in the copper windings and iron core | Tracks current with a thermal lag depending on motor mass and cooling |
| **Vibration** | Normal, or elevated if overcurrent is driven by mechanical binding or unbalance | Corroborating indicator for mechanical root causes vs. electrical supply issues | High vibration + high current points to mechanical jamming or misalignment |
| **Pressure** | Abnormally high in discharge lines if flow resistance causes hydraulic overload | Systemic indicator in fluid transfer loops | High pump discharge pressure directly induces motor overcurrent |
| **Humidity** | Generally neutral; extreme humidity can compromise insulation resistance | Secondary contributing factor | Can lead to ground leakage currents if insulation is degraded |

## Recommended Checks
1. Compare measured line current on each phase against the motor nameplate FLA and Service Factor (SF).
2. Measure phase-to-phase line voltages under full operating load; determine voltage unbalance and check for under-voltage.
3. Check the driven load: uncouple the motor and run uncoupled to isolate whether overcurrent is driven by internal motor faults or external machine drag.
4. Manually rotate the uncoupled pump/shaft by hand (with power locked out) to check for binding, rubbing, or tight spots.
5. Inspect downstream valves, line blockages, or high-viscosity product delivery issues contributing to pump overload.
6. Verify overcurrent protection relay settings, VFD current limit parameters, and overload trip curves.

## Safety
- High electrical arc-flash hazard: Do not open energized motor control centers or terminal boxes without appropriate NFPA 70E arc-rated PPE.
- Rapid thermal rise: Overloaded motors and feeder conduits can reach flashpoint temperatures; keep combustible materials clear.
- Lockout/Tagout (LOTO): Isolate and verify zero energy before opening electrical junction boxes or performing mechanical load uncoupling.

## Related Faults
- [FAULT-003: Motor Overheating](motor-overheating.md)
- [FAULT-009: High Pressure](high-pressure.md)
- [FAULT-005: Excessive Motor Vibration](motor-vibration.md)

---
id: FAULT-003
title: Motor Overheating
category: thermal
equipment: motor
severity: critical
sensors:
  - temperature
  - current
  - vibration
---

# Motor Overheating

## Description
Motor overheating is an operating condition where the stator winding insulation, rotor, or motor frame exceeds the designated maximum thermal limit (such as NEMA or IEC insulation classes B, F, or H). Thermal stress is one of the leading causes of premature electric motor failure. Operating a motor above its rated insulation temperature reduces winding insulation life exponentially (the Arrhenius rule states insulation life halves for roughly every 10 °C rise above thermal class), ultimately causing turn-to-turn shorts, ground faults, and catastrophic motor burnout.

## Typical Symptoms
- Abnormally high casing, stator, or bearing frame surface temperatures detectable by touch or thermal imaging.
- Burning odor of varnish, insulation resin, or overheated cable jacket material.
- Tripping of thermal overload relays, motor circuit protectors (MCP), or embedded RTD/PTC alarms.
- Discoloration or blistered paint on the motor stator frame.
- Reduced motor speed or increased acoustic drone under load.

## Possible Causes
- Electrical overload: Motor operating above rated shaft horsepower or service factor for prolonged durations.
- High supply voltage, low supply voltage, or phase voltage unbalance (even a 2-3% voltage unbalance causes substantial winding heating).
- Restricted or blocked cooling airflow (clogged fan cowl, dust accumulation on motor cooling fins, broken fan impellers).
- Excessive ambient temperature or restricted enclosure ventilation in the operating environment.
- High start-stop duty cycle exceeding the motor's rated thermal capacity and starts-per-hour limit.
- Mechanical binding, severe bearing degradation, or pump downstream clogging exerting excessive counter-torque.
- Harmonic heating caused by variable frequency drives (VFD) without appropriate dV/dt or sine-wave filtering.

## Sensor Indicators

| Sensor Parameter | Observed Pattern | Diagnostic Significance | Correlation with Other Readings |
| :--- | :--- | :--- | :--- |
| **Temperature** | High, sustained or escalating trend across motor body and stator | Primary symptom confirming thermal overload | Directly matches thermal dissipation trends across stator |
| **Current** | Consistently elevated above full-load amperage (FLA) rating | Direct root cause indicator if overheating is due to electrical overload | Strong correlation with temperature rise when current is sustained above FLA |
| **Vibration** | Normal to moderately elevated (thermal expansion unbalance or bearing friction) | Secondary or contributing factor; mechanical drag increases current | Elevated vibration combined with high current indicates mechanical binding |
| **Pressure** | High in downstream pumping lines if flow restriction creates motor overload | Indirect indicator in pumping systems | High discharge pressure correlates with motor overcurrent and thermal rise |
| **Humidity** | High ambient humidity combined with thermal cycling may degrade winding insulation | Environmental factor | Condensation within enclosure when cooled down accelerates insulation breakdown |

## Recommended Checks
1. Measure surface temperature profile using an infrared camera to locate hotspots (stator core vs. drive-end bearing vs. cooling fins).
2. Measure three-phase operating currents and phase voltages using a true-RMS clamp meter; calculate voltage unbalance percentage.
3. Verify that cooling air intake and discharge pathways are clean, fan cowl is unobstructed, and external cooling fins are free of oil and debris.
4. Inspect external cooling fan on the non-drive-end to ensure it is intact and securely keyed to the shaft.
5. Check motor nameplate ratings against actual operating duty (service factor, ambient rating, continuous duty rating S1).
6. Perform winding insulation resistance (Megger test) and winding resistance balance test when motor is safely isolated and de-energized.

## Safety
- Burn hazard: Motor casing and terminal enclosure can reach temperatures well in excess of 90 °C; avoid unshielded skin contact.
- Fire/Explosion hazard: Severely overheated motors present fire risks in the presence of volatile dust, fibers, or chemical vapors.
- Electrical Isolation: Adhere strictly to LOTO procedures before inspecting the terminal box, measuring winding resistance, or opening cooling shrouds.

## Related Faults
- [FAULT-004: Motor Overcurrent](motor-overcurrent.md)
- [FAULT-001: Bearing Overheating](bearing-overheating.md)
- [FAULT-009: High Pressure](high-pressure.md)

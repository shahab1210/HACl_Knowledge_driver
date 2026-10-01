---
id: FAULT-009
title: High Pressure
category: hydraulic
equipment: pump
severity: high
sensors:
  - pressure
  - current
  - temperature
---

# High Pressure

## Description
A high-pressure fault condition occurs when fluid pressure within the pump casing, discharge manifold, or downstream distribution network exceeds rated design limits. Excessive pressure puts severe mechanical stress on pipe walls, pump casings, gaskets, and mechanical seals. In positive displacement pumps, unchecked high pressure can cause catastrophic casing rupture or motor stall. In centrifugal pumps, prolonged high pressure (operating near or at shut-off head) leads to rapid fluid churning, violent overheating of the fluid volume inside the casing, vapor expansion, and mechanical seal destruction.

## Typical Symptoms
- Pressure sensors and analog pressure gauges indicating values consistently exceeding normal upper operating thresholds.
- Frequent popping or continuous venting of pressure safety relief valves (PRV) or rupture disks.
- Motor straining, drawing high current (in positive displacement pumps) or excessive casing heating (in dead-headed centrifugal pumps).
- Deformed pipe hangers, pipe hammering, or strained flange connections.
- Weeping or extrusion of flange gaskets and premature failure of pump mechanical seals.

## Possible Causes
- Downstream blockage: Closed or throttled isolation valve, clogged filter/strainer, or blocked line orifice.
- Sluggish or jammed pressure regulating valve, backpressure control valve, or downstream control valve failing closed.
- Solidification, crystallization, or excessive viscosity increase of process fluid in cold or uninsulated lines.
- Over-speed operation of a variable speed drive (VFD) driving the pump beyond rated RPM.
- Over-filling or hydraulic lock in closed-loop thermal expansion systems without accumulator cushioning.
- Starting a positive displacement pump against a closed discharge valve.

## Sensor Indicators

| Sensor Parameter | Observed Pattern | Diagnostic Significance | Correlation with Other Readings |
| :--- | :--- | :--- | :--- |
| **Pressure** | Sustained high reading or sharp escalation above safe operational threshold | Primary and direct indicator of downstream restriction or hydraulic overpressure | Direct measure defining the fault |
| **Current** | Significantly high in positive displacement pumps; low to moderate in dead-headed centrifugal pumps | Key discriminator for pump type and operating state under high-pressure conditions | High pressure + high current indicates positive displacement overload |
| **Temperature** | Steep rise in pump casing and seal cavity temperature under dead-head conditions | Energy input from rotating impeller converts directly into fluid thermal energy | High pressure + high pump casing temp confirms dead-head operation |
| **Vibration** | Elevated low-frequency vibration or acoustic resonance from hydraulic turbulence | Hydraulic shock and pressure wave reflections against casing cutwater | Correlates with fluid pulsations and hydraulic strain |
| **Humidity** | Ambient; may spike if safety relief valve discharges steam or hot fluid | Secondary indicator of safety relief discharge | Elevated humidity confirms relief valve release into environment |

## Recommended Checks
1. Immediately inspect line lineup: verify all manual and automated downstream isolation valves are in their correct operating position.
2. Check differential pressure across downstream inline filters, heat exchangers, strainers, or check valves.
3. Test operation and setpoint of pressure safety valves (PSV) and automated pressure relief bypass circuits.
4. Verify pump speed command and feedback from the variable frequency drive (VFD).
5. In dead-head centrifugal scenarios, inspect casing temperature and vent vapor pockets safely after cooling.
6. Check for product freezing, waxing, or crystallization in heat-traced lines or ambient exposed piping.

## Safety
- Catastrophic rupture risk: Overpressured vessels, pump casings, and piping can suffer explosive failure, throwing metal fragments.
- Thermal scalding: Dead-headed pumps turn trapped water into superheated steam within minutes; opening drains or vents can cause severe steam burns.
- Pressure Relief: Always ensure certified pressure relief devices are installed upstream of any potential block valve.
- Lockout/Tagout (LOTO): Depressurize system completely and tag out motor power prior to breaking flanges or disassembling valves.

## Related Faults
- [FAULT-004: Motor Overcurrent](motor-overcurrent.md)
- [FAULT-003: Motor Overheating](motor-overheating.md)
- [FAULT-008: Low Pressure](low-pressure.md)

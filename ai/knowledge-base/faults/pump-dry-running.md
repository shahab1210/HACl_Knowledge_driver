---
id: FAULT-007
title: Pump Dry Running
category: hydraulic
equipment: pump
severity: critical
sensors:
  - current
  - pressure
  - temperature
---

# Pump Dry Running

## Description
Pump dry running occurs when a pump operates without sufficient liquid inside the casing and internal passages. Fluid pumps rely on the pumped liquid not only to generate hydraulic head and flow, but crucially to lubricate and cool internal wear rings, bushings, sleeve bearings, and mechanical seal faces. Operating dry causes immediate loss of hydraulic load, thermal destruction of seal faces within seconds, galling or seizing of rotating wear rings, thermal distortion of the shaft, and catastrophic pump failure.

## Typical Symptoms
- Sudden drop of motor current to near no-load baseline amperage.
- Complete loss of pump discharge pressure and zero fluid flow in the process line.
- Intense squealing, screaming, or rattling noise from unlubricated seal faces and contact rings.
- Rapid, severe temperature spike on the stuffing box, seal gland, and pump casing.
- Visible smoke, vapor emissions, or charred seal elastomers around the shaft gland.

## Possible Causes
- Empty supply reservoir, tank dry-out, or liquid level dropping below intake pipe suction bell.
- Closed suction isolation valve or completely blocked suction strainer.
- Loss of pump prime or air-binding within the pump casing and suction volute.
- Vapor pocket entrapment following improper system startup or incomplete venting procedures.
- Upstream pipe rupture, foot-valve failure, or false level transmitter reading in suction vessel.

## Sensor Indicators

| Sensor Parameter | Observed Pattern | Diagnostic Significance | Correlation with Other Readings |
| :--- | :--- | :--- | :--- |
| **Current** | Drops abruptly to no-load motor current level | Key diagnostic indicator; fluid pump operates with zero hydraulic work | Coincides directly with zero discharge pressure |
| **Pressure** | Plummets to zero or ambient atmospheric head | Primary hydraulic indicator confirming absence of fluid displacement | Correlates with drop in electrical current |
| **Temperature** | Rapid, intense temperature spike at mechanical seal and pump casing | Result of dry friction between stationary and rotating seal faces / wear rings | Rises rapidly while current remains minimal |
| **Vibration** | Variable: high friction squeal or low hydraulic turbulence vibration | Reflects mechanical rubbing without hydraulic damping | High-frequency friction spikes without hydraulic fluid pulses |
| **Humidity** | May rise if residual fluid flashes into steam around hot seal faces | Secondary environmental indicator | Steam release near gland can register localized humidity increase |

## Recommended Checks
1. Immediately check motor current draw; confirm whether the motor is spinning with minimal electrical load (no-load amps).
2. Inspect liquid level and suction tank transmitters; verify actual physical liquid level via sight glass.
3. Check status of all suction line isolation valves and automated control valves.
4. Verify whether the pump volute and suction line are properly vented and primed with liquid.
5. Inspect mechanical seal faces for thermal cracking (heat checking), blistered carbon, or melted elastomer O-rings.
6. Once de-energized, check if the pump shaft can still be freely turned by hand; check for galling or seizure between impeller wear rings and casing.

## Safety
- Immediate equipment damage: Dry running must trigger immediate automatic shutdown to avoid seal explosion or shaft seizure.
- Thermal flash / Pressure hazard: Never suddenly inject cold liquid into a dry-run overheated pump casing; thermal shock can shatter cast iron/alloy volutes.
- Toxic / Hot Vapor Release: Scorched seal faces can release toxic decomposition gases or superheated steam.
- Lockout/Tagout (LOTO): Isolate power and hydraulic pressure before opening pump casing or disassembling the seal gland.

## Related Faults
- [FAULT-006: Pump Cavitation](pump-cavitation.md)
- [FAULT-008: Low Pressure](low-pressure.md)
- [FAULT-001: Bearing Overheating](bearing-overheating.md)
